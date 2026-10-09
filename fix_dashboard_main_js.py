import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

# 1. Change default mode to main
content = content.replace("let activeMode = 'phone';", "let activeMode = 'main';")

# 2. Fix startup marker
old_startup = """        // Default marker on startup is Phone Marker
        phoneMarker.addTo(map);
        activeMarker = phoneMarker;"""
new_startup = """        // Default marker on startup
        if (activeMode === 'phone') {
            phoneMarker.addTo(map);
            activeMarker = phoneMarker;
        }"""
content = content.replace(old_startup, new_startup)

# 3. Add 'main' to setDashboardMode
old_set_mode = """        if (activeMode === 'phone') {
            // Update Tab styles"""
new_set_mode = """        if (activeMode === 'main') {
            elements.tabPhoneMode.className = 'mode-tab';
            elements.tabDroneMode.className = 'mode-tab';
            
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);
            
            if (elements.testModeBadge) elements.testModeBadge.style.display = 'none';
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'none';
            
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Main Mode (Overview)';
            if (elements.mapRouteHud) {
                elements.mapRouteHud.textContent = 'Overview';
                elements.mapRouteHud.style.background = '#e0f2fe';
                elements.mapRouteHud.style.borderColor = '#bae6fd';
                elements.mapRouteHud.style.color = '#0369a1';
            }
        } else if (activeMode === 'phone') {
            // Update Tab styles"""
content = content.replace(old_set_mode, new_set_mode)

# 4. Remove phone from `selectMod` in dashboard.html? No, we already call `window.setDashboardMode('main')`.
# Actually `selectMod` is in dashboard.html and I missed calling `setDashboardMode`.

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Updated dashboard.js")
