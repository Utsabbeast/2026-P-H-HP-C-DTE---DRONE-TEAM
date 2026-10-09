import os

filepath = 'templates/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace map-stats-container
content = content.replace(
    '<div class="map-stats-container"',
    '<div id="mapStatsContainer" class="map-stats-container"'
)

# Add IDs to the value containers
content = content.replace(
    '''<div style="width: 36px; height: 36px; display: flex; justify-content: center; align-items: center; flex-shrink: 0; font-weight: bold; font-size: 1.1rem;">
                            {{ total_registered_drones|default:"0" }}
                        </div>''',
    '''<div id="valRegisteredDrones" style="width: 36px; height: 36px; display: flex; justify-content: center; align-items: center; flex-shrink: 0; font-weight: bold; font-size: 1.1rem;" data-original="{{ total_registered_drones|default:'0' }}">
                            {{ total_registered_drones|default:"0" }}
                        </div>'''
)

content = content.replace(
    '''<div style="width: 36px; height: 36px; display: flex; justify-content: center; align-items: center; flex-shrink: 0; font-weight: bold; font-size: 1.1rem;">
                            {{ total_flying_drones|default:"0" }}
                        </div>''',
    '''<div id="valDronesInAir" style="width: 36px; height: 36px; display: flex; justify-content: center; align-items: center; flex-shrink: 0; font-weight: bold; font-size: 1.1rem;" data-original="{{ total_flying_drones|default:'0' }}">
                            {{ total_flying_drones|default:"0" }}
                        </div>'''
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dashboard.html with IDs")
