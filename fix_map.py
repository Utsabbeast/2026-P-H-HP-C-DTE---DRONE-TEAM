import re

with open('static/js/dashboard.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Change map init
old_map = '''    function initMap() {
        map = L.map('droneMap', {
            zoomControl: true,
            attributionControl: true,
            maxZoom: 22
        }).setView([lastKnownLat, lastKnownLon], 16);'''

new_map = '''    function initMap() {
        map = L.map('droneMap', {
            zoomControl: false, // We add it manually to position it
            attributionControl: true,
            maxZoom: 22
        }).setView([lastKnownLat, lastKnownLon], 16);
        
        // Add zoom control to topright
        L.control.zoom({ position: 'topright' }).addTo(map);'''

content = content.replace(old_map, new_map)

# Change layer control init
old_layer = '''        L.control.layers(baseMaps).addTo(map);'''
new_layer = '''        L.control.layers(baseMaps, null, { position: 'topright' }).addTo(map);'''

content = content.replace(old_layer, new_layer)

with open('static/js/dashboard.js', 'w', encoding='utf-8') as f:
    f.write(content)
