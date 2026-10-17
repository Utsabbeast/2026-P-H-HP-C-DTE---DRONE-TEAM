import json
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
import paho.mqtt.client as mqtt
from telemetry.models import DroneTelemetry

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs real-time HiveMQ MQTT background listener to ingest drone fleet telemetry into database'

    def handle(self, *args, **options):
        broker_host = "broker.hivemq.com"
        broker_port = 1883

        self.stdout.write(self.style.SUCCESS(f"Starting UTM Fleet MQTT Bridge listening on {broker_host}:{broker_port}..."))

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("Connected to HiveMQ Cloud MQTT Broker!"))
                client.subscribe([
                    ("utm/drones/+/telemetry", 0),
                    ("utm/drones/+/status", 0),
                    ("utm/+/telemetry", 0),
                    ("utm/drone-alpha/telemetry", 0),
                    ("utm/#", 0),
                ])
                self.stdout.write(self.style.SUCCESS("Subscribed to all fleet telemetry topics (utm/#)"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to connect to HiveMQ, return code {rc}"))

        prev_positions = {}

        def on_message(client, userdata, msg):
            try:
                raw_payload = msg.payload.decode('utf-8')
                data = json.loads(raw_payload)

                # Extract drone ID from payload or fallback to topic
                drone_id = data.get('drone_id') or data.get('id')
                if not drone_id and msg.topic:
                    parts = msg.topic.split('/')
                    if len(parts) >= 3 and parts[1] == 'drones':
                        drone_id = parts[2]
                if not drone_id:
                    drone_id = 'DRONE-ALPHA'

                # Ignore broker-retained messages from previous sessions
                if getattr(msg, 'retain', False):
                    return

                # If status heartbeat packet (e.g. {"status": "online"} or {"status": "offline"})
                if msg.topic.endswith('/status') or ('status' in data and 'lat' not in data and 'latitude' not in data):
                    status_val = str(data.get('status', '')).lower()
                    if status_val == 'offline':
                        self.stdout.write(self.style.WARNING(f"[{timezone.now():%H:%M:%S}] Drone {drone_id} reported offline."))
                        return

                    self.stdout.write(self.style.NOTICE(f"[{timezone.now():%H:%M:%S}] Live Online Heartbeat for {drone_id}: {data}"))
                    # Look up last known position for this drone
                    prev = DroneTelemetry.objects.filter(drone_id=drone_id).order_by('-received_at').first()
                    pos_lat = prev.latitude if prev and abs(prev.latitude) > 0.0001 else 30.9010
                    pos_lon = prev.longitude if prev and abs(prev.longitude) > 0.0001 else 75.8573
                    pos_alt = prev.altitude if prev else 0.0
                    pos_hdg = prev.heading if prev else 0.0
                    pos_batt_v = prev.batt_v if prev else 15.8
                    pos_batt_pct = prev.batt_pct if prev else 95
                    pos_mode = prev.flight_mode if prev else 'ONLINE'

                    DroneTelemetry.objects.create(
                        drone_id=drone_id,
                        latitude=pos_lat,
                        longitude=pos_lon,
                        altitude=pos_alt,
                        heading=pos_hdg,
                        batt_v=pos_batt_v,
                        batt_pct=pos_batt_pct,
                        speed=0.0,
                        flight_mode=pos_mode,
                        timestamp=timezone.now(),
                        is_simulated=False
                    )
                    return

                if data.get('lat') is None and data.get('latitude') is None:
                    return

                lat = float(data.get('lat') if data.get('lat') is not None else data.get('latitude', 0))
                lon = float(data.get('lon') if data.get('lon') is not None else data.get('longitude', 0))
                alt = float(data.get('alt') if data.get('alt') is not None else data.get('altitude', 0))
                raw_hdg = float(data.get('hdg') if data.get('hdg') is not None else data.get('heading', 0))
                hdg = 0.0 if (raw_hdg > 360.0 or raw_hdg < 0.0) else raw_hdg

                # If drone GPS has not locked yet (0,0), fallback to previous fix or base station
                if abs(lat) < 0.0001 and abs(lon) < 0.0001:
                    prev = DroneTelemetry.objects.filter(drone_id=drone_id).exclude(latitude=0.0, longitude=0.0).order_by('-received_at').first()
                    if prev:
                        lat, lon = prev.latitude, prev.longitude
                    else:
                        lat, lon = 30.9010, 75.8573

                # Calculate speed dynamically from consecutive GPS positions or use reported speed
                now_ts = timezone.now()
                raw_spd = data.get('speed') if data.get('speed') is not None else data.get('spd')
                speed = float(raw_spd) if raw_spd is not None else None

                if drone_id in prev_positions:
                    p_lat, p_lon, p_time = prev_positions[drone_id]
                    dt = (now_ts - p_time).total_seconds()
                    if 0.4 <= dt <= 30.0:
                        import math
                        dlat = math.radians(lat - p_lat)
                        dlon = math.radians(lon - p_lon)
                        a = math.sin(dlat / 2)**2 + math.cos(math.radians(p_lat)) * math.cos(math.radians(lat)) * math.sin(dlon / 2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                        dist_m = 6371000.0 * c
                        calc_speed = 0.0 if dist_m < 0.25 else (dist_m / dt)
                        if speed is None:
                            speed = round(calc_speed, 1)

                prev_positions[drone_id] = (lat, lon, now_ts)
                flight_mode = str(data.get('flight_mode') or data.get('mode') or 'POSHOLD').upper()

                roll = float(data.get('roll')) if data.get('roll') is not None else None
                pitch = float(data.get('pitch')) if data.get('pitch') is not None else None
                batt_v = float(data.get('batt_v')) if data.get('batt_v') is not None else None
                batt_pct = int(data.get('batt_pct')) if data.get('batt_pct') is not None else None
                if batt_pct is not None:
                    batt_pct = max(0, min(100, batt_pct))

                record = DroneTelemetry.objects.create(
                    drone_id=drone_id,
                    latitude=lat,
                    longitude=lon,
                    altitude=alt,
                    heading=hdg,
                    roll=roll,
                    pitch=pitch,
                    batt_v=batt_v,
                    batt_pct=batt_pct,
                    speed=speed,
                    flight_mode=flight_mode,
                    timestamp=timezone.now(),
                    is_simulated=False
                )

                self.stdout.write(self.style.SUCCESS(
                    f"[{timezone.now():%H:%M:%S}] Ingested {drone_id} | Pos: ({lat:.5f}, {lon:.5f}) | Alt: {alt:.1f}m | Spd: {speed}m/s | Mode: {flight_mode} | Batt: {batt_v}V ({batt_pct}%)"
                ))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error parsing MQTT packet on {msg.topic}: {e}"))

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="utm_server_ingest_bridge")
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(broker_host, broker_port, 60)
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.NOTICE("Stopping MQTT bridge..."))
            client.disconnect()
