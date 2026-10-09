import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add logic to update valDronesInAir after simulator initialization
target = "map.setView([startLat, startLng], 14, {animate: true});"
replacement = """map.setView([startLat, startLng], 14, {animate: true});

        if (elements.valDronesInAir) {
            elements.valDronesInAir.textContent = simulatorState.markers.length;
        }"""

if target in content:
    content = content.replace(target, replacement)

# We also need to remove any place in setDashboardMode where simulator overrides valDronesInAir to original, if any.
# Let's see if we need to remove that.
# In setDashboardMode:
# if (elements.valRegisteredDrones && elements.valDronesInAir) {
#      if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
#      // the simulation polling will update drones in air if needed
# }
# Since it doesn't touch valDronesInAir in the simulator block (except for the comment), we don't need to change setDashboardMode.

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated simulator drone count logic")
