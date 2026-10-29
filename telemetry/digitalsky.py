"""
Digital Sky Platform Airspace Map Service
Conforming to DGCA Drone Rules 2021 & Ministry of Civil Aviation (MoCA) DigitalSky Specifications.

Airspace Zone Classifications under Drone Rules 2021:
1. GREEN ZONE:
   - Airspace up to 400 feet (120 meters) AGL outside yellow/red zones.
   - Operations require no prior flight permission under Drone Rules 2021.
2. YELLOW ZONE:
   - Controlled airspace between 8 km and 12 km from operational airport perimeter (above 200 ft).
   - Airspace between 5 km and 8 km from operational airport perimeter (up to 400 ft).
   - Airspace above 400 feet in designated green zones.
   - Requires prior Air Traffic Control (ATC / AAI / MoD) clearance via DigitalSky.
3. RED ZONE (Strictly Prohibited Airspace - No-Fly Zone):
   - 0 to 5 km perimeter around operational civil/defense airport runways.
   - 25 km buffer zone along ALL International Land Borders (LOC / LAC / IB).
     Includes: India-Pakistan, India-China, India-Nepal, India-Bhutan, India-Bangladesh, India-Myanmar.
   - Entire northern frontier / Kashmir Line of Control & high-altitude defense corridors.
   - Military defense areas, IAF airbases, Naval stations, Army Cantonments & Firing ranges.
   - Defense factories & Ordnance manufacturing production facilities.
   - Hazardous petrochemical refineries & industrial mega-complexes.
   - Major dams, reservoirs & sensitive water bodies (hydrological security).
   - Strategic and nuclear installations (BARC, NPCIL plants, spaceports, refineries).
   - Temporary Red Zones (TFR - VIP Security, Parliament, Rashtrapati Bhavan, National Events).
   - Drone operations strictly prohibited unless exempted by Central Government.
"""

import os
import json
import logging
import math
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_BOUNDARY_FILE = os.path.join(_DATA_DIR, "india_boundary.json")
_CORRIDORS_FILE = os.path.join(_DATA_DIR, "border_corridors.json")

def _load_json_data(file_path: str) -> Optional[Any]:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Could not load %s: %s", file_path, e)
    return None

_INDIA_BOUNDARY_DATA = _load_json_data(_BOUNDARY_FILE)
_BORDER_CORRIDORS_DATA = _load_json_data(_CORRIDORS_FILE)



def generate_circle_polygon(lat: float, lon: float, radius_km: float, num_points: int = 36) -> List[List[float]]:
    """Generates GeoJSON Polygon coordinates [[lon, lat], ...] for a circle given center and radius in km."""
    coords = []
    lat_deg_per_km = 1.0 / 110.574
    cos_lat = math.cos(math.radians(lat))
    lon_deg_per_km = 1.0 / (111.320 * cos_lat) if abs(cos_lat) > 0.001 else 1.0 / 111.320

    for i in range(num_points):
        angle = math.radians((360.0 / num_points) * i)
        dx = radius_km * math.sin(angle)
        dy = radius_km * math.cos(angle)
        p_lat = lat + (dy * lat_deg_per_km)
        p_lon = lon + (dx * lon_deg_per_km)
        coords.append([round(p_lon, 6), round(p_lat, 6)])
    coords.append(coords[0])
    return coords


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def is_point_in_polygon(lat: float, lon: float, polygon_coords: List[List[float]]) -> bool:
    """Ray casting algorithm to determine if (lat, lon) is inside a polygon with [lon, lat] coordinates."""
    inside = False
    n = len(polygon_coords)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = polygon_coords[i][0], polygon_coords[i][1]  # xi=lon, yi=lat
        xj, yj = polygon_coords[j][0], polygon_coords[j][1]
        intersect = ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside


# ==============================================================================
# 1. MAJOR CIVIL & DUAL-USE AIRPORTS (0-5 km RED, 5-12 km YELLOW)
# ==============================================================================
from telemetry.data.aerodromes_master import ALL_INDIAN_AERODROMES

INDIAN_AERODROMES = ALL_INDIAN_AERODROMES

# ==============================================================================
# 2. CONTINUOUS 25 KM INTERNATIONAL LAND BORDER RIBBON CORRIDORS & DEFENSE ZONES
# ==============================================================================
def _get_corridor_coords(key: str, fallback: List[List[float]]) -> List[List[float]]:
    if _BORDER_CORRIDORS_DATA and key in _BORDER_CORRIDORS_DATA:
        return _BORDER_CORRIDORS_DATA[key]
    return fallback

def _get_northern_frontier_red_zone_coords() -> List[List[float]]:
    if _INDIA_BOUNDARY_DATA and "mainland" in _INDIA_BOUNDARY_DATA:
        mainland_pts = _INDIA_BOUNDARY_DATA["mainland"]
        if len(mainland_pts) >= 1500:
            outer = mainland_pts[1496:] + mainland_pts[:71]
            cutline = [
                [79.22, 33.24],
                [79.00, 33.20],
                [78.70, 33.60],
                [78.30, 33.95],
                [77.95, 34.20],
                [77.60, 34.45],
                [77.10, 34.45],
                [76.15, 34.40],
                [75.80, 34.45],
                [75.05, 34.25],
                [74.75, 34.25],
                [74.40, 34.25],
                [73.5946, 33.8916]
            ]
            return outer + cutline
    return [
        [73.60, 33.90], [73.40, 34.80], [73.10, 35.50], [73.00, 36.30], [73.50, 36.80],
        [74.20, 37.05], [74.80, 37.12], [75.60, 36.95], [76.50, 36.50],
        [77.20, 36.10], [77.80, 35.70], [78.50, 35.60], [79.20, 35.30],
        [79.80, 34.80], [80.30, 34.20], [79.80, 33.70], [79.30, 33.00], [79.22, 33.24],
        [78.70, 33.60], [77.60, 34.45], [76.15, 34.40], [74.75, 34.25], [73.60, 33.90]
    ]

INTERNATIONAL_BORDER_POLYGONS = [
    {
        "id": "DS-CORRIDOR-WEST-IB",
        "name": "Western International Border 25 km Red Zone Ribbon (Gujarat - Rajasthan - Punjab)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the International Border from Sir Creek/Rann of Kutch to Pathankot.",
        "coordinates": _get_corridor_coords("west_ib", [
            [68.20, 23.65], [68.75, 24.35], [70.15, 25.10], [70.05, 26.50],
            [69.95, 27.25], [71.20, 27.95], [72.30, 28.60], [73.50, 29.80],
            [73.95, 30.40], [74.55, 31.60], [75.05, 32.15], [75.45, 32.40],
            [75.72, 32.22], [75.32, 31.98], [74.82, 31.42], [74.28, 30.22],
            [73.80, 29.55], [72.58, 28.38], [71.48, 27.75], [70.32, 27.05],
            [70.42, 26.35], [70.45, 24.95], [69.05, 24.20], [68.60, 23.55],
            [68.20, 23.65]
        ])
    },
    {
        "id": "DS-CORRIDOR-NORTH-LOC-LAC-OUTER",
        "name": "Northern Frontier 25 km International Boundary Ribbon (J&K LOC - Gilgit - Ladakh LAC)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km statutory defense buffer ribbon along the Line of Control (LOC) and Line of Actual Control (LAC) covering Kathua, Jammu, Poonch, Uri, Kupwara, Gilgit, Hunza, Baltistan, Siachen, Aksai Chin, and Eastern Ladakh.",
        "coordinates": _get_corridor_coords("north_jk_ladakh", [
            [75.32, 32.30], [74.70, 32.66], [73.82, 33.01], [73.45, 34.57],
            [74.13, 35.12], [73.13, 35.72], [72.52, 36.08], [73.85, 36.72],
            [74.56, 36.97], [75.42, 36.96], [76.39, 36.31], [77.47, 35.65],
            [78.18, 35.67], [79.27, 35.93], [80.28, 35.20], [79.79, 34.63],
            [78.99, 34.04], [79.22, 33.24], [79.28, 32.56], [79.20, 32.34],
            [75.05, 32.30], [75.32, 32.30]
        ])
    },
    {
        "id": "DS-CORRIDOR-CHINA-LAC-HIMALAYAS",
        "name": "Middle Sector China LAC 25 km Red Zone Ribbon (Himachal - Uttarakhand)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km Line of Actual Control (LAC) Red Zone across Himachal Pradesh (Kinnaur/Spiti) and Uttarakhand (Uttarkashi, Chamoli/Mana, Pithoragarh/Lipulekh).",
        "coordinates": _get_corridor_coords("middle_lac", [
            [78.50, 32.05], [78.85, 31.60], [79.25, 31.25], [79.75, 30.95],
            [80.35, 30.45], [80.70, 30.15],
            [80.45, 29.95], [80.10, 30.25], [79.55, 30.70], [79.05, 31.05],
            [78.60, 31.40], [78.25, 31.85], [78.50, 32.05]
        ])
    },
    {
        "id": "DS-CORRIDOR-NEPAL-BORDER",
        "name": "Indo-Nepal International Border 25 km Red Zone Ribbon (Uttarakhand - UP - Bihar - Bengal)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the entire Indo-Nepal international land border across Uttarakhand, Uttar Pradesh, Bihar, and North Bengal.",
        "coordinates": _get_corridor_coords("nepal", [
            [80.50, 30.25], [80.12, 29.05], [80.20, 28.70], [80.65, 28.35],
            [81.60, 27.80], [82.25, 27.70], [82.80, 27.50], [83.45, 27.45],
            [83.95, 27.40], [84.85, 26.98], [85.50, 26.75], [86.15, 26.60],
            [87.00, 26.50], [87.30, 26.40], [88.05, 26.35], [88.15, 26.70],
            [88.04, 27.04]
        ])
    },
    {
        "id": "DS-CORRIDOR-SIKKIM-BORDER",
        "name": "Sikkim International Border 25 km Red Zone Ribbon (Nepal - Tibet - Bhutan Perimeters)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km statutory defense buffer ribbon wrapping around the international borders of Sikkim with Nepal, Tibet/China and Bhutan, preserving central Sikkim and Pakyong civil airspace.",
        "coordinates": _get_corridor_coords("sikkim", [
            [88.04, 27.04], [88.20, 27.75], [88.75, 28.10], [88.90, 27.50], [88.87, 27.11],
            [88.65, 27.25], [88.40, 27.50], [88.25, 27.20], [88.04, 27.04]
        ])
    },
    {
        "id": "DS-CORRIDOR-BHUTAN-BORDER",
        "name": "Indo-Bhutan International Border 25 km Red Zone Ribbon (Bengal - Assam - Arunachal)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the India-Bhutan international border across East Sikkim, North Bengal (Jaigaon), Western/Central Assam (Alipurduar, Kokrajhar, Chirang, Baksa, Udalguri), and West Kameng.",
        "coordinates": _get_corridor_coords("bhutan", [
            [88.90, 27.15], [89.40, 26.85], [89.70, 26.75], [90.25, 26.85],
            [90.55, 26.88], [91.50, 26.82], [92.10, 26.90], [91.80, 27.35],
            [91.50, 27.55],
            [91.75, 27.45], [91.95, 27.15], [92.15, 26.68], [91.50, 26.60],
            [90.55, 26.65], [90.25, 26.62], [89.40, 26.62], [88.95, 26.92],
            [88.90, 27.15]
        ])
    },
    {
        "id": "DS-CORRIDOR-CHINA-ARUNACHAL-MCMAHON",
        "name": "Arunachal McMahon Line 25 km Red Zone Ribbon (Tawang to Kibithu/Walong)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km Line of Actual Control (LAC) McMahon Line Red Zone covering Arunachal Pradesh frontier from Tawang and Bum La to Kibithu and Walong.",
        "coordinates": _get_corridor_coords("mcmahon", [
            [91.85, 27.70], [92.80, 27.85], [93.50, 28.15], [94.20, 28.35],
            [95.00, 28.95], [95.80, 28.85], [96.50, 28.45], [97.05, 28.25],
            [96.95, 28.00], [96.35, 28.20], [95.65, 28.60], [94.95, 28.70],
            [94.15, 28.10], [93.45, 27.90], [92.75, 27.60], [91.95, 27.45],
            [91.85, 27.70]
        ])
    },
    {
        "id": "DS-CORRIDOR-MYANMAR-BORDER",
        "name": "Indo-Myanmar International Border 25 km Red Zone Ribbon (Arunachal - Nagaland - Manipur - Mizoram)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the India-Myanmar international border across Eastern Arunachal (Pangsau Pass), Nagaland (Mon/Kiphire), Manipur (Moreh/Chandel) and Mizoram (Zokhawthar/Champhai/Parva).",
        "coordinates": _get_corridor_coords("myanmar", [
            [97.20, 28.00], [96.25, 27.25], [95.55, 26.85], [95.15, 26.50],
            [94.90, 25.70], [94.80, 25.50], [94.55, 25.10], [94.40, 24.25],
            [94.00, 23.90], [93.45, 23.50], [93.38, 23.05], [93.18, 22.40],
            [92.88, 21.95],
            [92.60, 22.10], [92.90, 22.50], [93.10, 23.25], [93.65, 24.00],
            [94.05, 24.45], [94.20, 25.00], [94.50, 25.60], [94.85, 26.30],
            [95.30, 27.00], [95.90, 27.35], [96.95, 27.85], [97.20, 28.00]
        ])
    },
    {
        "id": "DS-CORRIDOR-BANGLADESH-BORDER",
        "name": "Indo-Bangladesh International Border 25 km Red Zone Ribbon",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the entire India-Bangladesh border across West Bengal, Meghalaya, Assam, Tripura, and Mizoram.",
        "coordinates": _get_corridor_coords("bangladesh", [
            [89.15, 21.65], [88.95, 22.20], [88.88, 23.05], [88.65, 23.75],
            [88.35, 24.45], [88.25, 25.10], [88.98, 25.28], [88.25, 26.20],
            [88.90, 26.35], [89.85, 26.30], [89.95, 26.00], [89.85, 25.75],
            [90.15, 25.90], [89.65, 26.45], [88.80, 26.50], [88.10, 26.15],
            [88.75, 25.25], [88.05, 25.00], [88.15, 24.30], [88.45, 23.60],
            [88.65, 22.85], [88.75, 22.15], [88.90, 21.65], [89.15, 21.65]
        ])
    }
]

# ==============================================================================
# 2B. STRATEGIC INLAND & OFFSHORE DEFENSE ENCLAVE RED ZONES (AAI DIGITAL SKY)
# ==============================================================================
STRATEGIC_DEFENSE_POLYGONS = [
    {
        "id": "DS-POLY-ONDA-BANKURA-PURULIA-DEFENSE",
        "name": "Onda - Bankura - Purulia - Dhanbad Strategic Defense & Armament Corridor",
        "category": "Military Strategic Area",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Eastern military transit corridor, defense ammunition depots, and heavy tactical logistical staging area across Dhanbad, Purulia, Bankura, and Onda.",
        "coordinates": [[86.20, 23.95], [87.35, 23.10], [87.45, 22.95], [87.45, 22.65], [86.95, 22.65], [86.95, 23.00], [86.20, 23.00], [86.20, 23.95]]
    },
    {
        "id": "DS-POLY-MP-SIDHI-DEFENSE",
        "name": "Sidhi - Singrauli Strategic Energy & Defense Zone",
        "category": "Strategic Defense Red Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Critical national energy grid infrastructure and strategic defense security envelope across Sidhi and Singrauli.",
        "coordinates": [[81.80, 24.25], [82.00, 24.60], [82.25, 24.45], [82.05, 24.10], [81.80, 24.25]]
    },
    {
        "id": "DS-POLY-RAJ-SAWAI-MADHOPUR",
        "name": "Sawai Madhopur - Ranthambore Strategic Buffer Zone",
        "category": "Border Strategic Defense Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Central Rajasthan military strategic corridor and tactical observation security zone.",
        "coordinates": [[76.35, 25.95], [76.55, 26.20], [76.70, 26.05], [76.45, 25.85], [76.35, 25.95]]
    },
    {
        "id": "DS-POLY-RAJ-KOTA-RAWATBHATA",
        "name": "Kota - Rawatbhata Nuclear & Heavy Water Strategic Envelope",
        "category": "Nuclear Installation & Coastal Defense",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Rajasthan Atomic Power Station (RAPS) and heavy water production security corridor along Chambal river.",
        "coordinates": [[75.50, 24.95], [75.65, 25.10], [76.00, 24.85], [75.85, 24.70], [75.50, 24.95]]
    },

    {
        "id": "DS-POLY-OFFSHORE-BOMBAY-HIGH",
        "name": "Bombay High Offshore Oil & Western Naval Exclusion Red Zone (Arabian Sea)",
        "category": "Offshore Strategic Installation",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Critical national energy offshore platform and Western Naval Command maritime defense exclusion zone in the Arabian Sea.",
        "coordinates": [[70.80, 18.70], [70.80, 19.80], [72.30, 20.00], [72.60, 18.70], [70.80, 18.70]]
    },
    {
        "id": "DS-POLY-OFFSHORE-MUMBAI-COAST",
        "name": "Mumbai Coastal Naval Air Arm & Harbor Security Exclusion Zone",
        "category": "Naval Strategic Maritime Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Western Naval Command coastal and harbor defense zone off Mumbai/Palghar.",
        "coordinates": [[71.60, 19.05], [71.60, 19.50], [72.45, 19.50], [72.45, 19.05], [71.60, 19.05]]
    },
    {
        "id": "DS-POLY-OFFSHORE-CHANDIPUR",
        "name": "Chandipur & APJ Abdul Kalam Island DRDO Missile Launch Corridor (Bay of Bengal)",
        "category": "Strategic Missile Test Range",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Integrated Test Range (ITR) Chandipur and Wheeler Island high-security missile launch envelope in the Bay of Bengal.",
        "coordinates": [[87.35, 20.35], [87.35, 21.15], [88.50, 21.15], [88.50, 20.35], [87.35, 20.35]]
    },
    {
        "id": "DS-POLY-MAHAJAN-FIRING-RANGE",
        "name": "Mahajan Field Firing Range (MFFR Bikaner / Suratgarh / Lunkaransar)",
        "category": "Military Field Firing Range",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Asia's largest army field firing and combat maneuver range complex in Thar Desert.",
        "coordinates": [[73.40, 28.25], [73.60, 28.95], [74.05, 28.85], [74.00, 28.45], [73.70, 28.10], [73.40, 28.25]]
    },
    {
        "id": "DS-POLY-GARHWAL-CORBETT-DEFENSE",
        "name": "Garhwal Strategic Defense & Corbett Range (Pauri - Almora - Lansdowne)",
        "category": "Military Strategic Area",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Strategic high-altitude mountain warfare training and defense enclave in Garhwal Himalayas.",
        "coordinates": [[78.55, 29.55], [78.95, 30.20], [79.60, 29.90], [79.25, 29.25], [78.55, 29.55]]
    },
    {
        "id": "DS-POLY-SAHARANPUR-MUZAFFARNAGAR",
        "name": "Saharanpur - Sarsawa AFS - Muzaffarnagar Defense Corridor",
        "category": "Military Armament & Air Defense Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Sarsawa Air Force Station combat helicopter wing and Western UP military cantonment defense envelope.",
        "coordinates": [[77.05, 29.40], [77.20, 30.15], [77.85, 30.10], [77.90, 29.50], [77.60, 29.30], [77.05, 29.40]]
    },
    {
        "id": "DS-DEFENSE-DUDHWA-BUFFER",
        "name": "Dudhwa - Palia - Nighasan Border Strategic Defense Area",
        "category": "Border Strategic Defense Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Indo-Nepal border strategic security envelope across Dudhwa, Palia, and Lakhimpur Kheri.",
        "coordinates": [[80.40, 28.00], [80.20, 28.35], [80.50, 28.75], [81.10, 28.55], [81.20, 28.10], [80.70, 27.90], [80.40, 28.00]]
    },
    {
        "id": "DS-POLY-MH-DEFENSE-CORRIDOR",
        "name": "Pune - Ahmednagar - Baramati - Solapur Military Defense Corridor",
        "category": "Military Armament & Training Complex",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Southern Command armored combat training center (ACC&S Ahmednagar), Pune military garrison, and Solapur defense envelope.",
        "coordinates": [[73.65, 18.60], [74.15, 19.30], [75.10, 19.25], [75.65, 18.75], [76.15, 17.65], [75.60, 17.40], [74.65, 18.05], [73.65, 18.60]]
    },
    {
        "id": "DS-POLY-MH-SHIRPUR-DEFENSE",
        "name": "North Maharashtra Shirpur - Sendhwa Strategic Defense Polygon",
        "category": "Military Strategic Area",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Satpura mountain pass military strategic transit and defense training enclave.",
        "coordinates": [[74.65, 21.15], [74.95, 21.65], [75.40, 21.50], [74.65, 21.15]]
    },
    {
        "id": "DS-POLY-MH-JALGAON-DEFENSE",
        "name": "North Maharashtra Chopda - Jalgaon - Burhanpur Defense Polygon",
        "category": "Military Strategic Area",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Khandesh corridor strategic defense and armament security enclave.",
        "coordinates": [[75.40, 21.50], [75.80, 21.65], [75.85, 20.90], [75.40, 21.50]]
    },
    {
        "id": "DS-POLY-BABINA-JHANSI-FIRING-RANGE",
        "name": "Babina - Jhansi - Shivpuri Army Field Firing Range Complex",
        "category": "Military Field Firing Range",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "White Tiger Division armored artillery and combat vehicle live-firing maneuvers zone spanning UP and MP.",
        "coordinates": [[78.05, 24.95], [78.20, 25.75], [78.75, 25.80], [78.90, 25.20], [78.45, 24.85], [78.05, 24.95]]
    },
    {
        "id": "DS-POLY-JH-DEFENSE-CORRIDOR",
        "name": "Jharkhand Jamshedpur - Bokaro - Ramgarh Strategic Industrial Defense Area",
        "category": "Critical Defense Metallurgy Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Strategic heavy industrial and defense metal manufacturing facilities across Chota Nagpur plateau.",
        "coordinates": [[85.80, 23.35], [86.35, 23.85], [86.55, 23.15], [86.10, 22.75], [85.80, 23.35]]
    },
    {
        "id": "DS-POLY-POKHRAN-FIRING-RANGE",
        "name": "Pokhran Desert Army Field Firing Range & Nuclear Test Grounds",
        "category": "Strategic Weapon Test Facility",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Desert corps combined arms strike weapon testing grounds and historical nuclear test site in Jaisalmer district.",
        "coordinates": [[71.60, 26.75], [71.60, 27.45], [72.25, 27.45], [72.25, 26.75], [71.60, 26.75]]
    },
    {
        "id": "DS-POLY-DELHI-NCT-VVIP",
        "name": "National Capital Territory (Delhi VVIP & Parliament Red Zone)",
        "category": "National Capital Security Perimeter",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "VVIP Security envelope covering Rashtrapati Bhavan, Prime Minister Residence, Central Vista, Parliament House, and diplomatic enclave.",
        "coordinates": [[77.10, 28.52], [77.10, 28.66], [77.26, 28.66], [77.26, 28.52], [77.10, 28.52]]
    },
    {
        "id": "DS-POLY-SRIHARIKOTA-ISRO",
        "name": "Satish Dhawan Space Centre (SDSC SHAR) Launch Facility",
        "category": "Space Launch Center",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "ISRO spaceport barrier envelope covering Sriharikota island, rocket launch pads, and Pulicat Lake security zone.",
        "coordinates": [[80.15, 13.60], [80.15, 13.95], [80.35, 13.95], [80.35, 13.60], [80.15, 13.60]]
    },
    {
        "id": "DS-POLY-JAMNAGAR-PORBANDAR",
        "name": "Jamnagar - Porbandar IAF Fighter Base & Naval Air Station",
        "category": "Military Strategic Coastal Base",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Jaguar fighter base, INS Sardar Patel, and Indian Coast Guard western air command security envelope.",
        "coordinates": [[69.45, 21.60], [69.45, 22.50], [70.15, 22.50], [70.15, 21.60], [69.45, 21.60]]
    },
    {
        "id": "DS-ZONE-NORTHERN-FRONTIER-KASHMIR-LADAKH",
        "name": "Northern Kashmir & Ladakh Strategic Defense Red Zone",
        "category": "High-Security Defense Frontier",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Solid high-altitude strategic defense frontier covering entire Northern Kashmir LOC, Gilgit, Hunza, Nagar, Skardu, Siachen, Nubra Valley, Galwan, Aksai Chin, and Pangong Tso up to sovereign boundary, leaving civil airspace pockets around Leh and Srinagar.",
        "coordinates": _get_northern_frontier_red_zone_coords()
    },
    {
        "id": "DS-POLY-SE-LADAKH-DEFENSE",
        "name": "South-Eastern Ladakh Strategic Defense Red Zone (Hanle / Chumar / Nyoma)",
        "category": "Strategic Defense Red Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "High-altitude eastern Ladakh military defense zone covering Nyoma airbase, Hanle observatory security envelope, and Chumar LAC frontier.",
        "coordinates": [[78.40, 32.60], [79.05, 32.50], [79.20, 33.15], [78.45, 33.25], [78.40, 32.60]]
    },
    {
        "id": "DS-POLY-KISHANGANJ-PURNEA",
        "name": "Kishanganj - Purnia Strategic Defense Red Zone (Bihar - Bengal Border)",
        "category": "Border Strategic Defense Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Siliguri neck strategic southern flank defense corridor and military logistical transit security envelope spanning Kishanganj and Purnia districts.",
        "coordinates": [[87.70, 26.35], [88.25, 26.40], [88.20, 26.05], [87.80, 25.95], [87.70, 26.35]]
    },
    {
        "id": "DS-POLY-ASSAM-BONGAIGAON-SRIJANG",
        "name": "Lower Assam Bongaigaon - Srijang Strategic Defense Enclave",
        "category": "Military Strategic Area",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Brahmaputra northern corridor defense armament installation and army transit staging complex across Bongaigaon, Srijang and Chirang.",
        "coordinates": [[89.95, 26.45], [90.80, 26.40], [90.75, 26.15], [89.90, 26.25], [89.95, 26.45]]
    },
    {
        "id": "DS-POLY-ASSAM-RUPSI-DEFENSE",
        "name": "Rupsi - Dhubri Defense Enclave & Airfield Security Zone",
        "category": "Military Armament & Air Defense Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Rupsi air station and western Brahmaputra border tactical defense envelope.",
        "coordinates": [[89.65, 26.20], [90.10, 26.20], [90.05, 25.95], [89.60, 26.00], [89.65, 26.20]]
    },
    {
        "id": "DS-POLY-OFFSHORE-PRAKASAM",
        "name": "Prakasam & Nellore Coastal Missile & Rocket Hazard Area (Bay of Bengal)",
        "category": "Offshore Strategic Missile Hazard Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Eastern Naval Command and defense launch trajectory hazard envelope extending eastward into the Bay of Bengal off Prakasam and Nellore coast.",
        "coordinates": [[80.05, 15.65], [80.70, 15.75], [81.50, 15.45], [80.15, 15.15], [80.05, 15.65]]
    },
    {
        "id": "DS-POLY-OFFSHORE-GOA-SINDHUDURG",
        "name": "Goa - Sindhudurg - Karwar Naval Exercise & Firing Range (Arabian Sea)",
        "category": "Offshore Naval Exercise Area",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "INS Hansa naval air station and INS Kadamba Karwar naval base maritime gunnery and anti-submarine exercise exclusion zone.",
        "coordinates": [[73.10, 16.05], [73.55, 15.75], [73.35, 15.30], [72.90, 15.60], [73.10, 16.05]]
    },
    {
        "id": "DS-POLY-OFFSHORE-SRIHARIKOTA-HAZARD",
        "name": "Sriharikota Space Launch Offshore Hazard Envelope (Bay of Bengal)",
        "category": "Offshore Space Launch Hazard Zone",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Downrange rocket launch safety corridor and maritime exclusion zone off Satish Dhawan Space Centre (SHAR).",
        "coordinates": [[80.20, 14.15], [80.50, 14.05], [80.45, 13.65], [80.22, 13.70], [80.20, 14.15]]
    },
    {
        "id": "DS-POLY-KUDANKULAM-KANYAKUMARI",
        "name": "Kudankulam Nuclear Complex & Cape Comorin Defense Zone",
        "category": "Nuclear Installation & Coastal Defense",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Kudankulam Nuclear Power Plant (KKNPP) statutory safety perimeter and southern tip naval coastal monitoring envelope.",
        "coordinates": [[77.55, 8.40], [78.00, 8.45], [77.90, 8.10], [77.50, 8.12], [77.55, 8.40]]
    }
]

# ==============================================================================
# 3. 25 KM INTERNATIONAL BORDER BUFFER ZONES (CHECKPOINT & SECTOR CIRCLES)
# ==============================================================================
INTERNATIONAL_BORDER_RED_ZONES = [
    # --- INDIA - PAKISTAN BORDER & LOC ---
    {"id": "DS-BORDER-PB-AMRITSAR", "name": "Punjab Border 25 km Red Zone (Amritsar / Attari / Wagah Sector)", "lat": 31.6046, "lon": 74.5750, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Land Border Red Zone along India-Pakistan IB (Amritsar/Tarn Taran)."},
    {"id": "DS-BORDER-PB-FEROZEPUR", "name": "Punjab Border 25 km Red Zone (Ferozepur / Hussainiwala Sector)", "lat": 30.9500, "lon": 74.5200, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border buffer covering Ferozepur & Hussainiwala frontier."},
    {"id": "DS-BORDER-PB-FAZILKA", "name": "Punjab Border 25 km Red Zone (Fazilka / Sadiqi Sector)", "lat": 30.4000, "lon": 74.0200, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border security envelope along Fazilka/Abohar corridor."},
    {"id": "DS-BORDER-PB-GURDASPUR", "name": "Punjab Border 25 km Red Zone (Gurdaspur / Dera Baba Nanak Sector)", "lat": 31.9800, "lon": 75.0500, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border Corridor near Kartarpur/Dera Baba Nanak frontier."},
    {"id": "DS-BORDER-PB-PATHANKOT", "name": "Punjab Border 25 km Red Zone (Pathankot / Narot Jaimal Singh Sector)", "lat": 32.2800, "lon": 75.4800, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border security zone covering Ravi river and frontier."},
    {"id": "DS-BORDER-RJ-JAISALMER", "name": "Rajasthan Border 25 km Red Zone (Jaisalmer / Tanot / Longewala Sector)", "lat": 27.2000, "lon": 70.4000, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km International Border Red Zone along Thar Desert / Longewala defense frontier."},
    {"id": "DS-BORDER-RJ-BARMER", "name": "Rajasthan Border 25 km Red Zone (Barmer / Munabao Sector)", "lat": 25.7500, "lon": 70.3000, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km Border buffer covering Munabao / Gadra Road border corridor."},
    {"id": "DS-BORDER-RJ-BIKANER", "name": "Rajasthan Border 25 km Red Zone (Bikaner / Khajuwala Sector)", "lat": 28.3000, "lon": 72.5000, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km International Border security zone covering Khajuwala / Pugal corridor."},
    {"id": "DS-BORDER-RJ-GANGANAGAR", "name": "Rajasthan Border 25 km Red Zone (Sri Ganganagar / Hindumalkot Sector)", "lat": 29.9500, "lon": 73.8800, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km Border Corridor along Hindumalkot and Anupgarh frontier."},
    {"id": "DS-BORDER-GJ-KUTCH", "name": "Gujarat Border 25 km Red Zone (Rann of Kutch & Sir Creek Sector)", "lat": 23.8500, "lon": 68.7500, "radius_km": 25.0, "sector": "GUJARAT_IB", "desc": "DGCA 25 km International Land Border & Sir Creek maritime corridor. Strictly Prohibited."},
    {"id": "DS-BORDER-JK-SAMBA-KATHUA", "name": "Jammu Border 25 km Red Zone (Jammu / Samba / Kathua IB Sector)", "lat": 32.5500, "lon": 75.1000, "radius_km": 25.0, "sector": "JK_IB", "desc": "DGCA 25 km International Border buffer across Jammu, Samba, and Hiranagar."},
    {"id": "DS-BORDER-JK-RS-PURA", "name": "Jammu Border 25 km Red Zone (RS Pura / Suchetgarh Sector)", "lat": 32.6200, "lon": 74.7200, "radius_km": 25.0, "sector": "JK_IB", "desc": "DGCA 25 km International Border buffer along Suchetgarh border crossing."},
    {"id": "DS-BORDER-JK-POONCH-RAJOURI", "name": "Line of Control 25 km Red Zone (Rajouri / Poonch LOC Sector)", "lat": 33.7700, "lon": 74.1000, "radius_km": 25.0, "sector": "JK_LOC", "desc": "DGCA 25 km Line of Control (LOC) strict defense Red Zone."},
    {"id": "DS-BORDER-JK-KUPWARA-URI", "name": "Line of Control 25 km Red Zone (Kupwara / Uri / Tangdhar Sector)", "lat": 34.3500, "lon": 74.0500, "radius_km": 25.0, "sector": "JK_LOC", "desc": "DGCA 25 km LOC high-altitude defense corridor."},
    {"id": "DS-BORDER-JK-GUREZ", "name": "Line of Control 25 km Red Zone (Gurez / Bandipora Sector)", "lat": 34.6500, "lon": 74.8500, "radius_km": 25.0, "sector": "JK_LOC", "desc": "DGCA 25 km northern Kashmir LOC high-altitude defense corridor."},
    {"id": "DS-BORDER-LADAKH-KARGIL", "name": "Line of Control 25 km Red Zone (Dras / Kargil / Batalik Sector)", "lat": 34.5800, "lon": 75.8000, "radius_km": 25.0, "sector": "LADAKH_LOC", "desc": "DGCA 25 km high-altitude Line of Control defense envelope across Kargil and Dras."},
    {"id": "DS-BORDER-LADAKH-DBO", "name": "Ladakh LAC 25 km Red Zone (Daulat Beg Oldie / Siachen Sector)", "lat": 35.2500, "lon": 77.9000, "radius_km": 25.0, "sector": "LADAKH_LAC", "desc": "DGCA 25 km northern LAC and Karakoram high-altitude prohibited airspace."},
    {"id": "DS-BORDER-LADAKH-EAST", "name": "Ladakh LAC 25 km Red Zone (Pangong Tso / Chushul / Galwan Sector)", "lat": 33.7500, "lon": 78.7000, "radius_km": 25.0, "sector": "LADAKH_LAC", "desc": "DGCA 25 km Line of Actual Control (LAC) high-security border corridor."},
    {"id": "DS-BORDER-LADAKH-DEMCHOK", "name": "Ladakh LAC 25 km Red Zone (Demchok / Indus Valley Sector)", "lat": 32.7000, "lon": 79.4500, "radius_km": 25.0, "sector": "LADAKH_LAC", "desc": "DGCA 25 km southern Ladakh Line of Actual Control prohibited airspace."},

    # --- INDIA - CHINA LAC (MIDDLE SECTOR) ---
    {"id": "DS-BORDER-HP-SHIPKILA", "name": "Himachal LAC 25 km Red Zone (Kinnaur / Spiti / Shipki La Sector)", "lat": 31.8500, "lon": 78.7500, "radius_km": 25.0, "sector": "HIMACHAL_LAC", "desc": "DGCA 25 km Line of Actual Control buffer along Tibet border in Kinnaur & Spiti."},
    {"id": "DS-BORDER-UK-MANAPASS", "name": "Uttarakhand LAC 25 km Red Zone (Chamoli / Mana Pass / Niti Sector)", "lat": 31.0500, "lon": 79.4500, "radius_km": 25.0, "sector": "UTTARAKHAND_LAC", "desc": "DGCA 25 km Himalayan Line of Actual Control defense corridor."},
    {"id": "DS-BORDER-UK-LIPULEKH", "name": "Uttarakhand Border 25 km Red Zone (Pithoragarh / Lipulekh / Kalapani)", "lat": 30.2500, "lon": 80.5000, "radius_km": 25.0, "sector": "UTTARAKHAND_BORDER", "desc": "DGCA 25 km International Border buffer across Indo-Tibet-Nepal tri-junction."},

    # --- INDIA - NEPAL BORDER ---
    {"id": "DS-BORDER-UK-BANBASA", "name": "Uttarakhand Nepal Border 25 km Red Zone (Champawat / Tanakpur / Banbasa)", "lat": 29.0500, "lon": 80.1000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer along Sharda Barrage and Nepal border."},
    {"id": "DS-BORDER-UP-PILIBHIT", "name": "UP Nepal Border 25 km Red Zone (Pilibhit / Sharda River Sector)", "lat": 28.6500, "lon": 80.2000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border corridor along Pilibhit tiger reserve frontier."},
    {"id": "DS-BORDER-UP-DUDHWA", "name": "UP Nepal Border 25 km Red Zone (Lakhimpur Kheri / Gauriphanta Sector)", "lat": 28.3500, "lon": 80.6500, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer near Dhangadhi / Gauriphanta crossing."},
    {"id": "DS-BORDER-UP-RUPAIDIHA", "name": "UP Nepal Border 25 km Red Zone (Bahraich / Rupaidiha Sector)", "lat": 27.8000, "lon": 81.6000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer along Nepalgunj / Rupaidiha trade corridor."},
    {"id": "DS-BORDER-UP-BADHNI", "name": "UP Nepal Border 25 km Red Zone (Siddharthnagar / Badhni Sector)", "lat": 27.5000, "lon": 82.8000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border envelope along Kapilvastu frontier."},
    {"id": "DS-BORDER-UP-SONAULI", "name": "UP Nepal Border 25 km Red Zone (Maharajganj / Sonauli Sector)", "lat": 27.4500, "lon": 83.5000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border corridor along Sonauli / Bhairahawa integrated check post."},
    {"id": "DS-BORDER-BIHAR-VALMIKI", "name": "Bihar Nepal Border 25 km Red Zone (West Champaran / Valmiki Nagar)", "lat": 27.4000, "lon": 83.9500, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer along Gandak Barrage and Nepal frontier."},
    {"id": "DS-BORDER-BIHAR-RAXAUL", "name": "Bihar Nepal Border 25 km Red Zone (East Champaran / Raxaul Sector)", "lat": 26.9800, "lon": 84.8500, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer along major Raxaul / Birgunj gateway."},
    {"id": "DS-BORDER-BIHAR-SITAMARHI", "name": "Bihar Nepal Border 25 km Red Zone (Sitamarhi / Bairgania / Sonbarsa)", "lat": 26.7500, "lon": 85.5000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer across Sitamarhi frontier."},
    {"id": "DS-BORDER-BIHAR-JAYANAGAR", "name": "Bihar Nepal Border 25 km Red Zone (Madhubani / Jayanagar Sector)", "lat": 26.6000, "lon": 86.1500, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer near Janakpur railway corridor."},
    {"id": "DS-BORDER-BIHAR-JOGBANI", "name": "Bihar Nepal Border 25 km Red Zone (Araria / Jogbani / Biratnagar Sector)", "lat": 26.4000, "lon": 87.3000, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer along Jogbani Integrated Check Post."},
    {"id": "DS-BORDER-BIHAR-GALGALIA", "name": "Bihar Nepal Border 25 km Red Zone (Kishanganj / Galgalia Sector)", "lat": 26.3500, "lon": 88.0500, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border corridor along Mechi River."},
    {"id": "DS-BORDER-WB-PANITANKI", "name": "Bengal Nepal Border 25 km Red Zone (Darjeeling / Panitanki / Naxalbari)", "lat": 26.7000, "lon": 88.1500, "radius_km": 25.0, "sector": "NEPAL_IB", "desc": "DGCA 25 km International Border buffer near Kakarbhitta bridge and Siliguri corridor."},

    # --- INDIA - BHUTAN BORDER ---
    {"id": "DS-BORDER-WB-JAIGAON", "name": "Bengal Bhutan Border 25 km Red Zone (Alipurduar / Jaigaon / Phuentsholing)", "lat": 26.8500, "lon": 89.4000, "radius_km": 25.0, "sector": "BHUTAN_IB", "desc": "DGCA 25 km International Border corridor along Jaigaon / Phuentsholing main gateway."},
    {"id": "DS-BORDER-ASSAM-KOKRAJHAR", "name": "Assam Bhutan Border 25 km Red Zone (Kokrajhar / Sarpang Sector)", "lat": 26.8500, "lon": 90.2500, "radius_km": 25.0, "sector": "BHUTAN_IB", "desc": "DGCA 25 km International Border buffer in Western Assam."},
    {"id": "DS-BORDER-ASSAM-GELEPHU", "name": "Assam Bhutan Border 25 km Red Zone (Chirang / Gelephu Sector)", "lat": 26.8800, "lon": 90.5500, "radius_km": 25.0, "sector": "BHUTAN_IB", "desc": "DGCA 25 km International Border buffer near Gelephu border check post."},
    {"id": "DS-BORDER-ASSAM-DARRANGA", "name": "Assam Bhutan Border 25 km Red Zone (Baksa / Udalguri / Samdrup Jongkhar)", "lat": 26.8500, "lon": 91.5000, "radius_km": 25.0, "sector": "BHUTAN_IB", "desc": "DGCA 25 km International Border buffer along Darranga / Samdrup gateway."},

    # --- INDIA - CHINA LAC (EASTERN SECTOR) ---
    {"id": "DS-BORDER-SIKKIM-NATHULA", "name": "Sikkim Border 25 km Red Zone (Nathu La / Doklam Sector)", "lat": 27.3800, "lon": 88.8300, "radius_km": 25.0, "sector": "SIKKIM_BORDER", "desc": "DGCA 25 km International Land Border buffer in East/North Sikkim."},
    {"id": "DS-BORDER-SIKKIM-NORTH", "name": "Sikkim Border 25 km Red Zone (Cho Lhamo / Gurudongmar / LAC)", "lat": 27.9500, "lon": 88.6500, "radius_km": 25.0, "sector": "SIKKIM_BORDER", "desc": "DGCA 25 km high-altitude Line of Actual Control frontier in North Sikkim."},
    {"id": "DS-BORDER-AP-TAWANG", "name": "Arunachal LAC 25 km Red Zone (Tawang / Bum La Sector)", "lat": 27.6000, "lon": 91.8700, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km Line of Actual Control frontier in Western Arunachal Pradesh."},
    {"id": "DS-BORDER-AP-MECHUKA", "name": "Arunachal LAC 25 km Red Zone (Shi Yomi / Mechuka Sector)", "lat": 28.3500, "lon": 94.2000, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km McMahon Line defense frontier in central Arunachal."},
    {"id": "DS-BORDER-AP-TUTING", "name": "Arunachal LAC 25 km Red Zone (Upper Siang / Tuting / Gelling)", "lat": 28.9500, "lon": 95.0000, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km LAC corridor where Yarlung Tsangpo enters India as Siang/Brahmaputra."},
    {"id": "DS-BORDER-AP-ANINI", "name": "Arunachal LAC 25 km Red Zone (Dibang Valley / Anini Sector)", "lat": 28.8500, "lon": 95.8000, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km high-altitude Line of Actual Control security zone."},
    {"id": "DS-BORDER-AP-WALONG", "name": "Arunachal LAC 25 km Red Zone (Walong / Kibithu Eastern Sector)", "lat": 28.2500, "lon": 97.0500, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km easternmost LAC border corridor and historic battleground."},

    # --- INDIA - BANGLADESH BORDER ---
    {"id": "DS-BORDER-WB-SUNDARBANS", "name": "Bengal Border 25 km Red Zone (Sundarbans / Harinbhanga Sector)", "lat": 21.8000, "lon": 89.0500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Maritime & Estuarine Border corridor."},
    {"id": "DS-BORDER-WB-PETRAPOLE", "name": "West Bengal Border 25 km Red Zone (Petrapole / Benapole Sector)", "lat": 23.0500, "lon": 88.8800, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Land Border corridor across South Bengal frontier."},
    {"id": "DS-BORDER-WB-GEDE", "name": "West Bengal Border 25 km Red Zone (Nadia / Gede / Darshana Sector)", "lat": 23.4000, "lon": 88.6500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border buffer near Maitree Express railway crossing."},
    {"id": "DS-BORDER-WB-MURSHIDABAD", "name": "West Bengal Border 25 km Red Zone (Murshidabad / Lalgola / Padma Sector)", "lat": 24.4500, "lon": 88.3500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border corridor along Padma River."},
    {"id": "DS-BORDER-WB-MALDA", "name": "West Bengal Border 25 km Red Zone (Malda / Mahadipur Sector)", "lat": 25.1000, "lon": 88.2500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border buffer near Mahadipur Land Port."},
    {"id": "DS-BORDER-WB-HILI", "name": "West Bengal Border 25 km Red Zone (Dakshin Dinajpur / Hili Sector)", "lat": 25.2800, "lon": 88.9800, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border security zone along historic Hili frontier."},
    {"id": "DS-BORDER-WB-CHANGRABANDHA", "name": "West Bengal Border 25 km Red Zone (Cooch Behar / Changrabandha / Teen Bigha)", "lat": 26.3500, "lon": 88.9000, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border corridor along Teen Bigha corridor."},
    {"id": "DS-BORDER-ASSAM-DHUBRI", "name": "Assam Border 25 km Red Zone (Dhubri / Golakganj / Brahmaputra)", "lat": 26.0000, "lon": 89.9500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border buffer along Western Assam riverine frontier."},
    {"id": "DS-BORDER-MEGHALAYA-GARO", "name": "Meghalaya Border 25 km Red Zone (Garo Hills / Mahendraganj / Dalu)", "lat": 25.2500, "lon": 90.2500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border security envelope in West/South Garo Hills."},
    {"id": "DS-BORDER-MEGHALAYA-DAWKI", "name": "Meghalaya Border 25 km Red Zone (East Khasi Hills / Dawki / Tamabil)", "lat": 25.1800, "lon": 92.0500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border corridor along Umngot river and Tamabil ICP."},
    {"id": "DS-BORDER-ASSAM-KARIMGANJ", "name": "Assam Border 25 km Red Zone (Barak Valley / Karimganj / Sutarkandi)", "lat": 24.8500, "lon": 92.3500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border buffer along Kushiara river frontier."},
    {"id": "DS-BORDER-TRIPURA-AGARTALA", "name": "Tripura Border 25 km Red Zone (Agartala / Akhaura Integrated Check Post)", "lat": 23.8500, "lon": 91.2700, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border security envelope surrounding state capital Agartala."},
    {"id": "DS-BORDER-TRIPURA-BELONIA", "name": "Tripura Border 25 km Red Zone (South Tripura / Belonia / Sabroom)", "lat": 23.1500, "lon": 91.5500, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border buffer near Feni river and Maitri Setu."},
    {"id": "DS-BORDER-MIZORAM-TLABUNG", "name": "Mizoram Border 25 km Red Zone (Lunglei / Tlabung / Demagiri Sector)", "lat": 22.9000, "lon": 92.5000, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Border corridor along Western Mizoram frontier."},

    # --- INDIA - MYANMAR BORDER ---
    {"id": "DS-BORDER-AP-PANGSAU", "name": "Arunachal Border 25 km Red Zone (Changlang / Pangsau Pass / Stillwell)", "lat": 27.2500, "lon": 96.1500, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km International Border security corridor near Patkai range."},
    {"id": "DS-BORDER-NAGALAND-MON", "name": "Nagaland Border 25 km Red Zone (Mon / Longwa Border Village)", "lat": 26.5000, "lon": 95.1000, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km International Border buffer across Longwa and Konyak frontier."},
    {"id": "DS-BORDER-NAGALAND-SARAMATI", "name": "Nagaland Border 25 km Red Zone (Kiphire / Phek / Mount Saramati)", "lat": 25.7500, "lon": 94.8500, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km high-altitude international border corridor."},
    {"id": "DS-BORDER-MANIPUR-MOREH", "name": "Manipur Border 25 km Red Zone (Moreh / Indo-Myanmar ICP Sector)", "lat": 24.2500, "lon": 94.3000, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km International Land Border buffer along Indo-Myanmar Asian Highway frontier."},
    {"id": "DS-BORDER-MANIPUR-BEHIANG", "name": "Manipur Border 25 km Red Zone (Churachandpur / Behiang Sector)", "lat": 23.9000, "lon": 93.9000, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km International Border buffer in Southern Manipur."},
    {"id": "DS-BORDER-MIZORAM-ZOKHAWTHAR", "name": "Mizoram Border 25 km Red Zone (Champhai / Zokhawthar / Tiau Sector)", "lat": 23.3500, "lon": 93.3500, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km International Border trade corridor along Tiau river."},
    {"id": "DS-BORDER-MIZORAM-SAIHA", "name": "Mizoram Border 25 km Red Zone (Saiha / Lawngtlai / Parva Tri-Junction)", "lat": 22.2000, "lon": 92.9500, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km southern international border buffer near Bangladesh-Myanmar-India tri-point."}
]

# ==============================================================================
# 4. MILITARY DEFENSE BASES, AIR FORCE STATIONS & NAVAL HUBS
# ==============================================================================
MILITARY_DEFENSE_RED_ZONES = [
    {"id": "DS-DEFENSE-CHITRADURGA-DRDO-ATR", "name": "Chitradurga DRDO Aeronautical Test Range (ATR Challakere)", "lat": 14.2800, "lon": 76.5800, "radius_km": 18.0, "state": "Karnataka", "desc": "DRDO premier unmanned aerial vehicles (UAV) and stealth combat drone test range."},

    {"id": "DS-MIL-IAF-AMBALA", "name": "Ambala Air Force Station (Rafale Fighter Base)", "city": "Ambala", "state": "Haryana", "lat": 30.3686, "lon": 76.8172, "radius_km": 6.5, "service": "IAF", "desc": "No. 17 Golden Arrows Rafale Squadron Air Base. High-Security Military Airspace."},
    {"id": "DS-MIL-IAF-HALWARA", "name": "Halwara Air Force Station (Ludhiana AFS - Su-30MKI)", "city": "Halwara", "state": "Punjab", "lat": 30.7494, "lon": 75.6339, "radius_km": 6.0, "service": "IAF", "desc": "Frontline IAF Sukhoi Su-30MKI Fighter Station."},
    {"id": "DS-MIL-IAF-PATHANKOT", "name": "Pathankot Air Force Station (MiG-21 / Apache Wing)", "city": "Pathankot", "state": "Punjab", "lat": 32.2336, "lon": 75.6341, "radius_km": 6.0, "service": "IAF", "desc": "IAF Forward Fighter Air Base & Attack Helicopter Wing."},
    {"id": "DS-MIL-IAF-ADAMPUR", "name": "Adampur Air Force Station (Jalandhar - MiG-29 Base)", "city": "Jalandhar", "state": "Punjab", "lat": 31.4338, "lon": 75.7583, "radius_km": 6.0, "service": "IAF", "desc": "No. 47 & No. 8 Squadron MiG-29 UPG Fighter Base."},
    {"id": "DS-MIL-IAF-HINDON", "name": "Hindon Air Force Station (Strategic Airlift C-17 / C-130J)", "city": "Ghaziabad", "state": "Uttar Pradesh", "lat": 28.7078, "lon": 77.3592, "radius_km": 6.5, "service": "IAF", "desc": "Asia's largest air base, home to C-17 Globemaster & C-130J."},
    {"id": "DS-MIL-IAF-JODHPUR", "name": "Jodhpur Air Force Station (SWAC)", "city": "Jodhpur", "state": "Rajasthan", "lat": 26.2511, "lon": 73.0489, "radius_km": 6.0, "service": "IAF", "desc": "Major IAF Su-30MKI Fighter Base and Air Defense Center."},
    {"id": "DS-MIL-IAF-UTTARLAI", "name": "Uttarlai Air Force Station (Barmer Forward Base)", "city": "Barmer", "state": "Rajasthan", "lat": 25.8117, "lon": 71.4883, "radius_km": 6.0, "service": "IAF", "desc": "Strategic frontline forward operational base near Rajasthan border."},
    {"id": "DS-MIL-IAF-JAMNAGAR", "name": "Jamnagar Air Force Station (Jaguar Maritime Strike Base)", "city": "Jamnagar", "state": "Gujarat", "lat": 22.4647, "lon": 70.0125, "radius_km": 6.0, "service": "IAF", "desc": "IAF Tactical Air Command & Jaguar Maritime Strike Fighter Base."},
    {"id": "DS-MIL-IAF-BHUJ", "name": "Bhuj Air Force Station (Kutch Border Forward Base)", "city": "Bhuj", "state": "Gujarat", "lat": 23.2878, "lon": 69.6700, "radius_km": 5.5, "service": "IAF", "desc": "IAF Forward Fighter Base defending Gujarat border and Gulf of Kutch."},
    {"id": "DS-MIL-IAF-GWALIOR", "name": "Maharajpur Air Force Station (Gwalior - Mirage 2000)", "city": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2933, "lon": 78.2278, "radius_km": 6.0, "service": "IAF", "desc": "Home to IAF Mirage 2000 multi-role fighter fleet & TACDE."},
    {"id": "DS-MIL-IAF-BAREILLY", "name": "Bareilly Air Force Station (Trishul Air Base - Su-30MKI)", "city": "Bareilly", "state": "Uttar Pradesh", "lat": 28.4222, "lon": 79.4503, "radius_km": 6.0, "service": "IAF", "desc": "Central Air Command frontline Su-30MKI Air Base."},
    {"id": "DS-MIL-IAF-TEZPUR", "name": "Tezpur Air Force Station (Su-30MKI Eastern Frontier)", "city": "Tezpur", "state": "Assam", "lat": 26.7094, "lon": 92.7842, "radius_km": 6.0, "service": "IAF", "desc": "Eastern Air Command primary air defense base covering LAC."},
    {"id": "DS-MIL-IAF-HASIMARA", "name": "Hasimara Air Force Station (Rafale - Siliguri Corridor)", "city": "Alipurduar", "state": "West Bengal", "lat": 26.7039, "lon": 89.3694, "radius_km": 6.0, "service": "IAF", "desc": "No. 101 Squadron Rafale Base guarding Siliguri Chicken's Neck."},
    {"id": "DS-MIL-IAF-PUNE", "name": "Lohegaon Air Force Station (Pune - Su-30MKI)", "city": "Pune", "state": "Maharashtra", "lat": 18.5822, "lon": 73.9197, "radius_km": 5.5, "service": "IAF", "desc": "No. 20 Squadron Lightnings Su-30MKI base."},
    {"id": "DS-MIL-IAF-SULUR", "name": "Sulur Air Force Station (Coimbatore - LCA Tejas)", "city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0142, "lon": 77.1611, "radius_km": 5.5, "service": "IAF", "desc": "No. 45 Squadron Flying Daggers & No. 18 Squadron Tejas LCA."},
    {"id": "DS-MIL-IAF-SRINAGAR", "name": "Srinagar Air Force Station & Awantipora AFS", "city": "Srinagar", "state": "Jammu & Kashmir", "lat": 33.8767, "lon": 74.9686, "radius_km": 7.0, "service": "IAF", "desc": "Critical northern air defense fighter base."},
    {"id": "DS-MIL-IAF-LEH", "name": "Leh Kushok Bakula AFS & Thoise Air Base", "city": "Leh", "state": "Ladakh", "lat": 34.1359, "lon": 77.5465, "radius_km": 6.5, "service": "IAF", "desc": "Highest military operational air base in Ladakh theater."},
    {"id": "DS-MIL-NAVY-HANSA", "name": "INS Hansa (Goa - MiG-29K Carrier Air Wing)", "city": "Dabolim", "state": "Goa", "lat": 15.3808, "lon": 73.8314, "radius_km": 5.5, "service": "NAVY", "desc": "Naval air station & INS Vikramaditya / Vikrant fighter base."},
    {"id": "DS-MIL-NAVY-KADAMBA", "name": "INS Kadamba / Project Seabird (Karwar Naval Base)", "city": "Karwar", "state": "Karnataka", "lat": 14.7700, "lon": 74.1500, "radius_km": 6.5, "service": "NAVY", "desc": "Deep-water naval base, aircraft carrier homeport & missile base."},
    {"id": "DS-MIL-NAVY-DEGA", "name": "INS Dega / Eastern Naval Command HQ", "city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.7214, "lon": 83.2244, "radius_km": 6.0, "service": "NAVY", "desc": "Eastern Naval Command Headquarters & submarine airbase."},
    {"id": "DS-MIL-NAVY-RAJALI", "name": "INS Rajali (Arakkonam - P-8I Neptune Maritime Recon)", "city": "Arakkonam", "state": "Tamil Nadu", "lat": 13.0717, "lon": 79.6914, "radius_km": 5.5, "service": "NAVY", "desc": "Longest military runway in Asia; Boeing P-8I Maritime Patrol."},
    {"id": "DS-MIL-NAVY-GARUDA", "name": "INS Garuda / Southern Naval Command", "city": "Kochi", "state": "Kerala", "lat": 9.9400, "lon": 76.2750, "radius_km": 5.0, "service": "NAVY", "desc": "Southern Naval Command Naval Air Station."},
    {"id": "DS-MIL-NAVY-SHIKRA", "name": "INS Shikra (Colaba Naval Base)", "city": "Mumbai", "state": "Maharashtra", "lat": 18.9050, "lon": 72.8150, "radius_km": 4.5, "service": "NAVY", "desc": "Western Naval Command helicopter airbase & strategic fleet station."},
    {"id": "DS-MIL-ARMY-POKHRAN", "name": "Pokhran Field Firing Range (Nuclear & Artillery Range)", "city": "Pokhran", "state": "Rajasthan", "lat": 27.0500, "lon": 71.7500, "radius_km": 12.0, "service": "ARMY", "desc": "India's premier strategic nuclear & live-fire artillery complex."},
    {"id": "DS-MIL-ARMY-BABINA", "name": "Babina Field Firing Range (Armoured Corps Heavy Range)", "city": "Babina", "state": "Uttar Pradesh", "lat": 25.2500, "lon": 78.4500, "radius_km": 8.0, "service": "ARMY", "desc": "Main Battle Tank Arjun/T-90 mechanized combat firing range."},
    {"id": "DS-MIL-ARMY-UDHAMPUR", "name": "HQ Northern Command (Udhampur Military Cantonment)", "city": "Udhampur", "state": "Jammu & Kashmir", "lat": 32.9261, "lon": 75.1419, "radius_km": 5.5, "service": "ARMY", "desc": "Headquarters of the Indian Army Northern Command."},
    {"id": "DS-MIL-ARMY-CHANDIMANDIR", "name": "HQ Western Command (Chandimandir Cantonment)", "city": "Panchkula", "state": "Haryana", "lat": 30.7200, "lon": 76.8800, "radius_km": 5.0, "service": "ARMY", "desc": "Headquarters of the Indian Army Western Command."},
    {"id": "DS-MIL-ARMY-GOPALPUR", "name": "Army Air Defence College & Gopalpur Seaward Range", "city": "Gopalpur", "state": "Odisha", "lat": 19.2600, "lon": 84.9100, "radius_km": 7.0, "service": "ARMY", "desc": "Surface-to-air missile testing & live Air Defence artillery range."},
    {"id": "DS-MIL-DRDO-CHANDIPUR", "name": "Integrated Test Range (ITR Chandipur & APJ Abdul Kalam Island)", "city": "Balasore", "state": "Odisha", "lat": 21.4600, "lon": 87.0200, "radius_km": 10.0, "service": "DRDO", "desc": "Strategic missile launch & testing facility (Agni, Prithvi, BrahMos)."},
    {"id": "DS-MIL-ISRO-SHAR", "name": "Satish Dhawan Space Centre (SDSC SHAR Sriharikota)", "city": "Sriharikota", "state": "Andhra Pradesh", "lat": 13.7199, "lon": 80.2304, "radius_km": 9.0, "service": "ISRO", "desc": "ISRO Space Launch Complex & Rocket Launch Pads."},
    {"id": "DS-MIL-ISRO-VSSC", "name": "Vikram Sarabhai Space Centre (VSSC Thumba)", "city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5300, "lon": 76.8700, "radius_km": 5.0, "service": "ISRO", "desc": "Launch vehicle design, solid motor research & rocket development."}
]

# ==============================================================================
# 5. ORDNANCE FACTORIES & DEFENSE PRODUCTION UNITS
# ==============================================================================
ORDNANCE_DEFENSE_FACTORIES = [
    {"id": "DS-FACT-OF-AVADI", "name": "Heavy Vehicles Factory (HVF Avadi - Tank Production)", "city": "Chennai", "state": "Tamil Nadu", "lat": 13.1250, "lon": 80.1000, "radius_km": 4.5, "desc": "Manufactures Main Battle Tanks (Arjun Mk-1A, T-90 Bhishma). Defense Production Red Zone."},
    {"id": "DS-FACT-OF-KHAMARIA", "name": "Ordnance Factory Khamaria (Ammunition & Explosives)", "city": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1800, "lon": 80.0200, "radius_km": 4.5, "desc": "India's premier heavy ammunition, aerial bombs & artillery shells manufacturing plant."},
    {"id": "DS-FACT-OF-MEDAK", "name": "Ordnance Factory Medak (Armoured Vehicles)", "city": "Yeddumailaram", "state": "Telangana", "lat": 17.5500, "lon": 78.1300, "radius_km": 4.0, "desc": "Infantry Combat Vehicles BMP-2 Sarath & armored defense systems production."},
    {"id": "DS-FACT-OF-ISHAPORE", "name": "Rifle Factory Ishapore (Small Arms & Weapons)", "city": "Ishapore", "state": "West Bengal", "lat": 22.7800, "lon": 88.3700, "radius_km": 4.0, "desc": "Historic defense small arms, assault rifles & sniper systems facility."},
    {"id": "DS-FACT-OF-ARUVANKADU", "name": "Cordite Factory Aruvankadu (Propellants & High Explosives)", "city": "Nilgiris", "state": "Tamil Nadu", "lat": 11.3650, "lon": 76.7750, "radius_km": 4.0, "desc": "Manufactures military propellants and cordite nitrocellulose explosives."},
    {"id": "DS-FACT-OF-MURADNAGAR", "name": "Ordnance Factory Muradnagar (Defense Metallurgy & Castings)", "city": "Ghaziabad", "state": "Uttar Pradesh", "lat": 28.7800, "lon": 77.5000, "radius_km": 4.0, "desc": "Special steel alloy castings for tanks, armored vehicles and bombs."},
    {"id": "DS-FACT-HAL-NASHIK", "name": "HAL Aircraft Manufacturing Division (Ozar Nashik)", "city": "Nashik", "state": "Maharashtra", "lat": 20.1200, "lon": 73.9100, "radius_km": 5.0, "desc": "Assembly, overhaul & manufacturing of Su-30MKI fighter aircraft and electronics."},
    {"id": "DS-FACT-BEL-BENGALURU", "name": "Bharat Electronics Limited (BEL Strategic Defense Electronics)", "city": "Bengaluru", "state": "Karnataka", "lat": 13.0600, "lon": 77.5500, "radius_km": 4.0, "desc": "Radars, electronic warfare systems & tactical communication hardware."},
    {"id": "DS-FACT-BDL-BHANUR", "name": "Bharat Dynamics Limited (BDL Missile Production Complex)", "city": "Bhanur / Hyderabad", "state": "Telangana", "lat": 17.5200, "lon": 78.1800, "radius_km": 4.5, "desc": "Guided missile production facility for Akash, Milan & anti-tank weapon systems."},
    {"id": "DS-FACT-MDL-MUMBAI", "name": "Mazagon Dock Shipbuilders (Submarine & Warship Yard)", "city": "Mumbai", "state": "Maharashtra", "lat": 18.9650, "lon": 72.8450, "radius_km": 4.0, "desc": "Construction of Scorpene Kalvari class submarines & frontline stealth destroyers."}
]

# ==============================================================================
# 6. HAZARDOUS PETROCHEMICAL REFINERIES & INDUSTRIAL MEGA-FACTORIES
# ==============================================================================
STRATEGIC_PETROCHEM_FACTORIES = [
    {"id": "DS-IND-JAMNAGAR-REF", "name": "Jamnagar Energy Mega-Complex & Reliance Refinery", "city": "Jamnagar", "state": "Gujarat", "lat": 22.4707, "lon": 70.0667, "radius_km": 6.5, "desc": "World's largest petroleum refinery cluster (1.24M bpd capacity). Critical Energy Infrastructure."},
    {"id": "DS-IND-PANIPAT-REF", "name": "IOCL Panipat Petrochemical Refinery Mega-Plant", "city": "Panipat", "state": "Haryana", "lat": 29.4300, "lon": 76.8800, "radius_km": 5.0, "desc": "Major northern petroleum refinery, naphtha cracker and polymer complex."},
    {"id": "DS-IND-BARAUNI-REF", "name": "Barauni Petroleum Refinery Complex", "city": "Begusarai", "state": "Bihar", "lat": 25.4600, "lon": 85.9800, "radius_km": 4.5, "desc": "Strategic refinery supplying fuel to eastern India and international pipeline."},
    {"id": "DS-IND-MATHURA-REF", "name": "Mathura Oil Refinery Complex", "city": "Mathura", "state": "Uttar Pradesh", "lat": 27.4200, "lon": 77.6800, "radius_km": 4.5, "desc": "IOCL strategic refinery in Taj Trapezium environmental and safety zone."},
    {"id": "DS-IND-PARADIP-REF", "name": "IOCL Paradip Coastal Mega-Refinery", "city": "Paradip", "state": "Odisha", "lat": 20.3000, "lon": 86.6000, "radius_km": 5.0, "desc": "Eastern sea-board coastal crude processing and polymer manufacturing facility."},
    {"id": "DS-IND-HAZIRA-PETRO", "name": "Hazira Petrochemicals, LNG & Steel Mega-Hub", "city": "Surat", "state": "Gujarat", "lat": 21.1200, "lon": 72.6400, "radius_km": 5.5, "desc": "Heavy LNG regasification terminal, chemical synthesis & steel manufacturing hub."},
    {"id": "DS-IND-VIZAG-HPCL", "name": "HPCL Visakhapatnam Coastal Refinery", "city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6900, "lon": 83.2500, "radius_km": 4.5, "desc": "Deepwater oil processing and petrochemical distillation hub."},
    {"id": "DS-IND-KOCHI-BPCL", "name": "BPCL Kochi Refinery & Petrochemical Park", "city": "Ambalamugal", "state": "Kerala", "lat": 9.9800, "lon": 76.3800, "radius_km": 4.5, "desc": "South India's premier crude refining and specialty chemicals complex."}
]

# ==============================================================================
# 7. STRATEGIC MEGA-DAMS, RESERVOIRS & SENSITIVE WATER BODIES
# ==============================================================================
MAJOR_DAMS_WATER_BODIES = [
    {"id": "DS-WATER-TEHRI-DAM", "name": "Tehri Hydroelectric Mega-Dam & Reservoir", "city": "Tehri Garhwal", "state": "Uttarakhand", "lat": 30.3780, "lon": 78.4800, "radius_km": 5.5, "desc": "India's highest dam (260.5m) and primary Himalayan water reservoir. Critical hydrological security."},
    {"id": "DS-WATER-BHAKRA-DAM", "name": "Bhakra Nangal Dam & Gobind Sagar Reservoir", "city": "Bilaspur / Nangal", "state": "Himachal Pradesh", "lat": 31.4100, "lon": 76.4350, "radius_km": 5.5, "desc": "Lifeline reservoir for Punjab, Haryana, Rajasthan. High-security concrete gravity dam."},
    {"id": "DS-WATER-SARDAR-SAROVAR", "name": "Sardar Sarovar Mega-Dam & Narmada Basin", "city": "Kevadia", "state": "Gujarat", "lat": 21.8300, "lon": 73.7500, "radius_km": 5.5, "desc": "Major gravity dam on Narmada River powering Gujarat, MP, and Maharashtra."},
    {"id": "DS-WATER-HIRAKUD-DAM", "name": "Hirakud Dam & Reservoir (Mahanadi River)", "city": "Sambalpur", "state": "Odisha", "lat": 21.5200, "lon": 83.8700, "radius_km": 6.0, "desc": "One of the longest earthen dams in the world. Vital flood control & hydroelectric asset."},
    {"id": "DS-WATER-IDUKKI-DAM", "name": "Idukki Arch Dam & Hydroelectric Reservoir", "city": "Idukki", "state": "Kerala", "lat": 9.8500, "lon": 76.9700, "radius_km": 5.0, "desc": "Double curvature arch dam constructed between Kuravan and Kurathi hills."},
    {"id": "DS-WATER-NAGARJUNA", "name": "Nagarjuna Sagar Dam & Krishna River Reservoir", "city": "Nalgonda / Guntur", "state": "Telangana / AP", "lat": 16.5700, "lon": 79.3100, "radius_km": 5.0, "desc": "World's largest masonry dam with 26 crest gates and major hydroelectric station."},
    {"id": "DS-WATER-KOYNA-DAM", "name": "Koyna Hydroelectric Dam Complex", "city": "Koynanagar", "state": "Maharashtra", "lat": 17.4000, "lon": 73.7500, "radius_km": 5.0, "desc": "Largest completed hydroelectric plant in India with underground powerhouse."},
    {"id": "DS-WATER-SUNDARBANS", "name": "Sundarbans Estuary & Coastal Delta Biosphere", "city": "South 24 Parganas", "state": "West Bengal", "lat": 21.9500, "lon": 88.8500, "radius_km": 15.0, "desc": "Sensitive international mangrove wetland, marine sanctuary & international water border."},
    {"id": "DS-WATER-CHILIKA-LAKE", "name": "Chilika Lake Coastal Lagoon & INS Chilka Naval Area", "city": "Puri / Ganjam", "state": "Odisha", "lat": 19.7000, "lon": 85.3500, "radius_km": 10.0, "desc": "Asia's largest brackish lagoon, sailor training base INS Chilka & sensitive marine habitat."},
    {"id": "DS-WATER-GULF-MANNAR", "name": "Gulf of Mannar Marine Biosphere & International Straits", "city": "Rameshwaram", "state": "Tamil Nadu", "lat": 9.2800, "lon": 79.3000, "radius_km": 12.0, "desc": "Maritime international boundary strait with Sri Lanka & coastal biodiversity sanctuary."}
]

# ==============================================================================
# 8. STRATEGIC NUCLEAR POWER & RESEARCH RED ZONES
# ==============================================================================
STRATEGIC_NUCLEAR_RED_ZONES = [
    {"id": "DS-RED-MUM-BARC", "name": "Bhabha Atomic Research Centre (BARC Trombay)", "city": "Mumbai", "state": "Maharashtra", "lat": 19.0067, "lon": 72.9192, "radius_km": 5.0, "category": "NUCLEAR_RESEARCH", "desc": "BARC Trombay Nuclear Complex & reactor containment. Strictly Prohibited."},
    {"id": "DS-RED-TN-KALPAKKAM", "name": "Madras Atomic Power Station (MAPS Kalpakkam / IGCAR)", "city": "Kalpakkam", "state": "Tamil Nadu", "lat": 12.5574, "lon": 80.1743, "radius_km": 5.5, "category": "NUCLEAR_POWER", "desc": "Kalpakkam Nuclear & Fast Breeder Reactor Research Centre."},
    {"id": "DS-RED-UP-NARORA", "name": "Narora Atomic Power Station (NAPS)", "city": "Narora", "state": "Uttar Pradesh", "lat": 28.1578, "lon": 78.4069, "radius_km": 5.0, "category": "NUCLEAR_POWER", "desc": "NPCIL heavy water nuclear power generation station."},
    {"id": "DS-RED-TN-KUDANKULAM", "name": "Kudankulam Nuclear Power Plant (KKNPP)", "city": "Kudankulam", "state": "Tamil Nadu", "lat": 8.1691, "lon": 77.7126, "radius_km": 5.5, "category": "NUCLEAR_POWER", "desc": "India's highest capacity VVER nuclear power station."},
    {"id": "DS-RED-KA-KAIGA", "name": "Kaiga Atomic Power Station (KGS)", "city": "Kaiga", "state": "Karnataka", "lat": 14.8650, "lon": 74.4370, "radius_km": 5.0, "category": "NUCLEAR_POWER", "desc": "Western Ghats nuclear generation complex."},
    {"id": "DS-RED-RJ-RAWATBHATA", "name": "Rajasthan Atomic Power Station (RAPS Rawatbhata)", "city": "Rawatbhata", "state": "Rajasthan", "lat": 24.8720, "lon": 75.5990, "radius_km": 5.0, "category": "NUCLEAR_POWER", "desc": "Chambal river atomic power generating station."},
    {"id": "DS-RED-GJ-KAKRAPAR", "name": "Kakrapar Atomic Power Station (KAPS)", "city": "Vyara", "state": "Gujarat", "lat": 21.2380, "lon": 73.3500, "radius_km": 5.0, "category": "NUCLEAR_POWER", "desc": "Pressurized Heavy Water Reactor complex in South Gujarat."}
]

# ==============================================================================
# 9. TEMPORARY RED ZONES (TFR - TEMPORARY FLIGHT RESTRICTIONS)
# ==============================================================================
TEMPORARY_RED_ZONES = [
    {"id": "DS-TFR-DEL-CENTRAL-VISTA", "name": "Central Vista VIP Security Zone (Parliament, Rashtrapati Bhavan, PM Residence)", "city": "New Delhi", "state": "Delhi", "lat": 28.6143, "lon": 77.2008, "radius_km": 4.5, "category": "TFR_VIP_SECURITY", "validity": "PERMANENT_RESTRICTED (NOTAM A-01)", "desc": "Kartavya Path, Rashtrapati Bhavan, PM Residence & Parliament House. Zero tolerance drone ban."},
    {"id": "DS-TFR-DEL-REDFORT", "name": "Red Fort National Independence Security Envelope (TFR)", "city": "Old Delhi", "state": "Delhi", "lat": 28.6562, "lon": 77.2410, "radius_km": 3.0, "category": "TFR_NATIONAL_HERITAGE", "validity": "HIGH_SECURITY_TFR", "desc": "Red Fort VIP ramparts, Chandni Chowk & National Independence Day security zone."},
    {"id": "DS-TFR-PB-WAGAH", "name": "Attari-Wagah Border Retreat Arena (TFR Security Zone)", "city": "Attari", "state": "Punjab", "lat": 31.6047, "lon": 74.5714, "radius_km": 3.5, "category": "TFR_BORDER_CEREMONY", "validity": "DAILY_ACTIVE_TFR", "desc": "International joint retreat flag ceremony amphitheatre. BSF High-Alert Airspace."},
    {"id": "DS-TFR-UP-AYODHYA", "name": "Ayodhya Shri Ram Janmabhoomi High-Security Complex (TFR)", "city": "Ayodhya", "state": "Uttar Pradesh", "lat": 26.7950, "lon": 82.1940, "radius_km": 4.0, "category": "TFR_SPECIAL_SECURITY", "validity": "ACTIVE_TFR", "desc": "Special Security Force (SSF) & NSG designated anti-drone protective red zone."},
    {"id": "DS-TFR-GJ-KEVADIA", "name": "Statue of Unity National Security Envelope (TFR)", "city": "Kevadia", "state": "Gujarat", "lat": 21.8380, "lon": 73.7190, "radius_km": 4.0, "category": "TFR_NATIONAL_MONUMENT", "validity": "ACTIVE_TFR", "desc": "National security VIP perimeter surrounding Sardar Patel memorial and Narmada reservoir."},
    {"id": "DS-TFR-UP-KASHI", "name": "Kashi Vishwanath Corridor & Ganga Ghats Security Envelope", "city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3100, "lon": 83.0100, "radius_km": 3.5, "category": "TFR_HERITAGE_SECURITY", "validity": "ACTIVE_TFR", "desc": "Ganga Aarti Ghats, Kashi Vishwanath temple corridor and riverfront high-security zone."}
]

# Pan-India boundary
INDIA_AIRSPACE_BOUNDARY = [
    [74.8, 37.1], [77.8, 35.5], [80.3, 31.1], [88.2, 27.5], [97.4, 28.3],
    [96.1, 26.3], [93.1, 23.7], [91.8, 22.3], [89.0, 21.6], [86.9, 20.8],
    [82.8, 16.9], [80.3, 13.1], [79.9, 9.3], [77.5, 8.1], [75.8, 11.9],
    [73.8, 15.4], [72.8, 19.1], [68.2, 23.7], [70.5, 27.2], [74.2, 32.5],
    [74.8, 37.1]
]


def build_digitalsky_geojson() -> Dict[str, Any]:
    features = []

    # 1. GREEN ZONE
    mainland_coords = _INDIA_BOUNDARY_DATA["mainland"] if (_INDIA_BOUNDARY_DATA and "mainland" in _INDIA_BOUNDARY_DATA) else INDIA_AIRSPACE_BOUNDARY
    features.append({
        "type": "Feature",
        "id": "DS-GREEN-PAN-INDIA",
        "properties": {
            "id": "DS-GREEN-PAN-INDIA",
            "name": "Pan-India Airspace (Green Zone)",
            "zone_type": "GREEN",
            "layer_group": "green_zone",
            "category": "Open Airspace",
            "max_altitude_agl_ft": 400,
            "max_altitude_agl_m": 120,
            "permission_required": "NONE (Up to 400 ft AGL)",
            "authority": "DGCA — No prior flight approval needed",
            "rule_ref": "Drone Rules 2021, Rule 22(1)",
            "description": "Standard green airspace zone covering sovereign Indian territory outside designated red and yellow zones. Autonomous & manual flights up to 400 ft AGL freely permitted.",
            "color": "#059669",
            "fillColor": "#10b981",
            "fillOpacity": 0.12,
            "strokeWeight": 1.5,
            "zIndex": 100
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [mainland_coords]
        }
    })

    # Island chains (Andaman & Nicobar, Lakshadweep, Sagar Island)
    if _INDIA_BOUNDARY_DATA and "islands" in _INDIA_BOUNDARY_DATA:
        for idx, island_ring in enumerate(_INDIA_BOUNDARY_DATA["islands"]):
            features.append({
                "type": "Feature",
                "id": f"DS-GREEN-ISLAND-{idx}",
                "properties": {
                    "id": f"DS-GREEN-ISLAND-{idx}",
                    "name": "Indian Island Territory Airspace (Green Zone)",
                    "zone_type": "GREEN",
                    "layer_group": "green_zone",
                    "category": "Open Airspace",
                    "max_altitude_agl_ft": 400,
                    "max_altitude_agl_m": 120,
                    "permission_required": "NONE (Up to 400 ft AGL)",
                    "authority": "DGCA",
                    "rule_ref": "Drone Rules 2021, Rule 22(1)",
                    "color": "#059669",
                    "fillColor": "#10b981",
                    "fillOpacity": 0.12,
                    "strokeWeight": 1.5,
                    "zIndex": 100
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [island_ring]
                }
            })

# Helper for adding Red Zone lists
    def add_red_features(items, category_tag, color, fill_color, opacity, stroke_weight, dash="", layer_group="red_zone"):
        for item in items:
            lat, lon, r = item["lat"], item["lon"], item["radius_km"]
            coords = generate_circle_polygon(lat, lon, r)
            p = {
                "id": item["id"],
                "name": item["name"],
                "zone_type": "RED",
                "category": category_tag,
                "layer_group": layer_group,
                "radius_km": r,
                "max_altitude_agl_ft": 0,
                "max_altitude_agl_m": 0,
                "permission_required": "STRICTLY PROHIBITED (No-Fly Zone)",
                "authority": "Ministry of Civil Aviation & Central Authority",
                "rule_ref": "Drone Rules 2021, Rule 22(3)",
                "description": item.get("desc", ""),
                "color": color,
                "fillColor": fill_color,
                "fillOpacity": opacity,
                "strokeWeight": stroke_weight,
                "zIndex": 1200
            }
            if dash:
                p["strokeDashArray"] = dash
            features.append({
                "type": "Feature",
                "id": item["id"],
                "properties": p,
                "geometry": {"type": "Polygon", "coordinates": [coords]}
            })

    # 2. Strategic Inland & Offshore Defense Polygons (Red Zone)
    for poly_item in STRATEGIC_DEFENSE_POLYGONS:
        features.append({
            "type": "Feature",
            "id": poly_item["id"],
            "properties": {
                "id": poly_item["id"],
                "name": f"🛡️ {poly_item['name']}",
                "zone_type": "RED",
                "layer_group": "red_zone",
                "category": poly_item["category"],
                "radius_km": 20.0,
                "max_altitude_agl_ft": 0,
                "max_altitude_agl_m": 0,
                "permission_required": "STRICTLY PROHIBITED (Strategic Defense / Exclusion Zone)",
                "authority": "MoD / Armed Forces / DGCA India",
                "rule_ref": poly_item["rule_ref"],
                "description": poly_item["desc"],
                "color": "#991b1b",
                "fillColor": "#dc2626",
                "fillOpacity": 0.45,
                "strokeWeight": 2.5,
                "zIndex": 1260
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [poly_item["coordinates"]]
            }
        })

    # 3. Continuous 25 km International Land Border Ribbon Corridors
    for poly_item in INTERNATIONAL_BORDER_POLYGONS:
        features.append({
            "type": "Feature",
            "id": poly_item["id"],
            "properties": {
                "id": poly_item["id"],
                "name": f"🛡️ {poly_item['name']}",
                "zone_type": "RED",
                "layer_group": "boundary_25km",
                "category": poly_item["category"],
                "radius_km": 25.0,
                "max_altitude_agl_ft": 0,
                "max_altitude_agl_m": 0,
                "permission_required": "STRICTLY PROHIBITED (25 km International Land Border Buffer)",
                "authority": "MoD / MHA / DGCA India",
                "rule_ref": poly_item["rule_ref"],
                "description": poly_item["desc"],
                "color": "#dc2626",
                "fillColor": "#ef4444",
                "fillOpacity": 0.45,
                "strokeWeight": 1.8,
                "zIndex": 1250
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [poly_item["coordinates"]]
            }
        })

    # Note: Circular checkpoint overlays along international borders removed per DGCA DigitalSky specifications;
    # continuous 25 km statutory boundary ribbons are used instead. INTERNATIONAL_BORDER_RED_ZONES is retained for backend classification.

    # 5. Military Defense Areas
    add_red_features(MILITARY_DEFENSE_RED_ZONES, "Military Defense Airspace", "#7f1d1d", "#b91c1c", 0.44, 2.2, layer_group="red_zone")

    # 6. Ordnance Factories & Defense Production
    add_red_features(ORDNANCE_DEFENSE_FACTORIES, "Defense Ordnance Factory", "#831843", "#be185d", 0.45, 2.2, layer_group="red_zone")

    # 7. Petrochemical Refineries & Hazardous Factories
    add_red_features(STRATEGIC_PETROCHEM_FACTORIES, "Industrial Petrochemical Refinery", "#9a3412", "#ea580c", 0.42, 2.2, layer_group="red_zone")

    # 8. Major Dams & Sensitive Water Bodies
    add_red_features(MAJOR_DAMS_WATER_BODIES, "Strategic Water Body / Dam", "#1e3a8a", "#2563eb", 0.40, 2.2, layer_group="red_zone")

    # 9. Strategic Nuclear Facilities
    add_red_features(STRATEGIC_NUCLEAR_RED_ZONES, "Strategic Nuclear Installation", "#881337", "#e11d48", 0.48, 2.2, layer_group="red_zone")

    # 10. Temporary Red Zones (TFR)
    add_red_features(TEMPORARY_RED_ZONES, "Temporary Flight Restriction (TFR)", "#4c0519", "#be123c", 0.52, 2.5, "6, 3", layer_group="temporary_red_zone")

    # 11. Aerodrome 3-Tier Official DigitalSky Envelopes
    for aero in INDIAN_AERODROMES:
        lat, lon = aero["lat"], aero["lon"]
        # Tier 0: Aerodrome Center Marker with Plane Icon & Name Label
        features.append({
            "type": "Feature",
            "id": f"DS-AIRPORT-PIN-{aero['id']}",
            "properties": {
                "id": f"DS-AIRPORT-PIN-{aero['id']}",
                "name": f"{aero['name']}",
                "zone_type": "AIRPORT_PIN",
                "layer_group": "airport_red",
                "category": "Aerodrome Facility",
                "aerodrome_id": aero["id"],
                "city": aero["city"],
                "state": aero["state"],
                "lat": lat,
                "lon": lon,
                "color": "#0284c7"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        })
        # Tier 1: Airport Red (0 - 5 km)
        coords_5k = generate_circle_polygon(lat, lon, 5.0)
        f_id_red = f"DS-AIRPORT-RED-{aero['id']}"
        features.append({
            "type": "Feature",
            "id": f_id_red,
            "properties": {
                "id": f_id_red,
                "name": f"✈️ {aero['name']} (Airport Red Zone)",
                "zone_type": "RED",
                "layer_group": "airport_red",
                "category": "Airport Red",
                "aerodrome_id": aero["id"],
                "city": aero["city"],
                "state": aero["state"],
                "radius_km": 5.0,
                "max_altitude_agl_ft": 0,
                "max_altitude_agl_m": 0,
                "permission_required": "STRICTLY PROHIBITED (0-5 km Aerodrome Runway Perimeter)",
                "authority": "AAI & Directorate General of Civil Aviation",
                "rule_ref": "Drone Rules 2021, Rule 22(3)",
                "description": f"Mandatory 5 km runway perimeter around {aero['name']}. Drone flights strictly banned.",
                "color": "#b91c1c",
                "fillColor": "#ef4444",
                "fillOpacity": 0.45,
                "strokeWeight": 2.2,
                "zIndex": 1100
            },
            "geometry": {"type": "Polygon", "coordinates": [coords_5k]}
        })

        # Tier 2: Airport Yellow [5-8]km
        coords_8k = generate_circle_polygon(lat, lon, 8.0)
        f_id_y58 = f"DS-AIRPORT-YEL-5-8-{aero['id']}"
        features.append({
            "type": "Feature",
            "id": f_id_y58,
            "properties": {
                "id": f_id_y58,
                "name": f"✈️ {aero['name']} (Airport Yellow [5-8]km)",
                "zone_type": "YELLOW",
                "layer_group": "airport_yellow_5_8",
                "category": "Airport Yellow [5-8]km",
                "aerodrome_id": aero["id"],
                "city": aero["city"],
                "state": aero["state"],
                "radius_km": 8.0,
                "max_altitude_agl_ft": 200,
                "max_altitude_agl_m": 60,
                "permission_required": "ATC / AAI Clearance required for flights above 200 ft (60 m) AGL",
                "authority": "Airports Authority of India (AAI)",
                "rule_ref": "Drone Rules 2021, Rule 22(2)",
                "description": f"5 to 8 km controlled airspace perimeter around {aero['name']}. Max altitude 200 ft AGL.",
                "color": "#d97706",
                "fillColor": "#f59e0b",
                "fillOpacity": 0.28,
                "strokeWeight": 1.8,
                "strokeDashArray": "4, 4",
                "zIndex": 950
            },
            "geometry": {"type": "Polygon", "coordinates": [coords_8k]}
        })

        # Tier 3: Airport Yellow [8-12]km
        coords_12k = generate_circle_polygon(lat, lon, 12.0)
        f_id_y812 = f"DS-AIRPORT-YEL-8-12-{aero['id']}"
        features.append({
            "type": "Feature",
            "id": f_id_y812,
            "properties": {
                "id": f_id_y812,
                "name": f"✈️ {aero['name']} (Airport Yellow [8-12]km)",
                "zone_type": "YELLOW",
                "layer_group": "airport_yellow_8_12",
                "category": "Airport Yellow [8-12]km",
                "aerodrome_id": aero["id"],
                "city": aero["city"],
                "state": aero["state"],
                "radius_km": 12.0,
                "max_altitude_agl_ft": 400,
                "max_altitude_agl_m": 120,
                "permission_required": "ATC / AAI Clearance required for flights above 400 ft (120 m) AGL",
                "authority": "Airports Authority of India (AAI)",
                "rule_ref": "Drone Rules 2021, Rule 22(2)",
                "description": f"8 to 12 km controlled airspace perimeter around {aero['name']}. Max altitude 400 ft AGL.",
                "color": "#ca8a04",
                "fillColor": "#facc15",
                "fillOpacity": 0.16,
                "strokeWeight": 1.5,
                "strokeDashArray": "6, 6",
                "zIndex": 900
            },
            "geometry": {"type": "Polygon", "coordinates": [coords_12k]}
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "provider": "DGCA India DigitalSky Platform (AAI)",
            "version": "Drone Rules 2021 Comprehensive Airspace Map (v6.0 Official Mirror)",
            "official_source": "https://digitalsky.aai.aero/digital-sky-map",
            "updated_at": "2026-10-29T07:00:00Z",
            "total_features": len(features),
            "zones_breakdown": {
                "green": 1,
                "airport_yellow_8_12km": len(INDIAN_AERODROMES),
                "airport_yellow_5_8km": len(INDIAN_AERODROMES),
                "airport_red_0_5km": len(INDIAN_AERODROMES),
                "red_international_border_ribbons": len(INTERNATIONAL_BORDER_POLYGONS),
                "red_strategic_defense_polygons": len(STRATEGIC_DEFENSE_POLYGONS),
                "red_international_border_sectors": len(INTERNATIONAL_BORDER_RED_ZONES),
                "red_military_defense_bases": len(MILITARY_DEFENSE_RED_ZONES),
                "red_ordnance_defense_factories": len(ORDNANCE_DEFENSE_FACTORIES),
                "red_petrochemical_refineries": len(STRATEGIC_PETROCHEM_FACTORIES),
                "red_dams_water_bodies": len(MAJOR_DAMS_WATER_BODIES),
                "red_strategic_nuclear": len(STRATEGIC_NUCLEAR_RED_ZONES),
                "red_temporary_flight_restrictions": len(TEMPORARY_RED_ZONES)
            }
        },
        "features": features
    }


def classify_coordinate_zone(lat: float, lon: float, altitude_m: Optional[float] = None) -> Dict[str, Any]:
    closest_distance = 99999.0
    closest_zone_info = None

    # 1. First evaluate against continuous 25 km International Land Border Ribbon Corridors
    for poly in INTERNATIONAL_BORDER_POLYGONS:
        if is_point_in_polygon(lat, lon, poly["coordinates"]):
            return {
                "zone": "RED",
                "zone_type": "RED",
                "zone_color": "#ef4444",
                "zone_name": poly["name"],
                "category": poly.get("category", "25 km International Border Corridor"),
                "status_badge": "🔴 RED ZONE (25 KM INTERNATIONAL BORDER)",
                "max_altitude_ft": 0,
                "max_altitude_m": 0,
                "is_flight_permitted": False,
                "permission_required": "STRICTLY PROHIBITED (25 km International Land Border Buffer)",
                "nearest_zone": poly["name"],
                "distance_to_boundary_km": 0.0,
                "rule_ref": poly.get("rule_ref", "Drone Rules 2021, Rule 22(3)")
            }

    # 1B. Strategic Inland & Offshore Defense Polygons
    for poly in STRATEGIC_DEFENSE_POLYGONS:
        if is_point_in_polygon(lat, lon, poly["coordinates"]):
            return {
                "zone": "RED",
                "zone_type": "RED",
                "zone_color": "#ef4444",
                "zone_name": poly["name"],
                "category": poly.get("category", "Strategic Defense Red Zone"),
                "status_badge": f"🔴 RED ZONE ({poly.get('category', 'DEFENSE').upper()})",
                "max_altitude_ft": 0,
                "max_altitude_m": 0,
                "is_flight_permitted": False,
                "permission_required": "STRICTLY PROHIBITED (Armed Forces / Strategic Exclusion Zone)",
                "nearest_zone": poly["name"],
                "distance_to_boundary_km": 0.0,
                "rule_ref": poly.get("rule_ref", "Drone Rules 2021, Rule 22(3)")
            }

    # 2. Check circular zone lists
    def check_zone_list(zone_list: List[Dict[str, Any]], zone_type: str, category_name: str, perm_text: str, rule: str):
        nonlocal closest_distance, closest_zone_info
        for z in zone_list:
            dist = haversine_distance_km(lat, lon, z["lat"], z["lon"])
            if dist < closest_distance:
                closest_distance = dist
                closest_zone_info = {"name": z["name"], "type": zone_type, "radius_km": z["radius_km"]}
            if dist <= z["radius_km"]:
                return {
                    "zone": zone_type,
                    "zone_type": zone_type,
                    "zone_color": "#ef4444" if zone_type == "RED" else ("#f59e0b" if zone_type == "YELLOW" else "#10b981"),
                    "zone_name": z["name"],
                    "category": category_name,
                    "status_badge": f"🔴 RED ZONE ({category_name.upper()})",
                    "max_altitude_ft": 0,
                    "max_altitude_m": 0,
                    "is_flight_permitted": False,
                    "permission_required": perm_text,
                    "nearest_zone": z["name"],
                    "distance_to_boundary_km": round(z["radius_km"] - dist, 2),
                    "rule_ref": rule
                }
        return None

    # Priority check
    for zl, cat, perm in [
        (TEMPORARY_RED_ZONES, "Temporary Flight Restriction (TFR)", "STRICTLY PROHIBITED — Active Temporary Flight Restriction"),
        (MILITARY_DEFENSE_RED_ZONES, "Military Defense Airspace", "STRICTLY PROHIBITED — MoD Armed Forces Operational Base"),
        (ORDNANCE_DEFENSE_FACTORIES, "Defense Ordnance Factory", "STRICTLY PROHIBITED — Strategic Defense Production Area"),
        (INTERNATIONAL_BORDER_RED_ZONES, "25 km International Border Corridor", "STRICTLY PROHIBITED — 25 km International Land Border Buffer"),
        (STRATEGIC_NUCLEAR_RED_ZONES, "Strategic Nuclear Installation", "STRICTLY PROHIBITED — Critical Nuclear Infrastructure"),
        (STRATEGIC_PETROCHEM_FACTORIES, "Petrochemical Refinery / Chemical Hazard", "STRICTLY PROHIBITED — Critical Energy Facility"),
        (MAJOR_DAMS_WATER_BODIES, "Strategic Water Body / Dam", "STRICTLY PROHIBITED — Critical Hydrological Facility")
    ]:
        res = check_zone_list(zl, "RED", cat, perm, "Drone Rules 2021, Rule 22(3)")
        if res:
            return res

    # 3. Aerodromes 3-Tier Evaluation (Airport Red 0-5 km, Airport Yellow [5-8]km, Airport Yellow [8-12]km)
    for aero in INDIAN_AERODROMES:
        dist = haversine_distance_km(lat, lon, aero["lat"], aero["lon"])
        if dist < closest_distance:
            closest_distance = dist
            closest_zone_info = {"name": aero["name"], "type": "RED" if dist <= 5.0 else "YELLOW", "radius_km": 5.0}

        if dist <= 5.0:
            return {
                "zone": "RED",
                "zone_type": "RED",
                "zone_color": "#ef4444",
                "zone_name": f"{aero['name']} (Airport Red Zone)",
                "category": "Airport Red",
                "status_badge": "🔴 RED ZONE (AIRPORT NO-FLY)",
                "max_altitude_ft": 0, "max_altitude_m": 0, "is_flight_permitted": False,
                "permission_required": "STRICTLY PROHIBITED — 0-5 km Runway Safety Perimeter",
                "nearest_zone": aero["name"], "distance_to_boundary_km": round(5.0 - dist, 2),
                "rule_ref": "Drone Rules 2021, Rule 22(3)"
            }
        elif dist <= 8.0:
            return {
                "zone": "YELLOW",
                "zone_type": "YELLOW",
                "zone_color": "#f59e0b",
                "zone_name": f"{aero['name']} (Airport Yellow [5-8]km)",
                "category": "Airport Yellow [5-8]km",
                "status_badge": "🟡 YELLOW ZONE (ATC AUTHORIZATION REQ)",
                "max_altitude_ft": 200, "max_altitude_m": 60,
                "is_flight_permitted": True if (altitude_m or 0) <= 60 else False,
                "permission_required": "ATC / AAI Clearance Required for flights above 200 ft (60 m) AGL",
                "nearest_zone": aero["name"], "distance_to_boundary_km": round(dist, 2),
                "rule_ref": "Drone Rules 2021, Rule 22(2)"
            }
        elif dist <= 12.0:
            return {
                "zone": "YELLOW",
                "zone_type": "YELLOW",
                "zone_color": "#eab308",
                "zone_name": f"{aero['name']} (Airport Yellow [8-12]km)",
                "category": "Airport Yellow [8-12]km",
                "status_badge": "🟡 YELLOW ZONE (ATC AUTHORIZATION REQ)",
                "max_altitude_ft": 400, "max_altitude_m": 120,
                "is_flight_permitted": True if (altitude_m or 0) <= 120 else False,
                "permission_required": "ATC / AAI Clearance Required for flights above 400 ft (120 m) AGL",
                "nearest_zone": aero["name"], "distance_to_boundary_km": round(dist, 2),
                "rule_ref": "Drone Rules 2021, Rule 22(2)"
            }

    # 4. Green Zone fallback
    return {
        "zone": "GREEN",
        "zone_type": "GREEN",
        "zone_color": "#10b981",
        "zone_name": "Standard Unrestricted Airspace (Green Zone)",
        "category": "Open Airspace",
        "status_badge": "🟢 GREEN ZONE (CLEAR FOR FLIGHT)",
        "max_altitude_ft": 400, "max_altitude_m": 120,
        "is_flight_permitted": True if (altitude_m or 0) <= 120 else False,
        "permission_required": "No Prior Permission Required (Permitted up to 400 ft AGL)",
        "nearest_zone": closest_zone_info["name"] if closest_zone_info else "Open Airspace",
        "distance_to_restricted_km": round(closest_distance, 2) if closest_zone_info else 0.0,
        "rule_ref": "Drone Rules 2021, Rule 22(1)"
    }
