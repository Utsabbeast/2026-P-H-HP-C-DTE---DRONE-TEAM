import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

# 1. Add updateTelemetryCards and generateDronePopup at the top, just after formatTime
old_formatters = """    function formatTime(isoString) {
        if (!isoString) return '--:--:--';
        try {
            const d = new Date(isoString);
            return d.toLocaleTimeString('en-GB', { hour12: false });
        } catch (e) {
            return '--:--:--';
        }
    }"""

new_formatters = """    function formatTime(isoString) {
        if (!isoString) return '--:--:--';
        try {
            const d = new Date(isoString);
            return d.toLocaleTimeString('en-GB', { hour12: false });
        } catch (e) {
            return '--:--:--';
        }
    }

    let activeTelemetryTargetId = null;

    function updateTelemetryCards(telemetryData) {
        if (!telemetryData) return;
        const lat = parseFloat(telemetryData.latitude);
        const lon = parseFloat(telemetryData.longitude);
        const alt = telemetryData.altitude !== null && telemetryData.altitude !== undefined ? parseFloat(telemetryData.altitude) : null;
        const hdg = telemetryData.heading !== null && telemetryData.heading !== undefined ? parseFloat(telemetryData.heading) : null;
        const speed = telemetryData.speed !== null && telemetryData.speed !== undefined ? parseFloat(telemetryData.speed) : null;
        const accuracy = telemetryData.accuracy !== null && telemetryData.accuracy !== undefined ? parseFloat(telemetryData.accuracy) : null;
        
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.hudHdg) elements.hudHdg.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.hudSpeed) elements.hudSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : 'N/A';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = accuracy !== null ? `${accuracy.toFixed(1)} m` : 'N/A';

        if (elements.valLatitude) elements.valLatitude.textContent = `${lat.toFixed(6)}°`;
        if (elements.subLatitude) elements.subLatitude.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;

        if (elements.valLongitude) elements.valLongitude.textContent = `${lon.toFixed(6)}°`;
        if (elements.subLongitude) elements.subLongitude.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;

        if (elements.valAltitude) elements.valAltitude.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.subAltitude) elements.subAltitude.textContent = alt !== null ? 'GPS MSL Altitude' : 'Unavailable from sensor';

        if (elements.valHeading) elements.valHeading.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.subHeading) elements.subHeading.textContent = hdg !== null ? headingToCardinal(hdg) : 'Unavailable';
        if (elements.compassNeedle && hdg !== null) {
            elements.compassNeedle.style.transform = `rotate(${hdg}deg)`;
        }

        if (elements.valSpeed) elements.valSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : 'N/A';
        if (elements.subSpeed) elements.subSpeed.textContent = speed !== null ? `${(speed * 3.6).toFixed(1)} km/h` : 'Stationary or unavailable';

        if (elements.valAccuracy) {
            if (accuracy !== null) {
                if (accuracy > 100) {
                    elements.valAccuracy.innerHTML = `<span style="color: #ef4444; font-weight: 700;">${accuracy.toFixed(0)} m ⚠️</span>`;
                } else if (accuracy > 25) {
                    elements.valAccuracy.innerHTML = `<span style="color: #f59e0b; font-weight: 700;">${accuracy.toFixed(1)} m</span>`;
                } else {
                    elements.valAccuracy.textContent = `${accuracy.toFixed(1)} m`;
                }
            } else {
                elements.valAccuracy.textContent = 'N/A';
            }
        }
    }

    function generateDronePopup(d) {
        return `
        <div style="background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(8px); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.4); box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 260px; font-family: 'Outfit', sans-serif;">
            <div style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(0,0,0,0.1);">
                <div style="width: 12px; height: 12px; border-radius: 50%; background: ${d.color || '#0ea5e9'}; margin-right: 10px;"></div>
                <strong style="font-size: 1.1rem; color: #1e293b;">${d.name || 'Drone'}</strong>
            </div>
            <div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
                <p style="margin: 0 0 6px 0;"><b>UIN:</b> ${d.uin || 'UIN-DEFAULT-001'}</p>
                <p style="margin: 0 0 6px 0;"><b>Owner:</b> ${d.owner || 'SkyNav Systems'}</p>
                <p style="margin: 0 0 6px 0;"><b>Purpose:</b> ${d.purpose || 'Basic maneuvers'}</p>
                <p style="margin: 0 0 6px 0;"><b>Duration:</b> ${d.duration || '2 hrs 15 mins'}</p>
                <p style="margin: 0;"><b>Status:</b> <span style="color: #15803d; font-weight: 600;">${d.status || 'Active - Permitted'}</span></p>
            </div>
        </div>
        `;
    }"""
content = content.replace(old_formatters, new_formatters)

# 2. In fetchMainModeDrones, use new popup and click handler
old_main_mode_popup = """                        mainModeMarkers[id] = L.marker(latlng, {
                            icon: L.divIcon({
                                className: 'drone-marker',
                                html: `<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#0ea5e9" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,
                                iconSize: [30, 30],
                                iconAnchor: [15, 15]
                            })
                        }).addTo(map).bindPopup(`<b>Drone ID:</b> ${id}<br><b>Lat:</b> ${telemetry.latitude}°<br><b>Lon:</b> ${telemetry.longitude}°<br><b>Alt:</b> ${telemetry.altitude}m<br><b>Speed:</b> ${telemetry.speed}m/s<br><b>Heading:</b> ${telemetry.heading}°`);
                    } else {
                        mainModeMarkers[id].setLatLng(latlng);
                    }
                });"""

new_main_mode_popup = """                        mainModeMarkers[id] = L.marker(latlng, {
                            icon: L.divIcon({
                                className: 'drone-marker',
                                html: `<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#0ea5e9" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,
                                iconSize: [30, 30],
                                iconAnchor: [15, 15]
                            })
                        }).addTo(map);
                        
                        let droneInfo = {
                            name: 'ESP32 Hardware ' + id,
                            uin: 'IND-' + id,
                            owner: 'Live Tracking Pilot',
                            purpose: 'Hardware Flight Test',
                            duration: 'Live Stream',
                            status: 'ACTIVE',
                            color: '#0ea5e9'
                        };
                        
                        mainModeMarkers[id].bindPopup(generateDronePopup(droneInfo));
                        
                        mainModeMarkers[id].on('click', function() {
                            activeTelemetryTargetId = id;
                            updateTelemetryCards(telemetry);
                        });
                    } else {
                        mainModeMarkers[id].setLatLng(latlng);
                    }
                    
                    if (activeTelemetryTargetId === id) {
                        updateTelemetryCards(telemetry);
                    }
                });"""
content = content.replace(old_main_mode_popup, new_main_mode_popup)


# 3. Clean up updatePhoneUI
old_phone_ui_bottom = """        // 2. Update Map HUD Overlay
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.hudHdg) elements.hudHdg.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.hudSpeed) elements.hudSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : 'N/A';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = accuracy !== null ? `${accuracy.toFixed(1)} m` : 'N/A';

        // 3. Update All 7 Telemetry Cards (Display N/A if null, do not invent values)
        if (elements.valLatitude) elements.valLatitude.textContent = `${lat.toFixed(6)}°`;
        if (elements.subLatitude) elements.subLatitude.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;

        if (elements.valLongitude) elements.valLongitude.textContent = `${lon.toFixed(6)}°`;
        if (elements.subLongitude) elements.subLongitude.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;

        if (elements.valAltitude) elements.valAltitude.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.subAltitude) elements.subAltitude.textContent = alt !== null ? 'GPS MSL Altitude' : 'Unavailable from sensor';

        if (elements.valHeading) elements.valHeading.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.subHeading) elements.subHeading.textContent = hdg !== null ? headingToCardinal(hdg) : 'Unavailable';
        if (elements.compassNeedle && hdg !== null) {
            elements.compassNeedle.style.transform = `rotate(${hdg}deg)`;
        }

        if (elements.valSpeed) elements.valSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : 'N/A';
        if (elements.subSpeed) elements.subSpeed.textContent = speed !== null ? `${(speed * 3.6).toFixed(1)} km/h` : 'Stationary or unavailable';

        if (elements.valAccuracy) {
            if (accuracy !== null) {
                if (accuracy > 100) {
                    elements.valAccuracy.innerHTML = `<span style="color: #ef4444; font-weight: 700;">${accuracy.toFixed(0)} m ⚠️</span>`;
                } else if (accuracy > 25) {
                    elements.valAccuracy.innerHTML = `<span style="color: #f59e0b; font-weight: 700;">${accuracy.toFixed(1)} m</span>`;
                } else {
                    elements.valAccuracy.textContent = `${accuracy.toFixed(1)} m`;
                }
            } else {
                elements.valAccuracy.textContent = 'N/A';
            }
        }

        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        if (elements.subLastUpdate) elements.subLastUpdate.textContent = `Age: ${Math.floor(apiState.seconds_since_update)}s`;
    }"""

new_phone_ui_bottom = """        updateTelemetryCards(telemetryData);
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        if (elements.subLastUpdate) elements.subLastUpdate.textContent = `Age: ${Math.floor(apiState.seconds_since_update)}s`;
    }"""
content = content.replace(old_phone_ui_bottom, new_phone_ui_bottom)

# Also updateDroneUI uses similar things
old_drone_ui = """        // 2. Update Map HUD Overlay
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.hudHdg) elements.hudHdg.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.hudSpeed) elements.hudSpeed.textContent = 'N/A'; // Need to calculate diff or get from drone
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = 'N/A'; // Need HDOP from MAVLink

        // 3. Update Telemetry Cards
        if (elements.valLatitude) elements.valLatitude.textContent = `${lat.toFixed(6)}°`;
        if (elements.subLatitude) elements.subLatitude.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;

        if (elements.valLongitude) elements.valLongitude.textContent = `${lon.toFixed(6)}°`;
        if (elements.subLongitude) elements.subLongitude.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;

        if (elements.valAltitude) elements.valAltitude.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.subAltitude) elements.subAltitude.textContent = alt !== null ? 'Relative Altitude (AGL)' : 'Unavailable';

        if (elements.valHeading) elements.valHeading.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.subHeading) elements.subHeading.textContent = hdg !== null ? headingToCardinal(hdg) : 'Unavailable';
        if (elements.compassNeedle && hdg !== null) {
            elements.compassNeedle.style.transform = `rotate(${hdg}deg)`;
        }

        if (elements.valSpeed) elements.valSpeed.textContent = 'N/A';
        if (elements.subSpeed) elements.subSpeed.textContent = 'Stationary or unavailable';

        if (elements.valAccuracy) elements.valAccuracy.textContent = 'N/A';

        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        if (elements.subLastUpdate) {
            elements.subLastUpdate.textContent = apiState.seconds_since_update !== undefined ? `Age: ${Math.floor(apiState.seconds_since_update)}s` : 'Live Stream';
        }
    }"""
new_drone_ui = """        updateTelemetryCards(telemetryData);
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        if (elements.subLastUpdate) {
            elements.subLastUpdate.textContent = apiState.seconds_since_update !== undefined ? `Age: ${Math.floor(apiState.seconds_since_update)}s` : 'Live Stream';
        }
    }"""
content = content.replace(old_drone_ui, new_drone_ui)

# 4. Bind phone popup
phone_popup_str = """        phoneMarker.bindPopup('<strong style="color: #0369a1; font-family:\\'Outfit\\'">📱 Android Phone</strong><br>Simulating movement data');"""
new_phone_popup_str = """        let phoneInfo = {
            name: 'Test Phone Tracker',
            uin: 'PHONE-TEST-100',
            owner: 'System Tester',
            purpose: 'Dashboard GPS Testing',
            duration: 'Continuous',
            status: 'ACTIVE',
            color: '#10b981'
        };
        phoneMarker.bindPopup(generateDronePopup(phoneInfo));
        phoneMarker.on('click', function() {
            // We already call updateTelemetryCards globally for phone, but it's good to keep consistency
        });"""
content = content.replace(phone_popup_str, new_phone_popup_str)

# 5. Fix Simulator logic
old_sim = """        SIM_DRONES.forEach((d) => {
            let lat = startLat + (Math.random() - 0.5) * 0.02;
            let lng = startLng + (Math.random() - 0.5) * 0.02;
            let marker = L.marker([lat, lng], {
                icon: createSimulatorIcon(d.color),
                title: d.desc
            }).addTo(map);
            marker.bindPopup(`<strong style="color:${d.color}; font-family:'Outfit'">${d.name} Drone</strong><br>${d.desc}`);
            simulatorState.markers.push({
                marker: marker,
                lat: lat,
                lng: lng,
                targetLat: lat,
                targetLng: lng
            });
        });

        map.setView([startLat, startLng], 14, {animate: true});

        simulatorState.interval = setInterval(() => {
            simulatorState.markers.forEach(d => {
                if (Math.random() < 0.05) {
                    d.targetLat = d.lat + (Math.random() - 0.5) * 0.005;
                    d.targetLng = d.lng + (Math.random() - 0.5) * 0.005;
                }
                d.lat += (d.targetLat - d.lat) * 0.1;
                d.lng += (d.targetLng - d.lng) * 0.1;
                d.marker.setLatLng([d.lat, d.lng]);
            });
        }, 100);
    };"""

new_sim = """        SIM_DRONES.forEach((d, index) => {
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
        });

        map.setView([startLat, startLng], 14, {animate: true});

        simulatorState.interval = setInterval(() => {
            simulatorState.markers.forEach(d => {
                if (Math.random() < 0.05) {
                    d.targetLat = d.lat + (Math.random() - 0.5) * 0.005;
                    d.targetLng = d.lng + (Math.random() - 0.5) * 0.005;
                }
                
                let oldLat = d.lat;
                let oldLng = d.lng;
                
                d.lat += (d.targetLat - d.lat) * 0.1;
                d.lng += (d.targetLng - d.lng) * 0.1;
                
                d.marker.setLatLng([d.lat, d.lng]);
                
                // Calculate heading and speed roughly
                let dy = d.lat - oldLat;
                let dx = d.lng - oldLng;
                if (Math.abs(dy) > 0.00001 || Math.abs(dx) > 0.00001) {
                    d.heading = (Math.atan2(dx, dy) * 180 / Math.PI + 360) % 360;
                    d.speed = Math.sqrt(dx*dx + dy*dy) * 111320; // roughly meters/sec
                }
                
                if (activeTelemetryTargetId === d.id) {
                    updateTelemetryCards({
                        latitude: d.lat,
                        longitude: d.lng,
                        altitude: 50,
                        heading: d.heading,
                        speed: d.speed,
                        accuracy: 2.5
                    });
                }
            });
        }, 100);
    };"""
content = content.replace(old_sim, new_sim)

# Ensure popup class is correctly styled in error.css if needed, but we used inline styles for transparency!
open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Updated dashboard.js with popups and generic cards update logic")
