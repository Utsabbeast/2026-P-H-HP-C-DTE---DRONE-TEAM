import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# For Phone Mode, look for the block starting with overviewHeaderTitle and ending with statusHwPacketsHint
# and replace it.
phone_block = re.search(r'if \(elements\.overviewHeaderTitle\).*?Phone GPS Telemetry Overview.*?\n.*?(?=\} else if \(activeMode === \'simulator\')', content, re.DOTALL)
if phone_block:
    replacement = '''if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Phone GPS Telemetry Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Android Phone';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Temporary test replacement';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Android Device GPS API';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Tested via Mobile Web';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Device: ${targetPhoneDeviceId}`;
        '''
    content = content[:phone_block.start()] + replacement + content[phone_block.end():]

# For Simulator Mode
sim_block = re.search(r'if \(elements\.statusFeedText\) elements\.statusFeedText\.textContent = \'ESP32 Wi-Fi\';\n.*?(?=\} else if \(activeMode === \'drone\')', content, re.DOTALL)
if sim_block:
    replacement = '''if (elements.statusFeedText) elements.statusFeedText.textContent = 'Simulation Engine';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Local Python Script';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Software In The Loop (SITL)';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Virtual hardware simulation';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`;
        '''
    content = content[:sim_block.start()] + replacement + content[sim_block.end():]

# For Drone Mode
drone_block = re.search(r'if \(elements\.testModeBadge\) elements\.testModeBadge\.style\.display = \'inline-flex\';\n\s*elements\.modeBadgeText\.textContent = \'Live Hardware Stream \(ESP32\)\';\n\s*elements\.gpsSourceText\.textContent = \'GPS Source: ESP32 / Cube Orange\+\';', content)
if drone_block:
    # insert the status stuff right after this block
    insert_str = '''
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Drone Telemetry & Hardware Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'ESP32 Wi-Fi';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Cube Orange+ Telem (UART2)';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Cube Orange+ → ESP32 → Wi-Fi';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Direct Hardware Stream';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`;
'''
    content = content[:drone_block.end()] + insert_str + content[drone_block.end():]

# For Main Mode
main_block = re.search(r'if \(elements\.mapMainTitle\) elements\.mapMainTitle\.textContent = \'Main Mode \(Overview\)\';', content)
if main_block:
    insert_str = '''
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'UTM Network Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Aggregated DB';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'All active drones';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Multi-Drone Network';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Cloud Database Aggregation';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = 'Network Traffic';
'''
    # Wait, in main mode we need to find exactly where to insert.
    # I'll just append it to the mapRouteHud style block.

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated via re")
