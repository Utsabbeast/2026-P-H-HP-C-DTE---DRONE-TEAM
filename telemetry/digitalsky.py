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
   - 25 km buffer zone along International Land Borders (LOC / LAC / IB).
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
    }
]

# ==============================================================================
# 2. 25 KM INTERNATIONAL BORDER BUFFER ZONES (RED ZONES)
# ==============================================================================
INTERNATIONAL_BORDER_RED_ZONES = [
    {"id": "DS-BORDER-PB-AMRITSAR", "name": "Punjab Border 25 km Red Zone (Amritsar / Attari / Wagah Sector)", "lat": 31.6046, "lon": 74.5750, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Land Border Red Zone along India-Pakistan IB (Amritsar/Tarn Taran)."},
    {"id": "DS-BORDER-PB-FEROZEPUR", "name": "Punjab Border 25 km Red Zone (Ferozepur / Hussainiwala Sector)", "lat": 30.9500, "lon": 74.5200, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border buffer covering Ferozepur & Hussainiwala frontier."},
    {"id": "DS-BORDER-PB-FAZILKA", "name": "Punjab Border 25 km Red Zone (Fazilka / Sadiqi Sector)", "lat": 30.4000, "lon": 74.0200, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border security envelope along Fazilka/Abohar corridor."},
    {"id": "DS-BORDER-PB-GURDASPUR", "name": "Punjab Border 25 km Red Zone (Gurdaspur / Dera Baba Nanak Sector)", "lat": 31.9800, "lon": 75.0500, "radius_km": 25.0, "sector": "PUNJAB_IB", "desc": "DGCA 25 km International Border Corridor near Kartarpur/Dera Baba Nanak frontier."},
    {"id": "DS-BORDER-RJ-JAISALMER", "name": "Rajasthan Border 25 km Red Zone (Jaisalmer / Tanot / Longewala Sector)", "lat": 27.2000, "lon": 70.4000, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km International Border Red Zone along Thar Desert / Longewala defense frontier."},
    {"id": "DS-BORDER-RJ-BARMER", "name": "Rajasthan Border 25 km Red Zone (Barmer / Munabao Sector)", "lat": 25.7500, "lon": 70.3000, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km Border buffer covering Munabao / Gadra Road border corridor."},
    {"id": "DS-BORDER-RJ-BIKANER", "name": "Rajasthan Border 25 km Red Zone (Bikaner / Khajuwala Sector)", "lat": 28.3000, "lon": 72.5000, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km International Border security zone covering Khajuwala / Pugal corridor."},
    {"id": "DS-BORDER-RJ-GANGANAGAR", "name": "Rajasthan Border 25 km Red Zone (Sri Ganganagar / Hindumalkot Sector)", "lat": 29.9500, "lon": 73.8800, "radius_km": 25.0, "sector": "RAJASTHAN_IB", "desc": "DGCA 25 km Border Corridor along Hindumalkot and Anupgarh frontier."},
    {"id": "DS-BORDER-GJ-KUTCH", "name": "Gujarat Border 25 km Red Zone (Rann of Kutch & Sir Creek Sector)", "lat": 23.8500, "lon": 68.7500, "radius_km": 25.0, "sector": "GUJARAT_IB", "desc": "DGCA 25 km International Land Border & Sir Creek maritime corridor. Strictly Prohibited."},
    {"id": "DS-BORDER-JK-SAMBA-KATHUA", "name": "Jammu Border 25 km Red Zone (Jammu / Samba / Kathua IB Sector)", "lat": 32.5500, "lon": 75.1000, "radius_km": 25.0, "sector": "JK_IB", "desc": "DGCA 25 km International Border buffer across Jammu, Samba, and Hiranagar."},
    {"id": "DS-BORDER-JK-POONCH-RAJOURI", "name": "Line of Control 25 km Red Zone (Rajouri / Poonch LOC Sector)", "lat": 33.7700, "lon": 74.1000, "radius_km": 25.0, "sector": "JK_LOC", "desc": "DGCA 25 km Line of Control (LOC) strict defense Red Zone."},
    {"id": "DS-BORDER-JK-KUPWARA-URI", "name": "Line of Control 25 km Red Zone (Kupwara / Uri / Tangdhar Sector)", "lat": 34.3500, "lon": 74.0500, "radius_km": 25.0, "sector": "JK_LOC", "desc": "DGCA 25 km LOC high-altitude defense corridor."},
    {"id": "DS-BORDER-LADAKH-EAST", "name": "Ladakh LAC 25 km Red Zone (Pangong Tso / Chushul / Galwan Sector)", "lat": 33.7500, "lon": 78.7000, "radius_km": 25.0, "sector": "LADAKH_LAC", "desc": "DGCA 25 km Line of Actual Control (LAC) high-security border corridor."},
    {"id": "DS-BORDER-LADAKH-DBO", "name": "Ladakh LAC 25 km Red Zone (Daulat Beg Oldie / Siachen Sector)", "lat": 35.2500, "lon": 77.9000, "radius_km": 25.0, "sector": "LADAKH_LAC", "desc": "DGCA 25 km northern LAC and Karakoram high-altitude prohibited airspace."},
    {"id": "DS-BORDER-UK-LIPULEKH", "name": "Uttarakhand Border 25 km Red Zone (Pithoragarh / Lipulekh / Mana Sector)", "lat": 30.5000, "lon": 80.5000, "radius_km": 25.0, "sector": "UTTARAKHAND_BORDER", "desc": "DGCA 25 km International Border buffer across Indo-Tibet frontier."},
    {"id": "DS-BORDER-SIKKIM-NATHULA", "name": "Sikkim Border 25 km Red Zone (Nathu La / Doklam Sector)", "lat": 27.3800, "lon": 88.8300, "radius_km": 25.0, "sector": "SIKKIM_BORDER", "desc": "DGCA 25 km International Land Border buffer in East/North Sikkim."},
    {"id": "DS-BORDER-AP-TAWANG", "name": "Arunachal LAC 25 km Red Zone (Tawang / Bum La Sector)", "lat": 27.6000, "lon": 91.8700, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km Line of Actual Control frontier in Western Arunachal Pradesh."},
    {"id": "DS-BORDER-AP-WALONG", "name": "Arunachal LAC 25 km Red Zone (Walong / Kibithu Eastern Sector)", "lat": 28.2500, "lon": 97.0500, "radius_km": 25.0, "sector": "ARUNACHAL_LAC", "desc": "DGCA 25 km easternmost LAC border corridor."},
    {"id": "DS-BORDER-WB-PETRAPOLE", "name": "West Bengal Border 25 km Red Zone (Petrapole / Benapole Sector)", "lat": 23.0500, "lon": 88.8800, "radius_km": 25.0, "sector": "BANGLADESH_IB", "desc": "DGCA 25 km International Land Border corridor across South Bengal frontier."},
    {"id": "DS-BORDER-MANIPUR-MOREH", "name": "Manipur Border 25 km Red Zone (Moreh / Indo-Myanmar Sector)", "lat": 24.2500, "lon": 94.3000, "radius_km": 25.0, "sector": "MYANMAR_IB", "desc": "DGCA 25 km International Land Border buffer along Indo-Myanmar frontier."}
]

# ==============================================================================
# 3. MILITARY DEFENSE BASES, AIR FORCE STATIONS & NAVAL HUBS
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
# 4. ORDNANCE FACTORIES & DEFENSE PRODUCTION UNITS (MILITARY FACTORIES)
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
# 5. HAZARDOUS PETROCHEMICAL REFINERIES & INDUSTRIAL MEGA-FACTORIES
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
# 6. STRATEGIC MEGA-DAMS, RESERVOIRS & SENSITIVE WATER BODIES
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
# 7. STRATEGIC NUCLEAR POWER & RESEARCH RED ZONES
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
# 8. TEMPORARY RED ZONES (TFR - TEMPORARY FLIGHT RESTRICTIONS)
# ==============================================================================
TEMPORARY_RED_ZONES = [
    {"id": "DS-TFR-DEL-CENTRAL-VISTA", "name": "Central Vista VIP Security Zone (Parliament, Rashtrapati Bhavan, PM Residence)", "city": "New Delhi", "state": "Delhi", "lat": 28.6143, "lon": 77.2008, "radius_km": 4.5, "category": "TFR_VIP_SECURITY", "validity": "PERMANENT_RESTRICTED (NOTAM A-01)", "desc": "Kartavya Path, Rashtrapati Bhavan, PM Residence & Parliament House. Zero tolerance drone ban."},
    {"id": "DS-TFR-DEL-REDFORT", "name": "Red Fort National Independence Security Envelope (TFR)", "city": "Old Delhi", "state": "Delhi", "lat": 28.6562, "lon": 77.2410, "radius_km": 3.0, "category": "TFR_NATIONAL_HERITAGE", "validity": "HIGH_SECURITY_TFR", "desc": "Red Fort VIP ramparts, Chandni Chowk & National Independence Day security zone."},
    {"id": "DS-TFR-PB-WAGAH", "name": "Attari-Wagah Border Retreat Arena (TFR Security Zone)", "city": "Attari", "state": "Punjab", "lat": 31.6047, "lon": 74.5714, "radius_km": 3.5, "category": "TFR_BORDER_CEREMONY", "validity": "DAILY_ACTIVE_TFR", "desc": "International joint retreat flag ceremony amphitheatre. BSF High-Alert Airspace."},
    {"id": "DS-TFR-UP-AYODHYA", "name": "Ayodhya Shri Ram Janmabhoomi High-Security Complex (TFR)", "city": "Ayodhya", "state": "Uttar Pradesh", "lat": 26.7950, "lon": 82.1940, "radius_km": 4.0, "category": "TFR_SPECIAL_SECURITY", "validity": "ACTIVE_TFR", "desc": "Special Security Force (SSF) & NSG designated anti-drone protective red zone."},
    {"id": "DS-TFR-GJ-KEVADIA", "name": "Statue of Unity National Security Envelope (TFR)", "city": "Kevadia", "state": "Gujarat", "lat": 21.8380, "lon": 73.7190, "radius_km": 4.0, "category": "TFR_NATIONAL_MONUMENT", "validity": "ACTIVE_TFR", "desc": "National security VIP perimeter surrounding Sardar Patel memorial and Narmada reservoir."},
    {"id": "DS-TFR-UP-KASHI", "name": "Kashi Vishwanath Corridor & Ganga Ghats Security Envelope", "city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3100, "lon": 83.0100, "radius_km": 3.5, "category": "TFR_HERITAGE_SECURITY", "validity": "ACTIVE_TFR", "desc": "Ganga Aarti Ghats, Kashi Vishwanath temple corridor and riverfront high-security zone."}
]

# Continuous 25 km International Land Border Ribbon Corridors
INTERNATIONAL_BORDER_POLYGONS = [
    {
        "id": "DS-CORRIDOR-WEST-IB",
        "name": "Western International Border 25 km Red Zone Ribbon (Gujarat - Rajasthan - Punjab)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km DGCA Red Zone security ribbon along the International Border from Sir Creek/Rann of Kutch to Pathankot.",
        "coordinates": [
            [68.30, 23.65], [68.75, 24.35], [70.15, 25.10], [70.05, 26.50],
            [69.95, 27.25], [71.20, 27.95], [72.30, 28.60], [73.50, 29.80],
            [73.95, 30.40], [74.55, 31.60], [75.05, 32.15], [75.45, 32.40],
            [75.72, 32.22], [75.32, 31.98], [74.82, 31.42], [74.28, 30.22],
            [73.80, 29.55], [72.58, 28.38], [71.48, 27.75], [70.32, 27.05],
            [70.42, 26.35], [70.45, 24.95], [69.05, 24.20], [68.60, 23.55],
            [68.30, 23.65]
        ]
    },
    {
        "id": "DS-CORRIDOR-NORTH-LOC-LAC",
        "name": "Northern Frontier 25 km Red Zone Ribbon (J&K LOC - Ladakh LAC)",
        "category": "25 km International Border Corridor",
        "rule_ref": "Drone Rules 2021, Rule 22(3)",
        "desc": "Continuous 25 km defense buffer ribbon along the Line of Control (LOC) and Line of Actual Control (LAC).",
        "coordinates": [
            [74.75, 32.65], [74.15, 33.15], [74.05, 33.80], [74.15, 34.25],
            [74.35, 34.65], [75.15, 34.78], [76.50, 34.85], [77.30, 35.40],
            [78.50, 35.20], [78.95, 34.10], [79.25, 33.00],
            [78.95, 33.10], [78.68, 34.00], [78.22, 35.00], [77.10, 35.15],
            [76.35, 34.60], [75.08, 34.55], [74.52, 34.40], [74.32, 33.95],
            [74.38, 33.30], [74.92, 32.80], [74.75, 32.65]
        ]
    }
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
    def add_red_features(items, category_tag, color, fill_color, opacity, stroke_weight, dash=""):
        for item in items:
            lat, lon, r = item["lat"], item["lon"], item["radius_km"]
            coords = generate_circle_polygon(lat, lon, r)
            p = {
                "id": item["id"],
                "name": item["name"],
                "zone_type": "RED",
                "category": category_tag,
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

    # 3. 25 km International Border Zones (Continuous Ribbons & Strategic Border Sectors)
    for poly_item in INTERNATIONAL_BORDER_POLYGONS:
        features.append({
            "type": "Feature",
            "id": poly_item["id"],
            "properties": {
                "id": poly_item["id"],
                "name": f"🛡️ {poly_item['name']}",
                "zone_type": "RED",
                "category": poly_item["category"],
                "radius_km": 25.0,
                "max_altitude_agl_ft": 0,
                "max_altitude_agl_m": 0,
                "permission_required": "STRICTLY PROHIBITED (25 km International Border Corridor)",
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

    add_red_features(INTERNATIONAL_BORDER_RED_ZONES, "25 km International Border Corridor", "#991b1b", "#dc2626", 0.38, 2.2)

    # 4. Military Defense Areas
    add_red_features(MILITARY_DEFENSE_RED_ZONES, "Military Defense Airspace", "#7f1d1d", "#b91c1c", 0.44, 2.2)

    # 5. Ordnance Factories & Defense Production
    add_red_features(ORDNANCE_DEFENSE_FACTORIES, "Defense Ordnance Factory", "#831843", "#be185d", 0.45, 2.2)

    # 6. Petrochemical Refineries & Hazardous Factories
    add_red_features(STRATEGIC_PETROCHEM_FACTORIES, "Industrial Petrochemical Refinery", "#9a3412", "#ea580c", 0.42, 2.2)

    # 7. Major Dams & Sensitive Water Bodies
    add_red_features(MAJOR_DAMS_WATER_BODIES, "Strategic Water Body / Dam", "#1e3a8a", "#2563eb", 0.40, 2.2)

    # 8. Strategic Nuclear Facilities
    add_red_features(STRATEGIC_NUCLEAR_RED_ZONES, "Strategic Nuclear Installation", "#881337", "#e11d48", 0.48, 2.2)

    # 9. Temporary Red Zones (TFR)
    add_red_features(TEMPORARY_RED_ZONES, "Temporary Flight Restriction (TFR)", "#4c0519", "#be123c", 0.52, 2.5, "6, 3")

    # 10. Civil Aerodrome 0-5 km Runways
    for aero in INDIAN_AERODROMES:
        lat, lon, r = aero["lat"], aero["lon"], aero["red_radius_km"]
        coords = generate_circle_polygon(lat, lon, r)
        f_id = f"DS-RED-{aero['id']}"
        features.append({
            "type": "Feature",
            "id": f_id,
            "properties": {
                "id": f_id,
                "name": f"✈️ {aero['name']} — No-Fly Zone (Red Zone)",
                "zone_type": "RED",
                "category": "Airport Runway Perimeter",
                "aerodrome_id": aero["id"],
                "city": aero["city"],
                "state": aero["state"],
                "radius_km": r,
                "max_altitude_agl_ft": 0,
                "max_altitude_agl_m": 0,
                "permission_required": "STRICTLY PROHIBITED (0-5 km Runway Safety Perimeter)",
                "authority": "AAI & Directorate General of Civil Aviation",
                "rule_ref": "Drone Rules 2021, Rule 22(3)",
                "description": f"Mandatory 5 km runway perimeter around {aero['name']}. Drone flights strictly banned.",
                "color": "#b91c1c",
                "fillColor": "#ef4444",
                "fillOpacity": 0.42,
                "strokeWeight": 2.2,
                "zIndex": 1100
            },
            "geometry": {"type": "Polygon", "coordinates": [coords]}
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "provider": "DGCA India DigitalSky Platform",
            "version": "Drone Rules 2021 Comprehensive Airspace Map (v4.5)",
            "updated_at": "2026-10-10T05:30:00Z",
            "total_features": len(features),
            "zones_breakdown": {
                "green": 1,
                "yellow_atc_controlled": len(INDIAN_AERODROMES),
                "red_international_borders_25km": len(INTERNATIONAL_BORDER_RED_ZONES),
                "red_military_defense_bases": len(MILITARY_DEFENSE_RED_ZONES),
                "red_ordnance_defense_factories": len(ORDNANCE_DEFENSE_FACTORIES),
                "red_petrochemical_refineries": len(STRATEGIC_PETROCHEM_FACTORIES),
                "red_dams_water_bodies": len(MAJOR_DAMS_WATER_BODIES),
                "red_strategic_nuclear": len(STRATEGIC_NUCLEAR_RED_ZONES),
                "red_temporary_flight_restrictions": len(TEMPORARY_RED_ZONES),
                "red_airport_perimeters": len(INDIAN_AERODROMES)
            }
        },
        "features": features
    }


def classify_coordinate_zone(lat: float, lon: float, altitude_m: Optional[float] = None) -> Dict[str, Any]:
    closest_distance = 99999.0
    closest_zone_info = None

    def check_zone_list(zone_list: List[Dict[str, Any]], zone_type: str, category_name: str, perm_text: str, rule: str):
        nonlocal closest_distance, closest_zone_info
        for z in zone_list:
            dist = haversine_distance_km(lat, lon, z["lat"], z["lon"])
            if dist < closest_distance:
                closest_distance = dist
                closest_zone_info = {"name": z["name"], "type": zone_type, "radius_km": z["radius_km"]}
            if dist <= z["radius_km"]:
                return {
                    "zone_type": zone_type,
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

    # Aerodromes
    for aero in INDIAN_AERODROMES:
        dist = haversine_distance_km(lat, lon, aero["lat"], aero["lon"])
        if dist < closest_distance:
            closest_distance = dist
            closest_zone_info = {"name": aero["name"], "type": "RED" if dist <= aero["red_radius_km"] else "YELLOW", "radius_km": aero["red_radius_km"]}
        if dist <= aero["red_radius_km"]:
            return {
                "zone_type": "RED",
                "zone_name": f"{aero['name']} (0-5 km Runway Perimeter)",
                "category": "Airport Runway Perimeter",
                "status_badge": "🔴 RED ZONE (AIRPORT NO-FLY)",
                "max_altitude_ft": 0, "max_altitude_m": 0, "is_flight_permitted": False,
                "permission_required": "STRICTLY PROHIBITED — Operational Aerodrome Perimeter",
                "nearest_zone": aero["name"], "distance_to_boundary_km": round(aero["red_radius_km"] - dist, 2),
                "rule_ref": "Drone Rules 2021, Rule 22(3)"
            }

    for aero in INDIAN_AERODROMES:
        dist = haversine_distance_km(lat, lon, aero["lat"], aero["lon"])
        if dist <= aero["yellow_radius_km"]:
            return {
                "zone_type": "YELLOW",
                "zone_name": f"{aero['name']} (5-12 km Controlled Airspace)",
                "category": "ATC Controlled Airspace",
                "status_badge": "🟡 YELLOW ZONE (ATC AUTHORIZATION REQ)",
                "max_altitude_ft": 200, "max_altitude_m": 60,
                "is_flight_permitted": True if (altitude_m or 0) <= 60 else False,
                "permission_required": "ATC / AAI Clearance Required for flights above 200 ft AGL",
                "nearest_zone": aero["name"], "distance_to_boundary_km": round(dist, 2),
                "rule_ref": "Drone Rules 2021, Rule 22(2)"
            }

    # Green Zone fallback
    return {
        "zone_type": "GREEN",
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
