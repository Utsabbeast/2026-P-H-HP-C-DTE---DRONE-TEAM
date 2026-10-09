import os
import re

file_path = 'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/static/js/dashboard.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update clearMapHistory
old_clear = """    window.clearMapHistory = function() { 
        trailCoordinates = []; 
        if (movementTrail) movementTrail.setLatLngs([]); 
    };"""

new_clear = """    window.clearMapHistory = function() { 
        trailCoordinates = []; 
        if (movementTrail) movementTrail.setLatLngs([]); 
        
        // Clear all main mode markers
        for (let id in mainModeMarkers) {
            if (mainModeMarkers[id]) map.removeLayer(mainModeMarkers[id]);
        }
        mainModeMarkers = {};
        
        // Clear phone/drone marker
        if (droneMarker) {
            map.removeLayer(droneMarker);
            droneMarker = null;
        }
        
        // Clear simulator markers
        if (typeof simulatorState !== 'undefined' && simulatorState.markers) {
            simulatorState.markers.forEach(m => {
                if (m.marker) map.removeLayer(m.marker);
                if (m.circle) map.removeLayer(m.circle);
            });
            simulatorState.markers = [];
        }
        
        activeMarker = null;
        updateTelemetryUI({
            lat: '--', lng: '--', alt: '--', hdg: '--', speed: '--', accuracy: '--',
            timestamp: '--', battery: '--', status: '--', id: '--'
        });
    };"""

if old_clear in content:
    content = content.replace(old_clear, new_clear)

# 2. Add map click listener
map_click_listener = """    // Deselect marker and clear telemetry on map click
    map.on('click', function(e) {
        activeMarker = null;
        updateTelemetryUI({
            lat: '--', lng: '--', alt: '--', hdg: '--', speed: '--', accuracy: '--',
            timestamp: '--', battery: '--', status: '--', id: '--'
        });
    });"""

if "map.on('click'," not in content:
    content = content.replace("L.control.zoom({ position: 'topleft' }).addTo(map);", 
                              "L.control.zoom({ position: 'topleft' }).addTo(map);\n\n" + map_click_listener)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated dashboard.js with clearMapHistory and map click listener.")
