import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

old_sim = """        SIM_DRONES.forEach((d, index) => {
            let lat = startLat + (Math.random() - 0.5) * 0.02;
            let lng = startLng + (Math.random() - 0.5) * 0.02;
            let marker = L.marker([lat, lng], {
                icon: createSimulatorIcon(d.color),
                title: d.desc
            }).addTo(map);
            
            let droneInfo = {
                name: d.name + ' Drone',
                uin: 'SIM-' + (index + 1000),
                owner: 'Simulated Entity',
                purpose: d.desc.split(': ')[1] || d.desc,
                duration: 'Simulator Lifetime',
                status: 'SIMULATED',
                color: d.color
            };
            
            marker.bindPopup(generateDronePopup(droneInfo));
            marker.on('click', function() {
                activeTelemetryTargetId = 'sim_' + index;
            });
            
            simulatorState.markers.push({
                id: 'sim_' + index,
                marker: marker,
                lat: lat,
                lng: lng,
                targetLat: lat,
                targetLng: lng,
                heading: 0,
                speed: 0
            });
        });"""

new_sim = """        SIM_DRONES.forEach((d, index) => {
            let lat = startLat + (Math.random() - 0.5) * 0.02;
            let lng = startLng + (Math.random() - 0.5) * 0.02;
            let marker = L.marker([lat, lng], {
                icon: createSimulatorIcon(d.color),
                title: d.desc
            }).addTo(map);
            
            let path = L.polyline([[lat, lng]], { color: d.color, weight: 3, opacity: 0.7, dashArray: '5, 5' }).addTo(map);
            
            let droneInfo = {
                name: d.name + ' Drone',
                uin: 'SIM-' + (index + 1000),
                owner: 'Simulated Entity',
                purpose: d.desc.split(': ')[1] || d.desc,
                duration: 'Simulator Lifetime',
                status: 'SIMULATED',
                color: d.color
            };
            
            marker.bindPopup(generateDronePopup(droneInfo));
            marker.on('click', function() {
                activeTelemetryTargetId = 'sim_' + index;
            });
            
            simulatorState.markers.push({
                id: 'sim_' + index,
                marker: marker,
                path: path,
                pathCoords: [[lat, lng]],
                lat: lat,
                lng: lng,
                targetLat: lat,
                targetLng: lng,
                heading: 0,
                speed: 0
            });
        });"""
content = content.replace(old_sim, new_sim)


old_sim_interval = """                let oldLat = d.lat;
                let oldLng = d.lng;
                
                d.lat += (d.targetLat - d.lat) * 0.1;
                d.lng += (d.targetLng - d.lng) * 0.1;
                
                d.marker.setLatLng([d.lat, d.lng]);"""
new_sim_interval = """                let oldLat = d.lat;
                let oldLng = d.lng;
                
                d.lat += (d.targetLat - d.lat) * 0.1;
                d.lng += (d.targetLng - d.lng) * 0.1;
                
                d.marker.setLatLng([d.lat, d.lng]);
                
                if (Math.abs(d.lat - oldLat) > 0.00001 || Math.abs(d.lng - oldLng) > 0.00001) {
                    d.pathCoords.push([d.lat, d.lng]);
                    if (d.pathCoords.length > 100) d.pathCoords.shift();
                    d.path.setLatLngs(d.pathCoords);
                }"""
content = content.replace(old_sim_interval, new_sim_interval)

old_sim_stop = """        simulatorState.markers.forEach(d => {
            map.removeLayer(d.marker);
        });"""
new_sim_stop = """        simulatorState.markers.forEach(d => {
            map.removeLayer(d.marker);
            if (d.path) map.removeLayer(d.path);
        });"""
content = content.replace(old_sim_stop, new_sim_stop)

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Updated simulator paths")
