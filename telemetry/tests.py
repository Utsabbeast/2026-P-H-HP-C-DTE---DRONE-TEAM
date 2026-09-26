from datetime import datetime, timezone as dt_timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from .models import DroneTelemetry, PhoneTelemetry
from .serializers import DroneTelemetrySerializer, PhoneTelemetrySerializer
from .simulation import SimulationEngine


class DroneTelemetryModelTest(TestCase):
    def test_create_telemetry_record(self):
        now = timezone.now()
        record = DroneTelemetry.objects.create(
            drone_id='drone01',
            latitude=30.9010,
            longitude=75.8573,
            altitude=125.4,
            heading=142.0,
            timestamp=now,
            is_simulated=False,
        )
        self.assertEqual(record.drone_id, 'drone01')
        self.assertAlmostEqual(record.latitude, 30.9010)
        self.assertAlmostEqual(record.longitude, 75.8573)
        self.assertFalse(record.is_simulated)
        self.assertTrue(record.is_connected())
        self.assertIn('30.9010', str(record))
        self.assertIn('HW', str(record))


class DroneTelemetrySerializerTest(TestCase):
    def test_valid_serializer(self):
        data = {
            "drone_id": "drone01",
            "latitude": 30.9010,
            "longitude": 75.8573,
            "altitude": 125.4,
            "heading": 142.0,
            "timestamp": "2026-09-26T12:45:32Z",
            "is_simulated": False
        }
        serializer = DroneTelemetrySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.drone_id, 'drone01')
        self.assertFalse(instance.is_simulated)

    def test_invalid_coordinates(self):
        data = {
            "drone_id": "drone01",
            "latitude": 95.0,  # Invalid latitude > 90
            "longitude": 75.8573,
            "altitude": 125.4,
            "heading": 142.0,
            "timestamp": "2026-09-26T12:45:32Z"
        }
        serializer = DroneTelemetrySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)


class DroneTelemetryAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_esp32_post_telemetry(self):
        payload = {
            "drone_id": "drone01",
            "latitude": 30.9010,
            "longitude": 75.8573,
            "altitude": 125.4,
            "heading": 142.0,
            "timestamp": "2026-09-26T12:45:32Z"
        }
        response = self.client.post(
            '/api/telemetry/',
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['is_simulated'], False)
        record = DroneTelemetry.objects.first()
        self.assertFalse(record.is_simulated)

    def test_latest_telemetry_endpoint(self):
        DroneTelemetry.objects.create(
            drone_id='drone01',
            latitude=30.9010,
            longitude=75.8573,
            altitude=125.4,
            heading=142.0,
            timestamp=timezone.now(),
            is_simulated=True
        )
        response = self.client.get('/api/telemetry/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('telemetry', data)
        self.assertIn('route_name', data)
        self.assertIn('hardware_connected', data)
        self.assertFalse(data['hardware_connected'])
        self.assertIn('Drone Not Connected', data['status_label'])

    def test_history_endpoint(self):
        for i in range(5):
            DroneTelemetry.objects.create(
                drone_id='drone01',
                latitude=30.9010 + i * 0.001,
                longitude=75.8573 + i * 0.001,
                altitude=100 + i,
                heading=90,
                timestamp=timezone.now(),
                is_simulated=True
            )
        response = self.client.get('/api/telemetry/history/?limit=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 5)

    def test_simulation_engine_step_and_randomize(self):
        sim = SimulationEngine.get_instance('drone01')
        route1 = sim.route_name
        self.assertTrue(len(sim.waypoints) >= 6)
        
        step_data = sim.step()
        self.assertIn('latitude', step_data)
        self.assertIn('longitude', step_data)
        self.assertIn('heading', step_data)
        self.assertTrue(step_data['is_simulated'])
        self.assertTrue(0.0 <= step_data['heading'] <= 360.0)

        # Test procedural randomizer creates routes
        new_route = sim.generate_random_route()
        self.assertIsNotNone(new_route)
        self.assertTrue(len(sim.waypoints) >= 6)

    def test_simulation_reset_endpoint(self):
        response = self.client.post(
            '/api/simulation/reset/',
            data={"drone_id": "drone01", "randomize": True},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('route_name', data)
        self.assertIn('pattern', data)

    def test_drone_status_endpoint(self):
        response = self.client.get('/api/telemetry/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertFalse(data['hardware_connected'])
        self.assertIn('Drone Not Connected', data['status_label'])


# ==============================================================================
# Phone GPS Test Mode Tests
# ==============================================================================

class PhoneTelemetryModelTest(TestCase):
    def test_create_phone_telemetry(self):
        now = timezone.now()
        record = PhoneTelemetry.objects.create(
            device_id='phone_test_01',
            latitude=30.9010,
            longitude=75.8573,
            altitude=125.4,
            heading=142.0,
            accuracy=8.5,
            speed=4.2,
            timestamp=now,
            source='phone_test'
        )
        self.assertEqual(record.device_id, 'phone_test_01')
        self.assertEqual(record.source, 'phone_test')
        self.assertTrue(record.is_connected())
        self.assertIn('PHONE', str(record))

    def test_phone_telemetry_nullable_fields(self):
        now = timezone.now()
        record = PhoneTelemetry.objects.create(
            device_id='phone_test_01',
            latitude=30.9010,
            longitude=75.8573,
            altitude=None,
            heading=None,
            accuracy=12.0,
            speed=None,
            timestamp=now,
            source='phone_test'
        )
        self.assertIsNone(record.altitude)
        self.assertIsNone(record.heading)
        self.assertIsNone(record.speed)
        self.assertEqual(record.accuracy, 12.0)


class PhoneTelemetrySerializerTest(TestCase):
    def test_valid_phone_payload(self):
        payload = {
            "device_id": "phone_test_01",
            "latitude": 30.9010,
            "longitude": 75.8573,
            "altitude": 125.4,
            "heading": 142.0,
            "accuracy": 8.5,
            "speed": 4.2,
            "timestamp": "2026-09-26T12:45:32Z",
            "source": "phone_test"
        }
        serializer = PhoneTelemetrySerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.device_id, "phone_test_01")
        self.assertEqual(instance.source, "phone_test")

    def test_valid_phone_payload_with_nulls(self):
        payload = {
            "device_id": "phone_test_01",
            "latitude": 30.9010,
            "longitude": 75.8573,
            "altitude": None,
            "heading": None,
            "accuracy": 5.0,
            "speed": None,
            "timestamp": "2026-09-26T12:45:32Z",
            "source": "phone_test"
        }
        serializer = PhoneTelemetrySerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_phone_payload_latitude(self):
        payload = {
            "device_id": "phone_test_01",
            "latitude": -95.0,
            "longitude": 75.8573,
            "timestamp": "2026-09-26T12:45:32Z"
        }
        serializer = PhoneTelemetrySerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)


class PhoneTelemetryAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_mobile_page_renders(self):
        response = self.client.get('/mobile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Phone GPS Test Mode')
        self.assertContains(response, 'Start GPS Tracking')
        self.assertContains(response, 'Stop GPS Tracking')

    def test_dashboard_page_renders(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'TEST MODE — PHONE GPS')
        self.assertContains(response, 'Clear Trail')
        self.assertContains(response, 'Center Phone')

    def test_phone_location_ingest(self):
        payload = {
            "device_id": "phone_test_01",
            "latitude": 30.9010,
            "longitude": 75.8573,
            "altitude": 125.4,
            "heading": 142.0,
            "accuracy": 8.5,
            "speed": 4.2,
            "timestamp": "2026-09-26T12:45:32Z",
            "source": "phone_test"
        }
        response = self.client.post(
            '/api/phone-location/',
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(PhoneTelemetry.objects.count(), 1)

    def test_phone_location_invalid_payload(self):
        payload = {
            "device_id": "phone_test_01",
            "latitude": "not-a-number",
            "longitude": 75.8573
        }
        response = self.client.post(
            '/api/phone-location/',
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['status'], 'error')

    def test_phone_location_latest_waiting_and_success(self):
        # 1. When no records exist yet
        res_empty = self.client.get('/api/phone-location/latest/?device_id=phone_test_01')
        self.assertEqual(res_empty.status_code, status.HTTP_200_OK)
        self.assertEqual(res_empty.json()['status'], 'waiting')
        self.assertFalse(res_empty.json()['is_connected'])

        # 2. When record is created
        PhoneTelemetry.objects.create(
            device_id='phone_test_01',
            latitude=30.9010,
            longitude=75.8573,
            altitude=125.4,
            heading=142.0,
            accuracy=8.5,
            speed=4.2,
            timestamp=timezone.now(),
            source='phone_test'
        )
        res_active = self.client.get('/api/phone-location/latest/?device_id=phone_test_01')
        self.assertEqual(res_active.status_code, status.HTTP_200_OK)
        self.assertEqual(res_active.json()['status'], 'success')
        self.assertTrue(res_active.json()['is_connected'])
        self.assertEqual(res_active.json()['status_label'], 'Phone Connected')
        self.assertAlmostEqual(res_active.json()['telemetry']['latitude'], 30.9010)

    def test_phone_location_history(self):
        for i in range(3):
            PhoneTelemetry.objects.create(
                device_id='phone_test_01',
                latitude=30.9010 + i * 0.001,
                longitude=75.8573 + i * 0.001,
                timestamp=timezone.now(),
                source='phone_test'
            )
        response = self.client.get('/api/phone-location/history/?device_id=phone_test_01')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 3)

