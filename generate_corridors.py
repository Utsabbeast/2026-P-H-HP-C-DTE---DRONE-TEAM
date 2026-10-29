import json
import math

with open('telemetry/data/india_boundary.json') as f:
    mainland = json.load(f)['mainland']

def offset_curve(pts, offset_km=25.0):
    n = len(pts)
    inward_pts = []
    for i in range(n):
        p_prev = pts[max(0, i-1)]
        p_curr = pts[i]
        p_next = pts[min(n-1, i+1)]
        
        lat_rad = math.radians(p_curr[1])
        m_per_deg_lat = 111139.0
        m_per_deg_lon = max(1000.0, 111139.0 * math.cos(lat_rad))
        
        dx = (p_next[0] - p_prev[0]) * m_per_deg_lon
        dy = (p_next[1] - p_prev[1]) * m_per_deg_lat
        length = math.hypot(dx, dy)
        if length == 0:
            nx, ny = 0, 0
        else:
            nx = -dy / length
            ny = dx / length
            
        offset_m = offset_km * 1000.0
        new_lon = p_curr[0] + (nx * offset_m) / m_per_deg_lon
        new_lat = p_curr[1] + (ny * offset_m) / m_per_deg_lat
        inward_pts.append([round(new_lon, 4), round(new_lat, 4)])
        
    return pts + list(reversed(inward_pts)) + [pts[0]]

# Milestone indices verified:
# Sir Creek: 1354 -> Pathankot: 1470
# Pathankot: 1470 -> 1581 + 0 -> HP Tripoint: 80
# HP Tripoint: 80 -> Kalapani: 126
# Kalapani: 126 -> Sikkim West: 229
# Sikkim West: 229 -> Sikkim East: 250
# Sikkim East: 250 -> Bhutan East: 284
# Bhutan East: 284 -> Arunachal Tri: 363
# Arunachal Tri: 363 -> Mizoram South: 452
# Mizoram South: 452 -> Sundarbans: 695

corridors = {}

# 1. Western IB (Gujarat, Rajasthan, Punjab to Pathankot)
west_ib_pts = mainland[1354:1471]
corridors["west_ib"] = offset_curve(west_ib_pts)

# 2. Northern J&K and Ladakh (Kathua/Pathankot, Jammu, LoC, Gilgit, Hunza, K2, Aksai Chin, Demchok to HP)
north_jk_pts = mainland[1470:] + mainland[:81]
corridors["north_jk_ladakh"] = offset_curve(north_jk_pts)

# 3. Middle Sector LAC (HP & Uttarakhand Tibet border)
middle_lac_pts = mainland[80:127]
corridors["middle_lac"] = offset_curve(middle_lac_pts)

# 4. Nepal border (Uttarakhand, UP, Bihar, WB to West Sikkim)
nepal_pts = mainland[126:230]
corridors["nepal"] = offset_curve(nepal_pts)

# 5. Sikkim (wrapping Sikkim's sovereign perimeter)
sikkim_pts = mainland[229:251]
corridors["sikkim"] = offset_curve(sikkim_pts)

# 6. Bhutan border (along entire southern border of Bhutan)
bhutan_pts = mainland[250:285]
corridors["bhutan"] = offset_curve(bhutan_pts)

# 7. Arunachal McMahon Line (Tibet border)
mcmahon_pts = mainland[284:364]
corridors["mcmahon"] = offset_curve(mcmahon_pts)

# 8. Myanmar border (Arunachal, Nagaland, Manipur, Mizoram)
myanmar_pts = mainland[363:453]
corridors["myanmar"] = offset_curve(myanmar_pts)

# 9. Bangladesh border (Mizoram, Tripura, Meghalaya, Assam, West Bengal)
bangladesh_pts = mainland[452:696]
corridors["bangladesh"] = offset_curve(bangladesh_pts)

with open('telemetry/data/border_corridors.json', 'w') as f:
    json.dump(corridors, f)

print("Successfully generated all 9 continuous 25 km statutory border ribbons.")
for k, v in corridors.items():
    print(f"  {k}: {len(v)} coordinates")
