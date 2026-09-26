import time
import requests
from django.core.management.base import BaseCommand
from telemetry.simulation import SimulationEngine


class Command(BaseCommand):
    help = "Simulates an ESP32 transmitter sending HTTP POST telemetry to the Django API."

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://127.0.0.1:8000/api/telemetry/',
            help='Target API endpoint URL'
        )
        parser.add_argument(
            '--interval',
            type=float,
            default=1.0,
            help='Transmission interval in seconds (default: 1.0s)'
        )
        parser.add_argument(
            '--drone-id',
            type=str,
            default='drone01',
            help='Drone identifier (default: drone01)'
        )
        parser.add_argument(
            '--direct-db',
            action='store_true',
            help='Write directly to database instead of HTTP POST'
        )

    def handle(self, *args, **options):
        url = options['url']
        interval = options['interval']
        drone_id = options['drone_id']
        direct_db = options['direct_db']

        sim = SimulationEngine.get_instance(drone_id=drone_id)
        self.stdout.write(self.style.SUCCESS(
            f"Starting UTM Drone Simulator for [{drone_id}] "
            f"(Interval: {interval}s, Mode: {'Direct DB' if direct_db else f'HTTP POST to {url}'})"
        ))
        self.stdout.write("Press Ctrl+C to stop simulation.\n")

        try:
            while True:
                if direct_db:
                    record = sim.step_and_save()
                    self.stdout.write(
                        f"[{record.received_at:%H:%M:%S}] Saved DB: Lat={record.latitude:.4f}, "
                        f"Lon={record.longitude:.4f}, Alt={record.altitude:.1f}m, Hdg={record.heading:.0f}°"
                    )
                else:
                    packet = sim.step()
                    payload = {
                        "drone_id": packet['drone_id'],
                        "latitude": packet['latitude'],
                        "longitude": packet['longitude'],
                        "altitude": packet['altitude'],
                        "heading": packet['heading'],
                        "timestamp": packet['timestamp'].isoformat()
                    }
                    try:
                        res = requests.post(url, json=payload, timeout=3.0)
                        if res.status_code == 201:
                            self.stdout.write(
                                f"[{packet['timestamp']:%H:%M:%S}] Transmitted: Lat={packet['latitude']:.4f}, "
                                f"Lon={packet['longitude']:.4f}, Alt={packet['altitude']:.1f}m, Hdg={packet['heading']:.0f}° -> 201 OK"
                            )
                        else:
                            self.stdout.write(self.style.WARNING(f"HTTP {res.status_code}: {res.text}"))
                    except Exception as err:
                        self.stdout.write(self.style.ERROR(f"Connection failed: {err}"))

                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nSimulator stopped."))
