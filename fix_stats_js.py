import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add element to elements object
element_insertion = "valRegisteredDrones: document.getElementById('valRegisteredDrones'),"
if "statRegisteredDronesBox:" not in content:
    content = content.replace(element_insertion, "statRegisteredDronesBox: document.getElementById('statRegisteredDronesBox'),\n          " + element_insertion)

# 2. Add visibility logic to setDashboardMode
set_mode_func = "function setDashboardMode(newMode) {\n        if (activeMode === newMode) return;\n        activeMode = newMode;\n"
if "elements.statRegisteredDronesBox.style.display" not in content:
    proper_logic = """
        // Handle Registered Drones Box visibility
        if (elements.statRegisteredDronesBox) {
            elements.statRegisteredDronesBox.style.display = (newMode === 'simulator') ? 'none' : 'flex';
        }
"""
    content = content.replace(set_mode_func, set_mode_func + proper_logic)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dashboard.js statRegisteredDronesBox logic.")
