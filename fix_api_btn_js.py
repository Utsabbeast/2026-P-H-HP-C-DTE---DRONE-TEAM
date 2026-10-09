import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove all existing instances of the button/panel toggling
content = re.sub(r'if \(elements\.btnToggleTester\) elements\.btnToggleTester\.style\.display = \'none\';\n*', '', content)
content = re.sub(r'if \(elements\.btnToggleTester\) elements\.btnToggleTester\.style\.display = \'flex\';\n*', '', content)
content = re.sub(r'if \(elements\.testerPanel\) elements\.testerPanel\.style\.display = \'none\';\n*', '', content)

# 2. Insert properly at the very beginning of setDashboardMode
set_mode_func = "function setDashboardMode(newMode) {\n        if (activeMode === newMode) return;\n        activeMode = newMode;\n"
if set_mode_func in content:
    proper_logic = """
        // Always hide API tools and panel when changing modes, only show for drone
        if (elements.btnToggleTester) elements.btnToggleTester.style.display = (newMode === 'drone') ? 'flex' : 'none';
        if (elements.testerPanel) elements.testerPanel.style.display = 'none';

"""
    content = content.replace(set_mode_func, set_mode_func + proper_logic)
else:
    print("Could not find setDashboardMode definition.")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated dashboard.js API button logic.")
