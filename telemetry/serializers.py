import math
from django.utils import timezone
from rest_framework import serializers
from .models import DroneTelemetry, PhoneTelemetry


class DroneTelemetrySerializer(serializers.ModelSerializer):
    """
    Serializer for ingesting and presenting drone telemetry packets.
    Used by the ESP32 POST API and the frontend dashboard polling API.
    """
    drone_id = serializers.CharField(
        max_length=64,
        default='drone01',
        trim_whitespace=True
    )
    latitude = serializers.FloatField(
        min_value=-90.0,
        max_value=90.0,
        help_text="GPS Latitude (-90.0 to 90.0)"
    )
    longitude = serializers.FloatField(
        min_value=-180.0,
        max_value=180.0,
        help_text="GPS Longitude (-180.0 to 180.0)"
    )
    altitude = serializers.FloatField(
        min_value=-500.0,
        max_value=50000.0,
        help_text="Altitude in meters"
    )
    heading = serializers.FloatField(
        min_value=0.0,
        max_value=360.0,
        help_text="Heading in degrees (0.0 to 360.0)"
    )
    timestamp = serializers.DateTimeField(
        required=False,
        default=timezone.now,
        help_text="ISO 8601 timestamp (e.g. 2026-09-26T12:45:32Z)"
    )
    is_simulated = serializers.BooleanField(default=False)
    received_at = serializers.DateTimeField(read_only=True)
    seconds_since_received = serializers.FloatField(read_only=True)

    class Meta:
        model = DroneTelemetry
        fields = [
            'id',
            'drone_id',
            'latitude',
            'longitude',
            'altitude',
            'heading',
            'timestamp',
            'received_at',
            'seconds_since_received',
            'is_simulated',
        ]
        read_only_fields = ['id', 'received_at', 'seconds_since_received']

    def to_internal_value(self, data):
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        # Map ESP32 short keys (from Esp_utm.ino) to model fields
        if 'id' in mutable_data and 'drone_id' not in mutable_data:
            mutable_data['drone_id'] = mutable_data['id']
        if 'lat' in mutable_data and 'latitude' not in mutable_data:
            mutable_data['latitude'] = mutable_data['lat']
        if 'lon' in mutable_data and 'longitude' not in mutable_data:
            mutable_data['longitude'] = mutable_data['lon']
        if 'alt' in mutable_data and 'altitude' not in mutable_data:
            mutable_data['altitude'] = mutable_data['alt']
        if 'hdg' in mutable_data and 'heading' not in mutable_data:
            mutable_data['heading'] = mutable_data['hdg']
        if 'heading' in mutable_data:
            try:
                hdg_val = float(mutable_data['heading'])
                if hdg_val > 360.0 or hdg_val < 0.0:
                    mutable_data['heading'] = 0.0
            except (ValueError, TypeError):
                mutable_data['heading'] = 0.0
        if 'timestamp' not in mutable_data or not mutable_data['timestamp']:
            from django.utils import timezone
            mutable_data['timestamp'] = timezone.now().isoformat()
        return super().to_internal_value(mutable_data)

    def validate_drone_id(self, value):
        if not value or not str(value).strip():
            return 'DRONE-ALPHA'
        return str(value).strip()


class DroneStatusSerializer(serializers.Serializer):
    """
    Provides a high-level operational status summary for a drone.
    Differentiates between physical hardware connectivity (ESP32) and
    simulation test mode.
    """
    drone_id = serializers.CharField()
    is_connected = serializers.BooleanField()
    status_label = serializers.CharField()
    hardware_connected = serializers.BooleanField()
    hardware_status_label = serializers.CharField()
    gps_fix = serializers.BooleanField()
    is_simulated = serializers.BooleanField()
    active_route_name = serializers.CharField(allow_null=True, required=False)
    last_telemetry = DroneTelemetrySerializer(allow_null=True)
    seconds_since_last_packet = serializers.FloatField(allow_null=True)
    seconds_since_last_hardware_packet = serializers.FloatField(allow_null=True)
    simulation_mode = serializers.BooleanField()
    total_packets_received = serializers.IntegerField()
    total_hardware_packets = serializers.IntegerField()


class PhoneTelemetrySerializer(serializers.ModelSerializer):
    """
    Serializer for ingesting and presenting phone GPS telemetry.
    Used by POST /api/phone-location/ and dashboard live polling.
    Accepts nulls for altitude, heading, accuracy, speed if browser doesn't supply them.
    """
    device_id = serializers.CharField(
        max_length=64,
        default='phone_test_01',
        trim_whitespace=True,
        required=False
    )
    latitude = serializers.FloatField(
        min_value=-90.0,
        max_value=90.0,
        help_text="Phone GPS Latitude (-90.0 to 90.0)"
    )
    longitude = serializers.FloatField(
        min_value=-180.0,
        max_value=180.0,
        help_text="Phone GPS Longitude (-180.0 to 180.0)"
    )
    altitude = serializers.FloatField(
        allow_null=True,
        required=False,
        help_text="Altitude in meters (null if unavailable)"
    )
    heading = serializers.FloatField(
        allow_null=True,
        required=False,
        help_text="Heading in degrees (0.0 to 360.0; null if unavailable)"
    )
    accuracy = serializers.FloatField(
        allow_null=True,
        required=False,
        help_text="Accuracy in meters (null if unavailable)"
    )
    speed = serializers.FloatField(
        allow_null=True,
        required=False,
        help_text="Speed in m/s (null if unavailable)"
    )
    timestamp = serializers.DateTimeField(
        help_text="ISO 8601 timestamp"
    )
    source = serializers.CharField(
        default='phone_test',
        required=False
    )
    received_at = serializers.DateTimeField(read_only=True)
    seconds_since_received = serializers.FloatField(read_only=True)

    class Meta:
        model = PhoneTelemetry
        fields = [
            'id',
            'device_id',
            'latitude',
            'longitude',
            'altitude',
            'heading',
            'accuracy',
            'speed',
            'timestamp',
            'source',
            'received_at',
            'seconds_since_received',
        ]
        read_only_fields = ['id', 'received_at', 'seconds_since_received']

    def to_internal_value(self, data):
        """
        Sanitize incoming phone GPS data to handle Android hardware sentinels.
        Android Location API and mobile browsers often provide:
          - heading = -1.0 or NaN when stationary or compass unavailable.
          - speed = -1.0 or NaN when speed is unavailable.
          - accuracy = -1.0 or NaN when unknown.
          - altitude = NaN when altimeter unavailable.
        We convert sentinel/invalid values to None rather than rejecting the packet.
        """
        if hasattr(data, 'copy'):
            data = data.copy()
        elif isinstance(data, dict):
            data = dict(data)

        # Sanitize heading (-1.0 sentinel on Android)
        if 'heading' in data:
            val = data.get('heading')
            if val is not None and val != '':
                try:
                    num = float(val)
                    if math.isnan(num) or num < 0:
                        data['heading'] = None
                    else:
                        data['heading'] = round(num % 360, 2)
                except (ValueError, TypeError):
                    data['heading'] = None
            else:
                data['heading'] = None

        # Sanitize speed (-1.0 sentinel on Android)
        if 'speed' in data:
            val = data.get('speed')
            if val is not None and val != '':
                try:
                    num = float(val)
                    if math.isnan(num) or num < 0:
                        data['speed'] = None
                    else:
                        data['speed'] = round(num, 2)
                except (ValueError, TypeError):
                    data['speed'] = None
            else:
                data['speed'] = None

        # Sanitize accuracy (-1.0 sentinel on Android)
        if 'accuracy' in data:
            val = data.get('accuracy')
            if val is not None and val != '':
                try:
                    num = float(val)
                    if math.isnan(num) or num < 0:
                        data['accuracy'] = None
                    else:
                        data['accuracy'] = round(num, 2)
                except (ValueError, TypeError):
                    data['accuracy'] = None
            else:
                data['accuracy'] = None

        # Sanitize altitude (NaN sentinel)
        if 'altitude' in data:
            val = data.get('altitude')
            if val is not None and val != '':
                try:
                    num = float(val)
                    if math.isnan(num):
                        data['altitude'] = None
                    else:
                        data['altitude'] = round(num, 2)
                except (ValueError, TypeError):
                    data['altitude'] = None
            else:
                data['altitude'] = None

        return super().to_internal_value(data)

    def validate_device_id(self, value):
        if not value or not value.strip():
            return 'phone_test_01'
        return value.strip()


class PhoneStatusSerializer(serializers.Serializer):
    """
    Status summary for Phone GPS Test Mode.
    """
    device_id = serializers.CharField()
    is_connected = serializers.BooleanField()
    status_label = serializers.CharField()
    seconds_since_last_packet = serializers.FloatField(allow_null=True)
    total_packets_received = serializers.IntegerField()
    source = serializers.CharField(default='phone_test')
    last_telemetry = PhoneTelemetrySerializer(allow_null=True)

