import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

# 1. Add mainModeMarkers dict
if 'let mainModeMarkers = {};' not in content:
    content = content.replace('let phoneMarker = null;', 'let phoneMarker = null;\n    let mainModeMarkers = {};')

# 2. Update selectMod to clear and hide things
if 'if (mode !== \'main\') {' not in content:
    old_selectMod = """        if (mode === 'main') {
            if (mapTitle) mapTitle.innerText = "Main Mode (Overview)";
            if (mapRoute) mapRoute.innerText = "Overview";
        } else if (mode === 'simulator') {"""
    
    new_selectMod = """        if (mode !== 'main') {
            for (let id in mainModeMarkers) {
                if (map.hasLayer(mainModeMarkers[id])) map.removeLayer(mainModeMarkers[id]);
            }
        }
        
        if (mode === 'main') {
            if (mapTitle) mapTitle.innerText = "Main Mode (Overview)";
            if (mapRoute) mapRoute.innerText = "Overview";
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);
            if (movementTrail) movementTrail.setLatLngs([]);
        } else if (mode === 'simulator') {"""
    content = content.replace(old_selectMod, new_selectMod)

# 3. Update fetchActiveTelemetry
old_fetch = """    async function fetchActiveTelemetry() {
        if (activeMode === 'simulator') {
            updateConnectionStatus(true, 0);
            return;
        }
        if (activeMode === 'phone') {
            await fetchPhoneTelemetry();
        } else {
            await fetchDroneTelemetry();
        }
    }"""
new_fetch = """    async function fetchActiveTelemetry() {
        if (activeMode === 'simulator') {
            updateConnectionStatus(true, 0);
            return;
        }
        if (activeMode === 'main') {
            await fetchMainModeDrones();
            return;
        }
        if (activeMode === 'phone') {
            await fetchPhoneTelemetry();
        } else {
            await fetchDroneTelemetry();
        }
    }

    async function fetchMainModeDrones() {
        try {
            const response = await fetch('/api/drones/all/');
            if (!response.ok) return;
            const data = await response.json();
            if (data.status === 'success' && data.results) {
                const currentIds = data.results.map(d => d.drone_id);
                for (let id in mainModeMarkers) {
                    if (!currentIds.includes(id)) {
                        map.removeLayer(mainModeMarkers[id]);
                        delete mainModeMarkers[id];
                    }
                }
                
                data.results.forEach(telemetry => {
                    const id = telemetry.drone_id;
                    const latlng = [telemetry.latitude, telemetry.longitude];
                    
                    if (!mainModeMarkers[id]) {
                        mainModeMarkers[id] = L.marker(latlng, {
                            icon: L.divIcon({
                                className: 'drone-marker',
                                html: `<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#0ea5e9" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,
                                iconSize: [30, 30],
                                iconAnchor: [15, 15]
                            })
                        }).addTo(map).bindPopup(`<b>Drone ID:</b> ${id}<br><b>Alt:</b> ${telemetry.altitude}m`);
                    } else {
                        mainModeMarkers[id].setLatLng(latlng);
                    }
                });
            }
        } catch (e) {
            console.warn('[UTM] Main Mode Drones error:', e);
        }
    }"""
content = content.replace(old_fetch, new_fetch)

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Updated dashboard.js")
