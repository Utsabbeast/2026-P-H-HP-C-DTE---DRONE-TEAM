import os

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Main mode
main_mode_target = '''if (elements.mapRouteHud) {
                elements.mapRouteHud.textContent = 'Overview';
                elements.mapRouteHud.style.background = '#e0f2fe';
                elements.mapRouteHud.style.borderColor = '#bae6fd';
                elements.mapRouteHud.style.color = '#0369a1';
            }'''

main_mode_replace = '''if (elements.mapRouteHud) {
                elements.mapRouteHud.textContent = 'Overview';
                elements.mapRouteHud.style.background = '#e0f2fe';
                elements.mapRouteHud.style.borderColor = '#bae6fd';
                elements.mapRouteHud.style.color = '#0369a1';
            }
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'UTM Network Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Aggregated DB';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'All connected active drones';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Multi-Drone Network';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Cloud Database Aggregation';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = 'Network Traffic';'''
            
content = content.replace(main_mode_target, main_mode_replace)

# 2. Phone Mode
# Phone mode currently has:
phone_mode_target = '''if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Phone GPS Telemetry Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Android Phone';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Temporary test replacement';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Cube Orange+ +' ESP32 +' Wi-Fi';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Currently tested via Phone GPS';'''

phone_mode_replace = '''if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Phone GPS Telemetry Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Android Phone';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Temporary test replacement';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Android Device GPS';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Tested via Mobile Web API';'''
content = content.replace(phone_mode_target, phone_mode_replace)

# Wait, 'Cube Orange+ +' ESP32 +' Wi-Fi' might be corrupt character encoding. Let me just use replace directly for the whole block if possible.
# Actually I will use regex or careful strings.
