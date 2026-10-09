import re

filepath = 'templates/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add ID to Registered Drones box
content = content.replace(
    '<div class="map-stat-box" style="background: #002D74; border: 2px solid #001A4A;" \ntitle="Registered Drones">',
    '<div class="map-stat-box" id="statRegisteredDronesBox" style="background: #002D74; border: 2px solid #001A4A;" \ntitle="Registered Drones">'
)

content = content.replace(
    '<div class="map-stat-box" style="background: #002D74; border: 2px solid #001A4A;" title="Registered Drones">',
    '<div class="map-stat-box" id="statRegisteredDronesBox" style="background: #002D74; border: 2px solid #001A4A;" title="Registered Drones">'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added id statRegisteredDronesBox to dashboard.html")
