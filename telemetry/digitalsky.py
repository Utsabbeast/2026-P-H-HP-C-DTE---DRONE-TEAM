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

import math
from typing import Dict, List, Any, Optional, Tuple


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
INDIAN_AERODROMES = [
    {
        "id": "VIDP", "name": "Indira Gandhi International Airport (IGI)", "city": "New Delhi", "state": "Delhi",
        "lat": 28.5562, "lon": 77.1000, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VABB", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "state": "Maharashtra",
        "lat": 19.0896, "lon": 72.8656, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOBL", "name": "Kempegowda International Airport", "city": "Bengaluru", "state": "Karnataka",
        "lat": 13.1986, "lon": 77.7066, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOMM", "name": "Chennai International Airport", "city": "Chennai", "state": "Tamil Nadu",
        "lat": 12.9941, "lon": 80.1709, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VECC", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata", "state": "West Bengal",
        "lat": 22.6547, "lon": 88.4467, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOHS", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "state": "Telangana",
        "lat": 17.2403, "lon": 78.4294, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VAAH", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "state": "Gujarat",
        "lat": 23.0772, "lon": 72.6347, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VIJP", "name": "Jaipur International Airport", "city": "Jaipur", "state": "Rajasthan",
        "lat": 26.8242, "lon": 75.8122, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOCI", "name": "Cochin International Airport", "city": "Kochi", "state": "Kerala",
        "lat": 10.1518, "lon": 76.3930, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VILK", "name": "Chaudhary Charan Singh International Airport", "city": "Lucknow", "state": "Uttar Pradesh",
        "lat": 26.7606, "lon": 80.8893, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VIPL", "name": "Sahnewal Airport (Ludhiana Civil)", "city": "Ludhiana", "state": "Punjab",
        "lat": 30.8549, "lon": 75.9525, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VICG", "name": "Shaheed Bhagat Singh International Airport", "city": "Chandigarh", "state": "Chandigarh",
        "lat": 30.6735, "lon": 76.7885, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VIAR", "name": "Sri Guru Ram Dass Jee International Airport", "city": "Amritsar", "state": "Punjab",
        "lat": 31.7096, "lon": 74.7973, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEGT", "name": "Lokpriya Gopinath Bordoloi International Airport", "city": "Guwahati", "state": "Assam",
        "lat": 26.1061, "lon": 91.5859, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOTV", "name": "Thiruvananthapuram International Airport", "city": "Thiruvananthapuram", "state": "Kerala",
        "lat": 8.4821, "lon": 76.9200, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VABO", "name": "Vadodara Airport", "city": "Vadodara", "state": "Gujarat",
        "lat": 22.3362, "lon": 73.2263, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOBZ", "name": "Vijayawada International Airport", "city": "Vijayawada", "state": "Andhra Pradesh",
        "lat": 16.5304, "lon": 80.7968, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEBN", "name": "Lal Bahadur Shastri International Airport", "city": "Varanasi", "state": "Uttar Pradesh",
        "lat": 25.4524, "lon": 82.8593, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEPT", "name": "Jay Prakash Narayan Airport", "city": "Patna", "state": "Bihar",
        "lat": 25.5913, "lon": 85.0880, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEBS", "name": "Biju Patnaik International Airport", "city": "Bhubaneswar", "state": "Odisha",
        "lat": 20.2444, "lon": 85.8178, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VAPO", "name": "Pune International Airport (Lohegaon AFS)", "city": "Pune", "state": "Maharashtra",
        "lat": 18.5822, "lon": 73.9197, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOGO", "name": "Dabolim International Airport", "city": "Dabolim", "state": "Goa",
        "lat": 15.3808, "lon": 73.8313, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VISR", "name": "Sheikh ul-Alam International Airport", "city": "Srinagar", "state": "Jammu & Kashmir",
        "lat": 33.9871, "lon": 74.7744, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VIJU", "name": "Jammu Civil Enclave", "city": "Jammu", "state": "Jammu & Kashmir",
        "lat": 32.6891, "lon": 74.8375, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VILH", "name": "Kushok Bakula Rimpochee Airport", "city": "Leh", "state": "Ladakh",
        "lat": 34.1359, "lon": 77.5465, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VABP", "name": "Raja Bhoj International Airport", "city": "Bhopal", "state": "Madhya Pradesh",
        "lat": 23.2875, "lon": 77.3377, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VAID", "name": "Devi Ahilyabai Holkar International Airport", "city": "Indore", "state": "Madhya Pradesh",
        "lat": 22.7217, "lon": 75.8011, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VANP", "name": "Dr. Babasaheb Ambedkar International Airport", "city": "Nagpur", "state": "Maharashtra",
        "lat": 21.0922, "lon": 79.0472, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VERC", "name": "Birsa Munda Airport", "city": "Ranchi", "state": "Jharkhand",
        "lat": 23.3143, "lon": 85.3217, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VARP", "name": "Swami Vivekananda Airport", "city": "Raipur", "state": "Chhattisgarh",
        "lat": 21.1804, "lon": 81.7388, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOVZ", "name": "Visakhapatnam International Airport (INS Dega)", "city": "Visakhapatnam", "state": "Andhra Pradesh",
        "lat": 17.7212, "lon": 83.2245, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOCB", "name": "Coimbatore International Airport", "city": "Coimbatore", "state": "Tamil Nadu",
        "lat": 11.03, "lon": 77.0434, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOMD", "name": "Madurai International Airport", "city": "Madurai", "state": "Tamil Nadu",
        "lat": 9.8345, "lon": 78.0934, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOML", "name": "Mangalore International Airport", "city": "Mangaluru", "state": "Karnataka",
        "lat": 12.9613, "lon": 74.89, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VASU", "name": "Surat International Airport", "city": "Surat", "state": "Gujarat",
        "lat": 21.1139, "lon": 72.7419, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VIJO", "name": "Jodhpur Airport (IAF Station)", "city": "Jodhpur", "state": "Rajasthan",
        "lat": 26.2511, "lon": 73.0489, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VAUD", "name": "Maharana Pratap Airport", "city": "Udaipur", "state": "Rajasthan",
        "lat": 24.6177, "lon": 73.8961, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VIDN", "name": "Dehradun Jolly Grant Airport", "city": "Dehradun", "state": "Uttarakhand",
        "lat": 30.1897, "lon": 78.1803, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEAT", "name": "Maharaja Bir Bikram Airport", "city": "Agartala", "state": "Tripura",
        "lat": 23.887, "lon": 91.2405, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEIM", "name": "Bir Tikendrajit International Airport", "city": "Imphal", "state": "Manipur",
        "lat": 24.76, "lon": 93.8967, "type": "INTERNATIONAL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VEBI", "name": "Shillong Airport (Umroi)", "city": "Shillong", "state": "Meghalaya",
        "lat": 25.7036, "lon": 91.9786, "type": "CIVIL_AIRPORT", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    },
    {
        "id": "VOPB", "name": "Veer Savarkar International Airport (INS Utkrosh)", "city": "Port Blair", "state": "Andaman & Nicobar",
        "lat": 11.641, "lon": 92.7297, "type": "DUAL_USE", "red_radius_km": 5.0, "yellow_radius_km": 12.0
    }
]

# ==============================================================================
# 2. CONTINUOUS 25 KM INTERNATIONAL LAND BORDER RIBBON CORRIDORS & DEFENSE ZONES
# ==============================================================================
INTERNATIONAL_BORDER_POLYGONS = [
    {
        "id": "DS-CORRIDOR-WEST-IB",
        "name": "Western International Border 25 km Red Zone Ribbon (Gujarat - Rajasthan - Punjab)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the International Border from Sir Creek/Rann of Kutch to Pathankot.",
        "coordinates": [
            [68.20, 23.65], [68.75, 24.35], [70.15, 25.10], [70.05, 26.50],
            [69.95, 27.25], [71.20, 27.95], [72.30, 28.60], [73.50, 29.80],
            [73.95, 30.40], [74.55, 31.60], [75.05, 32.15], [75.45, 32.40],
            [75.72, 32.22], [75.32, 31.98], [74.82, 31.42], [74.28, 30.22],
            [73.80, 29.55], [72.58, 28.38], [71.48, 27.75], [70.32, 27.05],
            [70.42, 26.35], [70.45, 24.95], [69.05, 24.20], [68.60, 23.55],
            [68.20, 23.65]
        ]
    },
    {
        "id": "DS-CORRIDOR-NORTH-LOC-LAC",
        "name": "Northern Frontier 25 km Red Zone Ribbon (J&K LOC - Ladakh LAC)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km defense buffer ribbon along the Line of Control (LOC) and Line of Actual Control (LAC) covering Jammu, Kashmir, Kargil, and Eastern Ladakh.",
        "coordinates": [
            [74.75, 32.65], [74.15, 33.15], [74.05, 33.80], [74.15, 34.25],
            [74.35, 34.65], [75.15, 34.78], [76.50, 34.85], [77.30, 35.40],
            [78.50, 35.20], [78.95, 34.10], [79.25, 33.00],
            [78.95, 33.10], [78.68, 34.00], [78.22, 35.00], [77.10, 35.15],
            [76.35, 34.60], [75.08, 34.55], [74.52, 34.40], [74.32, 33.95],
            [74.38, 33.30], [74.92, 32.80], [74.75, 32.65]
        ]
    },
    {
        "id": "DS-ZONE-KASHMIR-SECURITY",
        "name": "Northern Kashmir & LOC High-Security Defense Red Zone",
        "category": "High-Security Defense Frontier",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "High-altitude strategic defense frontier covering Kashmir Line of Control sectors, Kupwara, Uri, Gurez, Dras, Kargil, and Siachen frontier. Civilian drone flights strictly prohibited.",
        "coordinates": [
            [73.80, 34.30], [74.00, 34.75], [74.65, 34.80], [75.50, 34.75],
            [76.30, 34.90], [77.10, 35.50], [77.90, 35.60], [78.30, 35.10],
            [77.70, 34.60], [76.80, 34.30], [75.80, 34.20], [75.00, 34.25],
            [74.30, 34.10], [73.90, 34.05], [73.80, 34.30]
        ]
    },
    {
        "id": "DS-CORRIDOR-CHINA-LAC-HIMALAYAS",
        "name": "Middle Sector China LAC 25 km Red Zone Ribbon (Himachal - Uttarakhand)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km Line of Actual Control (LAC) Red Zone across Himachal Pradesh (Kinnaur/Spiti) and Uttarakhand (Uttarkashi, Chamoli/Mana, Pithoragarh/Lipulekh).",
        "coordinates": [
            [78.50, 32.05], [78.85, 31.60], [79.25, 31.25], [79.75, 30.95],
            [80.35, 30.45], [80.70, 30.15],
            [80.45, 29.95], [80.10, 30.25], [79.55, 30.70], [79.05, 31.05],
            [78.60, 31.40], [78.25, 31.85], [78.50, 32.05]
        ]
    },
    {
        "id": "DS-CORRIDOR-NEPAL-BORDER",
        "name": "Indo-Nepal International Border 25 km Red Zone Ribbon (Uttarakhand - UP - Bihar - Bengal - Sikkim)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the entire Indo-Nepal international land border across Uttarakhand, Uttar Pradesh, Bihar, North Bengal and West Sikkim.",
        "coordinates": [
            [80.50, 30.25], [80.12, 29.05], [80.20, 28.70], [80.65, 28.35],
            [81.60, 27.80], [82.25, 27.70], [82.80, 27.50], [83.45, 27.45],
            [83.95, 27.40], [84.85, 26.98], [85.50, 26.75], [86.15, 26.60],
            [87.00, 26.50], [87.30, 26.40], [88.05, 26.35], [88.15, 26.70],
            [88.02, 27.20], [88.15, 27.70],
            [88.35, 27.65], [88.25, 27.05], [88.30, 26.60], [88.00, 26.15],
            [87.35, 26.20], [87.00, 26.30], [86.15, 26.40], [85.50, 26.55],
            [84.85, 26.75], [84.00, 27.18], [83.50, 27.22], [82.85, 27.28],
            [82.25, 27.48], [81.60, 27.58], [80.65, 28.12], [80.15, 28.48],
            [79.90, 28.90], [80.25, 30.10], [80.50, 30.25]
        ]
    },
    {
        "id": "DS-CORRIDOR-BHUTAN-BORDER",
        "name": "Indo-Bhutan International Border 25 km Red Zone Ribbon (Sikkim - Bengal - Assam - Arunachal)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the India-Bhutan international border across East Sikkim, North Bengal (Jaigaon), Western/Central Assam, and West Kameng.",
        "coordinates": [
            [88.90, 27.15], [89.40, 26.85], [89.70, 26.75], [90.25, 26.85],
            [90.55, 26.88], [91.50, 26.82], [92.10, 26.90], [91.80, 27.35],
            [91.50, 27.55],
            [91.75, 27.45], [91.95, 27.15], [92.15, 26.68], [91.50, 26.60],
            [90.55, 26.65], [90.25, 26.62], [89.40, 26.62], [88.95, 26.92],
            [88.90, 27.15]
        ]
    },
    {
        "id": "DS-CORRIDOR-CHINA-SIKKIM-LAC",
        "name": "Sikkim China LAC 25 km Red Zone Ribbon (Nathu La - Doklam - Cho Lhamo)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km Line of Actual Control (LAC) Red Zone across North and East Sikkim along the Tibetan frontier.",
        "coordinates": [
            [88.55, 28.08], [88.95, 27.45], [88.95, 27.25], [88.65, 27.20],
            [88.35, 27.85], [88.55, 28.08]
        ]
    },
    {
        "id": "DS-CORRIDOR-CHINA-ARUNACHAL-MCMAHON",
        "name": "Arunachal McMahon Line 25 km Red Zone Ribbon (Tawang to Kibithu/Walong)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km Line of Actual Control (LAC) McMahon Line Red Zone covering Arunachal Pradesh frontier from Tawang and Bum La to Kibithu and Walong.",
        "coordinates": [
            [91.85, 27.70], [92.80, 27.85], [93.50, 28.15], [94.20, 28.35],
            [95.00, 28.95], [95.80, 28.85], [96.50, 28.45], [97.05, 28.25],
            [96.95, 28.00], [96.35, 28.20], [95.65, 28.60], [94.95, 28.70],
            [94.15, 28.10], [93.45, 27.90], [92.75, 27.60], [91.95, 27.45],
            [91.85, 27.70]
        ]
    },
    {
        "id": "DS-CORRIDOR-BANGLADESH-BORDER-WEST",
        "name": "Indo-Bangladesh Border 25 km Red Zone Ribbon (West Bengal & Assam Dhubri Sector)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the India-Bangladesh border from the Sundarbans coastal frontier through Petrapole, Nadia, Murshidabad, Malda, Dinajpur, Cooch Behar, to Assam Dhubri.",
        "coordinates": [
            [89.15, 21.65], [88.95, 22.20], [88.88, 23.05], [88.65, 23.75],
            [88.35, 24.45], [88.25, 25.10], [88.98, 25.28], [88.25, 26.20],
            [88.90, 26.35], [89.85, 26.30], [89.95, 26.00], [89.85, 25.75],
            [90.15, 25.90], [89.65, 26.45], [88.80, 26.50], [88.10, 26.15],
            [88.75, 25.25], [88.05, 25.00], [88.15, 24.30], [88.45, 23.60],
            [88.65, 22.85], [88.75, 22.15], [88.90, 21.65], [89.15, 21.65]
        ]
    },
    {
        "id": "DS-CORRIDOR-BANGLADESH-BORDER-EAST",
        "name": "Indo-Bangladesh Border 25 km Red Zone Ribbon (Meghalaya - Assam - Tripura - Mizoram)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the eastern Indo-Bangladesh international border across Meghalaya (Garo/Khasi/Dawki), Barak Valley, Tripura perimeter (Agartala, Belonia, Sabroom) and Western Mizoram.",
        "coordinates": [
            [89.85, 25.30], [90.65, 25.20], [91.30, 25.18], [92.05, 25.18],
            [92.35, 25.10], [92.35, 24.85], [92.30, 24.60], [92.05, 24.40],
            [91.80, 24.15], [91.60, 23.95], [91.27, 23.85], [91.25, 23.48],
            [91.45, 23.25], [91.70, 23.00], [92.30, 23.40], [92.50, 22.90],
            [92.75, 22.00],
            [92.95, 22.10], [92.70, 22.95], [91.85, 23.20], [91.45, 23.85],
            [91.90, 24.05], [92.55, 24.65], [92.25, 25.35], [91.85, 25.38],
            [91.20, 25.40], [90.25, 25.45], [89.85, 25.30]
        ]
    },
    {
        "id": "DS-CORRIDOR-MYANMAR-BORDER",
        "name": "Indo-Myanmar International Border 25 km Red Zone Ribbon (Arunachal - Nagaland - Manipur - Mizoram)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the India-Myanmar international border across Eastern Arunachal (Pangsau Pass), Nagaland (Mon/Kiphire), Manipur (Moreh/Chandel) and Mizoram (Zokhawthar/Champhai/Parva).",
        "coordinates": [
            [97.20, 28.00], [96.25, 27.25], [95.55, 26.85], [95.15, 26.50],
            [94.90, 25.70], [94.80, 25.50], [94.55, 25.10], [94.40, 24.25],
            [94.00, 23.90], [93.45, 23.50], [93.38, 23.05], [93.18, 22.40],
            [92.88, 21.95],
            [92.60, 22.10], [92.90, 22.50], [93.10, 23.25], [93.65, 24.00],
            [94.05, 24.45], [94.20, 25.00], [94.50, 25.60], [94.85, 26.30],
            [95.30, 27.00], [95.90, 27.35], [96.95, 27.85], [97.20, 28.00]
        ]
    }
]

# ==============================================================================
# 2B. STRATEGIC INLAND & OFFSHORE DEFENSE ENCLAVE RED ZONES (AAI DIGITAL SKY)
# ==============================================================================
STRATEGIC_DEFENSE_POLYGONS = [
    {
        "id": "DS-POLY-OFFSHORE-BOMBAY-HIGH",
        "name": "Bombay High Offshore Oil & Naval Exclusion Red Zone (Arabian Sea)",
        "category": "Offshore Strategic Installation",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Critical national energy offshore platform and Western Naval Command maritime defense exclusion zone in the Arabian Sea.",
        "coordinates": [[71.1, 18.75], [71.1, 19.95], [72.15, 19.95], [72.15, 18.75], [71.1, 18.75]]
    },
    {
        "id": "DS-POLY-OFFSHORE-CHANDIPUR",
        "name": "Chandipur & APJ Abdul Kalam Island DRDO Missile Test Range (Bay of Bengal)",
        "category": "Strategic Missile Test Range",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Integrated Test Range (ITR) Chandipur and Wheeler Island (Dr. APJ Abdul Kalam Island) high-security missile launch envelope.",
        "coordinates": [[86.85, 20.65], [86.85, 21.65], [87.65, 21.45], [87.45, 20.55], [86.85, 20.65]]
    },
    {
        "id": "DS-POLY-BABINA-JHANSI-FIRING-RANGE",
        "name": "Babina - Jhansi - Shivpuri Army Field Firing Range Complex",
        "category": "Military Field Firing Range",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "White Tiger Division armored artillery and combat vehicle live-firing maneuvers zone spanning UP and MP.",
        "coordinates": [[78.05, 24.95], [78.2, 25.75], [78.75, 25.8], [78.9, 25.2], [78.45, 24.85], [78.05, 24.95]]
    },
    {
        "id": "DS-POLY-MH-DEFENSE-CORRIDOR",
        "name": "Pune - Ahmednagar - Dehu Road Military Armament & Firing Enclave",
        "category": "Military Armament & Training Complex",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Armoured Corps Centre & School (ACC&S), Vehicle Research & Development Establishment (VRDE), and Southern Command cantonment envelope.",
        "coordinates": [[73.7, 18.55], [73.85, 19.3], [74.85, 19.2], [74.7, 18.45], [73.7, 18.55]]
    },
    {
        "id": "DS-POLY-JH-DEFENSE-CORRIDOR",
        "name": "Jharkhand Jamshedpur - Bokaro - Ramgarh Strategic Industrial Defense Area",
        "category": "Critical Defense Metallurgy Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Strategic heavy industrial and defense metal manufacturing facilities across Chota Nagpur plateau.",
        "coordinates": [[85.8, 23.35], [86.35, 23.85], [86.55, 23.15], [86.1, 22.75], [85.8, 23.35]]
    },
    {
        "id": "DS-POLY-POKHRAN-FIRING-RANGE",
        "name": "Pokhran Desert Army Field Firing Range & Nuclear Test Grounds",
        "category": "Strategic Weapon Test Facility",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Desert corps combined arms strike weapon testing grounds and historical nuclear test site in Jaisalmer district.",
        "coordinates": [[71.6, 26.75], [71.6, 27.45], [72.25, 27.45], [72.25, 26.75], [71.6, 26.75]]
    },
    {
        "id": "DS-POLY-DELHI-NCT-VVIP",
        "name": "National Capital Territory (Delhi VVIP & Parliament Red Zone)",
        "category": "National Capital Security Perimeter",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "VVIP Security envelope covering Rashtrapati Bhavan, Prime Minister Residence, Central Vista, Parliament House, and diplomatic enclave.",
        "coordinates": [[77.1, 28.52], [77.1, 28.66], [77.26, 28.66], [77.26, 28.52], [77.1, 28.52]]
    },
    {
        "id": "DS-POLY-SRIHARIKOTA-ISRO",
        "name": "Satish Dhawan Space Centre (SDSC SHAR) Launch Facility",
        "category": "Space Launch Center",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "ISRO spaceport barrier envelope covering Sriharikota island, rocket launch pads, and Pulicat Lake security zone.",
        "coordinates": [[80.15, 13.6], [80.15, 13.95], [80.35, 13.95], [80.35, 13.6], [80.15, 13.6]]
    },
    {
        "id": "DS-POLY-JAMNAGAR-PORBANDAR",
        "name": "Jamnagar - Porbandar IAF Fighter Base & Naval Air Station",
        "category": "Military Strategic Coastal Base",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Jaguar fighter base, INS Sardar Patel, and Indian Coast Guard western air command security envelope.",
        "coordinates": [[69.45, 21.6], [69.45, 22.5], [70.15, 22.5], [70.15, 21.6], [69.45, 21.6]]
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
    features.append({
        "type": "Feature",
        "id": "DS-GREEN-PAN-INDIA",
        "properties": {
            "id": "DS-GREEN-PAN-INDIA",
            "name": "Pan-India Airspace (Green Zone)",
            "zone_type": "GREEN",
            "category": "Open Airspace",
            "max_altitude_agl_ft": 400,
            "max_altitude_agl_m": 120,
            "permission_required": "NONE (Up to 400 ft AGL)",
            "authority": "DGCA — No prior flight approval needed",
            "rule_ref": "Drone Rules 2021, Rule 22(1)",
            "description": "Standard green airspace zone covering India territory outside designated red and yellow zones. Autonomous & manual flights up to 400 ft AGL freely permitted.",
            "color": "#059669",
            "fillColor": "#10b981",
            "fillOpacity": 0.10,
            "strokeWeight": 1.5,
            "zIndex": 100
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [INDIA_AIRSPACE_BOUNDARY]
        }
    })

    # 2. YELLOW ZONES (5-12 km around aerodromes)
    for aero in INDIAN_AERODROMES:
        lat, lon, r = aero["lat"], aero["lon"], aero["yellow_radius_km"]
        coords = generate_circle_polygon(lat, lon, r)
        f_id = f"DS-YEL-{aero['id']}"
        features.append({
            "type": "Feature",
            "id": f_id,
            "properties": {
                "id": f_id,
                "name": f"{aero['name']} — Controlled Airspace (Yellow Zone)",
                "zone_type": "YELLOW",
                "category": "ATC Controlled Airspace",
                "aerodrome_id": aero["id"],
                "city": aero["city"],
                "state": aero["state"],
                "radius_km": r,
                "max_altitude_agl_ft": 200,
                "max_altitude_agl_m": 60,
                "permission_required": "ATC / AAI Clearance Required (Above 200 ft between 8-12 km, all flights 5-8 km)",
                "authority": f"Air Traffic Control ({aero['city']} ATC / AAI)",
                "rule_ref": "Drone Rules 2021, Rule 22(2)",
                "description": f"Controlled airspace within {r} km radius of {aero['name']}. Prior flight plan clearance required via DigitalSky.",
                "color": "#d97706",
                "fillColor": "#f59e0b",
                "fillOpacity": 0.22,
                "strokeWeight": 1.5,
                "strokeDashArray": "4, 4",
                "zIndex": 500
            },
            "geometry": {"type": "Polygon", "coordinates": [coords]}
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
                "color": "#991b1b",
                "fillColor": "#dc2626",
                "fillOpacity": 0.45,
                "strokeWeight": 2.5,
                "zIndex": 1250
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [poly_item["coordinates"]]
            }
        })

    # 4. 25 km International Border Sector Checkpoint Circles
    add_red_features(INTERNATIONAL_BORDER_RED_ZONES, "25 km International Border Corridor", "#991b1b", "#dc2626", 0.38, 2.2, layer_group="boundary_25km")

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
