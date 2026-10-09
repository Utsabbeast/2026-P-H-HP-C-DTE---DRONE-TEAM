import os

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Elements cache
if 'mapStatsContainer: document.getElementById(\'mapStatsContainer\'),' not in content:
    content = content.replace(
        'testerPanel: document.getElementById(\'testerPanel\'),',
        '''mapStatsContainer: document.getElementById('mapStatsContainer'),
        valRegisteredDrones: document.getElementById('valRegisteredDrones'),
        valDronesInAir: document.getElementById('valDronesInAir'),
        testerPanel: document.getElementById('testerPanel'),'''
    )

# 2. Main Mode Stats logic (set Dashboard Mode)
content = content.replace(
    'if (elements.mapMainTitle) elements.mapMainTitle.textContent = \'Main Mode (Overview)\';',
    '''if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Main Mode (Overview)';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                elements.valDronesInAir.textContent = elements.valDronesInAir.getAttribute('data-original') || '0';
            }'''
)

# 3. Phone Mode Stats logic
content = content.replace(
    'if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = \'none\';',
    '''if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'none';'''
)

# 4. Sim Mode Stats logic
content = content.replace(
    'if (elements.esp32Banner) elements.esp32Banner.style.display = \'none\';',
    '''if (elements.esp32Banner) elements.esp32Banner.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                // the simulation polling will update drones in air if needed
            }'''
)

# 5. Drone Mode Stats logic
content = content.replace(
    'if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = \'Drone Telemetry & Hardware Overview\';',
    '''if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Drone Telemetry & Hardware Overview';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valDronesInAir) elements.valDronesInAir.textContent = '1';
            if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = '1';'''
)

# 6. Map Click logic (reset activeTelemetryTargetId)
content = content.replace(
    '''map.on('click', function(e) {
        activeMarker = null;
        resetTelemetryUI();
    });''',
    '''map.on('click', function(e) {
        activeMarker = null;
        activeTelemetryTargetId = null;
        resetTelemetryUI();
    });'''
)

# 7. updateDroneUI ignore if unselected
# We only want to block updating if they deselected the drone.
# In Drone Mode, there is only one drone. activeMarker = droneMarker is set when we select it, but if activeMarker is null, we shouldn't update the UI.
target_update_drone = '''updateTelemetryCards(telemetryData);
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;'''

replacement_update_drone = '''if (activeMarker !== null) {
            updateTelemetryCards(telemetryData);
            if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        }'''
content = content.replace(target_update_drone, replacement_update_drone)

# 8. updatePhoneUI ignore if unselected
target_update_phone = '''if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;'''
replacement_update_phone = '''if (activeMarker !== null) {
            if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        }'''
content = content.replace(target_update_phone, replacement_update_phone)

# Wait, in updatePhoneUI, I need to wrap all the UI updates. Let's do it cleanly:
target_phone_ui_block = '''// 2. Update Map HUD Overlay
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.hudHdg) elements.hudHdg.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.hudSpeed) elements.hudSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : 'N/A';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = accuracy !== null ? `${accuracy.toFixed(1)} m` : 'N/A';'''

replacement_phone_ui_block = '''// 2. Update Map HUD Overlay
        if (activeMarker === null) return; // Don't update HUD or Cards if user deselected map
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.hudHdg) elements.hudHdg.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.hudSpeed) elements.hudSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : 'N/A';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = accuracy !== null ? `${accuracy.toFixed(1)} m` : 'N/A';'''

content = content.replace(target_phone_ui_block, replacement_phone_ui_block)

target_drone_ui_block = '''// Update Map HUD
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }'''

replacement_drone_ui_block = '''// Update Map HUD
        if (activeMarker === null) return; // Don't update HUD or Cards if user deselected map
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }'''

content = content.replace(target_drone_ui_block, replacement_drone_ui_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dashboard.js logic")
