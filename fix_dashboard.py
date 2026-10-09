import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Clear simulator trail when clearing simulator markers
content = content.replace('if (m.circle) map.removeLayer(m.circle);', 'if (m.circle) map.removeLayer(m.circle);\n                if (m.path) map.removeLayer(m.path);')

# Fix 2: Recreate droneMarker if null in updateDroneUI
recreate_drone_marker = """
        // Update Drone Marker Position & Rotator
        if (!droneMarker) {
            droneMarker = L.marker([lat, lon], {
                icon: createDroneIcon(hdg),
                title: 'Drone 01 (Cube Orange+ / ESP32)',
                zIndexOffset: 1000
            });
            droneMarker.bindPopup(`
                <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                    <strong style="color: #0284c7;">Drone 01 — Cube Orange+</strong><br>
                    <span>Target: ESP32 Wi-Fi Telemetry</span>
                </div>
            `);
            if (activeMode === 'drone') {
                droneMarker.addTo(map);
                activeMarker = droneMarker;
            }
        }
        
        if (droneMarker) {
"""
content = content.replace('// Update Drone Marker Position & Rotator\n        if (droneMarker) {', recreate_drone_marker)

# Also ensure it is visible when switching to drone mode in setDashboardMode
# Wait, if they just switch to drone mode and the drone hasn't received telemetry, updateDroneUI might not have fired yet.
# In setDashboardMode:
ensure_drone_marker_visible = """
            if (!droneMarker) {
                droneMarker = L.marker([lastKnownLat || 30.9010, lastKnownLon || 75.8573], {
                    icon: createDroneIcon(lastKnownHeading || 0),
                    title: 'Drone 01 (Cube Orange+ / ESP32)',
                    zIndexOffset: 1000
                });
                droneMarker.bindPopup(`
                    <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                        <strong style="color: #0284c7;">Drone 01 — Cube Orange+</strong><br>
                        <span>Target: ESP32 Wi-Fi Telemetry</span>
                    </div>
                `);
            }
            if (droneMarker) {
"""
content = content.replace('// Switch markers\n            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);\n            if (droneMarker) {', '// Switch markers\n            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);\n' + ensure_drone_marker_visible)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Dashboard.js fixed.")
