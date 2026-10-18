import socket
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DroneTelemetry, PhoneTelemetry, FlightPermissionRequest
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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
        from django.contrib.auth.models import User
        from django.utils import timezone
        from datetime import timedelta
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        
        # Add requested counters (units count)
        context['total_registered_drones'] = User.objects.filter(is_superuser=False, is_staff=False).count()
        recent_time = timezone.now() - timedelta(seconds=15)
        # Note: In a real system, you might count unique drone_ids from recent DroneTelemetry
        # We can pass 0 or a query if there are records
        from .models import DroneTelemetry
        context['total_flying_drones'] = DroneTelemetry.objects.filter(received_at__gte=recent_time).values('drone_id').distinct().count()
        
        # Check registration status for pilots
        if self.request.session.get('user_role') == 'PILOT' and self.request.user.is_authenticated:
            from .models import PilotProfile
            p_prof = PilotProfile.objects.filter(user=self.request.user).first()
            context['pilot_profile'] = p_prof
            context['is_fully_registered'] = (p_prof is not None and p_prof.phase2_status == 'APPROVED')
        else:
            context['is_fully_registered'] = True
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
        from django.contrib.auth.models import User
        from django.utils import timezone
        from datetime import timedelta
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        
        # Add requested counters (units count)
        context['total_registered_drones'] = User.objects.filter(is_superuser=False, is_staff=False).count()
        recent_time = timezone.now() - timedelta(seconds=15)
        # Note: In a real system, you might count unique drone_ids from recent DroneTelemetry
        # We can pass 0 or a query if there are records
        from .models import DroneTelemetry
        context['total_flying_drones'] = DroneTelemetry.objects.filter(received_at__gte=recent_time).values('drone_id').distinct().count()
        
        # Check registration status for pilots
        if self.request.session.get('user_role') == 'PILOT' and self.request.user.is_authenticated:
            from .models import PilotProfile, DroneRegistration
            profile = PilotProfile.objects.filter(user=self.request.user, status='APPROVED').exists()
            drone = DroneRegistration.objects.filter(owner=self.request.user, status='APPROVED').exists()
            context['is_fully_registered'] = profile and drone
        else:
            context['is_fully_registered'] = True
        context['device_id'] = getattr(settings, 'DEFAULT_PHONE_DEVICE_ID', 'phone_test_01')
        context['local_ip'] = get_local_ip()
        context['mobile_url'] = self.request.build_absolute_uri('/mobile/')
        context['dashboard_url'] = self.request.build_absolute_uri('/dashboard/')
        context['server_host'] = host
        context['is_secure'] = self.request.is_secure()
        context['is_hosted'] = not (host.startswith('localhost') or host.startswith('127.0.0.1'))
        return context


@method_decorator(csrf_exempt, name='dispatch')
class TelemetryIngestView(APIView):
    """
    API endpoint designed for the ESP32 Wi-Fi module (and future Cube Orange+ telemetry).
    Accepts HTTP POST with JSON payload containing drone GPS telemetry.
    Flags all packets received here as real hardware telemetry (is_simulated=False).
    """
    authentication_classes = []
    permission_classes = []

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
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        drone_id = request.query_params.get('drone_id', getattr(settings, 'DEFAULT_DRONE_ID', 'drone01'))
        sim_mode = getattr(settings, 'SIMULATION_MODE', True)
        timeout = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 5)

        # Check if real hardware telemetry has arrived recently from an ESP32
        latest_hw = DroneTelemetry.objects.filter(drone_id=drone_id, is_simulated=False).first()
        if not latest_hw:
            # Resilient fallback: auto-detect any active hardware drone record (e.g., DRONE-ALPHA from ESP32)
            latest_hw = DroneTelemetry.objects.filter(is_simulated=False).first()
            if latest_hw:
                drone_id = latest_hw.drone_id

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

        if not latest or (not sim_mode and not hw_connected):
            return Response(
                {
                    "status": "waiting",
                    "message": f"Waiting for ESP32 hardware telemetry for {drone_id}...",
                    "simulation_mode": sim_mode,
                    "is_connected": False,
                    "hardware_connected": False,
                    "status_label": "Drone Not Connected (Hardware Offline)",
                    "hardware_status": "Hardware Offline (ESP32 Disconnected)",
                    "drone_id": drone_id,
                    "seconds_since_update": round(latest_hw.seconds_since_received, 1) if latest_hw else None,
                    "gps_fix": False,
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
                "drone_id": drone_id,
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
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        drone_id = request.query_params.get('drone_id', getattr(settings, 'DEFAULT_DRONE_ID', 'drone01'))
        limit = min(int(request.query_params.get('limit', 100)), 500)
        sim_mode = getattr(settings, 'SIMULATION_MODE', True)

        qs = DroneTelemetry.objects.filter(drone_id=drone_id)
        # Filter history by active mode so switching modes cleans up the trail
        if sim_mode:
            qs = qs.filter(is_simulated=True)
        else:
            qs = qs.filter(is_simulated=False).exclude(latitude=0.0, longitude=0.0)
            if not qs.exists():
                # Fallback to any hardware drone stream (e.g. DRONE-ALPHA)
                qs = DroneTelemetry.objects.filter(is_simulated=False).exclude(latitude=0.0, longitude=0.0)
                first_hw = qs.first()
                if first_hw:
                    drone_id = first_hw.drone_id

            # If physical drone is offline / disconnected, do not return old trail
            latest_check = qs.first()
            timeout = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 15)
            if not latest_check or latest_check.seconds_since_received > timeout:
                return Response(
                    {
                        "status": "disconnected",
                        "drone_id": drone_id,
                        "simulation_mode": sim_mode,
                        "count": 0,
                        "results": []
                    },
                    status=status.HTTP_200_OK
                )

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
        timeout = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 15)

        latest_all = DroneTelemetry.objects.filter(drone_id=drone_id).first()
        latest_hw = DroneTelemetry.objects.filter(drone_id=drone_id, is_simulated=False).first()
        if not latest_hw:
            latest_hw = DroneTelemetry.objects.filter(is_simulated=False).first()
            if latest_hw:
                drone_id = latest_hw.drone_id
                latest_all = latest_hw
        total_count = DroneTelemetry.objects.filter(drone_id=drone_id).count()
        total_hw_count = DroneTelemetry.objects.filter(drone_id=drone_id, is_simulated=False).count()

        sim = SimulationEngine.get_instance(drone_id=drone_id)
        hw_connected = bool(latest_hw and latest_hw.seconds_since_received <= timeout)
        hw_seconds_ago = latest_hw.seconds_since_received if latest_hw else None

        active_record = latest_all if sim_mode else (latest_hw if hw_connected else None)

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

@method_decorator(csrf_exempt, name='dispatch')
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



class PilotProfileView(View):
    """
    Renders and handles Phase 2 Profile Completion for pilot operators.
    Requires Phase 1 approval before submission is permitted.
    """
    template_name = 'profile.html'

    def get(self, request):
        if not request.user.is_authenticated or request.user.username == 'guest':
            messages.warning(request, 'Please log in with a registered pilot account to access your profile.')
            return redirect('telemetry:login')

        from .models import PilotProfile, DroneRegistration
        profile, _ = PilotProfile.objects.get_or_create(user=request.user)
        drone = DroneRegistration.objects.filter(owner=request.user).first()

        context = {
            'profile': profile,
            'drone': drone,
            'user_role': request.session.get('user_role', 'PILOT'),
            'user_role_label': request.session.get('user_role_label', 'Pilot Operator'),
            'category_choices': DroneRegistration.CATEGORY_CHOICES,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated or request.user.username == 'guest':
            return redirect('telemetry:login')

        from .models import PilotProfile, DroneRegistration
        profile, _ = PilotProfile.objects.get_or_create(user=request.user)

        # Ensure Phase 1 registration has been approved by Admin
        if profile.phase1_status != 'APPROVED':
            messages.warning(request, 'Your account is still pending Phase 1 approval by ATC Admin. Please wait for acceptance before submitting profile completion.')
            return redirect('telemetry:profile')

        # Read submitted profile fields
        profile.unit_name = request.POST.get('unit_name', '').strip() or profile.unit_name
        profile.full_name = request.POST.get('full_name', '').strip() or profile.full_name
        profile.base_location = request.POST.get('base_location', '').strip() or profile.base_location
        profile.phone_number = request.POST.get('phone_number', '').strip()
        profile.ncc_wing = request.POST.get('ncc_wing', '').strip()
        profile.ncc_unit = request.POST.get('ncc_unit', '').strip()
        profile.license_number = request.POST.get('license_number', '').strip()
        profile.organization = request.POST.get('organization', '').strip()

        try:
            profile.flying_experience_hours = float(request.POST.get('flying_experience_hours', 0.0) or 0.0)
        except (ValueError, TypeError):
            profile.flying_experience_hours = 0.0

        drone_model = request.POST.get('drone_model', '').strip()
        drone_uin = request.POST.get('drone_uin', '').strip()
        drone_category = request.POST.get('drone_category', 'MICRO')

        try:
            drone_max_alt = float(request.POST.get('drone_max_alt', 120.0) or 120.0)
        except (ValueError, TypeError):
            drone_max_alt = 120.0

        profile.drone_model = drone_model
        profile.drone_uin = drone_uin
        profile.phase2_status = 'PENDING'
        profile.phase2_submitted_at = timezone.now()
        profile.status = 'PENDING'
        profile.save()

        # Update or register Drone if model details provided
        if drone_model:
            DroneRegistration.objects.update_or_create(
                owner=request.user,
                defaults={
                    'name': drone_model,
                    'uin': drone_uin or None,
                    'category': drone_category,
                    'max_altitude_m': drone_max_alt,
                    'status': 'PENDING'
                }
            )

        if profile.full_name:
            request.session['user_name'] = profile.full_name

        messages.success(
            request,
            'Profile Completion details submitted successfully! Your submission is now awaiting final Phase 2 verification by ATC Admin.'
        )
        return redirect('telemetry:profile')


class RequestsView(TemplateView):
    """
    Renders ATC Admin operational requests management console:
    1. Phase 1 Profile Acceptance (User Registrations)
    2. Phase 2 Profile Completion Acceptance (Full Pilot & Drone Verifications)
    3. Flight Permission Requests
    4. Drone Registrations (UIN)
    """
    template_name = 'requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import FlightPermissionRequest, DroneRegistration, PilotProfile
        is_atc = bool(
            self.request.session.get('user_role') == 'ATC'
            or (self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff))
        )
        context['is_atc'] = is_atc
        context['user_role'] = 'ATC' if is_atc else self.request.session.get('user_role', 'GUEST')
        context['user_role_label'] = 'ATC Controller (All Access)' if is_atc else self.request.session.get('user_role_label', 'Guest Observer (Read-Only)')

        # Phase 1: User Registrations for Profile Acceptance
        context['phase1_requests'] = PilotProfile.objects.all().order_by('-created_at')

        # Phase 2: Completed Profiles submitted for final verification
        context['phase2_requests'] = PilotProfile.objects.exclude(phase2_status='NOT_SUBMITTED').order_by('-phase2_submitted_at')

        # For backwards compatibility in template
        context['profile_requests'] = PilotProfile.objects.all().order_by('-created_at')

        # Flight permission requests & Drone registrations
        context['flight_requests'] = FlightPermissionRequest.objects.all().order_by('-created_at')
        context['drone_registrations'] = DroneRegistration.objects.all().order_by('-created_at')
        return context


class RequestActionView(View):
    """
    Handles ATC Admin Approve / Reject actions for:
    - Phase 1: User Registration Acceptance
    - Phase 2: Completed Profile Acceptance
    - Flight Requests
    - Drone Registrations
    """
    def post(self, request):
        is_atc = bool(
            request.session.get('user_role') == 'ATC'
            or (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff))
        )
        if not is_atc:
            messages.error(request, 'Unauthorized. ATC Admin credentials required.')
            return redirect('telemetry:dev-error')

        from .models import PilotProfile, FlightPermissionRequest, DroneRegistration
        from django.http import JsonResponse

        action_type = request.POST.get('action_type') # 'phase1', 'phase2', 'flight', 'drone'
        item_id = request.POST.get('item_id')
        decision = request.POST.get('decision', '').lower() # 'approve', 'reject', 'resend'

        if not action_type or not item_id or decision not in ['approve', 'reject', 'resend']:
            messages.error(request, 'Invalid action parameters.')
            return redirect('telemetry:requests')

        is_approve = (decision == 'approve')

        try:
            if action_type == 'phase1':
                profile = PilotProfile.objects.get(id=item_id)
                from .email_service import generate_random_username, generate_secure_password, send_unit_credentials_email

                if decision == 'approve':
                    # Generate random Username for unit if not already set or was pending placeholder
                    if not profile.user.username or profile.user.username.startswith('pending_'):
                        assigned_username = generate_random_username('unit_')
                        profile.user.username = assigned_username
                    else:
                        assigned_username = profile.user.username

                    profile.phase1_status = 'APPROVED'
                    profile.phase1_reviewed_at = timezone.now()
                    profile.save()

                    unit_display = profile.unit_name or profile.user.username
                    messages.success(
                        request,
                        f'Phase 1 Registration for NCC Unit "{unit_display}" APPROVED! '
                        f'Unit Username: {profile.user.username}. Account is active.'
                    )

                elif decision == 'resend':
                    if profile.phase1_status != 'APPROVED':
                        messages.warning(request, 'Unit must be approved before resending credentials.')
                    else:
                        assigned_username = profile.user.username
                        assigned_password = profile.initial_password or generate_secure_password(9)
                        profile.user.set_password(assigned_password)
                        profile.user.save()
                        profile.initial_password = assigned_password
                        profile.credentials_sent_at = timezone.now()
                        profile.save()

                        email_ok, email_msg = send_unit_credentials_email(
                            profile, assigned_username, assigned_password, request=request
                        )
                        if email_ok:
                            messages.success(request, f'Credentials re-dispatched to {profile.user.email} (Username: {assigned_username}).')
                        else:
                            messages.warning(request, f'Notice: {email_msg}')

                else:
                    profile.phase1_status = 'REJECTED'
                    profile.phase1_reviewed_at = timezone.now()
                    profile.save()
                    messages.error(request, f'Phase 1 Registration for "{profile.unit_name or profile.user.username}" REJECTED.')

            elif action_type == 'phase2':
                profile = PilotProfile.objects.get(id=item_id)
                profile.phase2_status = 'APPROVED' if is_approve else 'REJECTED'
                profile.phase2_reviewed_at = timezone.now()
                profile.status = 'APPROVED' if is_approve else 'REJECTED'
                profile.save()

                # Synchronize DroneRegistration approval status
                DroneRegistration.objects.filter(owner=profile.user).update(
                    status='APPROVED' if is_approve else 'REJECTED'
                )

                if is_approve:
                    messages.success(request, f'Phase 2 Profile for pilot "{profile.user.username}" APPROVED! Full flight operations authorized.')
                else:
                    messages.error(request, f'Phase 2 Profile for pilot "{profile.user.username}" REJECTED.')

            elif action_type == 'flight':
                freq = FlightPermissionRequest.objects.get(id=item_id)
                freq.status = 'APPROVED' if is_approve else 'REJECTED'
                freq.save()
                messages.success(request, f'Flight request #{freq.id} {freq.status.lower()}.')

            elif action_type == 'drone':
                dreg = DroneRegistration.objects.get(id=item_id)
                dreg.status = 'APPROVED' if is_approve else 'REJECTED'
                dreg.save()
                messages.success(request, f'Drone registration #{dreg.id} ({dreg.name}) {dreg.status.lower()}.')

        except Exception as e:
            messages.error(request, f'Action failed: {str(e)}')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            from django.http import JsonResponse
            return JsonResponse({'status': 'ok', 'decision': decision})

        return redirect('telemetry:requests')


class StatusView(TemplateView):
    template_name = 'status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import FlightPermissionRequest, DroneRegistration, PilotProfile
        context['user_role'] = self.request.session.get('user_role', 'GUEST')
        context['user_role_label'] = self.request.session.get('user_role_label', 'Guest Observer (Read-Only)')

        if self.request.user.is_authenticated:
            user_role = self.request.session.get('user_role', 'GUEST')
            if user_role in ['ATC', 'ADMIN']:
                context['pilot_profile'] = PilotProfile.objects.filter(user=self.request.user).first() or PilotProfile.objects.first()
                context['drone_registration'] = DroneRegistration.objects.filter(owner=self.request.user).first() or DroneRegistration.objects.first()
                context['flight_requests'] = FlightPermissionRequest.objects.all().order_by('-created_at')
                context['latest_request'] = FlightPermissionRequest.objects.all().order_by('-created_at').first()
            else:
                context['pilot_profile'] = PilotProfile.objects.filter(user=self.request.user).first()
                context['drone_registration'] = DroneRegistration.objects.filter(owner=self.request.user).first()
                context['flight_requests'] = FlightPermissionRequest.objects.filter(pilot=self.request.user).order_by('-created_at')
                context['latest_request'] = FlightPermissionRequest.objects.filter(pilot=self.request.user).order_by('-created_at').first()
        return context

    def post(self, request, *args, **kwargs):
        from .models import FlightPermissionRequest, DroneRegistration, PilotProfile
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            profile, _ = PilotProfile.objects.get_or_create(user=request.user)
            license_num = request.POST.get('license', '').strip()
            if license_num:
                profile.license_number = license_num
            profile.phase2_status = 'PENDING'
            profile.phase2_submitted_at = timezone.now()
            profile.status = 'PENDING'
            profile.save()
            messages.success(request, 'Profile details submitted for Phase 2 ATC approval.')

        elif form_type == 'drone':
            drone_name = request.POST.get('drone_name', '').strip()
            uin = request.POST.get('uin', '').strip()
            category = request.POST.get('category', 'MICRO')
            try:
                max_alt = float(request.POST.get('max_alt', 120.0) or 120.0)
            except (ValueError, TypeError):
                max_alt = 120.0

            DroneRegistration.objects.update_or_create(
                owner=request.user,
                defaults={
                    'name': drone_name or 'My Drone',
                    'uin': uin or None,
                    'category': category,
                    'max_altitude_m': max_alt,
                    'status': 'PENDING'
                }
            )
            messages.success(request, 'Drone registration submitted for ATC approval.')

        elif form_type == 'flight':
            try:
                lat = float(request.POST.get('locLat', 0.0) or 0.0)
                lon = float(request.POST.get('locLon', 0.0) or 0.0)
                max_alt = float(request.POST.get('maxAlt', 0.0) or 0.0)
            except (ValueError, TypeError):
                lat, lon, max_alt = 0.0, 0.0, 0.0

            drone_id = request.POST.get('drone_identifier', '').strip()
            if not drone_id:
                profile = PilotProfile.objects.filter(user=request.user).first()
                if profile and profile.drone_uin:
                    drone_id = profile.drone_uin
                elif profile and profile.drone_model:
                    drone_id = profile.drone_model
                else:
                    drone_id = 'NCC-DRONE-01'

            FlightPermissionRequest.objects.create(
                pilot=request.user if request.user.is_authenticated else None,
                drone_identifier=drone_id,
                location_name=request.POST.get('locName', 'Unknown'),
                latitude=lat,
                longitude=lon,
                max_altitude=max_alt,
                purpose=request.POST.get('purpose', 'Training Flight'),
                status='PENDING'
            )
            messages.success(request, 'Flight permission request submitted for ATC approval.')

        return redirect('telemetry:status')

class TermsView(TemplateView):
    template_name = 'terms.html'

from django.views import View

class UnderConstructionView(View):
    def get(self, request):
        context = {
            'custom_message': 'This feature is currently under development. Please check back later.',
            'custom_title': 'Feature Unavailable'
        }
        return render(request, '404.html', context, status=403)


class HistoryView(TemplateView):
    template_name = 'history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.session.get('user_role', 'GUEST')
        context['user_role_label'] = self.request.session.get('user_role_label', 'Guest Observer (Read-Only)')
        context['flight_requests'] = FlightPermissionRequest.objects.all()
        return context


class NoSQLAdminView(TemplateView):
    template_name = 'nosql_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.session.get('user_role', 'GUEST')
        context['user_role_label'] = self.request.session.get('user_role_label', 'Guest Observer (Read-Only)')
        return context

class DevErrorView(TemplateView):
    template_name = 'dev_error.html'



class AllDronesLatestView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        from .models import DroneTelemetry, DroneRegistration, PilotProfile
        from .serializers import DroneTelemetrySerializer
        from django.db.models import Q
        
        # Get distinct drone IDs (calling order_by() clears Meta.ordering to ensure true distinct on SQLite)
        hw_ids = list(DroneTelemetry.objects.filter(is_simulated=False).order_by().values_list('drone_id', flat=True).distinct())
        all_ids = list(DroneTelemetry.objects.order_by().values_list('drone_id', flat=True).distinct())
        target_ids = list(dict.fromkeys(hw_ids if hw_ids else all_ids))
        timeout = getattr(settings, 'TELEMETRY_TIMEOUT_SECONDS', 15)
        include_offline = request.query_params.get('include_offline', 'false').lower() == 'true'

        latest_records = []
        for d_id in target_ids:
            latest = DroneTelemetry.objects.filter(drone_id=d_id).order_by('-received_at').first()
            if latest:
                if include_offline or latest.seconds_since_received <= timeout:
                    if abs(latest.latitude) < 0.0001 and abs(latest.longitude) < 0.0001:
                        prev = DroneTelemetry.objects.filter(drone_id=d_id).exclude(latitude=0.0, longitude=0.0).order_by('-received_at').first()
                        if prev:
                            latest.latitude = prev.latitude
                            latest.longitude = prev.longitude
                        else:
                            latest.latitude = 30.9010
                            latest.longitude = 75.8573
                    latest_records.append(latest)
                
        serializer = DroneTelemetrySerializer(latest_records, many=True)
        results = []
        for item in serializer.data:
            d_id = item.get('drone_id')
            # Look up registration and unit profile in database
            reg = DroneRegistration.objects.filter(Q(uin__iexact=d_id) | Q(name__iexact=d_id)).first()
            pilot = PilotProfile.objects.filter(Q(drone_uin__iexact=d_id) | Q(drone_model__iexact=d_id)).first()
            if not pilot and reg and hasattr(reg.owner, 'pilot_profile'):
                pilot = reg.owner.pilot_profile

            item['registered_name'] = reg.name if reg else d_id
            item['uin'] = reg.uin if reg and reg.uin else (pilot.drone_uin if pilot and pilot.drone_uin else d_id)
            item['category'] = reg.get_category_display() if reg else 'MICRO'
            item['unit_name'] = pilot.unit_name if pilot and pilot.unit_name else 'NCC Unit'
            item['group_name'] = pilot.group_name if pilot and pilot.group_name else 'Group HQ'
            item['dte_name'] = pilot.dte_name if pilot and pilot.dte_name else 'PHHP&C DTE'
            item['owner_name'] = pilot.full_name if pilot and pilot.full_name else (reg.owner.username if reg else 'Unit Pilot')
            if item.get('speed') is None:
                item['speed'] = 0.0
            if not item.get('flight_mode'):
                item['flight_mode'] = 'POSHOLD'
            results.append(item)

        return Response({
            "status": "success",
            "count": len(results),
            "results": results
        })
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import redirect

class UserDatabaseView(TemplateView):
    template_name = 'user_database.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.session.get('user_role') != 'ATC':
            return redirect('telemetry:dev-error')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import AccessLog
        from django.db.models import Q
        # Only units are shown in System Database & Access Logs (admin entries excluded)
        context['users'] = User.objects.filter(is_superuser=False, is_staff=False).order_by('date_joined')
        context['access_logs'] = AccessLog.objects.exclude(
            Q(user__is_superuser=True) | Q(user__is_staff=True) | Q(user__username__iexact='admin')
        ).order_by('-timestamp')[:200]
        return context


class DigitalSkyZonesApiView(APIView):
    """
    Returns official India Airspace GeoJSON zones (Red, Yellow, Green)
    as defined under DGCA Drone Rules 2021 & DigitalSky platform specifications.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        from .digitalsky import build_digitalsky_geojson
        zone_filter = request.GET.get('type', '').upper()
        geojson_data = build_digitalsky_geojson()

        if zone_filter in ['RED', 'YELLOW', 'GREEN']:
            filtered_features = [
                f for f in geojson_data['features']
                if f['properties'].get('zone_type') == zone_filter
            ]
            geojson_data['features'] = filtered_features
            geojson_data['metadata']['filtered_by'] = zone_filter
            geojson_data['metadata']['filtered_count'] = len(filtered_features)

        return Response(geojson_data)


class DigitalSkyZoneCheckApiView(APIView):
    """
    Real-time coordinate zone assessment API.
    Evaluates latitude, longitude, and optional altitude against DigitalSky airspace zones.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        from .digitalsky import classify_coordinate_zone
        try:
            lat = float(request.GET.get('lat', 30.9010))
            lon = float(request.GET.get('lon', 75.8573))
            alt = float(request.GET.get('alt', 0.0))
        except (ValueError, TypeError):
            return Response(
                {"status": "error", "message": "Invalid latitude or longitude parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        assessment = classify_coordinate_zone(lat, lon, alt)
        return Response({
            "status": "success",
            "coordinates": {"latitude": lat, "longitude": lon, "altitude_m": alt},
            "assessment": assessment
        })

