import socket
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DroneTelemetry, PhoneTelemetry
from .serializers import (
    DroneTelemetrySerializer,
    DroneStatusSerializer,
    PhoneTelemetrySerializer,
    PhoneStatusSerializer,
)
from .simulation import SimulationEngine


def get_local_ip():
    """Attempts to discover the host laptop's local LAN/hotspot IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


class DashboardView(TemplateView):
    """
    Renders the primary UTM monitoring dashboard.
    Supports both Phone GPS Test Mode and Drone / ESP32 Simulation Mode.
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        context['simulation_mode'] = getattr(settings, 'SIMULATION_MODE', True)
        context['drone_id'] = getattr(settings, 'DEFAULT_DRONE_ID', 'drone01')
        context['device_id'] = getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
        context['timeout_seconds'] = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 5)
        context['phone_timeout'] = getattr(settings, 'PHONE_TIMEOUT_SECONDS', 10)
        context['local_ip'] = get_local_ip()
        context['mobile_url'] = self.request.build_absolute_uri('/mobile/')
        context['is_hosted'] = not (host.startswith('localhost') or host.startswith('127.0.0.1'))
        context['server_host'] = host
        return context


class MobilePageView(TemplateView):
    """
    Renders the dedicated Phone GPS Test Mode page (/mobile/)
    designed for mobile browsers (cloud HTTPS or local Wi-Fi).
    """
    template_name = 'mobile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        context['device_id'] = getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
        context['local_ip'] = get_local_ip()
        context['mobile_url'] = self.request.build_absolute_uri('/mobile/')
        context['dashboard_url'] = self.request.build_absolute_uri('/dashboard/')
        context['server_host'] = host
        context['is_secure'] = self.request.is_secure()
        context['is_hosted'] = not (host.startswith('localhost') or host.startswith('127.0.0.1'))
        return context


class TelemetryIngestView(APIView):
    """
    API endpoint designed for the ESP32 Wi-Fi module (and future Cube Orange+ telemetry).
    Accepts HTTP POST with JSON payload containing drone GPS telemetry.
    Flags all packets received here as real hardware telemetry (is_simulated=False).
    """
    def post(self, request, *args, **kwargs):
        serializer = DroneTelemetrySerializer(data=request.data)
        if serializer.is_valid():
            telemetry_record = serializer.save(is_simulated=False)
            return Response(
                {
                    "status": "success",
                    "message": "Telemetry received successfully from hardware",
                    "id": telemetry_record.id,
                    "drone_id": telemetry_record.drone_id,
                    "is_simulated": False,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "error",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class TelemetryLatestView(APIView):
    """
    Returns the most recent telemetry packet for the specified drone (default: drone01).
    Distinguishes clearly between real hardware packets (from ESP32) and simulated data.
    When in simulation mode, reports physical drone as Not Connected and generates
    procedurally randomized flight paths.
    """
    def get(self, request, *args, **kwargs):
        drone_id = request.query_params.get('drone_id', getattr(settings, 'DEFAULT_DRONE_ID', 'drone01'))
        sim_mode = getattr(settings, 'SIMULATION_MODE', True)
        timeout = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 5)

        # Check if real hardware telemetry has arrived recently from an ESP32
        latest_hw = DroneTelemetry.objects.filter(drone_id=drone_id, is_simulated=False).first()
        hw_connected = bool(latest_hw and latest_hw.seconds_since_received <= timeout)

        sim = SimulationEngine.get_instance(drone_id=drone_id)

        if sim_mode:
            # Simulation Mode: generate procedural route steps
            latest = DroneTelemetry.objects.filter(drone_id=drone_id).first()
            if not latest or latest.seconds_since_received >= 0.8:
                latest = sim.step_and_save()
        else:
            # Live Hardware Mode: only show real packets from ESP32
            latest = latest_hw

        if not latest:
            return Response(
                {
                    "status": "waiting",
                    "message": f"Waiting for ESP32 hardware telemetry for {drone_id}...",
                    "simulation_mode": sim_mode,
                    "is_connected": False,
                    "hardware_connected": False,
                    "status_label": "Drone Not Connected (Hardware Offline)",
                    "hardware_status": "Hardware Offline (ESP32 Not Connected)",
                    "drone_id": drone_id,
                    "telemetry": None,
                },
                status=status.HTTP_200_OK
            )

        serializer = DroneTelemetrySerializer(latest)
        seconds_ago = latest.seconds_since_received
        is_packet_fresh = seconds_ago <= timeout

        # Distinct status labels for physical drone vs simulated feed
        if sim_mode:
            is_conn = False  # Physical drone is NOT connected!
            status_label = "Drone Not Connected (Simulation Mode)"
            hw_status_label = "Hardware Offline (ESP32 Not Connected)" if not hw_connected else "ESP32 Broadcasting (Sim Overriding)"
        else:
            is_conn = hw_connected
            status_label = "Drone Connected (ESP32 Live)" if hw_connected else "Drone Not Connected (Waiting for ESP32)"
            hw_status_label = "Hardware Online (ESP32 Streaming)" if hw_connected else "Hardware Offline (ESP32 Disconnected)"

        return Response(
            {
                "status": "success",
                "simulation_mode": sim_mode,
                "is_simulated": latest.is_simulated,
                "is_connected": is_conn,
                "hardware_connected": hw_connected,
                "status_label": status_label,
                "hardware_status": hw_status_label,
                "route_name": sim.route_name if sim_mode else None,
                "route_pattern": sim.current_pattern if sim_mode else None,
                "seconds_since_update": round(seconds_ago, 1),
                "gps_fix": is_packet_fresh,
                "telemetry": serializer.data
            },
            status=status.HTTP_200_OK
        )


class TelemetryHistoryView(APIView):
    """
    Returns recent telemetry records to plot the drone's flight trail/breadcrumb path.
    Filters by the active mode (simulated vs hardware) to avoid mixing trails.
    """
    def get(self, request, *args, **kwargs):
        drone_id = request.query_params.get('drone_id', getattr(settings, 'DEFAULT_DRONE_ID', 'drone01'))
        limit = min(int(request.query_params.get('limit', 100)), 500)
        sim_mode = getattr(settings, 'SIMULATION_MODE', True)

        qs = DroneTelemetry.objects.filter(drone_id=drone_id)
        # Filter history by active mode so switching modes cleans up the trail
        if sim_mode:
            qs = qs.filter(is_simulated=True)
        else:
            qs = qs.filter(is_simulated=False)

        records = list(qs.order_by('-received_at')[:limit])
        records.reverse()  # Chronological order

        serializer = DroneTelemetrySerializer(records, many=True)
        return Response(
            {
                "status": "success",
                "drone_id": drone_id,
                "simulation_mode": sim_mode,
                "count": len(records),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )


class DroneStatusView(APIView):
    """
    Provides connection and telemetry status summary.
    Clearly indicates physical drone hardware connectivity vs simulation mode.
    """
    def get(self, request, *args, **kwargs):
        drone_id = request.query_params.get('drone_id', getattr(settings, 'DEFAULT_DRONE_ID', 'drone01'))
        sim_mode = getattr(settings, 'SIMULATION_MODE', True)
        timeout = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 5)

        latest_all = DroneTelemetry.objects.filter(drone_id=drone_id).first()
        latest_hw = DroneTelemetry.objects.filter(drone_id=drone_id, is_simulated=False).first()
        total_count = DroneTelemetry.objects.filter(drone_id=drone_id).count()
        total_hw_count = DroneTelemetry.objects.filter(drone_id=drone_id, is_simulated=False).count()

        sim = SimulationEngine.get_instance(drone_id=drone_id)
        hw_connected = bool(latest_hw and latest_hw.seconds_since_received <= timeout)
        hw_seconds_ago = latest_hw.seconds_since_received if latest_hw else None

        active_record = latest_all if sim_mode else latest_hw

        if active_record:
            seconds_ago = active_record.seconds_since_received
            last_serialized = DroneTelemetrySerializer(active_record).data
        else:
            seconds_ago = None
            last_serialized = None

        if sim_mode:
            is_conn = False  # Physical drone is NOT connected!
            status_label = "Drone Not Connected (Simulation Mode)"
            hw_status_label = "Hardware Offline (ESP32 Not Connected)" if not hw_connected else "ESP32 Broadcasting"
        else:
            is_conn = hw_connected
            status_label = "Drone Connected (ESP32 Live)" if hw_connected else "Drone Not Connected (Hardware Offline)"
            hw_status_label = "Hardware Online (ESP32 Streaming)" if hw_connected else "Hardware Offline (ESP32 Disconnected)"

        return Response(
            {
                "drone_id": drone_id,
                "is_connected": is_conn,
                "status_label": status_label,
                "hardware_connected": hw_connected,
                "hardware_status_label": hw_status_label,
                "gps_fix": bool(active_record and (seconds_ago or 0) <= timeout),
                "is_simulated": active_record.is_simulated if active_record else sim_mode,
                "simulation_mode": sim_mode,
                "timeout_seconds": timeout,
                "active_route_name": sim.route_name if sim_mode else None,
                "seconds_since_last_packet": round(seconds_ago, 1) if seconds_ago is not None else None,
                "seconds_since_last_hardware_packet": round(hw_seconds_ago, 1) if hw_seconds_ago is not None else None,
                "total_packets_received": total_count,
                "total_hardware_packets": total_hw_count,
                "last_telemetry": last_serialized,
            },
            status=status.HTTP_200_OK
        )


class SimulationToggleView(APIView):
    """
    Toggles simulation mode on/off on the live server.
    When activating simulation mode, automatically generates a fresh random route.
    """
    def post(self, request, *args, **kwargs):
        current = getattr(settings, 'SIMULATION_MODE', True)
        requested = request.data.get('enabled')
        if requested is not None:
            settings.SIMULATION_MODE = bool(requested)
        else:
            settings.SIMULATION_MODE = not current

        sim = SimulationEngine.get_instance()
        if settings.SIMULATION_MODE:
            sim.generate_random_route()

        return Response({
            "status": "success",
            "simulation_mode": settings.SIMULATION_MODE,
            "route_name": sim.route_name if settings.SIMULATION_MODE else None,
            "message": f"Simulation mode {'enabled with route: ' + sim.route_name if settings.SIMULATION_MODE else 'disabled (waiting for ESP32 hardware)'}"
        })


class SimulationResetView(APIView):
    """
    Resets the simulated flight route.
    When randomize=True (default), generates a brand new randomized flight route!
    """
    def post(self, request, *args, **kwargs):
        drone_id = request.data.get('drone_id', getattr(settings, 'DEFAULT_DRONE_ID', 'drone01'))
        randomize = request.data.get('randomize', True)
        pattern = request.data.get('pattern', None)

        sim = SimulationEngine.get_instance(drone_id=drone_id)
        if randomize:
            route_name = sim.generate_random_route(pattern=pattern)
        else:
            route_name = sim.reset(randomize=False)

        return Response({
            "status": "success",
            "route_name": sim.route_name,
            "pattern": sim.current_pattern,
            "waypoint_count": len(sim.waypoints),
            "message": f"Generated new flight route: {sim.route_name} ({sim.current_pattern} pattern with {len(sim.waypoints)} waypoints)"
        })


# ==============================================================================
# Phone GPS Test Mode API Views
# ==============================================================================

class PhoneLocationIngestView(APIView):
    """
    POST /api/phone-location/
    Endpoint designed specifically for phone / browser GPS ingestion.
    Accepts real GPS coordinates from navigator.geolocation.watchPosition().
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            serializer = PhoneTelemetrySerializer(data=request.data)
            if serializer.is_valid():
                record = serializer.save()
                rx_time = record.received_at.isoformat() if record.received_at else timezone.now().isoformat()
                return Response(
                    {
                        "status": "success",
                        "id": record.id,
                        "device_id": record.device_id,
                        "received_at": rx_time,
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "status": "error",
                    "message": "Invalid phone telemetry payload",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("Phone ingest error: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": f"Server error ingesting phone telemetry: {str(exc)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PhoneLocationLatestView(APIView):
    """
    GET /api/phone-location/latest/
    Returns the most recent GPS location transmitted by the phone or browser.
    Polled by the dashboard in Phone GPS Test Mode.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            raw_device_id = request.query_params.get(
                'device_id',
                getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
            )
            device_id = raw_device_id.strip() if raw_device_id else getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
            timeout = getattr(settings, 'PHONE_TIMEOUT_SECONDS', 15)

            latest = PhoneTelemetry.objects.filter(device_id=device_id).first()
            total_packets = PhoneTelemetry.objects.filter(device_id=device_id).count()

            # Resilient fallback: If no record matches device_id, use any recent phone record
            if not latest:
                latest = PhoneTelemetry.objects.first()
                if latest:
                    device_id = latest.device_id
                    total_packets = PhoneTelemetry.objects.filter(device_id=device_id).count()

            if not latest:
                return Response(
                    {
                        "status": "waiting",
                        "device_id": device_id,
                        "is_connected": False,
                        "status_label": "Device Disconnected",
                        "seconds_since_update": None,
                        "total_packets_received": 0,
                        "source": "phone_test",
                        "message": "No phone GPS updates received yet. Open /mobile/ on Android or click Track My Location Live.",
                        "telemetry": None,
                    },
                    status=status.HTTP_200_OK
                )

            seconds_ago = latest.seconds_since_received
            is_conn = seconds_ago <= timeout

            serializer = PhoneTelemetrySerializer(latest)
            return Response(
                {
                    "status": "success",
                    "device_id": device_id,
                    "is_connected": is_conn,
                    "status_label": "Phone Connected" if is_conn else "Phone Disconnected",
                    "seconds_since_update": round(seconds_ago, 1),
                    "total_packets_received": total_packets,
                    "source": latest.source or "phone_test",
                    "telemetry": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("Phone latest view error: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": f"Server error: {str(exc)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PhoneLocationHistoryView(APIView):
    """
    GET /api/phone-location/history/
    Returns recent phone GPS records to draw the phone movement trail on Leaflet.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            raw_device_id = request.query_params.get(
                'device_id',
                getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
            )
            device_id = raw_device_id.strip() if raw_device_id else getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
            limit = min(int(request.query_params.get('limit', 100)), 500)

            records = list(
                PhoneTelemetry.objects.filter(device_id=device_id)
                .order_by('-received_at')[:limit]
            )
            if not records:
                latest = PhoneTelemetry.objects.first()
                if latest:
                    records = list(
                        PhoneTelemetry.objects.filter(device_id=latest.device_id)
                        .order_by('-received_at')[:limit]
                    )

            records.reverse()  # Chronological order for polyline drawing

            serializer = PhoneTelemetrySerializer(records, many=True)
            return Response(
                {
                    "status": "success",
                    "device_id": device_id,
                    "source": "phone_test",
                    "count": len(records),
                    "results": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("Phone history view error: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": f"Server error: {str(exc)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

