import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

center_old = """    function centerCurrentMarker() {
        if (map && activeMarker) {
            const pos = activeMarker.getLatLng();
            map.panTo(pos, { animate: true, duration: 0.8 });
        }
    }"""
center_new = """    function centerCurrentMarker() {
        if (!map) return;
        if (activeMode === 'main') {
            if (mainModeMarkers.length > 0) {
                const group = new L.featureGroup(mainModeMarkers.map(m => m.marker));
                map.fitBounds(group.getBounds(), { padding: [20, 20], animate: true });
            }
        } else if (activeMode === 'simulator') {
            if (typeof simulatorState !== 'undefined' && simulatorState.markers && simulatorState.markers.length > 0) {
                const group = new L.featureGroup(simulatorState.markers.map(m => m.marker));
                map.fitBounds(group.getBounds(), { padding: [20, 20], animate: true });
            }
        } else {
            if (activeMarker) {
                const pos = activeMarker.getLatLng();
                map.panTo(pos, { animate: true, duration: 0.8 });
            }
        }
    }"""
content = content.replace(center_old, center_new)

clear_old = """    function clearMovementTrail() {
        // Clear visually from map and memory immediately; DO NOT delete database records!
        trailCoordinates = [];
        if (activeMarker) {
            // Start recording new trail from current location
            const curPos = activeMarker.getLatLng();
            trailCoordinates.push([curPos.lat, curPos.lng]);
        }
        if (movementTrail) {
            movementTrail.setLatLngs(trailCoordinates);
        }
        console.log('[UTM] Movement trail cleared visually.');
    }"""
clear_new = """    function clearMovementTrail() {
        if (activeMode === 'simulator') {
            if (typeof simulatorState !== 'undefined' && simulatorState.markers) {
                simulatorState.markers.forEach(d => {
                    d.pathCoords = [[d.lat, d.lng]];
                    d.path.setLatLngs(d.pathCoords);
                });
            }
        } else {
            trailCoordinates = [];
            if (activeMarker) {
                const curPos = activeMarker.getLatLng();
                trailCoordinates.push([curPos.lat, curPos.lng]);
            }
            if (movementTrail) {
                movementTrail.setLatLngs(trailCoordinates);
            }
        }
        console.log('[UTM] Movement trail cleared visually.');
    }"""
content = content.replace(clear_old, clear_new)

toggle_old = """    function toggleTrailVisibility() {
        isTrailVisible = !isTrailVisible;
        if (isTrailVisible) {
            if (movementTrail) map.addLayer(movementTrail);
            if (elements.trailButtonText) elements.trailButtonText.textContent = 'Hide Trail';
        } else {
            if (movementTrail) map.removeLayer(movementTrail);
            if (elements.trailButtonText) elements.trailButtonText.textContent = 'Show Trail';
        }
    }"""
toggle_new = """    function toggleTrailVisibility() {
        isTrailVisible = !isTrailVisible;
        if (activeMode === 'simulator') {
            if (typeof simulatorState !== 'undefined' && simulatorState.markers) {
                simulatorState.markers.forEach(d => {
                    if (isTrailVisible) {
                        map.addLayer(d.path);
                    } else {
                        map.removeLayer(d.path);
                    }
                });
            }
        } else {
            if (isTrailVisible) {
                if (movementTrail) map.addLayer(movementTrail);
            } else {
                if (movementTrail) map.removeLayer(movementTrail);
            }
        }
        if (elements.trailButtonText) {
            elements.trailButtonText.textContent = isTrailVisible ? 'Hide Trail' : 'Show Trail';
        }
    }"""
content = content.replace(toggle_old, toggle_new)

reset_old = """    function resetMapView() {
        if (map) {
            map.setView([lastKnownLat, lastKnownLon], 16, { animate: true });
        }
    }"""
reset_new = """    function resetMapView() {
        if (!map) return;
        let zoom = (activeMode === 'main' || activeMode === 'simulator') ? 5 : 16;
        if (lastKnownLat && lastKnownLon) {
            map.setView([lastKnownLat, lastKnownLon], zoom, { animate: true });
        } else {
            map.setView([28.6139, 77.2090], zoom, { animate: true });
        }
    }"""
content = content.replace(reset_old, reset_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated the 4 map action controls in dashboard.js")
