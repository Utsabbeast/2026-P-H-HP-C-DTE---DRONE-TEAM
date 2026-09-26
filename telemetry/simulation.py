import math
import random
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from .models import DroneTelemetry


class SimulationEngine:
    """
    Simulates a drone executing realistic reconnaissance and patrol routes.
    Generates procedural randomized flight paths (Perimeter Circuits, Search Grids,
    Figure-8 Orbits, Star Recon) around base coordinates (30.9010, 75.8573).

    Each simulation run or reset can generate a fresh, unique flight pattern
    with varied altitudes, headings, and flight speeds.
    """

    BASE_LAT = 30.9010
    BASE_LON = 75.8573

    _instance = None

    def __init__(self, drone_id='drone01'):
        self.drone_id = drone_id
        self.current_waypoint_index = 0
        self.progress = 0.0  # Fraction between 0.0 and 1.0 along current leg
        self.step_size = 0.06  # Progress per tick (~14-20 ticks per leg)
        self.is_active = True
        self.last_heading = 142.0
        self.total_generated_packets = 0
        self.route_name = "Default Patrol"
        self.current_pattern = "circuit"
        self.waypoints = []
        self.generate_random_route()

    @classmethod
    def get_instance(cls, drone_id='drone01'):
        if cls._instance is None:
            cls._instance = cls(drone_id=drone_id)
        return cls._instance

    @staticmethod
    def calculate_bearing(lat1, lon1, lat2, lon2):
        """
        Calculates the initial compass bearing in degrees (0-360)
        from point 1 to point 2 using the spherical law of haversines.
        """
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)

        y = math.sin(delta_lambda) * math.cos(phi2)
        x = (math.cos(phi1) * math.sin(phi2) -
             math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))

        bearing_rad = math.atan2(y, x)
        bearing_deg = (math.degrees(bearing_rad) + 360.0) % 360.0
        return round(bearing_deg, 1)

    def generate_random_route(self, pattern=None):
        """
        Procedurally generates a new randomized flight route with variable waypoints,
        altitudes, and patterns.
        """
        patterns = ['circuit', 'search_grid', 'figure8', 'star']
        if not pattern or pattern not in patterns:
            pattern = random.choice(patterns)

        self.current_pattern = pattern
        center_lat = self.BASE_LAT + random.uniform(-0.002, 0.002)
        center_lon = self.BASE_LON + random.uniform(-0.002, 0.002)

        new_waypoints = []
        code_suffix = random.choice(['Alpha', 'Bravo', 'Echo', 'Zulu', 'Sierra', 'Tango'])
        num_id = random.randint(10, 99)

        if pattern == 'circuit':
            # Organic polygon perimeter: 6 to 9 random radial vertices sorted by angle
            num_points = random.randint(6, 9)
            angles = sorted([random.uniform(0, 2 * math.pi) for _ in range(num_points)])
            base_alt = random.uniform(90.0, 140.0)

            for angle in angles:
                r_lat = random.uniform(0.004, 0.010)
                r_lon = random.uniform(0.005, 0.012)
                lat = round(center_lat + r_lat * math.sin(angle), 6)
                lon = round(center_lon + r_lon * math.cos(angle), 6)
                alt = round(base_alt + random.uniform(-15.0, 25.0), 1)
                new_waypoints.append((lat, lon, alt))

            self.route_name = f"Perimeter Circuit {code_suffix}-{num_id}"

        elif pattern == 'search_grid':
            # Search & Rescue lawn-mower sweep: 8 sweep points
            base_alt = random.uniform(80.0, 120.0)
            lat_start = center_lat - 0.005
            lat_step = 0.003
            lon_left = center_lon - 0.007
            lon_right = center_lon + 0.007

            for row in range(4):
                current_lat = round(lat_start + row * lat_step, 6)
                alt = round(base_alt + row * 4.5, 1)
                if row % 2 == 0:
                    new_waypoints.append((current_lat, round(lon_left, 6), alt))
                    new_waypoints.append((current_lat, round(lon_right, 6), alt))
                else:
                    new_waypoints.append((current_lat, round(lon_right, 6), alt))
                    new_waypoints.append((current_lat, round(lon_left, 6), alt))

            self.route_name = f"Search Grid {code_suffix}-{num_id}"

        elif pattern == 'figure8':
            # Dual-loop figure 8 surveillance pattern: 8 waypoints
            base_alt = random.uniform(100.0, 150.0)
            num_points = 8
            for i in range(num_points):
                t = (2 * math.pi * i) / num_points
                # Lemniscate of Bernoulli
                scale = 0.007
                lat = round(center_lat + (scale * math.sin(t)), 6)
                lon = round(center_lon + (scale * math.sin(t) * math.cos(t) * 1.5), 6)
                alt = round(base_alt + 12.0 * math.sin(t), 1)
                new_waypoints.append((lat, lon, alt))

            self.route_name = f"Figure-8 Orbit {code_suffix}-{num_id}"

        else:  # 'star'
            # Star perimeter reconnaissance: alternating inner/outer points
            num_spokes = 6
            base_alt = random.uniform(95.0, 135.0)
            for i in range(num_spokes * 2):
                angle = (math.pi * i) / num_spokes
                r = 0.009 if (i % 2 == 0) else 0.004
                lat = round(center_lat + r * math.sin(angle), 6)
                lon = round(center_lon + r * 1.3 * math.cos(angle), 6)
                alt = round(base_alt + (10.0 if i % 2 == 0 else -5.0), 1)
                new_waypoints.append((lat, lon, alt))

            self.route_name = f"Star Recon {code_suffix}-{num_id}"

        self.waypoints = new_waypoints
        self.current_waypoint_index = 0
        self.progress = 0.0
        self.step_size = round(random.uniform(0.045, 0.075), 3)

        # Initial heading calculation
        if len(self.waypoints) >= 2:
            self.last_heading = self.calculate_bearing(
                self.waypoints[0][0], self.waypoints[0][1],
                self.waypoints[1][0], self.waypoints[1][1]
            )

        return self.route_name

    def step(self):
        """
        Advances the simulated drone by one step along the current waypoint circuit.
        Returns a dict of telemetry values.
        """
        if not self.waypoints:
            self.generate_random_route()

        num_waypoints = len(self.waypoints)
        wp_from = self.waypoints[self.current_waypoint_index]
        next_wp_idx = (self.current_waypoint_index + 1) % num_waypoints
        wp_to = self.waypoints[next_wp_idx]

        # Advance along the leg
        self.progress += self.step_size
        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_waypoint_index = next_wp_idx
            wp_from = self.waypoints[self.current_waypoint_index]
            next_wp_idx = (self.current_waypoint_index + 1) % num_waypoints
            wp_to = self.waypoints[next_wp_idx]

        # Linear interpolation between waypoints
        t = self.progress
        lat = wp_from[0] + (wp_to[0] - wp_from[0]) * t
        lon = wp_from[1] + (wp_to[1] - wp_from[1]) * t
        base_alt = wp_from[2] + (wp_to[2] - wp_from[2]) * t

        # Small micro-perturbation for realistic sensor noise
        lat_noise = random.uniform(-0.00003, 0.00003)
        lon_noise = random.uniform(-0.00003, 0.00003)
        alt_noise = random.uniform(-0.3, 0.3)

        current_lat = round(lat + lat_noise, 6)
        current_lon = round(lon + lon_noise, 6)
        current_alt = round(base_alt + alt_noise, 1)

        # Calculate heading to target waypoint
        raw_heading = self.calculate_bearing(current_lat, current_lon, wp_to[0], wp_to[1])
        # Smooth heading transition
        heading = round((0.85 * raw_heading + 0.15 * self.last_heading) % 360.0, 1)
        self.last_heading = heading

        now = timezone.now()
        self.total_generated_packets += 1

        return {
            'drone_id': self.drone_id,
            'latitude': current_lat,
            'longitude': current_lon,
            'altitude': current_alt,
            'heading': heading,
            'timestamp': now,
            'is_simulated': True,
            'route_name': self.route_name,
        }

    def step_and_save(self):
        """
        Generates the next simulated point and persists it to SQLite with is_simulated=True.
        Returns the saved DroneTelemetry model instance.
        """
        telemetry_data = self.step()
        record = DroneTelemetry.objects.create(
            drone_id=telemetry_data['drone_id'],
            latitude=telemetry_data['latitude'],
            longitude=telemetry_data['longitude'],
            altitude=telemetry_data['altitude'],
            heading=telemetry_data['heading'],
            timestamp=telemetry_data['timestamp'],
            is_simulated=True,
        )
        return record

    def reset(self, randomize=True):
        """
        Resets the simulation. If randomize is True, generates a brand new flight route.
        Otherwise resets to the start of the current route.
        """
        if randomize:
            self.generate_random_route()
        else:
            self.current_waypoint_index = 0
            self.progress = 0.0
            if len(self.waypoints) >= 2:
                self.last_heading = self.calculate_bearing(
                    self.waypoints[0][0], self.waypoints[0][1],
                    self.waypoints[1][0], self.waypoints[1][1]
                )
        return self.route_name
