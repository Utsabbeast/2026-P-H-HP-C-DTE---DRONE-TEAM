import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

old_popup = "`<b>Drone ID:</b> ${id}<br><b>Alt:</b> ${telemetry.altitude}m`"
new_popup = "`<b>Drone ID:</b> ${id}<br><b>Lat:</b> ${telemetry.latitude}°<br><b>Lon:</b> ${telemetry.longitude}°<br><b>Alt:</b> ${telemetry.altitude}m<br><b>Speed:</b> ${telemetry.speed}m/s<br><b>Heading:</b> ${telemetry.heading}°`"

content = content.replace(old_popup, new_popup)

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)

print("Updated popup in dashboard.js")
