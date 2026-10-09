import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

center_old = """    function centerCurrentMarker() {
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

center_new = """    function centerCurrentMarker() {
        if (!map) return;
        if (activeMode === 'main') {
            if (activeTelemetryTargetId && mainModeMarkers[activeTelemetryTargetId]) {
                map.panTo(mainModeMarkers[activeTelemetryTargetId].getLatLng(), { animate: true, duration: 0.8 });
            }
        } else if (activeMode === 'simulator') {
            if (activeTelemetryTargetId && typeof simulatorState !== 'undefined' && simulatorState.markers) {
                let d = simulatorState.markers.find(m => m.id === activeTelemetryTargetId);
                if (d && d.marker) {
                    map.panTo(d.marker.getLatLng(), { animate: true, duration: 0.8 });
                }
            }
        } else {
            if (activeMarker) {
                map.panTo(activeMarker.getLatLng(), { animate: true, duration: 0.8 });
            }
        }
    }"""

if center_old in content:
    content = content.replace(center_old, center_new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated centerCurrentMarker logic to center on the last clicked drone")
else:
    print("Could not find centerCurrentMarker block to replace")
