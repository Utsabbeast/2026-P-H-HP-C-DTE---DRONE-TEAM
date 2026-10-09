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
    const targetDroneId = bodyEl.getAttribute('data-drone-id') || 'drone01';
    const targetPhoneDeviceId = bodyEl.getAttribute('data-phone-device-id') || 'phone_test_01';
    const droneTimeoutSeconds = parseFloat(bodyEl.getAttribute('data-timeout')) || 5.0;
    const phoneTimeoutSeconds = parseFloat(bodyEl.getAttribute('data-phone-timeout')) || 10.0;
    const localIp = bodyEl.getAttribute('data-local-ip') || window.location.hostname;

    // Active Dashboard Mode: 'phone' (Phone GPS) or 'drone' (ESP32 Hardware)
    let activeMode = 'main';

    // Leaflet State
    let map = null;
    let phoneMarker = null;
    let mainModeMarkers = {};
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

    // Last known coordinates (fallback default: Ludhiana test site 30.9010°, 75.8573°)
    let lastKnownLat = 30.9010;
    let lastKnownLon = 75.8573;
    let lastKnownHeading = 142.0;
    let hasReceivedFirstPhoneFix = false;
    let hasReceivedFirstDroneFix = false;

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
        
        // ESP32 Hardware Banner Elements
        esp32Banner: document.getElementById('esp32Banner'),
        esp32WsInput: document.getElementById('esp32WsInput'),
        btnConnectEspWs: document.getElementById('btnConnectEspWs'),
        btnDisconnectEspWs: document.getElementById('btnDisconnectEspWs'),
        esp32WsStatusBadge: document.getElementById('esp32WsStatusBadge'),
        esp32WsDot: document.getElementById('esp32WsDot'),
        esp32WsStatusText: document.getElementById('esp32WsStatusText'),
        esp32HttpsTip: document.getElementById('esp32HttpsTip'),
        
        // Map HUD & Header
        mapMainTitle: document.getElementById('mapMainTitle'),
        mapRouteHud: document.getElementById('mapRouteHud'),
        mapCoordinatesHud: document.getElementById('mapCoordinatesHud'),
        hudAlt: document.getElementById('hudAlt'),
        hudHdg: document.getElementById('hudHdg'),
        hudSpeed: document.getElementById('hudSpeed'),
        hudAccuracy: document.getElementById('hudAccuracy'),
        
        // Buttons
        btnCenterDrone: document.getElementById('btnCenterDrone'),
        centerButtonText: document.getElementById('centerButtonText'),
        btnClearTrail: document.getElementById('btnClearTrail'),
        btnToggleTrail: document.getElementById('btnToggleTrail'),
        trailButtonText: document.getElementById('trailButtonText'),
        btnResetView: document.getElementById('btnResetView'),
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
        mapStatsContainer: document.getElementById('mapStatsContainer'),
        statRegisteredDronesBox: document.getElementById('statRegisteredDronesBox'),
          valRegisteredDrones: document.getElementById('valRegisteredDrones'),
        valDronesInAir: document.getElementById('valDronesInAir'),
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
            zoomControl: false, // We add it manually to position it
            attributionControl: true,
            maxZoom: 22
        }).setView([lastKnownLat, lastKnownLon], 16);
        
        // Add zoom control to topleft (first in column)
        L.control.zoom({ position: 'topleft' }).addTo(map);

    // Deselect marker and clear telemetry on map click
    map.on('click', function(e) {
        activeMarker = null;
        activeTelemetryTargetId = null;
        resetTelemetryUI();
    });

        // Premier Map Tile Providers
        const googleStreets = L.tileLayer('http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            attribution: '&copy; Google Maps'
        });

        const googleSatellite = L.tileLayer('http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            attribution: '&copy; Google Maps Satellite'
        });

        const esriStreet = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 22,
            attribution: '&copy; Esri World Street Map'
        });

        const esriDark = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 22,
            attribution: '&copy; Esri Dark Tactical'
        });

        // Add Default Layer (Google Streets)
        googleStreets.addTo(map);

        const baseMaps = {
            'Google Streets': googleStreets,
            'Google Satellite': googleSatellite,
            'Esri Street': esriStreet,
            'Esri Dark': esriDark
        };
        L.control.layers(baseMaps, null, { position: 'topleft' }).addTo(map);

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

        // Default marker on startup
        if (activeMode === 'phone') {
            phoneMarker.addTo(map);
            activeMarker = phoneMarker;
        }

        // Load initial trail
        loadHistoryForCurrentMode();
    }

    // -------------------------------------------------------------------------
    // Mode Switcher Handler
    // -------------------------------------------------------------------------
    function setDashboardMode(newMode) {
        if (activeMode === newMode) return;
        activeMode = newMode;

        // Handle Registered Drones Box visibility
        if (elements.statRegisteredDronesBox) {
            elements.statRegisteredDronesBox.style.display = (newMode === 'simulator') ? 'none' : 'flex';
        }

        // Always hide API tools and panel when changing modes, only show for drone
        if (elements.btnToggleTester) elements.btnToggleTester.style.display = (newMode === 'drone') ? 'flex' : 'none';
        if (elements.testerPanel) elements.testerPanel.style.display = 'none';


        // Clear displayed trail when switching modes
        trailCoordinates = [];
        if (movementTrail) {
            movementTrail.setLatLngs([]);
        }

        if (activeMode === 'main') {
            if (elements.tabPhoneMode) elements.tabPhoneMode.className = 'mode-tab';
            if (elements.tabDroneMode) elements.tabDroneMode.className = 'mode-tab';
            
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);
            
            if (elements.testModeBadge) elements.testModeBadge.style.display = 'none';
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                // the simulation polling will update drones in air if needed
            }
            
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Main Mode (Overview)';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                if (elements.valDronesInAir) elements.valDronesInAir.textContent = elements.valDronesInAir.getAttribute('data-original') || '0';
            }
            if (elements.mapRouteHud) {
                if (elements.mapRouteHud) elements.mapRouteHud.textContent = 'Overview';
                if (elements.mapRouteHud) elements.mapRouteHud.style.background = '#e0f2fe';
                if (elements.mapRouteHud) elements.mapRouteHud.style.borderColor = '#bae6fd';
                if (elements.mapRouteHud) elements.mapRouteHud.style.color = '#0369a1';
            }
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'UTM Network Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Aggregated DB';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'All active drones';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Multi-Drone Network';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Cloud Database Aggregation';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = 'Network Traffic';
                                } else if (activeMode === 'phone') {
            // Update Tab styles
            if (elements.tabPhoneMode) elements.tabPhoneMode.className = 'mode-tab active phone-tab';
            if (elements.tabDroneMode) elements.tabDroneMode.className = 'mode-tab';
            
            // Switch markers
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);
            if (phoneMarker) {
                phoneMarker.addTo(map);
                activeMarker = phoneMarker;
                if (map) map.setView(phoneMarker.getLatLng(), 17, { animate: true });
            }

            // Update polyline styling for phone
            if (movementTrail) {
                movementTrail.setStyle({ color: '#10b981' });
            }

            // Mode Badge
            if (elements.testModeBadge) elements.testModeBadge.style.display = 'inline-flex';
            if (elements.modeBadgeText) elements.modeBadgeText.textContent = '🟢 TEST MODE — PHONE GPS';
            if (elements.gpsSourceText) elements.gpsSourceText.textContent = 'GPS Source: Android Phone';
            if (elements.sourcePill) elements.sourcePill.style.background = '#e0f2fe';
            if (elements.sourcePill) elements.sourcePill.style.color = '#0369a1';
            if (elements.sourcePill) elements.sourcePill.style.borderColor = '#bae6fd';

            // Show hotspot banner, hide esp32 banner, sim bar and offline alert
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'flex';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                // the simulation polling will update drones in air if needed
            }
            if (elements.simFloatingBar) elements.simFloatingBar.style.display = 'none';
            if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'none';
                                    // Buttons & Headers
            if (elements.centerButtonText) elements.centerButtonText.textContent = 'Center Phone';
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Live Tactical Map (Phone GPS)';
            if (elements.mapRouteHud) {
                if (elements.mapRouteHud) elements.mapRouteHud.textContent = 'Source: Android Phone';
                if (elements.mapRouteHud) elements.mapRouteHud.style.background = '#ecfdf5';
                if (elements.mapRouteHud) elements.mapRouteHud.style.borderColor = '#a7f3d0';
                if (elements.mapRouteHud) elements.mapRouteHud.style.color = '#047857';
            }
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Phone GPS Telemetry Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Android Phone';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Temporary test replacement';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Android Device GPS API';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Tested via Mobile Web';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Device: ${targetPhoneDeviceId}`;
        } else if (activeMode === 'simulator') {
            // Simulator Mode
            if (elements.tabPhoneMode) elements.tabPhoneMode.className = 'mode-tab';
            if (elements.tabDroneMode) elements.tabDroneMode.className = 'mode-tab';
            
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);
            
            if (elements.testModeBadge) elements.testModeBadge.style.display = 'none';
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                // the simulation polling will update drones in air if needed
            }
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Drone Telemetry & Hardware Overview';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'Simulation Engine';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Local Python Script';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Software In The Loop (SITL)';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Virtual hardware simulation';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`;
                                } else if (activeMode === 'drone') {
            // Drone Mode (ESP32 Live Hardware)
            if (elements.tabPhoneMode) elements.tabPhoneMode.className = 'mode-tab';
            if (elements.tabDroneMode) elements.tabDroneMode.className = 'mode-tab active';

            // Switch markers
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);

            if (!droneMarker) {
                droneMarker = L.marker([lastKnownLat || 30.9010, lastKnownLon || 75.8573], {
                    icon: createDroneIcon(lastKnownHeading || 0),
                    title: 'Drone 01 (Cube Orange+ / ESP32)',
                    zIndexOffset: 1000
                });
                droneMarker.bindPopup(`
                    <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                        <strong style="color: #0284c7;">Drone 01 — Cube Orange+</strong><br>
                        <span>Target: ESP32 Wi-Fi Telemetry</span>
                    </div>
                `);
            }
            if (droneMarker) {

                droneMarker.addTo(map);
                activeMarker = droneMarker;
                if (map) map.setView(droneMarker.getLatLng(), 17, { animate: true });
            }

            // Update polyline styling for drone
            if (movementTrail) {
                movementTrail.setStyle({ color: '#0284c7' });
            }

            // Mode Badge
            if (elements.testModeBadge) elements.testModeBadge.style.display = 'inline-flex';
            if (elements.modeBadgeText) elements.modeBadgeText.textContent = 'Live Hardware Stream (ESP32)';
            if (elements.gpsSourceText) elements.gpsSourceText.textContent = 'GPS Source: ESP32 / Cube Orange+';

            // Hide phone hotspot banner, show ESP32 WebSocket bridge banner
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'flex';
            if (location.protocol === 'https:' && elements.esp32HttpsTip) {
                if (elements.esp32HttpsTip) elements.esp32HttpsTip.style.display = 'block';
            }

            // Buttons & Headers
            if (elements.centerButtonText) elements.centerButtonText.textContent = 'Center Drone';
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Live Tactical Map (Cube Orange+ / ESP32)';
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Drone Telemetry & Hardware Overview';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valDronesInAir) elements.valDronesInAir.textContent = '1';
            if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = '1';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'ESP32 Wi-Fi';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'Cube Orange+ Telem (UART2)';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Cube Orange+ → ESP32 → Wi-Fi';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Direct Hardware Stream';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`;
                    }

        try {
            localStorage.setItem('utm_active_mode', newMode);
        } catch (e) {}

        if (newMode === 'drone' && !esp32WebSocket && location.protocol !== 'https:') {
            setTimeout(connectEsp32WebSocket, 250);
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

    let activeTelemetryTargetId = null;

    
    function resetTelemetryUI() {
        if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = 'Coordinates: --, --';
        if (elements.hudAlt) elements.hudAlt.textContent = '--';
        if (elements.hudHdg) elements.hudHdg.textContent = '--';
        if (elements.hudSpeed) elements.hudSpeed.textContent = '--';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = '--';

        if (elements.valLatitude) elements.valLatitude.textContent = '--';
        if (elements.subLatitude) elements.subLatitude.textContent = '--';
        if (elements.valLongitude) elements.valLongitude.textContent = '--';
        if (elements.valAltitude) elements.valAltitude.textContent = '--';
        if (elements.valHeading) elements.valHeading.textContent = '--';
        if (elements.valSpeed) elements.valSpeed.textContent = '--';
        if (elements.valAccuracy) elements.valAccuracy.textContent = '--';
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = '--';
    }

    function updateTelemetryCards(telemetryData) {
        if (!telemetryData) return;
        const lat = parseFloat(telemetryData.latitude);
        const lon = parseFloat(telemetryData.longitude);
        const alt = telemetryData.altitude !== null && telemetryData.altitude !== undefined ? parseFloat(telemetryData.altitude) : null;
        const hdg = telemetryData.heading !== null && telemetryData.heading !== undefined ? parseFloat(telemetryData.heading) : null;
        const speed = telemetryData.speed !== null && telemetryData.speed !== undefined ? parseFloat(telemetryData.speed) : null;
        const accuracy = telemetryData.accuracy !== null && telemetryData.accuracy !== undefined ? parseFloat(telemetryData.accuracy) : null;
        
        if (elements.mapCoordinatesHud) {
            if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
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
                    if (elements.valAccuracy) elements.valAccuracy.textContent = `${accuracy.toFixed(1)} m`;
                }
            } else {
                if (elements.valAccuracy) elements.valAccuracy.textContent = 'N/A';
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
        if (activeMarker === null) return; // Don't update HUD or Cards if user deselected map
        if (elements.mapCoordinatesHud) {
            if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
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
                    elements.valAccuracy.innerHTML = `<span style="color: #10b981; font-weight: 700;">${accuracy.toFixed(1)} m</span>`;
                }
            } else {
                if (elements.valAccuracy) elements.valAccuracy.textContent = 'N/A';
            }
        }

        if (elements.subAccuracy) {
            if (accuracy !== null) {
                if (accuracy > 100) {
                    if (elements.subAccuracy) elements.subAccuracy.textContent = 'Coarse Cell Tower (~1.4km) — Enable Precise Location on Phone';
                    if (elements.subAccuracy) elements.subAccuracy.style.color = '#ef4444';
                } else if (accuracy > 25) {
                    if (elements.subAccuracy) elements.subAccuracy.textContent = 'Moderate GPS accuracy (Acquiring satellites)';
                    if (elements.subAccuracy) elements.subAccuracy.style.color = '#b45309';
                } else {
                    if (elements.subAccuracy) elements.subAccuracy.textContent = 'High-precision satellite lock';
                    if (elements.subAccuracy) elements.subAccuracy.style.color = '#047857';
                }
            } else {
                if (elements.subAccuracy) elements.subAccuracy.textContent = 'Unavailable';
                if (elements.subAccuracy) elements.subAccuracy.style.color = 'var(--text-muted)';
            }
        }

        if (activeMarker !== null) {
            if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        }

        // 4. Update Connection Status
        const secondsAgo = apiState ? apiState.seconds_since_update : 0;
        updateConnectionStatus(apiState ? apiState.is_connected : true, secondsAgo);
    }

    // -------------------------------------------------------------------------
    // Drone Telemetry Update (For Drone Mode)
    // -------------------------------------------------------------------------
    function updateDroneUI(telemetryData, apiState) {
        if (!telemetryData) return;

        const lat = parseFloat(telemetryData.latitude !== undefined ? telemetryData.latitude : telemetryData.lat);
        const lon = parseFloat(telemetryData.longitude !== undefined ? telemetryData.longitude : telemetryData.lon);
        const alt = parseFloat(telemetryData.altitude !== undefined ? telemetryData.altitude : (telemetryData.alt !== undefined ? telemetryData.alt : 0));
        const rawHdg = parseFloat(telemetryData.heading !== undefined ? telemetryData.heading : (telemetryData.hdg !== undefined ? telemetryData.hdg : 0));
        const hdg = (isNaN(rawHdg) || rawHdg > 360 || rawHdg < 0) ? 0 : rawHdg;
        const timeStr = formatTime(telemetryData.timestamp || telemetryData.received_at || new Date().toISOString());

        if (isNaN(lat) || isNaN(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) {
            console.warn('[UTM] Out-of-bounds or NaN coordinates received:', lat, lon);
            return;
        }

        // If GPS has not acquired 3D lock yet (Cube sends 0, 0)
        if (lat === 0 && lon === 0) {
            if (elements.mapCoordinatesHud) {
                if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = 'GPS: Waiting for 3D satellite lock (lat: 0, lon: 0)';
            }
            if (elements.hudAccuracy) elements.hudAccuracy.textContent = 'No Lock';
            if (elements.valAccuracy) elements.valAccuracy.innerHTML = '<span style="color: #f59e0b; font-weight: 700;">Acquiring Sats</span>';
            if (elements.subAccuracy) elements.subAccuracy.textContent = 'Hardware Connected (Indoor / Searching)';
            if (elements.valAltitude) elements.valAltitude.textContent = `${alt.toFixed(1)} m`;
            return;
        }

        lastKnownLat = lat;
        lastKnownLon = lon;
        lastKnownHeading = hdg;

        // Auto-center map on first valid drone GPS fix
        if (!hasReceivedFirstDroneFix && map && lat !== 0 && lon !== 0) {
            map.setView([lat, lon], 17, { animate: true });
            hasReceivedFirstDroneFix = true;
        }

        
        // Update Drone Marker Position & Rotator
        if (!droneMarker) {
            droneMarker = L.marker([lat, lon], {
                icon: createDroneIcon(hdg),
                title: 'Drone 01 (Cube Orange+ / ESP32)',
                zIndexOffset: 1000
            });
            droneMarker.bindPopup(`
                <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                    <strong style="color: #0284c7;">Drone 01 — Cube Orange+</strong><br>
                    <span>Target: ESP32 Wi-Fi Telemetry</span>
                </div>
            `);
            if (activeMode === 'drone') {
                droneMarker.addTo(map);
                activeMarker = droneMarker;
            }
        }
        
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
        if (activeMarker === null) return; // Don't update HUD or Cards if user deselected map
        if (elements.mapCoordinatesHud) {
            if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.mapRouteHud) {
            if (elements.mapRouteHud) elements.mapRouteHud.textContent = `Source: ESP32 (${telemetryData.drone_id || telemetryData.id || 'DRONE-ALPHA'})`;
            if (elements.mapRouteHud) elements.mapRouteHud.style.background = '#e0f2fe';
            if (elements.mapRouteHud) elements.mapRouteHud.style.borderColor = '#bae6fd';
            if (elements.mapRouteHud) elements.mapRouteHud.style.color = '#0369a1';
        }
        if (elements.hudAlt) elements.hudAlt.textContent = `${alt.toFixed(1)} m`;
        if (elements.hudHdg) elements.hudHdg.textContent = `${Math.round(hdg)}°`;

        const rawSpeed = telemetryData.speed !== undefined ? parseFloat(telemetryData.speed) : null;
        const spdText = (rawSpeed !== null && !isNaN(rawSpeed)) ? `${rawSpeed.toFixed(1)} m/s` : 'Stationary';
        const spdKmText = (rawSpeed !== null && !isNaN(rawSpeed)) ? `${(rawSpeed * 3.6).toFixed(1)} km/h` : '0.0 km/h';

        if (elements.hudSpeed) elements.hudSpeed.textContent = spdText;
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = 'Hardware Fix';

        // Update Cards using unified generic function
        if (activeMarker !== null) {
            updateTelemetryCards(telemetryData);
            if (activeMarker !== null) {
            if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;
        }
        }

        const isHw = apiState ? apiState.hardware_connected : true;
        const secondsAgo = apiState ? apiState.seconds_since_update : 0;
        updateConnectionStatus(isHw, secondsAgo, apiState ? apiState.status_label : null);
    }

    // -------------------------------------------------------------------------
    // Connection Status Manager
    // -------------------------------------------------------------------------
    function updateConnectionStatus(isConnected, secondsAgo, customLabel) {
        const secText = (secondsAgo !== null && secondsAgo !== undefined) ? `${secondsAgo.toFixed(1)}s ago` : 'never';

        if (elements.statusHeartbeatSec) {
            if (elements.statusHeartbeatSec) elements.statusHeartbeatSec.textContent = (secondsAgo !== null && secondsAgo !== undefined) ? secondsAgo.toFixed(1) : '--';
        }
        if (elements.subLastUpdate) {
            if (activeMode === 'phone' && !isConnected && secondsAgo && secondsAgo > 10) {
                if (elements.subLastUpdate) elements.subLastUpdate.textContent = `Last update: ${secText} (disconnected / frozen)`;
                if (elements.subLastUpdate) elements.subLastUpdate.style.color = '#ef4444';
            } else {
                if (elements.subLastUpdate) elements.subLastUpdate.textContent = `Last update: ${secText}`;
                if (elements.subLastUpdate) elements.subLastUpdate.style.color = 'var(--text-muted)';
            }
        }

        if (activeMode === 'simulator') {
            if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status connected';
            if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-green';
            if (elements.statusLabel) elements.statusLabel.textContent = '🟢 Simulation Connected';

            if (elements.statusConnBadge) {
                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill pill-green';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-green';
                if (elements.statusConnText) elements.statusConnText.textContent = '🟢 Simulated Drones Active';
                if (elements.statusConnHint) elements.statusConnHint.textContent = 'Random flight paths';
            }
        } else if (activeMode === 'phone') {
            if (isConnected) {
                // 🟢 Phone Connected
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status connected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-green';
                if (elements.statusLabel) elements.statusLabel.textContent = '🟢 Phone Connected';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill pill-green';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-green';
                if (elements.statusConnText) elements.statusConnText.textContent = '🟢 Phone Connected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = `Live GPS packets active (${secText})`;

                // Update Banner for Connected state
                if (elements.hotspotBanner) elements.hotspotBanner.classList.add('is-connected');
                if (elements.bannerTitle) elements.bannerTitle.textContent = `🟢 Phone GPS Streaming Live (${targetPhoneDeviceId})`;
                if (elements.bannerHelpText) elements.bannerHelpText.textContent = `Streaming to tactical map (${secText}):`;
            } else {
                // 🔴 Phone Disconnected
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status disconnected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-red';
                if (elements.statusLabel) elements.statusLabel.textContent = '🔴 Phone Disconnected';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-red';
                if (elements.statusConnText) elements.statusConnText.textContent = '🔴 Phone Disconnected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = `No GPS updates (${secText}). Coordinates frozen. Check /mobile/`;

                // Update Banner for Disconnected state
                if (elements.hotspotBanner) elements.hotspotBanner.classList.remove('is-connected');
                if (elements.bannerTitle) elements.bannerTitle.textContent = '📱 Phone GPS Test Mode — Connect Your Smartphone';
                if (elements.bannerHelpText) elements.bannerHelpText.textContent = 'Open on phone or scan QR code:';
            }
        } else {
            // Drone Mode (ESP32 Hardware)
            if (isConnected) {
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status connected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-green';
                if (elements.statusLabel) elements.statusLabel.textContent = 'Drone Connected (ESP32 Live)';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill pill-green';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-green';
                if (elements.statusConnText) elements.statusConnText.textContent = 'ESP32 Broadcasting';
                if (elements.statusConnHint) elements.statusConnHint.textContent = 'Hardware online';
            } else {
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status disconnected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-red';
                if (elements.statusLabel) elements.statusLabel.textContent = 'Drone Not Connected';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-red';
                if (elements.statusConnText) elements.statusConnText.textContent = 'Disconnected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = 'Awaiting ESP32 packet';
            }
        }
    }

    // -------------------------------------------------------------------------
    // Polling Logic
    // -------------------------------------------------------------------------
    async function fetchActiveTelemetry() {
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
                });
            }
        } catch (e) {
            console.warn('[UTM] Main Mode Drones error:', e);
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
        try {
            const response = await fetch(`/api/telemetry/latest/?drone_id=${targetDroneId}`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.status === 'success' && data.telemetry) {
                totalPacketCount++;
                if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                lastReceivedTimestamp = Date.now();
                updateDroneUI(data.telemetry, data);
            } else if (data.status === 'waiting') {
                if (!esp32WebSocket || esp32WebSocket.readyState !== WebSocket.OPEN) {
                    updateConnectionStatus(false, null, data.status_label);
                }
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
                if (elements.statusHeartbeatSec) elements.statusHeartbeatSec.textContent = secondsAgo.toFixed(1);
            }
            if (elements.subLastUpdate) {
                if (elements.subLastUpdate) elements.subLastUpdate.textContent = `Last update: ${secondsAgo.toFixed(1)}s ago`;
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
                if (elements.btnTrackThisDeviceText) elements.btnTrackThisDeviceText.textContent = '⏹️ Stop Live Tracking';
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
                    if (elements.bannerTitle) elements.bannerTitle.textContent = `🟢 Device GPS Live (Accurate to ${accuracy !== null ? accuracy + 'm' : 'GPS fix'})`;
                }
                if (elements.bannerHelpText) {
                    if (elements.bannerHelpText) elements.bannerHelpText.textContent = `Streaming location directly to tactical map:`;
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
                timeout: 30000,
                maximumAge: 0
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
                if (elements.btnTrackThisDeviceText) elements.btnTrackThisDeviceText.textContent = 'Track My Location Live';
            }
        }
        if (elements.bannerTitle) {
            if (elements.bannerTitle) elements.bannerTitle.textContent = '📱 Live GPS Mode — Track Direct or Connect Phone';
        }
        if (elements.bannerHelpText) {
            if (elements.bannerHelpText) elements.bannerHelpText.textContent = 'Click below to track this device live, or scan QR code on smartphone:';
        }
    }

    // -------------------------------------------------------------------------
    // ESP32 Direct WebSocket Bridge Client
    // -------------------------------------------------------------------------
    let esp32WebSocket = null;

    function connectEsp32WebSocket() {
        const wsUrl = (elements.esp32WsInput ? elements.esp32WsInput.value.trim() : '') || 'ws://192.168.43.150:81';
        if (!wsUrl.startsWith('ws://') && !wsUrl.startsWith('wss://')) {
            alert('Invalid WebSocket URL. Must start with ws:// or wss:// (e.g. ws://192.168.43.150:81)');
            return;
        }

        if (location.protocol === 'https:' && wsUrl.startsWith('ws://')) {
            console.warn('[UTM] Browser security blocks insecure ws:// from an https:// origin.');
            if (elements.esp32HttpsTip) elements.esp32HttpsTip.style.display = 'block';
            updateEsp32WsStatus('disconnected', 'HTTPS Blocked ws://');
            return;
        }

        try {
            localStorage.setItem('utm_esp32_ws_url', wsUrl);
        } catch (e) {}

        if (esp32WebSocket) {
            try { esp32WebSocket.close(); } catch (e) {}
            esp32WebSocket = null;
        }

        updateEsp32WsStatus('connecting', 'Connecting...');

        try {
            esp32WebSocket = new WebSocket(wsUrl);

            esp32WebSocket.onopen = () => {
                console.log('[UTM] ESP32 WebSocket connected to:', wsUrl);
                updateEsp32WsStatus('connected', '🟢 ESP32 Live');
                if (elements.btnConnectEspWs) elements.btnConnectEspWs.style.display = 'none';
                if (elements.btnDisconnectEspWs) elements.btnDisconnectEspWs.style.display = 'inline-block';
            };

            esp32WebSocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    // Handle Esp_utm.ino format:
                    // {"id":"DRONE-ALPHA","lat":30.981485,"lon":76.525563,"alt":15.4,"heading":142.5}
                    const lat = parseFloat(data.lat !== undefined ? data.lat : data.latitude);
                    const lon = parseFloat(data.lon !== undefined ? data.lon : data.longitude);
                    const alt = parseFloat(data.alt !== undefined ? data.alt : (data.altitude || 0));
                    const hdg = parseFloat(data.heading !== undefined ? data.heading : (data.hdg || 0));
                    const droneId = data.id || data.drone_id || 'DRONE-ALPHA';

                    if (isNaN(lat) || isNaN(lon)) return;

                    // Automatically switch to Drone mode if currently in Phone mode
                    if (activeMode !== 'drone') {
                        setDashboardMode('drone');
                    }

                    totalPacketCount++;
                    if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                    lastReceivedTimestamp = Date.now();

                    const telemetryObj = {
                        drone_id: droneId,
                        latitude: lat,
                        longitude: lon,
                        altitude: alt,
                        heading: hdg,
                        timestamp: new Date().toISOString(),
                        received_at: new Date().toISOString(),
                        is_simulated: false
                    };

                    const apiState = {
                        hardware_connected: true,
                        is_connected: true,
                        seconds_since_update: 0.1,
                        status_label: 'Drone Connected (ESP32 Live)',
                        hardware_status_label: 'Hardware Online (ESP32 Live Stream)'
                    };

                    // Update Map & Telemetry Cards immediately with sub-10ms latency!
                    updateDroneUI(telemetryObj, apiState);

                    // Forward to Django backend asynchronously so history & breadcrumbs are preserved
                    fetch('/api/telemetry/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(telemetryObj)
                    }).catch(() => {});

                } catch (parseErr) {
                    console.warn('[UTM] Error parsing ESP32 WebSocket packet:', parseErr);
                }
            };

            esp32WebSocket.onerror = (err) => {
                console.warn('[UTM] ESP32 WebSocket error:', err);
                updateEsp32WsStatus('disconnected', 'ESP32 Error');
            };

            esp32WebSocket.onclose = () => {
                console.log('[UTM] ESP32 WebSocket disconnected.');
                updateEsp32WsStatus('disconnected', 'ESP32 Offline');
                if (elements.btnConnectEspWs) elements.btnConnectEspWs.style.display = 'inline-block';
                if (elements.btnDisconnectEspWs) elements.btnDisconnectEspWs.style.display = 'none';
            };

        } catch (err) {
            console.error('[UTM] Failed to create WebSocket connection:', err);
            updateEsp32WsStatus('disconnected', 'Connection Failed');
        }
    }

    function disconnectEsp32WebSocket() {
        if (esp32WebSocket) {
            try { esp32WebSocket.close(); } catch (e) {}
            esp32WebSocket = null;
        }
        updateEsp32WsStatus('disconnected', 'ESP32 Offline');
        if (elements.btnConnectEspWs) elements.btnConnectEspWs.style.display = 'inline-block';
        if (elements.btnDisconnectEspWs) elements.btnDisconnectEspWs.style.display = 'none';
    }

    function updateEsp32WsStatus(state, text) {
        if (!elements.esp32WsStatusBadge || !elements.esp32WsDot || !elements.esp32WsStatusText) return;
        if (elements.esp32WsStatusText) elements.esp32WsStatusText.textContent = text;
        if (state === 'connected') {
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.background = '#ecfdf5';
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.color = '#065f46';
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.borderColor = '#a7f3d0';
            elements.esp32WsDot.className = 'status-indicator-dot dot-green';
        } else if (state === 'connecting') {
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.background = '#fffbeb';
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.color = '#b45309';
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.borderColor = '#fde68a';
            elements.esp32WsDot.className = 'status-indicator-dot dot-amber';
        } else {
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.background = '#fef2f2';
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.color = '#b91c1c';
            if (elements.esp32WsStatusBadge) elements.esp32WsStatusBadge.style.borderColor = '#fecaca';
            elements.esp32WsDot.className = 'status-indicator-dot dot-red';
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

        // ESP32 WebSocket Bridge Controls
        if (elements.btnConnectEspWs) elements.btnConnectEspWs.addEventListener('click', connectEsp32WebSocket);
        if (elements.btnDisconnectEspWs) elements.btnDisconnectEspWs.addEventListener('click', disconnectEsp32WebSocket);
        if (elements.esp32WsInput) {
            elements.esp32WsInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') connectEsp32WebSocket();
            });
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

        // Tester Panel
        if (elements.btnToggleTester) {
            elements.btnToggleTester.addEventListener('click', () => {
                const isHidden = elements.testerPanel && elements.testerPanel.style.display === 'none';
                if (elements.testerPanel) elements.testerPanel.style.display = isHidden ? 'block' : 'none';
                if (isHidden) elements.testerPanel.scrollIntoView({ behavior: 'smooth' });
            });
        }
        if (elements.btnCloseTester) {
            elements.btnCloseTester.addEventListener('click', () => {
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
                    if (elements.testerFeedback) elements.testerFeedback.style.display = 'block';
                    elements.testerFeedback.className = res.ok ? 'tester-feedback success' : 'tester-feedback error';
                    if (elements.testerFeedback) elements.testerFeedback.textContent = res.ok ?
                        `Packet transmitted successfully (${res.status} Created) to ${endpoint}` :
                        `Error: ${JSON.stringify(resData)}`;
                    fetchActiveTelemetry();
                } catch (err) {
                    if (elements.testerFeedback) elements.testerFeedback.style.display = 'block';
                    elements.testerFeedback.className = 'tester-feedback error';
                    if (elements.testerFeedback) elements.testerFeedback.textContent = `Transmission failed: ${err.message}`;
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
                if (!elements.qrModalBackdrop) return;
                if (elements.qrModalBackdrop) elements.qrModalBackdrop.style.display = 'flex';
                const skeleton = document.getElementById('qrCardSkeleton');
                const actual = document.getElementById('qrCardActual');
                const gradientBg = document.getElementById('qrGradientBg');
                
                // Reset initial state
                if(skeleton) skeleton.style.opacity = '1';
                if(actual) {
                    actual.style.display = 'none';
                    actual.style.opacity = '0';
                }
                if(gradientBg) gradientBg.style.opacity = '0';

                // Sequence
                setTimeout(() => {
                    if(gradientBg) gradientBg.style.opacity = '1';
                    setTimeout(() => {
                        if(skeleton) skeleton.style.opacity = '0';
                        setTimeout(() => {
                            if(actual) {
                                actual.style.display = 'flex';
                                // Trigger reflow
                                void actual.offsetWidth;
                                actual.style.opacity = '1';
                            }
                        }, 500);
                    }, 500);
                }, 800);
            });
        }
        if (elements.btnCloseQrModal) {
            elements.btnCloseQrModal.addEventListener('click', () => {
                if (elements.qrModalBackdrop) elements.qrModalBackdrop.style.display = 'none';
            });
        }
        if (elements.qrModalBackdrop) {
            elements.qrModalBackdrop.addEventListener('click', (e) => {
                if (e.target === elements.qrModalBackdrop) {
                    if (elements.qrModalBackdrop) elements.qrModalBackdrop.style.display = 'none';
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
    // Simulator Mode Logic
    // -------------------------------------------------------------------------
    const SIM_DRONES = [
        { name: 'Personal', color: '#3b82f6', desc: 'Blue: Personal' },
        { name: 'Commercial', color: '#eab308', desc: 'Yellow: Commercial (point to point delivery, medical)' },
        { name: 'Education/Research', color: '#22c55e', desc: 'Green: Education/Research' },
        { name: 'Training', color: '#ef4444', desc: 'Red: Training (RPTO/NCC/others)' },
        { name: 'Government', color: '#000000', desc: 'Black: Govt. (for surveillance & others)' }
    ];

    let simulatorState = {
        active: false,
        markers: [],
        interval: null,
        legend: null
    };

    function createSimulatorIcon(color) {
        return L.divIcon({
            className: 'custom-drone-icon',
            html: `
                <div style="position:relative; width:48px; height:48px;">
                    <svg viewBox="0 0 100 100" style="width:100%; height:100%;">
                        <circle cx="22" cy="22" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                        <circle cx="78" cy="22" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                        <circle cx="22" cy="78" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                        <circle cx="78" cy="78" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                        <rect x="36" y="36" width="28" height="28" rx="6" fill="${color}" stroke="#ffffff" stroke-width="2"/>
                    </svg>
                </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });
    }

    window.startSimulator = function() {
        if (simulatorState.active) return;
        simulatorState.active = true;
        
        const LegendControl = L.Control.extend({
            onAdd: function (map) {
                let div = L.DomUtil.create('div', 'simulator-legend');
                div.style.backgroundColor = 'white';
                div.style.padding = '12px';
                div.style.borderRadius = '8px';
                div.style.boxShadow = '0 2px 10px rgba(0,0,0,0.15)';
                div.style.fontSize = '13px';
                div.style.fontFamily = 'Outfit, sans-serif';
                div.style.color = '#333';
                div.innerHTML = '<strong style="display:block;margin-bottom:8px;font-size:14px;color:#002D74;">Simulated Drones</strong>';
                SIM_DRONES.forEach(d => {
                    let row = document.createElement('div');
                    row.style.display = 'flex';
                    row.style.alignItems = 'center';
                    row.style.marginBottom = '6px';
                    row.style.cursor = 'help';
                    row.title = d.desc;
                    row.innerHTML = `<span style="display:inline-block;width:14px;height:14px;background-color:${d.color};margin-right:10px;border-radius:3px;border:1px solid #ccc;"></span><span style="font-weight:500;">${d.name}</span>`;
                    div.appendChild(row);
                });
                return div;
            }
        });
        simulatorState.legend = new LegendControl({ position: 'bottomright' });
        simulatorState.legend.addTo(map);

        let startLat = lastKnownLat || 28.6139;
        let startLng = lastKnownLon || 77.2090;

        SIM_DRONES.forEach((d, index) => {
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
        });

        map.setView([startLat, startLng], 14, {animate: true});

        if (elements.valDronesInAir) {
            elements.valDronesInAir.textContent = simulatorState.markers.length;
        }

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
                
                if (Math.abs(d.lat - oldLat) > 0.00001 || Math.abs(d.lng - oldLng) > 0.00001) {
                    d.pathCoords.push([d.lat, d.lng]);
                    if (d.pathCoords.length > 100) d.pathCoords.shift();
                    d.path.setLatLngs(d.pathCoords);
                }
                
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
    };

    window.stopSimulator = function() {
        if (!simulatorState.active) return;
        simulatorState.active = false;
        if (simulatorState.legend) {
            map.removeControl(simulatorState.legend);
            simulatorState.legend = null;
        }
        simulatorState.markers.forEach(d => {
            map.removeLayer(d.marker);
            if (d.path) map.removeLayer(d.path);
        });
        simulatorState.markers = [];
        if (simulatorState.interval) {
            clearInterval(simulatorState.interval);
            simulatorState.interval = null;
        }
    };

    // -------------------------------------------------------------------------
    // Main Initialization
    // -------------------------------------------------------------------------
    function init() {
        initMap();
        bindEvents();
        startHeartbeatCounter();

        try {
            const savedWsUrl = localStorage.getItem('utm_esp32_ws_url');
            if (savedWsUrl && elements.esp32WsInput) {
                elements.esp32WsInput.value = savedWsUrl;
            }
        } catch (e) {}

        const urlParams = new URLSearchParams(window.location.search);
        const requestedMode = urlParams.get('mode') || (function() {
            try { return localStorage.getItem('utm_active_mode'); } catch (e) { return null; }
        })();

        if (requestedMode === 'drone') {
            setDashboardMode('drone');
        }

        pollTimer = setInterval(fetchActiveTelemetry, 1000);
        fetchActiveTelemetry();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.setDashboardMode = setDashboardMode; 
    window.clearMapHistory = function() { 
        trailCoordinates = []; 
        if (movementTrail) movementTrail.setLatLngs([]); 
        
        // Clear all main mode markers
        for (let id in mainModeMarkers) {
            if (mainModeMarkers[id]) map.removeLayer(mainModeMarkers[id]);
        }
        mainModeMarkers = {};
        
        // Clear phone/drone marker
        if (droneMarker) {
            map.removeLayer(droneMarker);
            droneMarker = null;
        }
        
        // Clear simulator markers
        if (typeof simulatorState !== 'undefined' && simulatorState.markers) {
            simulatorState.markers.forEach(m => {
                if (m.marker) map.removeLayer(m.marker);
                if (m.circle) map.removeLayer(m.circle);
                if (m.path) map.removeLayer(m.path);
            });
            simulatorState.markers = [];
        }
        
        activeMarker = null;
        resetTelemetryUI();
    }; 
})();

