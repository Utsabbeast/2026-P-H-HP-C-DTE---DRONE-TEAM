/**
 * UTM — Unified Telemetry Monitor
 * Interactive Map & Live Telemetry Polling Client
 *
 * Supports:
 * 1. Phone GPS Test Mode (Default):
 *    - Real Android phone coordinates from /api/phone-location/
 *    - Dedicated Phone SVG marker with heading rotation
 *    - Continuous GPS movement trail + "Clear Trail" + "Center Phone"
 *    - 7 Live Telemetry Cards (Lat, Lon, Alt, Hdg, Spd, Acc, Last Update)
 *    - Telemetry connection status (🟢 Phone Connected / 🔴 Phone Disconnected + X seconds ago)
 * 2. Drone Hardware / Simulation Mode (Future Cube Orange+ & ESP32):
 *    - Ingest from /api/telemetry/ with procedural flight simulation
 */

(function () {
    'use strict';

    // Application Configuration from Body Data Attributes
    const bodyEl = document.body;
    const initialSimMode = bodyEl.getAttribute('data-simulation') === 'true';
    const targetDroneId = bodyEl.getAttribute('data-drone-id') || 'drone01';
    const targetPhoneDeviceId = bodyEl.getAttribute('data-phone-device-id') || 'phone_test_01';
    const droneTimeoutSeconds = parseFloat(bodyEl.getAttribute('data-timeout')) || 5.0;
    const phoneTimeoutSeconds = parseFloat(bodyEl.getAttribute('data-phone-timeout')) || 10.0;
    const localIp = bodyEl.getAttribute('data-local-ip') || window.location.hostname;

    // Active Dashboard Mode: 'phone' (Phone GPS Test) or 'drone' (ESP32/Sim)
    let activeMode = 'phone';

    // Leaflet State
    let map = null;
    let phoneMarker = null;
    let droneMarker = null;
    let activeMarker = null;
    let movementTrail = null;
    let trailCoordinates = [];
    let isTrailVisible = true;

    // Telemetry State
    let lastReceivedTimestamp = null;
    let totalPacketCount = 0;
    let pollTimer = null;
    let heartbeatTimer = null;
    let isSimulationPaused = false;
    let currentSimMode = initialSimMode;

    // Last known coordinates (fallback default: Ludhiana test site 30.9010°, 75.8573°)
    let lastKnownLat = 30.9010;
    let lastKnownLon = 75.8573;
    let lastKnownHeading = 142.0;
    let hasReceivedFirstPhoneFix = false;

    // DOM Elements Cache
    const elements = {
        // Mode Tabs & Badges
        tabPhoneMode: document.getElementById('tabPhoneMode'),
        tabDroneMode: document.getElementById('tabDroneMode'),
        testModeBadge: document.getElementById('testModeBadge'),
        modeBadgeText: document.getElementById('modeBadgeText'),
        sourcePill: document.getElementById('sourcePill'),
        gpsSourceText: document.getElementById('gpsSourceText'),
        hotspotBanner: document.getElementById('hotspotBanner'),
        hotspotBannerIcon: document.getElementById('hotspotBannerIcon'),
        bannerTitle: document.getElementById('bannerTitle'),
        bannerSub: document.getElementById('bannerSub'),
        bannerHelpText: document.getElementById('bannerHelpText'),
        bannerCodeUrl: document.getElementById('bannerCodeUrl'),
        btnTrackThisDevice: document.getElementById('btnTrackThisDevice'),
        btnTrackThisDeviceText: document.getElementById('btnTrackThisDeviceText'),
        btnShowQrModal: document.getElementById('btnShowQrModal'),
        btnCopyMobileUrl: document.getElementById('btnCopyMobileUrl'),
        copyBtnText: document.getElementById('copyBtnText'),
        btnOpenMobileLink: document.getElementById('btnOpenMobileLink'),
        qrModalBackdrop: document.getElementById('qrModalBackdrop'),
        qrCodeImage: document.getElementById('qrCodeImage'),
        qrModalUrlText: document.getElementById('qrModalUrlText'),
        btnCloseQrModal: document.getElementById('btnCloseQrModal'),
        btnModalCopyLink: document.getElementById('btnModalCopyLink'),
        btnModalClose: document.getElementById('btnModalClose'),
        connectionStatusPill: document.getElementById('connectionStatusPill'),
        statusDot: document.getElementById('statusDot'),
        statusLabel: document.getElementById('statusLabel'),
        
        // Map HUD & Header
        mapMainTitle: document.getElementById('mapMainTitle'),
        mapRouteHud: document.getElementById('mapRouteHud'),
        mapCoordinatesHud: document.getElementById('mapCoordinatesHud'),
        hudAlt: document.getElementById('hudAlt'),
        hudHdg: document.getElementById('hudHdg'),
        hudSpeed: document.getElementById('hudSpeed'),
        hudAccuracy: document.getElementById('hudAccuracy'),
        simFloatingBar: document.getElementById('simFloatingBar'),
        
        // Buttons
        btnCenterDrone: document.getElementById('btnCenterDrone'),
        centerButtonText: document.getElementById('centerButtonText'),
        btnClearTrail: document.getElementById('btnClearTrail'),
        btnToggleTrail: document.getElementById('btnToggleTrail'),
        trailButtonText: document.getElementById('trailButtonText'),
        btnResetView: document.getElementById('btnResetView'),
        btnPauseSim: document.getElementById('btnPauseSim'),
        btnResetSim: document.getElementById('btnResetSim'),
        btnNewRandomRoute: document.getElementById('btnNewRandomRoute'),
        btnToggleMode: document.getElementById('btnToggleMode'),
        btnToggleTester: document.getElementById('btnToggleTester'),
        btnCloseTester: document.getElementById('btnCloseTester'),

        // Telemetry Cards
        valLatitude: document.getElementById('valLatitude'),
        subLatitude: document.getElementById('subLatitude'),
        valLongitude: document.getElementById('valLongitude'),
        subLongitude: document.getElementById('subLongitude'),
        valAltitude: document.getElementById('valAltitude'),
        subAltitude: document.getElementById('subAltitude'),
        valHeading: document.getElementById('valHeading'),
        subHeading: document.getElementById('subHeading'),
        compassNeedle: document.getElementById('compassNeedle'),
        valSpeed: document.getElementById('valSpeed'),
        subSpeed: document.getElementById('subSpeed'),
        valAccuracy: document.getElementById('valAccuracy'),
        subAccuracy: document.getElementById('subAccuracy'),
        valLastUpdate: document.getElementById('valLastUpdate'),
        subLastUpdate: document.getElementById('subLastUpdate'),

        // Status Card
        overviewHeaderTitle: document.getElementById('overviewHeaderTitle'),
        statusMetaPkt: document.getElementById('statusMetaPkt'),
        statusConnBadge: document.getElementById('statusConnBadge'),
        statusConnDot: document.getElementById('statusConnDot'),
        statusConnText: document.getElementById('statusConnText'),
        statusConnHint: document.getElementById('statusConnHint'),
        statusFeedBadge: document.getElementById('statusFeedBadge'),
        statusFeedDot: document.getElementById('statusFeedDot'),
        statusFeedText: document.getElementById('statusFeedText'),
        statusFeedHint: document.getElementById('statusFeedHint'),
        statusRouteName: document.getElementById('statusRouteName'),
        statusRouteHint: document.getElementById('statusRouteHint'),
        statusHeartbeatSec: document.getElementById('statusHeartbeatSec'),
        statusHwPacketsHint: document.getElementById('statusHwPacketsHint'),
        hardwareOfflineAlert: document.getElementById('hardwareOfflineAlert'),

        // Tester Panel
        testerPanel: document.getElementById('testerPanel'),
        testerForm: document.getElementById('testerForm'),
        testerFeedback: document.getElementById('testerFeedback'),
    };

    // -------------------------------------------------------------------------
    // Custom Leaflet Icons
    // -------------------------------------------------------------------------
    function createPhoneIcon(heading) {
        const hdg = heading !== null && !isNaN(heading) ? heading : 0;
        return L.divIcon({
            className: 'phone-custom-marker-wrapper',
            html: `
                <div class="phone-marker-container">
                    <div class="phone-marker-pulse"></div>
                    <div class="phone-marker-rotator" id="phoneRotator" style="transform: rotate(${hdg}deg);">
                        <svg class="phone-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <!-- Heading Orientation Arrow pointing Up -->
                            <path d="M50 2 L59 18 H41 Z" fill="#10b981"/>
                            <!-- Phone Body Outer Frame -->
                            <rect x="26" y="14" width="48" height="74" rx="10" fill="#0f172a" stroke="#10b981" stroke-width="3"/>
                            <!-- Phone Screen Area -->
                            <rect x="30" y="24" width="40" height="54" rx="4" fill="#064e3b"/>
                            <!-- Phone Speaker Bar Top -->
                            <line x1="44" y1="19" x2="56" y2="19" stroke="#94a3b8" stroke-width="2.5" stroke-linecap="round"/>
                            <!-- Phone Screen Radar Pulse -->
                            <circle cx="50" cy="51" r="10" stroke="#34d399" stroke-width="1.5" stroke-dasharray="2,2"/>
                            <circle cx="50" cy="51" r="4" fill="#10b981"/>
                            <!-- Phone Home Indicator Bar Bottom -->
                            <line x1="42" y1="83" x2="58" y2="83" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </div>
                </div>
            `,
            iconSize: [48, 48],
            iconAnchor: [24, 24]
        });
    }

    function createDroneIcon(heading) {
        const hdg = heading !== null && !isNaN(heading) ? heading : 0;
        return L.divIcon({
            className: 'drone-custom-marker-wrapper',
            html: `
                <div class="drone-marker-container">
                    <div class="drone-marker-pulse"></div>
                    <div class="drone-marker-rotator" id="droneRotator" style="transform: rotate(${hdg}deg);">
                        <svg class="drone-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <!-- Forward Direction Indicator -->
                            <path d="M50 6 L62 28 H38 Z" fill="#dc2626"/>
                            <!-- Diagonal Quadcopter Carbon Arms -->
                            <line x1="22" y1="22" x2="78" y2="78" stroke="#0284c7" stroke-width="6" stroke-linecap="round"/>
                            <line x1="78" y1="22" x2="22" y2="78" stroke="#0284c7" stroke-width="6" stroke-linecap="round"/>
                            <!-- 4 Rotor Motors -->
                            <circle cx="22" cy="22" r="11" stroke="#0284c7" stroke-width="3" fill="#e0f2fe"/>
                            <circle cx="78" cy="22" r="11" stroke="#0284c7" stroke-width="3" fill="#e0f2fe"/>
                            <circle cx="22" cy="78" r="11" stroke="#0284c7" stroke-width="3" fill="#e0f2fe"/>
                            <circle cx="78" cy="78" r="11" stroke="#0284c7" stroke-width="3" fill="#e0f2fe"/>
                            <!-- Center Flight Avionics Housing (Cube Orange+) -->
                            <rect x="36" y="36" width="28" height="28" rx="6" fill="#0f172a" stroke="#38bdf8" stroke-width="2.5"/>
                            <circle cx="50" cy="50" r="5" fill="#22c55e"/>
                        </svg>
                    </div>
                </div>
            `,
            iconSize: [48, 48],
            iconAnchor: [24, 24]
        });
    }

    // -------------------------------------------------------------------------
    // Map Initialization
    // -------------------------------------------------------------------------
    function initMap() {
        map = L.map('droneMap', {
            zoomControl: true,
            attributionControl: true,
        }).setView([lastKnownLat, lastKnownLon], 16);

        // Standard OpenStreetMap Tile Layer
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | UTM'
        }).addTo(map);

        // Movement trail polyline
        movementTrail = L.polyline([], {
            color: '#10b981', // Emerald for phone test mode
            weight: 3.5,
            opacity: 0.85,
            lineCap: 'round',
            lineJoin: 'round',
            dashArray: '5, 5'
        }).addTo(map);

        // Create phone marker
        phoneMarker = L.marker([lastKnownLat, lastKnownLon], {
            icon: createPhoneIcon(lastKnownHeading),
            title: 'Android Phone (GPS Test Mode)',
            zIndexOffset: 1000
        });

        phoneMarker.bindPopup(`
            <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                <strong style="color: #059669;">📱 Phone GPS Test Mode</strong><br>
                <span>Device: <code>${targetPhoneDeviceId}</code></span><br>
                <span>Temporary drone GPS replacement</span>
            </div>
        `);

        // Create drone marker
        droneMarker = L.marker([lastKnownLat, lastKnownLon], {
            icon: createDroneIcon(lastKnownHeading),
            title: 'Drone 01 (Cube Orange+ / ESP32)',
            zIndexOffset: 1000
        });

        droneMarker.bindPopup(`
            <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                <strong style="color: #0284c7;">Drone 01 — Cube Orange+</strong><br>
                <span>Target: ESP32 Wi-Fi Telemetry</span>
            </div>
        `);

        // Default marker on startup is Phone Marker
        phoneMarker.addTo(map);
        activeMarker = phoneMarker;

        // Load initial trail
        loadHistoryForCurrentMode();
    }

    // -------------------------------------------------------------------------
    // Mode Switcher Handler
    // -------------------------------------------------------------------------
    function setDashboardMode(newMode) {
        if (activeMode === newMode) return;
        activeMode = newMode;

        // Clear displayed trail when switching modes
        trailCoordinates = [];
        if (movementTrail) {
            movementTrail.setLatLngs([]);
        }

        if (activeMode === 'phone') {
            // Update Tab styles
            elements.tabPhoneMode.className = 'mode-tab active phone-tab';
            elements.tabDroneMode.className = 'mode-tab';
            
            // Switch markers
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);
            if (phoneMarker) {
                phoneMarker.addTo(map);
                activeMarker = phoneMarker;
            }

            // Update polyline styling for phone
            if (movementTrail) {
                movementTrail.setStyle({ color: '#10b981' });
            }

            // Mode Badge
            elements.testModeBadge.style.display = 'inline-flex';
            elements.modeBadgeText.textContent = '🟢 TEST MODE — PHONE GPS';
            elements.gpsSourceText.textContent = 'GPS Source: Android Phone';
            elements.sourcePill.style.background = '#e0f2fe';
            elements.sourcePill.style.color = '#0369a1';
            elements.sourcePill.style.borderColor = '#bae6fd';

            // Show hotspot banner, hide sim bar and offline alert
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'flex';
            if (elements.simFloatingBar) elements.simFloatingBar.style.display = 'none';
            if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';

            // Buttons & Headers
            if (elements.centerButtonText) elements.centerButtonText.textContent = 'Center Phone';
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Live Tactical Map (Phone GPS)';
            if (elements.mapRouteHud) {
                elements.mapRouteHud.textContent = 'Source: Android Phone';
                elements.mapRouteHud.style.background = '#ecfdf5';
                elements.mapRouteHud.style.borderColor = '#a7f3d0';
                elements.mapRouteHud.style.color = '#047857';
            }
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Phone GPS Telemetry Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Android Phone';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Temporary test replacement';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Cube Orange+ → ESP32 → Wi-Fi';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Currently tested via Phone GPS';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Device: ${targetPhoneDeviceId}`;

        } else {
            // Drone Mode (ESP32 / Simulation)
            elements.tabPhoneMode.className = 'mode-tab';
            elements.tabDroneMode.className = 'mode-tab active';

            // Switch markers
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);
            if (droneMarker) {
                droneMarker.addTo(map);
                activeMarker = droneMarker;
            }

            // Update polyline styling for drone
            if (movementTrail) {
                movementTrail.setStyle({ color: '#0284c7' });
            }

            // Mode Badge
            if (currentSimMode) {
                elements.testModeBadge.style.display = 'inline-flex';
                elements.modeBadgeText.textContent = 'Simulation Mode Active';
                elements.gpsSourceText.textContent = 'GPS Source: Simulation Engine';
            } else {
                elements.testModeBadge.style.display = 'inline-flex';
                elements.modeBadgeText.textContent = 'Live Hardware Stream (ESP32)';
                elements.gpsSourceText.textContent = 'GPS Source: ESP32 / Cube Orange+';
            }

            // Hide hotspot banner, show sim controls if in sim mode
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.simFloatingBar && currentSimMode) elements.simFloatingBar.style.display = 'flex';

            // Buttons & Headers
            if (elements.centerButtonText) elements.centerButtonText.textContent = 'Center Drone';
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Live Tactical Map (Drone 01)';
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Drone Telemetry & Hardware Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = currentSimMode ? 'Simulation Engine' : 'ESP32 Wi-Fi';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = currentSimMode ? 'Procedural flight test' : 'Real Hardware';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`;
        }

        // Reset connection status until first poll of the new mode returns
        updateConnectionStatus(false, null);
        loadHistoryForCurrentMode();
        fetchActiveTelemetry();
    }

    // -------------------------------------------------------------------------
    // Formatters
    // -------------------------------------------------------------------------
    function headingToCardinal(heading) {
        if (heading === null || isNaN(heading)) return 'N/A';
        const cardinals = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
        const normalized = ((heading % 360) + 360) % 360;
        const index = Math.round(normalized / 45) % 8;
        return cardinals[index];
    }

    function formatTime(isoString) {
        if (!isoString) return '--:--:--';
        try {
            const d = new Date(isoString);
            return d.toLocaleTimeString('en-GB', { hour12: false });
        } catch (e) {
            return '--:--:--';
        }
    }

    // -------------------------------------------------------------------------
    // Phone GPS Telemetry Update
    // -------------------------------------------------------------------------
    function updatePhoneUI(telemetryData, apiState) {
        if (!telemetryData) return;

        const lat = parseFloat(telemetryData.latitude);
        const lon = parseFloat(telemetryData.longitude);
        const alt = telemetryData.altitude !== null ? parseFloat(telemetryData.altitude) : null;
        const hdg = telemetryData.heading !== null ? parseFloat(telemetryData.heading) : null;
        const speed = telemetryData.speed !== null ? parseFloat(telemetryData.speed) : null;
        const accuracy = telemetryData.accuracy !== null ? parseFloat(telemetryData.accuracy) : null;
        const timeStr = formatTime(telemetryData.timestamp || telemetryData.received_at);

        lastKnownLat = lat;
        lastKnownLon = lon;
        if (hdg !== null) lastKnownHeading = hdg;

        // Auto-center map on first phone fix received
        if (!hasReceivedFirstPhoneFix && map) {
            map.setView([lat, lon], 17);
            hasReceivedFirstPhoneFix = true;
        }

        // 1. Update Phone Marker Position & Heading Rotator
        if (phoneMarker) {
            phoneMarker.setLatLng([lat, lon]);
            const rotatorEl = document.getElementById('phoneRotator');
            if (rotatorEl && hdg !== null) {
                rotatorEl.style.transform = `rotate(${hdg}deg)`;
            }

            // Append to GPS movement trail
            if (movementTrail && isTrailVisible) {
                trailCoordinates.push([lat, lon]);
                if (trailCoordinates.length > 300) {
                    trailCoordinates.shift();
                }
                movementTrail.setLatLngs(trailCoordinates);
            }
        }

        // 2. Update Map HUD Overlay
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

        if (elements.valAccuracy) elements.valAccuracy.textContent = accuracy !== null ? `${accuracy.toFixed(1)} m` : 'N/A';
        if (elements.subAccuracy) elements.subAccuracy.textContent = accuracy !== null ? 'Horizontal GPS accuracy' : 'Unavailable';

        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;

        // 4. Update Connection Status
        const secondsAgo = apiState ? apiState.seconds_since_update : 0;
        updateConnectionStatus(apiState ? apiState.is_connected : true, secondsAgo);
    }

    // -------------------------------------------------------------------------
    // Drone Telemetry Update (For Drone Mode)
    // -------------------------------------------------------------------------
    function updateDroneUI(telemetryData, apiState) {
        if (!telemetryData) return;

        const lat = parseFloat(telemetryData.latitude);
        const lon = parseFloat(telemetryData.longitude);
        const alt = parseFloat(telemetryData.altitude);
        const hdg = parseFloat(telemetryData.heading);
        const timeStr = formatTime(telemetryData.timestamp || telemetryData.received_at);

        lastKnownLat = lat;
        lastKnownLon = lon;
        lastKnownHeading = hdg;

        // Update Drone Marker Position & Rotator
        if (droneMarker) {
            droneMarker.setLatLng([lat, lon]);
            const rotatorEl = document.getElementById('droneRotator');
            if (rotatorEl) {
                rotatorEl.style.transform = `rotate(${hdg}deg)`;
            }

            if (movementTrail && isTrailVisible) {
                trailCoordinates.push([lat, lon]);
                if (trailCoordinates.length > 300) trailCoordinates.shift();
                movementTrail.setLatLngs(trailCoordinates);
            }
        }

        // Update Map HUD
        if (elements.mapCoordinatesHud) {
            elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.mapRouteHud && apiState && apiState.route_name) {
            elements.mapRouteHud.textContent = `Route: ${apiState.route_name}`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = `${alt.toFixed(1)} m`;
        if (elements.hudHdg) elements.hudHdg.textContent = `${Math.round(hdg)}°`;
        if (elements.hudSpeed) elements.hudSpeed.textContent = '12.0 m/s';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = '0.5 m';

        // Update Cards
        if (elements.valLatitude) elements.valLatitude.textContent = `${lat.toFixed(6)}°`;
        if (elements.subLatitude) elements.subLatitude.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;
        if (elements.valLongitude) elements.valLongitude.textContent = `${lon.toFixed(6)}°`;
        if (elements.subLongitude) elements.subLongitude.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;
        if (elements.valAltitude) elements.valAltitude.textContent = `${alt.toFixed(1)} m`;
        if (elements.subAltitude) elements.subAltitude.textContent = 'AGL Altitude';
        if (elements.valHeading) elements.valHeading.textContent = `${Math.round(hdg)}°`;
        if (elements.subHeading) elements.subHeading.textContent = headingToCardinal(hdg);
        if (elements.compassNeedle) elements.compassNeedle.style.transform = `rotate(${hdg}deg)`;
        if (elements.valSpeed) elements.valSpeed.textContent = '12.0 m/s';
        if (elements.subSpeed) elements.subSpeed.textContent = '43.2 km/h';
        if (elements.valAccuracy) elements.valAccuracy.textContent = 'RTK Fix';
        if (elements.subAccuracy) elements.subAccuracy.textContent = 'Precision 0.5m';
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;

        const isHw = apiState ? apiState.hardware_connected : false;
        const secondsAgo = apiState ? apiState.seconds_since_update : 0;
        updateConnectionStatus(isHw, secondsAgo, apiState ? apiState.status_label : null);
    }

    // -------------------------------------------------------------------------
    // Connection Status Manager
    // -------------------------------------------------------------------------
    function updateConnectionStatus(isConnected, secondsAgo, customLabel) {
        const secText = (secondsAgo !== null && secondsAgo !== undefined) ? `${secondsAgo.toFixed(1)}s ago` : 'never';

        if (elements.statusHeartbeatSec) {
            elements.statusHeartbeatSec.textContent = (secondsAgo !== null && secondsAgo !== undefined) ? secondsAgo.toFixed(1) : '--';
        }
        if (elements.subLastUpdate) {
            elements.subLastUpdate.textContent = `Last update: ${secText}`;
        }

        if (activeMode === 'phone') {
            if (isConnected) {
                // 🟢 Phone Connected
                elements.connectionStatusPill.className = 'connection-status connected';
                elements.statusDot.className = 'status-indicator-dot dot-green';
                elements.statusLabel.textContent = '🟢 Phone Connected';

                elements.statusConnBadge.className = 'item-value-pill pill-green';
                elements.statusConnDot.className = 'dot-indicator dot-green';
                elements.statusConnText.textContent = '🟢 Phone Connected';
                elements.statusConnHint.textContent = `Live GPS packets active (${secText})`;

                // Update Banner for Connected state
                if (elements.hotspotBanner) elements.hotspotBanner.classList.add('is-connected');
                if (elements.bannerTitle) elements.bannerTitle.textContent = `🟢 Phone GPS Streaming Live (${targetPhoneDeviceId})`;
                if (elements.bannerHelpText) elements.bannerHelpText.textContent = `Streaming to tactical map (${secText}):`;
            } else {
                // 🔴 Phone Disconnected
                elements.connectionStatusPill.className = 'connection-status disconnected';
                elements.statusDot.className = 'status-indicator-dot dot-red';
                elements.statusLabel.textContent = '🔴 Phone Disconnected';

                elements.statusConnBadge.className = 'item-value-pill';
                elements.statusConnDot.className = 'dot-indicator dot-red';
                elements.statusConnText.textContent = '🔴 Phone Disconnected';
                elements.statusConnHint.textContent = `No GPS updates (${secText}). Check /mobile/`;

                // Update Banner for Disconnected state
                if (elements.hotspotBanner) elements.hotspotBanner.classList.remove('is-connected');
                if (elements.bannerTitle) elements.bannerTitle.textContent = '📱 Phone GPS Test Mode — Connect Your Smartphone';
                if (elements.bannerHelpText) elements.bannerHelpText.textContent = 'Open on phone or scan QR code:';
            }
        } else {
            // Drone Mode
            if (currentSimMode) {
                elements.connectionStatusPill.className = 'connection-status disconnected';
                elements.statusDot.className = 'status-indicator-dot dot-amber';
                elements.statusLabel.textContent = 'Drone Not Connected (Simulation Mode)';

                elements.statusConnBadge.className = 'item-value-pill pill-amber';
                elements.statusConnDot.className = 'dot-indicator dot-amber';
                elements.statusConnText.textContent = 'Drone Not Connected';
                elements.statusConnHint.textContent = 'ESP32 hardware offline';
            } else if (isConnected) {
                elements.connectionStatusPill.className = 'connection-status connected';
                elements.statusDot.className = 'status-indicator-dot dot-green';
                elements.statusLabel.textContent = 'Drone Connected (ESP32 Live)';

                elements.statusConnBadge.className = 'item-value-pill pill-green';
                elements.statusConnDot.className = 'dot-indicator dot-green';
                elements.statusConnText.textContent = 'ESP32 Broadcasting';
                elements.statusConnHint.textContent = 'Hardware online';
            } else {
                elements.connectionStatusPill.className = 'connection-status disconnected';
                elements.statusDot.className = 'status-indicator-dot dot-red';
                elements.statusLabel.textContent = 'Drone Not Connected';

                elements.statusConnBadge.className = 'item-value-pill';
                elements.statusConnDot.className = 'dot-indicator dot-red';
                elements.statusConnText.textContent = 'Disconnected';
                elements.statusConnHint.textContent = 'Awaiting ESP32 packet';
            }
        }
    }

    // -------------------------------------------------------------------------
    // Polling Logic
    // -------------------------------------------------------------------------
    async function fetchActiveTelemetry() {
        if (activeMode === 'phone') {
            await fetchPhoneTelemetry();
        } else {
            await fetchDroneTelemetry();
        }
    }

    async function fetchPhoneTelemetry() {
        try {
            const response = await fetch(`/api/phone-location/latest/?device_id=${targetPhoneDeviceId}`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.status === 'success' && data.telemetry) {
                totalPacketCount++;
                if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${data.total_packets_received || totalPacketCount}`;
                const secAgo = (typeof data.seconds_since_update === 'number') ? data.seconds_since_update : 0;
                lastReceivedTimestamp = Date.now() - (secAgo * 1000);
                updatePhoneUI(data.telemetry, data);
            } else if (data.status === 'waiting') {
                updateConnectionStatus(false, null);
            }
        } catch (err) {
            console.warn('[UTM] Phone telemetry fetch error:', err.message);
        }
    }

    async function fetchDroneTelemetry() {
        if (isSimulationPaused) return;

        try {
            const response = await fetch(`/api/telemetry/latest/?drone_id=${targetDroneId}`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.status === 'success' && data.telemetry) {
                totalPacketCount++;
                if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                lastReceivedTimestamp = Date.now();
                updateDroneUI(data.telemetry, data);
            }
        } catch (err) {
            console.warn('[UTM] Drone telemetry fetch error:', err.message);
        }
    }

    // -------------------------------------------------------------------------
    // History Loader (Reconstructs movement trail without deleting DB)
    // -------------------------------------------------------------------------
    async function loadHistoryForCurrentMode() {
        try {
            if (activeMode === 'phone') {
                const response = await fetch(`/api/phone-location/history/?device_id=${targetPhoneDeviceId}&limit=100`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.results && data.results.length > 0) {
                        trailCoordinates = data.results.map(r => [r.latitude, r.longitude]);
                        if (movementTrail) movementTrail.setLatLngs(trailCoordinates);
                    }
                }
            } else {
                const response = await fetch(`/api/telemetry/history/?drone_id=${targetDroneId}&limit=50`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.results && data.results.length > 0) {
                        trailCoordinates = data.results.map(r => [r.latitude, r.longitude]);
                        if (movementTrail) movementTrail.setLatLngs(trailCoordinates);
                    }
                }
            }
        } catch (e) {
            console.warn('[UTM] Error loading history:', e);
        }
    }

    // -------------------------------------------------------------------------
    // Map Controls: Center, Clear Trail, Toggle Trail, Reset
    // -------------------------------------------------------------------------
    function centerCurrentMarker() {
        if (map && activeMarker) {
            const pos = activeMarker.getLatLng();
            map.panTo(pos, { animate: true, duration: 0.8 });
        }
    }

    function clearMovementTrail() {
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
    }

    function toggleTrailVisibility() {
        isTrailVisible = !isTrailVisible;
        if (isTrailVisible) {
            if (movementTrail) map.addLayer(movementTrail);
            if (elements.trailButtonText) elements.trailButtonText.textContent = 'Hide Trail';
        } else {
            if (movementTrail) map.removeLayer(movementTrail);
            if (elements.trailButtonText) elements.trailButtonText.textContent = 'Show Trail';
        }
    }

    function resetMapView() {
        if (map) {
            map.setView([lastKnownLat, lastKnownLon], 16, { animate: true });
        }
    }

    // -------------------------------------------------------------------------
    // Client-side Heartbeat Counter
    // -------------------------------------------------------------------------
    function startHeartbeatCounter() {
        heartbeatTimer = setInterval(() => {
            if (!lastReceivedTimestamp) return;
            const secondsAgo = (Date.now() - lastReceivedTimestamp) / 1000;
            const timeout = activeMode === 'phone' ? phoneTimeoutSeconds : droneTimeoutSeconds;

            if (elements.statusHeartbeatSec) {
                elements.statusHeartbeatSec.textContent = secondsAgo.toFixed(1);
            }
            if (elements.subLastUpdate) {
                elements.subLastUpdate.textContent = `Last update: ${secondsAgo.toFixed(1)}s ago`;
            }

            if (secondsAgo > timeout) {
                updateConnectionStatus(false, secondsAgo);
            }
        }, 500);
    }

    // -------------------------------------------------------------------------
    // Direct Browser Device GPS Tracking (No phone/QR required)
    // -------------------------------------------------------------------------
    let localWatchId = null;
    let isLocalTracking = false;

    function toggleLocalDeviceTracking() {
        if (isLocalTracking) {
            stopLocalDeviceTracking();
        } else {
            startLocalDeviceTracking();
        }
    }

    function startLocalDeviceTracking() {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser.');
            return;
        }

        // Switch to Phone/Device GPS Mode if not already active
        if (activeMode !== 'phone') {
            setDashboardMode('phone');
        }

        if (elements.btnTrackThisDevice) {
            elements.btnTrackThisDevice.classList.add('is-active');
            if (elements.btnTrackThisDeviceText) {
                elements.btnTrackThisDeviceText.textContent = '⏹️ Stop Live Tracking';
            }
        }

        isLocalTracking = true;
        if (elements.bannerTitle) elements.bannerTitle.textContent = '📍 Acquiring Device GPS...';
        if (elements.bannerHelpText) elements.bannerHelpText.textContent = 'Please click "Allow" on the browser location prompt to track live.';

        localWatchId = navigator.geolocation.watchPosition(
            (pos) => {
                const coords = pos.coords;
                const lat = coords.latitude;
                const lon = coords.longitude;
                const rawAlt = coords.altitude;
                const rawHdg = coords.heading;
                const rawAcc = coords.accuracy;
                const rawSpd = coords.speed;

                const alt = (rawAlt !== null && !isNaN(rawAlt)) ? Number(rawAlt.toFixed(1)) : null;
                const heading = (rawHdg !== null && !isNaN(rawHdg) && rawHdg >= 0) ? Number((rawHdg % 360).toFixed(1)) : null;
                const accuracy = (rawAcc !== null && !isNaN(rawAcc) && rawAcc >= 0) ? Number(rawAcc.toFixed(1)) : null;
                const speed = (rawSpd !== null && !isNaN(rawSpd) && rawSpd >= 0) ? Number(rawSpd.toFixed(1)) : null;

                const telemetryObj = {
                    latitude: lat,
                    longitude: lon,
                    altitude: alt,
                    heading: heading,
                    accuracy: accuracy,
                    speed: speed,
                    timestamp: new Date(pos.timestamp || Date.now()).toISOString(),
                    received_at: new Date().toISOString(),
                    source: 'browser_gps'
                };

                const apiState = {
                    is_connected: true,
                    status_label: 'Device Connected',
                    seconds_since_update: 0.1,
                    total_packets_received: totalPacketCount + 1
                };

                lastReceivedTimestamp = Date.now();
                totalPacketCount++;
                updatePhoneUI(telemetryObj, apiState);

                if (elements.bannerTitle) {
                    elements.bannerTitle.textContent = `🟢 Device GPS Live (Accurate to ${accuracy !== null ? accuracy + 'm' : 'GPS fix'})`;
                }
                if (elements.bannerHelpText) {
                    elements.bannerHelpText.textContent = `Streaming location directly to tactical map:`;
                }

                // Also persist packet to backend database so history is preserved
                fetch('/api/phone-location/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({
                        device_id: targetPhoneDeviceId,
                        latitude: Number(lat.toFixed(6)),
                        longitude: Number(lon.toFixed(6)),
                        altitude: alt,
                        heading: heading,
                        accuracy: accuracy,
                        speed: speed,
                        timestamp: telemetryObj.timestamp,
                        source: 'browser_gps'
                    })
                }).catch(() => {});
            },
            (err) => {
                console.warn('[UTM] Browser geolocation error:', err);
                if (err.code === err.TIMEOUT && lastKnownLat) {
                    return; // Ignore intermittent timeout
                }
                let msg = 'Failed to acquire device location.';
                if (err.code === err.PERMISSION_DENIED) {
                    msg = 'Location permission was denied. Please allow location access in your browser address bar/site settings to track this device.';
                } else if (err.code === err.POSITION_UNAVAILABLE) {
                    msg = 'Location signal currently unavailable. Check that Location Services are enabled on this computer.';
                }
                alert(msg);
                stopLocalDeviceTracking();
            },
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 5000
            }
        );
    }

    function stopLocalDeviceTracking() {
        if (localWatchId !== null) {
            navigator.geolocation.clearWatch(localWatchId);
            localWatchId = null;
        }
        isLocalTracking = false;
        if (elements.btnTrackThisDevice) {
            elements.btnTrackThisDevice.classList.remove('is-active');
            if (elements.btnTrackThisDeviceText) {
                elements.btnTrackThisDeviceText.textContent = 'Track My Location Live';
            }
        }
        if (elements.bannerTitle) {
            elements.bannerTitle.textContent = '📱 Live GPS Mode — Track Direct or Connect Phone';
        }
        if (elements.bannerHelpText) {
            elements.bannerHelpText.textContent = 'Click below to track this device live, or scan QR code on smartphone:';
        }
    }

    // -------------------------------------------------------------------------
    // Event Listeners & Startup
    // -------------------------------------------------------------------------
    function bindEvents() {
        // Direct Device GPS Tracking
        if (elements.btnTrackThisDevice) {
            elements.btnTrackThisDevice.addEventListener('click', toggleLocalDeviceTracking);
        }

        // Mode Switcher Tabs
        if (elements.tabPhoneMode) {
            elements.tabPhoneMode.addEventListener('click', () => setDashboardMode('phone'));
        }
        if (elements.tabDroneMode) {
            elements.tabDroneMode.addEventListener('click', () => setDashboardMode('drone'));
        }

        // Action Buttons
        if (elements.btnCenterDrone) elements.btnCenterDrone.addEventListener('click', centerCurrentMarker);
        if (elements.btnClearTrail) elements.btnClearTrail.addEventListener('click', clearMovementTrail);
        if (elements.btnToggleTrail) elements.btnToggleTrail.addEventListener('click', toggleTrailVisibility);
        if (elements.btnResetView) elements.btnResetView.addEventListener('click', resetMapView);

        // Simulation Controls (Drone mode)
        if (elements.btnPauseSim) {
            elements.btnPauseSim.addEventListener('click', () => {
                isSimulationPaused = !isSimulationPaused;
                elements.btnPauseSim.textContent = isSimulationPaused ? '▶ Resume' : '⏸ Pause';
            });
        }
        if (elements.btnResetSim) {
            elements.btnResetSim.addEventListener('click', async () => {
                await fetch('/api/simulation/reset/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ randomize: false })
                });
                clearMovementTrail();
            });
        }
        if (elements.btnNewRandomRoute) {
            elements.btnNewRandomRoute.addEventListener('click', async () => {
                const res = await fetch('/api/simulation/reset/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ randomize: true })
                });
                if (res.ok) {
                    const data = await res.json();
                    if (elements.mapRouteHud) elements.mapRouteHud.textContent = `Route: ${data.route_name}`;
                    clearMovementTrail();
                }
            });
        }
        if (elements.btnToggleMode) {
            elements.btnToggleMode.addEventListener('click', async () => {
                const res = await fetch('/api/simulation/toggle/', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
                if (res.ok) {
                    const data = await res.json();
                    currentSimMode = data.simulation_mode;
                    elements.btnToggleMode.textContent = currentSimMode ? 'Switch to Live' : 'Switch to Sim';
                    clearMovementTrail();
                }
            });
        }

        // Tester Panel
        if (elements.btnToggleTester) {
            elements.btnToggleTester.addEventListener('click', () => {
                const isHidden = elements.testerPanel.style.display === 'none';
                elements.testerPanel.style.display = isHidden ? 'block' : 'none';
                if (isHidden) elements.testerPanel.scrollIntoView({ behavior: 'smooth' });
            });
        }
        if (elements.btnCloseTester) {
            elements.btnCloseTester.addEventListener('click', () => {
                elements.testerPanel.style.display = 'none';
            });
        }

        // Tester Form Submit (Supports both phone and drone test packet injection)
        if (elements.testerForm) {
            elements.testerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const idVal = document.getElementById('inputDroneId').value;
                const latVal = parseFloat(document.getElementById('inputLat').value);
                const lonVal = parseFloat(document.getElementById('inputLon').value);
                const altVal = parseFloat(document.getElementById('inputAlt').value);
                const hdgVal = parseFloat(document.getElementById('inputHdg').value);

                const endpoint = activeMode === 'phone' ? '/api/phone-location/' : '/api/telemetry/';
                const payload = activeMode === 'phone' ? {
                    device_id: idVal,
                    latitude: latVal,
                    longitude: lonVal,
                    altitude: altVal,
                    heading: hdgVal,
                    accuracy: 5.0,
                    speed: 2.5,
                    timestamp: new Date().toISOString(),
                    source: 'phone_test'
                } : {
                    drone_id: idVal,
                    latitude: latVal,
                    longitude: lonVal,
                    altitude: altVal,
                    heading: hdgVal,
                    timestamp: new Date().toISOString()
                };

                try {
                    const res = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const resData = await res.json();
                    elements.testerFeedback.style.display = 'block';
                    elements.testerFeedback.className = res.ok ? 'tester-feedback success' : 'tester-feedback error';
                    elements.testerFeedback.textContent = res.ok ?
                        `Packet transmitted successfully (${res.status} Created) to ${endpoint}` :
                        `Error: ${JSON.stringify(resData)}`;
                    fetchActiveTelemetry();
                } catch (err) {
                    elements.testerFeedback.style.display = 'block';
                    elements.testerFeedback.className = 'tester-feedback error';
                    elements.testerFeedback.textContent = `Transmission failed: ${err.message}`;
                }
            });
        }

        // Dynamic Mobile Connection & QR Code Logic
        const mobilePortalUrl = window.location.origin + '/mobile/';
        if (elements.bannerCodeUrl) elements.bannerCodeUrl.textContent = mobilePortalUrl;
        if (elements.btnOpenMobileLink) elements.btnOpenMobileLink.href = mobilePortalUrl;
        if (elements.qrModalUrlText) elements.qrModalUrlText.textContent = mobilePortalUrl;
        if (elements.qrCodeImage) {
            elements.qrCodeImage.src = 'https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=' + encodeURIComponent(mobilePortalUrl);
        }

        // QR Code Modal
        if (elements.btnShowQrModal) {
            elements.btnShowQrModal.addEventListener('click', () => {
                if (elements.qrModalBackdrop) elements.qrModalBackdrop.style.display = 'flex';
            });
        }
        if (elements.btnCloseQrModal) {
            elements.btnCloseQrModal.addEventListener('click', () => {
                if (elements.qrModalBackdrop) elements.qrModalBackdrop.style.display = 'none';
            });
        }
        if (elements.btnModalClose) {
            elements.btnModalClose.addEventListener('click', () => {
                if (elements.qrModalBackdrop) elements.qrModalBackdrop.style.display = 'none';
            });
        }
        if (elements.qrModalBackdrop) {
            elements.qrModalBackdrop.addEventListener('click', (e) => {
                if (e.target === elements.qrModalBackdrop) {
                    elements.qrModalBackdrop.style.display = 'none';
                }
            });
        }

        // Copy Link to Clipboard
        function copyMobileLink(btnEl, textSpan) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(mobilePortalUrl).then(() => {
                    const originalText = textSpan ? textSpan.textContent : 'Copy Link';
                    if (textSpan) textSpan.textContent = '✅ Copied!';
                    setTimeout(() => {
                        if (textSpan) textSpan.textContent = originalText;
                    }, 2200);
                }).catch(() => {
                    prompt('Copy this link:', mobilePortalUrl);
                });
            } else {
                prompt('Copy this link:', mobilePortalUrl);
            }
        }

        if (elements.btnCopyMobileUrl) {
            elements.btnCopyMobileUrl.addEventListener('click', () => {
                copyMobileLink(elements.btnCopyMobileUrl, elements.copyBtnText);
            });
        }
        if (elements.btnModalCopyLink) {
            elements.btnModalCopyLink.addEventListener('click', () => {
                copyMobileLink(elements.btnModalCopyLink, elements.btnModalCopyLink);
            });
        }
    }

    // -------------------------------------------------------------------------
    // Main Initialization
    // -------------------------------------------------------------------------
    function init() {
        initMap();
        bindEvents();
        startHeartbeatCounter();

        // Start polling active telemetry every 1000ms
        pollTimer = setInterval(fetchActiveTelemetry, 1000);
        fetchActiveTelemetry();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
