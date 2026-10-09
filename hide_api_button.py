import os
import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add display:none to Phone Mode
phone_block = re.search(r'if \(elements\.hardwareOfflineAlert\) elements\.hardwareOfflineAlert\.style\.display = \'none\';\s*if \(elements\.mapStatsContainer\) elements\.mapStatsContainer\.style\.display = \'none\';', content)
if phone_block:
    insert_str = '''
            if (elements.btnToggleTester) elements.btnToggleTester.style.display = 'none';
            if (elements.testerPanel) elements.testerPanel.style.display = 'none';
'''
    content = content[:phone_block.end()] + insert_str + content[phone_block.end():]

# Add display:none to Simulator Mode
sim_block = re.search(r'if \(elements\.statusHwPacketsHint\) elements\.statusHwPacketsHint\.textContent = `Target: \$\{targetDroneId\}`;', content)
if sim_block:
    # Need to check we are in the simulator block. The above matches the end of the simulator block.
    insert_str = '''
            if (elements.btnToggleTester) elements.btnToggleTester.style.display = 'none';
            if (elements.testerPanel) elements.testerPanel.style.display = 'none';
'''
    content = content[:sim_block.end()] + insert_str + content[sim_block.end():]

# Add display:none to Main Mode
main_block = re.search(r'if \(elements\.statusHwPacketsHint\) elements\.statusHwPacketsHint\.textContent = \'Network Traffic\';', content)
if main_block:
    insert_str = '''
            if (elements.btnToggleTester) elements.btnToggleTester.style.display = 'none';
            if (elements.testerPanel) elements.testerPanel.style.display = 'none';
'''
    content = content[:main_block.end()] + insert_str + content[main_block.end():]


# Add display:flex to Drone Mode
# Look for: if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`; inside the drone block.
# Wait, the same line exists in both drone and sim modes.
# I will use a different anchor for drone mode:
drone_anchor = re.search(r'if \(elements\.statusRouteHint\) elements\.statusRouteHint\.textContent = \'Direct Hardware Stream\';\s*if \(elements\.statusHwPacketsHint\) elements\.statusHwPacketsHint\.textContent = `Target: \$\{targetDroneId\}`;', content)
if drone_anchor:
    insert_str = '''
            if (elements.btnToggleTester) elements.btnToggleTester.style.display = 'flex';
'''
    content = content[:drone_anchor.end()] + insert_str + content[drone_anchor.end():]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated API button visibility")
