import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

# Remove setPopupContent from updateDroneUI
old_drone_ui_popup = """            droneMarker.setPopupContent(`
                <div style="font-family: inherit; font-size: 13px; line-height: 1.5; min-width: 170px;">
                    <strong style="color: #0284c7;">🛰️ Drone (${telemetryData.drone_id || telemetryData.id || 'DRONE-ALPHA'})</strong><br>
                    <span>Lat: <strong>${lat.toFixed(6)}°</strong></span><br>
                    <span>Lon: <strong>${lon.toFixed(6)}°</strong></span><br>
                    <span>Alt: <strong>${alt.toFixed(1)} m</strong></span><br>
                    <span>Heading: <strong>${Math.round(hdg)}° (${headingToCardinal(hdg)})</strong></span>
                </div>
            `);"""

content = content.replace(old_drone_ui_popup, "")

# The user mentioned: "and the same you have to remove from the simulation mode is... no where just do this much."
# This confirms the previous fix where I removed phoneMarker from simulator was partially what they wanted, or they were noting it.
# They said "it will be showing the drone here not the phone"
# Wait! In dashboard.html there's an HTML element for the test mode badge.
# Let's ensure the dropdown in dashboard.html updates if we auto-switch.
# Actually, I'll just remove the auto-switch from dashboard.js or ensure the dropdown is updated.
# Let's leave the auto-switch as is, but make sure phoneMarker is really removed.
# Wait, look at fetchPhoneTelemetry:
#             if (phoneMarker) {
#                 phoneMarker.setLatLng([lat, lon]);
# What if phoneMarker is NOT on the map, but setLatLng is called? Leaflet doesn't throw an error, it just updates the coords.
# But wait! If phoneMarker was NOT removed from map?
# "if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);"
# This is safe and removes it.

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Removed drone popup overwrite")
