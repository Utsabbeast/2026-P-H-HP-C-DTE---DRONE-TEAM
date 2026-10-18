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
    const droneTimeoutSeconds = 15.0; // Strictly show only packets from the last 15 seconds
    const phoneTimeoutSeconds = 15.0;
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

    // Digital Sky Platform Airspace State
    let isDigitalSkyActive = false;
    let digitalSkyAirspaceGroup = null;
    let digitalSkyGeojsonData = null;
    let currentAirspaceAssessment = null;
    let baseMapsControl = null;
    let tileLayers = {
        googleStreets: null,
        googleSatellite: null,
        googleHybrid: null,
        googleTerrain: null
    };

    // Telemetry State
    let lastReceivedTimestamp = null;
    let totalPacketCount = 0;
    let pollTimer = null;
    let heartbeatTimer = null;
    var esp32MqttClient = null;

    // Last known coordinates (fallback default: Ludhiana test site 30.9010°, 75.8573°)
    let lastKnownLat = 30.9010;
    let lastKnownLon = 75.8573;
    let lastKnownHeading = 142.0;
    let hasReceivedFirstPhoneFix = false;
    let hasReceivedFirstDroneFix = false;
    const lastPositionsPerDrone = {};

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

        // ESP32 4G LTE MQTT Elements
        esp32MqttTopic: document.getElementById('esp32MqttTopic'),
        btnConnectEspMqtt: document.getElementById('btnConnectEspMqtt'),
        btnDisconnectEspMqtt: document.getElementById('btnDisconnectEspMqtt'),
        esp32MqttStatusBadge: document.getElementById('esp32MqttStatusBadge'),
        esp32MqttDot: document.getElementById('esp32MqttDot'),
        esp32MqttStatusText: document.getElementById('esp32MqttStatusText'),
        esp32BattBadge: document.getElementById('esp32BattBadge'),
        esp32BattText: document.getElementById('esp32BattText'),
        esp32AttitudeBadge: document.getElementById('esp32AttitudeBadge'),
        esp32AttitudeText: document.getElementById('esp32AttitudeText'),

        // Legacy ESP32 Hardware Banner Elements
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
        hudZone: document.getElementById('hudZone'),
        hudZoneContainer: document.getElementById('hudZoneContainer'),

        // Buttons
        btnCenterDrone: document.getElementById('btnCenterDrone'),
        centerButtonText: document.getElementById('centerButtonText'),
        btnClearTrail: document.getElementById('btnClearTrail'),
        btnToggleTrail: document.getElementById('btnToggleTrail'),
        trailButtonText: document.getElementById('trailButtonText'),
        btnResetView: document.getElementById('btnResetView'),
        btnToggleDigitalSky: document.getElementById('btnToggleDigitalSky'),
        digitalSkyButtonText: document.getElementById('digitalSkyButtonText'),
        digitalSkyLegend: document.getElementById('digitalSkyLegend'),
        btnCloseLegend: document.getElementById('btnCloseLegend'),
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
        cardBattery: document.getElementById('cardBattery'),
        valBattery: document.getElementById('valBattery'),
        subBattery: document.getElementById('subBattery'),
        cardFlightMode: document.getElementById('cardFlightMode'),
        valFlightMode: document.getElementById('valFlightMode'),
        subFlightMode: document.getElementById('subFlightMode'),
        cardAttitude: document.getElementById('cardAttitude'),
        valAttitude: document.getElementById('valAttitude'),
        subAttitude: document.getElementById('subAttitude'),
        cardDroneId: document.getElementById('cardDroneId'),
        valDroneId: document.getElementById('valDroneId'),
        subDroneId: document.getElementById('subDroneId'),
        hudBattery: document.getElementById('hudBattery'),
        hudAttitude: document.getElementById('hudAttitude'),
        hudDroneId: document.getElementById('hudDroneId'),
        btnFitFleet: document.getElementById('btnFitFleet'),
        fleetCountBtn: document.getElementById('fleetCountBtn'),
        fleetSelectorContainer: document.getElementById('fleetSelectorContainer'),
        fleetDronePills: document.getElementById('fleetDronePills'),
        hudFleetItem: document.getElementById('hudFleetItem'),
        hudFleetDivider: document.getElementById('hudFleetDivider'),
        hudFleetCount: document.getElementById('hudFleetCount'),

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

    function getDroneColor(droneId) {
        if (!droneId) return '#0284c7';
        if (droneId.includes('40573255F188')) return '#ea580c'; // Assigned Orange/Amber for DRONE-40573255F188
        if (droneId.includes('ALPHA') || droneId.includes('01')) return '#0284c7'; // Sky Blue for Drone 1
        const palette = ['#0284c7', '#ea580c', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4'];
        let hash = 0;
        for (let i = 0; i < droneId.length; i++) hash += droneId.charCodeAt(i);
        return palette[Math.abs(hash) % palette.length];
    }

    function createMultiDroneIcon(heading, droneId, color = '#0284c7', alt = null) {
        const hdg = heading !== null && !isNaN(heading) ? heading : 0;
        const safeDroneId = droneId || 'DRONE-ALPHA';
        const sanitizedId = safeDroneId.replace(/[^a-zA-Z0-9_-]/g, '_');
        const label = safeDroneId.length > 14 ? safeDroneId.slice(-6) : safeDroneId;
        const altText = (alt !== null && alt !== undefined && !isNaN(alt)) ? `${alt.toFixed(1)}m` : '';

        return L.divIcon({
            className: 'drone-custom-marker-wrapper',
            html: `
                <div class="drone-marker-container" style="position: relative;">
                    <div class="drone-marker-pulse" style="border-color: ${color};"></div>
                    <div class="drone-marker-rotator" id="droneRotator_${sanitizedId}" style="transform: rotate(${hdg}deg); transition: transform 0.3s ease;">
                        <svg class="drone-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <!-- Forward Direction Indicator -->
                            <path d="M50 6 L62 28 H38 Z" fill="#ef4444"/>
                            <!-- Diagonal Quadcopter Carbon Arms -->
                            <line x1="22" y1="22" x2="78" y2="78" stroke="${color}" stroke-width="6" stroke-linecap="round"/>
                            <line x1="78" y1="22" x2="22" y2="78" stroke="${color}" stroke-width="6" stroke-linecap="round"/>
                            <!-- 4 Rotor Motors -->
                            <circle cx="22" cy="22" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                            <circle cx="78" cy="22" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                            <circle cx="22" cy="78" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                            <circle cx="78" cy="78" r="11" stroke="${color}" stroke-width="3" fill="#ffffff"/>
                            <!-- Center Flight Avionics Housing (Cube Orange+) -->
                            <rect x="34" y="34" width="32" height="32" rx="7" fill="#0f172a" stroke="${color}" stroke-width="2.5"/>
                            <circle cx="50" cy="50" r="5" fill="#22c55e"/>
                        </svg>
                    </div>
                    <!-- Drone Callout Badge with ID & Altitude -->
                    <div style="position: absolute; top: -16px; left: 50%; transform: translateX(-50%); background: #0f172a; color: #ffffff; border: 1.5px solid ${color}; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 800; font-family: monospace; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.4); pointer-events: none; z-index: 10;">
                        ${label}${altText ? ' • ' + altText : ''}
                    </div>
                </div>
            `,
            iconSize: [48, 48],
            iconAnchor: [24, 24]
        });
    }

    function createDroneIcon(heading, droneId = 'DRONE-ALPHA') {
        const color = getDroneColor(droneId);
        return createMultiDroneIcon(heading, droneId, color);
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
        map.on('click', function (e) {
            activeMarker = null;
            activeTelemetryTargetId = null;
            resetTelemetryUI();
        });

        // Premier Map Tile Providers (4 Google Maps Modes)
        tileLayers.googleStreets = L.tileLayer('https://mt1.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            attribution: '&copy; Google Maps (Roadmap)'
        });

        tileLayers.googleSatellite = L.tileLayer('https://mt1.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            attribution: '&copy; Google Maps (Satellite)'
        });

        tileLayers.googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            attribution: '&copy; Google Maps (Hybrid)'
        });

        tileLayers.googleTerrain = L.tileLayer('https://mt1.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            attribution: '&copy; Google Maps (Terrain)'
        });

        // Add Default Base Layer (Google Streets)
        tileLayers.googleStreets.addTo(map);

        // Custom Leaflet Panes for strictly layered Airspace visibility
        if (!map.getPane('greenZonePane')) {
            map.createPane('greenZonePane');
            map.getPane('greenZonePane').style.zIndex = '405';
        }
        if (!map.getPane('yellowZonePane')) {
            map.createPane('yellowZonePane');
            map.getPane('yellowZonePane').style.zIndex = '420';
        }
        if (!map.getPane('redZonePane')) {
            map.createPane('redZonePane');
            map.getPane('redZonePane').style.zIndex = '450';
        }

        // Digital Sky Airspace Feature Group (Red, Yellow, Green Zones)
        digitalSkyAirspaceGroup = L.featureGroup();
        // Add to map by default so Red Zones are visibly highlighted immediately
        digitalSkyAirspaceGroup.addTo(map);
        isDigitalSkyActive = true;
        showDigitalSkyLegend(true);

        const baseMaps = {
            'Google Streets': tileLayers.googleStreets,
            'Google Satellite': tileLayers.googleSatellite,
            'Google Hybrid': tileLayers.googleHybrid,
            'Google Terrain': tileLayers.googleTerrain
        };

        const overlayMaps = {
            'Digital Sky Airspace (Zonal Overlays)': digitalSkyAirspaceGroup
        };

        baseMapsControl = L.control.layers(baseMaps, overlayMaps, { position: 'topleft' }).addTo(map);

        // Ensure proper Leaflet container sizing
        setTimeout(() => {
            if (map) map.invalidateSize();
        }, 250);
        window.addEventListener('resize', () => {
            if (map) map.invalidateSize();
        });

        map.on('overlayadd', function (e) {
            if (e.layer === digitalSkyAirspaceGroup) {
                isDigitalSkyActive = true;
                showDigitalSkyLegend(true);
            }
        });

        map.on('overlayremove', function (e) {
            if (e.layer === digitalSkyAirspaceGroup) {
                isDigitalSkyActive = false;
                showDigitalSkyLegend(false);
            }
        });

        // Load Digital Sky Airspace GeoJSON in background
        loadDigitalSkyAirspaceData();

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
                <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #e2e8f0; font-size: 11px;">
                    <span>Airspace: <strong id="popupAirspacePhone" style="color: #059669;">Green Zone (0-400ft)</strong></span>
                </div>
            </div>
        `);

        // Create drone marker template (markers for live drones are added dynamically via activeDrones only when connected)
        droneMarker = L.marker([lastKnownLat, lastKnownLon], {
            icon: createDroneIcon(lastKnownHeading),
            title: 'PHHP&C Drone 1',
            zIndexOffset: 1000
        });

        droneMarker.bindPopup(`
            <div style="font-family: inherit; font-size: 13px; line-height: 1.4;">
                <strong style="color: #0284c7;">PHHP&C Drone 1</strong><br>
                <span>Target: ESP32 Wi-Fi / 4G Telemetry</span>
                <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #e2e8f0; font-size: 11px;">
                    <span>Airspace: <strong id="popupAirspaceDrone" style="color: #0284c7;">Green Zone (0-400ft)</strong></span>
                </div>
            </div>
        `);

        // Startup: Markers in phone mode are always placed immediately
        if (activeMode === 'phone') {
            phoneMarker.addTo(map);
            activeMarker = phoneMarker;
        }
    }

    // -------------------------------------------------------------------------
    // Digital Sky Airspace Map Engine (DGCA India Drone Rules 2021)
    // -------------------------------------------------------------------------
    async function loadDigitalSkyAirspaceData() {
        try {
            const res = await fetch('/api/digitalsky/zones/');
            if (!res.ok) throw new Error('HTTP ' + res.status);
            digitalSkyGeojsonData = await res.json();

            if (digitalSkyGeojsonData && digitalSkyGeojsonData.features) {
                renderDigitalSkyZones(digitalSkyGeojsonData.features);
                console.log(`[UTM DigitalSky] Loaded ${digitalSkyGeojsonData.features.length} airspace zones.`);
            }
        } catch (err) {
            console.warn('[UTM DigitalSky] Airspace zones fetch notice:', err.message);
        }
    }

    function renderDigitalSkyZones(features) {
        if (!digitalSkyAirspaceGroup) return;
        digitalSkyAirspaceGroup.clearLayers();

        features.forEach(feat => {
            const props = feat.properties || {};
            const zoneType = (props.zone_type || 'GREEN').toUpperCase();
            const geom = feat.geometry;
            if (!geom || (geom.type !== 'Polygon' && geom.type !== 'MultiPolygon')) return;

            // Coordinates in GeoJSON are [lon, lat], Leaflet expects [lat, lon]
            let latlngs;
            if (geom.type === 'Polygon') {
                latlngs = geom.coordinates.map(ring => ring.map(pt => [pt[1], pt[0]]));
            } else {
                latlngs = geom.coordinates.map(poly => poly.map(ring => ring.map(pt => [pt[1], pt[0]])));
            }

            let strokeColor = props.color || '#059669';
            let fillColor = props.fillColor || '#10b981';
            let fillOpacity = props.fillOpacity !== undefined ? props.fillOpacity : 0.12;
            let weight = props.strokeWeight || 1.5;
            let dashArray = props.strokeDashArray || null;

            if (zoneType === 'RED') {
                strokeColor = props.color || '#b91c1c';
                fillColor = props.fillColor || '#ef4444';
                fillOpacity = props.fillOpacity !== undefined ? props.fillOpacity : 0.45;
                weight = props.strokeWeight || 2.5;
            } else if (zoneType === 'YELLOW') {
                strokeColor = props.color || '#d97706';
                fillColor = props.fillColor || '#f59e0b';
                fillOpacity = props.fillOpacity !== undefined ? props.fillOpacity : 0.26;
                weight = props.strokeWeight || 2.0;
                dashArray = props.strokeDashArray || '5, 5';
            }

            const targetPane = zoneType === 'RED' ? 'redZonePane' : (zoneType === 'YELLOW' ? 'yellowZonePane' : 'greenZonePane');

            const polygon = L.polygon(latlngs, {
                pane: targetPane,
                color: strokeColor,
                fillColor: fillColor,
                fillOpacity: fillOpacity,
                weight: weight,
                dashArray: dashArray,
                interactive: true
            });

            // Interactive popup
            const badgeClass = zoneType === 'RED' ? 'red' : (zoneType === 'YELLOW' ? 'yellow' : 'green');
            const badgeIcon = zoneType === 'RED' ? '🔴' : (zoneType === 'YELLOW' ? '🟡' : '🟢');
            const catLabel = props.category ? `<span style="opacity: 0.85; font-size: 0.62rem; margin-left: 4px;">• ${props.category.replace(/_/g, ' ')}</span>` : '';
            const popupHtml = `
                <div class="ds-popup-card">
                    <div class="ds-popup-badge ${badgeClass}">
                        <span>${badgeIcon}</span>
                        <span>${zoneType} ZONE</span>
                        ${catLabel}
                    </div>
                    <div class="ds-popup-title">${props.name || 'Airspace Zone'}</div>
                    <div class="ds-popup-desc">${props.description || ''}</div>
                    <div class="ds-popup-meta">
                        <div class="ds-popup-row">
                            <span class="ds-popup-label">Max Permissible Alt:</span>
                            <span class="ds-popup-val">${props.max_altitude_agl_ft} ft AGL (${props.max_altitude_agl_m || 0} m)</span>
                        </div>
                        <div class="ds-popup-row">
                            <span class="ds-popup-label">Permission:</span>
                            <span class="ds-popup-val" style="color: ${zoneType === 'RED' ? '#f87171' : (zoneType === 'YELLOW' ? '#fbbf24' : '#34d399')}; font-size: 0.68rem;">${props.permission_required || 'None'}</span>
                        </div>
                        <div class="ds-popup-row">
                            <span class="ds-popup-label">Authority:</span>
                            <span class="ds-popup-val">${props.authority || 'DGCA India'}</span>
                        </div>
                        <div class="ds-popup-row">
                            <span class="ds-popup-label">Regulation:</span>
                            <span class="ds-popup-val">${props.rule_ref || 'Drone Rules 2021'}</span>
                        </div>
                    </div>
                </div>
            `;

            polygon.bindPopup(popupHtml, { className: 'digitalsky-popup' });

            // Hover effects
            polygon.on('mouseover', function () {
                polygon.setStyle({
                    weight: weight + 1.5,
                    fillOpacity: Math.min(fillOpacity + 0.15, 0.7)
                });
            });
            polygon.on('mouseout', function () {
                polygon.setStyle({
                    weight: weight,
                    fillOpacity: fillOpacity
                });
            });

            digitalSkyAirspaceGroup.addLayer(polygon);
        });

        const countEl = document.getElementById('legendZoneCount');
        if (countEl && features.length > 0) {
            countEl.textContent = `${features.length} Zones Active`;
        }
    }

    function showDigitalSkyLegend(show) {
        if (!elements.digitalSkyLegend) return;
        elements.digitalSkyLegend.style.display = show ? 'block' : 'none';
    }

    // Real-time Airspace Zone Check
    let lastZoneCheckTime = 0;
    async function evaluateAirspaceZone(lat, lon, alt) {
        if (!lat || !lon) return;
        const now = Date.now();
        if (now - lastZoneCheckTime < 2500) return;
        lastZoneCheckTime = now;

        try {
            const res = await fetch(`/api/digitalsky/check/?lat=${lat}&lon=${lon}&alt=${alt || 0}`);
            if (!res.ok) return;
            const data = await res.json();
            if (data.status === 'success' && data.assessment) {
                currentAirspaceAssessment = data.assessment;
                updateAirspaceHud(data.assessment);
            }
        } catch (e) {
            // Silently ignore
        }
    }

    function updateAirspaceHud(assessment) {
        if (!elements.hudZone) return;
        const zType = assessment.zone_type;
        if (zType === 'RED') {
            elements.hudZone.innerHTML = '🔴 RED (No-Fly)';
            elements.hudZone.style.color = '#ef4444';
        } else if (zType === 'YELLOW') {
            elements.hudZone.innerHTML = '🟡 YELLOW (ATC)';
            elements.hudZone.style.color = '#f59e0b';
        } else {
            elements.hudZone.innerHTML = '🟢 GREEN (Clear)';
            elements.hudZone.style.color = '#10b981';
        }

        const phoneAirspace = document.getElementById('popupAirspacePhone');
        if (phoneAirspace) {
            phoneAirspace.textContent = assessment.zone_name || `${zType} Zone`;
            phoneAirspace.style.color = zType === 'RED' ? '#ef4444' : (zType === 'YELLOW' ? '#f59e0b' : '#059669');
        }
        const droneAirspace = document.getElementById('popupAirspaceDrone');
        if (droneAirspace) {
            droneAirspace.textContent = assessment.zone_name || `${zType} Zone`;
            droneAirspace.style.color = zType === 'RED' ? '#ef4444' : (zType === 'YELLOW' ? '#f59e0b' : '#0284c7');
        }
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

            // In main mode, ensure all live active drone fleet markers and trails are displayed
            Object.values(activeDrones).forEach(d => {
                if (map && d.marker && !map.hasLayer(d.marker)) {
                    d.marker.addTo(map);
                }
                if (map && d.trail && isTrailVisible && !map.hasLayer(d.trail)) {
                    d.trail.addTo(map);
                }
            });

            // Focus on active drone if available and auto-fit or center
            const liveDroneList = Object.values(activeDrones);
            if (liveDroneList.length > 0) {
                const focusId = activeDroneFocusId || liveDroneList[0].id;
                if (activeDrones[focusId]) {
                    activeMarker = activeDrones[focusId].marker;
                    if (activeDrones[focusId].lastTelemetry) {
                        updateTelemetryCards(activeDrones[focusId].lastTelemetry);
                    }
                }
                if (map) {
                    if (liveDroneList.length === 1 && liveDroneList[0].marker) {
                        map.setView(liveDroneList[0].marker.getLatLng(), 16, { animate: true });
                    } else if (liveDroneList.length > 1) {
                        const group = L.featureGroup(liveDroneList.map(d => d.marker));
                        map.fitBounds(group.getBounds().pad(0.2), { animate: true });
                    }
                }
                if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
            }

            if (elements.testModeBadge) elements.testModeBadge.style.display = 'none';
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'none';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valRegisteredDrones && elements.valDronesInAir) {
                if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
                // the simulation polling will update drones in air if needed
            }

            if (elements.mapMainTitle) elements.mapMainTitle.textContent = window.MAIN_MODE_TITLE || 'Main Mode (Overview)';
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
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'NCC DITN Network Overview';
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
                if (!map.hasLayer(phoneMarker)) phoneMarker.addTo(map);
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

            // Switch markers: remove phone and standalone drone markers
            if (phoneMarker && map.hasLayer(phoneMarker)) map.removeLayer(phoneMarker);
            if (droneMarker && map.hasLayer(droneMarker)) map.removeLayer(droneMarker);

            // In drone mode, only display on map if actively connected
            const liveDroneCount = Object.keys(activeDrones).length;
            if (liveDroneCount === 0) {
                activeMarker = null;
                resetTelemetryUI();
                if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'flex';
                updateConnectionStatus(false, null, 'Drone Not Connected');
            } else if (activeDroneFocusId && activeDrones[activeDroneFocusId]) {
                activeMarker = activeDrones[activeDroneFocusId].marker;
                if (map) map.setView(activeMarker.getLatLng(), 17, { animate: true });
                if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
            }

            // Update polyline styling for drone
            if (movementTrail) {
                movementTrail.setStyle({ color: '#0284c7' });
            }

            // Mode Badge
            if (elements.testModeBadge) elements.testModeBadge.style.display = 'inline-flex';
            if (elements.modeBadgeText) elements.modeBadgeText.textContent = 'Live Hardware Stream (ESP32 4G LTE)';
            if (elements.gpsSourceText) elements.gpsSourceText.textContent = 'GPS Source: ESP32 + A7670C / Cube Orange+';

            // Hide phone hotspot banner, show ESP32 4G LTE banner
            if (elements.hotspotBanner) elements.hotspotBanner.style.display = 'none';
            if (elements.esp32Banner) elements.esp32Banner.style.display = 'flex';
            if (location.protocol === 'https:' && elements.esp32HttpsTip) {
                if (elements.esp32HttpsTip) elements.esp32HttpsTip.style.display = 'none';
            }

            // Buttons & Headers
            if (elements.centerButtonText) elements.centerButtonText.textContent = 'Center Drone';
            if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Live Tactical Map (Cube Orange+ / ESP32 4G)';
            if (elements.overviewHeaderTitle) elements.overviewHeaderTitle.textContent = 'Drone Telemetry & Hardware Overview';
            if (elements.mapStatsContainer) elements.mapStatsContainer.style.display = 'flex';
            if (elements.valDronesInAir) elements.valDronesInAir.textContent = Object.keys(activeDrones).length.toString();
            if (elements.valRegisteredDrones) elements.valRegisteredDrones.textContent = elements.valRegisteredDrones.getAttribute('data-original') || '0';
            if (elements.statusFeedText) elements.statusFeedText.textContent = 'ESP32 4G LTE';
            if (elements.statusFeedHint) elements.statusFeedHint.textContent = 'A7670C / Cube Orange+ (UART2)';
            if (elements.statusRouteName) elements.statusRouteName.textContent = 'Cube Orange+ → ESP32 → 4G HiveMQ';
            if (elements.statusRouteHint) elements.statusRouteHint.textContent = 'Cellular Cloud Stream (MQTT)';
            if (elements.statusHwPacketsHint) elements.statusHwPacketsHint.textContent = `Target: ${targetDroneId}`;
        }

        try {
            localStorage.setItem('utm_active_mode', newMode);
        } catch (e) { }

        if (newMode === 'drone') {
            setTimeout(connectEsp32Mqtt, 250);
        }

        // Reset connection status only if no fresh telemetry was recently received
        if (Date.now() - lastReceivedTimestamp > 15000) {
            updateConnectionStatus(false, null);
        }
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
        if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = 'Coordinates: Awaiting Drone Connection';
        if (elements.mapRouteHud) {
            elements.mapRouteHud.textContent = 'Disconnected';
            elements.mapRouteHud.style.background = '#fef2f2';
            elements.mapRouteHud.style.borderColor = '#fecaca';
            elements.mapRouteHud.style.color = '#ef4444';
        }
        if (elements.hudAlt) elements.hudAlt.textContent = '--';
        if (elements.hudHdg) elements.hudHdg.textContent = '--';
        if (elements.hudSpeed) elements.hudSpeed.textContent = '--';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = 'No Signal';
        if (elements.hudBattery) elements.hudBattery.textContent = '--';
        if (elements.hudAttitude) elements.hudAttitude.textContent = '--';
        if (elements.hudDroneId) elements.hudDroneId.textContent = '--';

        // 1. Battery Card
        if (elements.valBattery) elements.valBattery.textContent = '--';
        if (elements.subBattery) elements.subBattery.textContent = 'Disconnected';

        // 2. Flight Mode Card
        if (elements.valFlightMode) elements.valFlightMode.textContent = '--';
        if (elements.subFlightMode) elements.subFlightMode.textContent = 'Awaiting Drone Connection';

        // 3. Latitude Card
        if (elements.valLatitude) elements.valLatitude.textContent = '--';
        if (elements.subLatitude) elements.subLatitude.textContent = 'Awaiting GPS fix...';

        // 4. Longitude Card
        if (elements.valLongitude) elements.valLongitude.textContent = '--';
        if (elements.subLongitude) elements.subLongitude.textContent = 'Awaiting GPS fix...';

        // 5. Altitude Card
        if (elements.valAltitude) elements.valAltitude.textContent = '--';
        if (elements.subAltitude) elements.subAltitude.textContent = 'Awaiting altitude';

        // 6. Speed Card
        if (elements.valSpeed) elements.valSpeed.textContent = '--';
        if (elements.subSpeed) elements.subSpeed.textContent = 'Disconnected';

        // 7. Heading Card
        if (elements.valHeading) elements.valHeading.textContent = '--';
        if (elements.subHeading) elements.subHeading.textContent = 'Unavailable';
        if (elements.compassNeedle) elements.compassNeedle.style.transform = 'rotate(0deg)';

        // 8. Attitude Card
        if (elements.valAttitude) elements.valAttitude.textContent = '--';
        if (elements.subAttitude) elements.subAttitude.textContent = 'Disconnected';

        // 9. Accuracy Card
        if (elements.valAccuracy) elements.valAccuracy.textContent = '--';
        if (elements.subAccuracy) elements.subAccuracy.textContent = 'Awaiting fix';

        // 10. Drone Identity Card
        if (elements.valDroneId) elements.valDroneId.textContent = '--';
        if (elements.subDroneId) elements.subDroneId.textContent = 'No drone connected';

        // 11. Last Update Card
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = '--:--:--';
        if (elements.subLastUpdate) elements.subLastUpdate.textContent = 'Last update: never';

        if (elements.esp32BattBadge) elements.esp32BattBadge.style.display = 'none';
        if (elements.esp32AttitudeBadge) elements.esp32AttitudeBadge.style.display = 'none';
        if (elements.hardwareOfflineAlert && (activeMode === 'drone' || activeMode === 'main')) {
            elements.hardwareOfflineAlert.style.display = 'flex';
        }
        if (elements.valDronesInAir) elements.valDronesInAir.textContent = Object.keys(activeDrones).length.toString();
    }

    function removeDroneFromMap(droneId) {
        if (!droneId) return;
        if (activeDrones[droneId]) {
            const drone = activeDrones[droneId];
            if (map && drone.marker && map.hasLayer(drone.marker)) {
                map.removeLayer(drone.marker);
            }
            if (map && drone.trail && map.hasLayer(drone.trail)) {
                map.removeLayer(drone.trail);
            }
            delete activeDrones[droneId];
        }
        if (droneMarker && map && map.hasLayer(droneMarker)) {
            map.removeLayer(droneMarker);
        }
        if (activeDroneFocusId === droneId) {
            const remaining = Object.keys(activeDrones);
            if (remaining.length > 0) {
                focusDrone(remaining[0]);
            } else {
                activeDroneFocusId = null;
                activeMarker = null;
                resetTelemetryUI();
            }
        }
        updateFleetSelectorUI();
        if (elements.valDronesInAir) {
            elements.valDronesInAir.textContent = Object.keys(activeDrones).length.toString();
        }
    }

    function updateTelemetryCards(telemetryData) {
        if (!telemetryData) return;
        const lat = parseFloat(telemetryData.latitude);
        const lon = parseFloat(telemetryData.longitude);
        const alt = telemetryData.altitude !== null && telemetryData.altitude !== undefined ? parseFloat(telemetryData.altitude) : null;
        const hdg = telemetryData.heading !== null && telemetryData.heading !== undefined ? parseFloat(telemetryData.heading) : null;
        // Dynamic Speed Calculation (if not reported directly by hardware/sensor)
        const dId = telemetryData.drone_id || telemetryData.id || targetDroneId || 'DRONE-ALPHA';
        let speed = (telemetryData.speed !== null && telemetryData.speed !== undefined && !isNaN(telemetryData.speed))
            ? parseFloat(telemetryData.speed)
            : ((telemetryData.spd !== null && telemetryData.spd !== undefined && !isNaN(telemetryData.spd)) ? parseFloat(telemetryData.spd) : null);

        const now = Date.now();
        if ((speed === null || speed === 0) && lastPositionsPerDrone[dId] && !isNaN(lat) && !isNaN(lon)) {
            const prev = lastPositionsPerDrone[dId];
            const dt = (now - prev.time) / 1000.0;
            if (dt >= 0.5 && dt <= 30.0) {
                const R = 6371000.0;
                const dLat = (lat - prev.lat) * Math.PI / 180.0;
                const dLon = (lon - prev.lon) * Math.PI / 180.0;
                const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                          Math.cos(prev.lat * Math.PI / 180.0) * Math.cos(lat * Math.PI / 180.0) *
                          Math.sin(dLon / 2) * Math.sin(dLon / 2);
                const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                const distM = R * c;
                if (distM >= 0.25) {
                    speed = distM / dt;
                } else {
                    speed = 0.0;
                }
            }
        }
        if (!isNaN(lat) && !isNaN(lon)) {
            lastPositionsPerDrone[dId] = { lat: lat, lon: lon, time: now };
        }

        const accuracy = telemetryData.accuracy !== null && telemetryData.accuracy !== undefined ? parseFloat(telemetryData.accuracy) : null;

        if (elements.mapCoordinatesHud) {
            if (elements.mapCoordinatesHud) elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
        }
        if (elements.hudAlt) elements.hudAlt.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.hudHdg) elements.hudHdg.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.hudSpeed) elements.hudSpeed.textContent = (speed !== null && !isNaN(speed)) ? `${speed.toFixed(1)} m/s` : '0.0 m/s';
        if (elements.hudAccuracy) elements.hudAccuracy.textContent = accuracy !== null ? `${accuracy.toFixed(1)} m` : 'N/A';

        // 1. Battery Card (FIRST)
        const battV = (telemetryData.batt_v !== undefined && telemetryData.batt_v !== null) ? parseFloat(telemetryData.batt_v) : null;
        const battPct = (telemetryData.batt_pct !== undefined && telemetryData.batt_pct !== null) ? parseInt(telemetryData.batt_pct) : null;
        if (elements.valBattery) {
            if (battV !== null || battPct !== null) {
                const vStr = battV !== null ? `${battV.toFixed(1)}V` : '';
                const pctClamped = (battPct !== null && battPct >= 0) ? Math.min(100, battPct) : (battPct !== null ? 0 : null);
                const pctStr = pctClamped !== null ? `${pctClamped}%` : '';
                elements.valBattery.textContent = `${vStr} ${pctStr ? '(' + pctStr + ')' : ''}`.trim() || '--';
                if (elements.subBattery) {
                    elements.subBattery.textContent = (pctClamped !== null && pctClamped <= 20) ? '⚠️ Low Battery!' : '4G LTE MAVLink SYS_STATUS';
                    if (pctClamped !== null && pctClamped <= 20) elements.subBattery.style.color = '#ef4444';
                    else elements.subBattery.style.color = 'var(--text-muted)';
                }
            } else {
                elements.valBattery.textContent = '--';
                if (elements.subBattery) elements.subBattery.textContent = activeMode === 'drone' ? 'Awaiting MAVLink #1' : 'N/A (Phone Mode)';
            }
        }

        // 2. Flight Mode Card (SECOND)
        const rawMode = telemetryData.flight_mode || telemetryData.mode || 'POSHOLD';
        const flightMode = String(rawMode).toUpperCase();
        if (elements.valFlightMode) {
            elements.valFlightMode.textContent = flightMode;
        }
        if (elements.subFlightMode) {
            elements.subFlightMode.textContent = activeMode === 'drone' ? 'MAVLink Flight Mode' : 'Phone GPS Navigation';
        }

        if (elements.valLatitude) elements.valLatitude.textContent = `${lat.toFixed(6)}°`;
        if (elements.subLatitude) elements.subLatitude.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;

        if (elements.valLongitude) elements.valLongitude.textContent = `${lon.toFixed(6)}°`;
        if (elements.subLongitude) elements.subLongitude.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;

        if (elements.valAltitude) elements.valAltitude.textContent = alt !== null ? `${alt.toFixed(1)} m` : 'N/A';
        if (elements.subAltitude) elements.subAltitude.textContent = alt !== null ? 'GPS MSL Altitude' : 'Unavailable from sensor';

        // Speed Card Display
        if (elements.valSpeed) elements.valSpeed.textContent = (speed !== null && !isNaN(speed)) ? `${speed.toFixed(1)} m/s` : '0.0 m/s';
        if (elements.subSpeed) elements.subSpeed.textContent = (speed !== null && !isNaN(speed)) ? `${(speed * 3.6).toFixed(1)} km/h (Ground Speed)` : 'Stationary (0.0 km/h)';

        if (elements.valHeading) elements.valHeading.textContent = hdg !== null ? `${Math.round(hdg)}°` : 'N/A';
        if (elements.subHeading) elements.subHeading.textContent = hdg !== null ? headingToCardinal(hdg) : 'Unavailable';
        if (elements.compassNeedle && hdg !== null) {
            elements.compassNeedle.style.transform = `rotate(${hdg}deg)`;
        }

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

        // 9. Attitude Card (from 4G LTE MAVLink Msg #30)
        const roll = (telemetryData.roll !== undefined && telemetryData.roll !== null) ? parseFloat(telemetryData.roll) : null;
        const pitch = (telemetryData.pitch !== undefined && telemetryData.pitch !== null) ? parseFloat(telemetryData.pitch) : null;
        if (elements.valAttitude) {
            if (roll !== null || pitch !== null) {
                const rStr = roll !== null ? `R:${roll.toFixed(1)}°` : '';
                const pStr = pitch !== null ? `P:${pitch.toFixed(1)}°` : '';
                elements.valAttitude.textContent = `${rStr}  ${pStr}`.trim();
                if (elements.subAttitude) elements.subAttitude.textContent = 'Roll & Pitch (ATTITUDE #30)';
            } else {
                elements.valAttitude.textContent = '--';
                if (elements.subAttitude) elements.subAttitude.textContent = activeMode === 'drone' ? 'Awaiting MAVLink #30' : 'N/A (Phone Mode)';
            }
        }

        // 10. Drone Identity Card (JSON: drone_id)
        const displayTitle = telemetryData.registered_name && telemetryData.registered_name !== dId ? `${telemetryData.registered_name} (${dId})` : dId;
        if (elements.valDroneId) {
            elements.valDroneId.textContent = displayTitle;
            if (elements.subDroneId) {
                if (telemetryData.unit_name && telemetryData.unit_name !== 'NCC Unit') {
                    elements.subDroneId.textContent = `${telemetryData.unit_name} • ${telemetryData.group_name || 'NCC'}`;
                } else {
                    elements.subDroneId.textContent = telemetryData.is_simulated ? 'Procedural Test Simulation' : 'ESP32 4G Hardware Active';
                }
            }
        }

        // Floating HUD items (BATT, ATT, UAV)
        if (elements.hudBattery) {
            if (battV !== null || battPct !== null) {
                const v = battV !== null ? `${battV.toFixed(1)}V` : '';
                const p = battPct !== null ? `${battPct}%` : '';
                elements.hudBattery.textContent = `${v} ${p ? '(' + p + ')' : ''}`.trim();
                elements.hudBattery.style.color = (battPct !== null && battPct <= 20) ? '#ef4444' : '#10b981';
            } else {
                elements.hudBattery.textContent = '--';
            }
        }
        if (elements.hudAttitude) {
            if (roll !== null || pitch !== null) {
                const r = roll !== null ? `R:${roll > 0 ? '+' : ''}${roll.toFixed(0)}°` : '';
                const p = pitch !== null ? `P:${pitch > 0 ? '+' : ''}${pitch.toFixed(0)}°` : '';
                elements.hudAttitude.textContent = `${r} ${p}`.trim();
            } else {
                elements.hudAttitude.textContent = '--';
            }
        }
        if (elements.hudDroneId) {
            elements.hudDroneId.textContent = dId.length > 14 ? dId.substring(0, 13) + '..' : dId;
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
                <p style="margin: 0 0 6px 0;"><b>Airspace:</b> <span style="color: #059669; font-weight: 600;">🟢 Green Zone (DGCA Free Flight)</span></p>
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
        evaluateAirspaceZone(lat, lon, alt);

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
    // Multi-Drone Telemetry & Fleet Tracking Manager
    // -------------------------------------------------------------------------
    const activeDrones = {}; // drone_id -> { id, marker, trail, trailCoords, color, lastTelemetry, lastSeen }
    let activeDroneFocusId = null;

    function updateFleetSelectorUI() {
        const droneIds = Object.keys(activeDrones);
        const count = droneIds.length;

        if (elements.hudFleetItem && elements.hudFleetDivider) {
            if (count > 1) {
                elements.hudFleetItem.style.display = 'flex';
                elements.hudFleetDivider.style.display = 'block';
                if (elements.hudFleetCount) elements.hudFleetCount.textContent = `${count} UAVs`;
            } else {
                elements.hudFleetItem.style.display = 'none';
                elements.hudFleetDivider.style.display = 'none';
            }
        }

        // Never show "Fit Fleet (2)" button or fleet selector pills
        if (elements.btnFitFleet) {
            elements.btnFitFleet.style.display = 'none';
        }
        if (elements.fleetSelectorContainer) {
            elements.fleetSelectorContainer.style.display = 'none';
        }
        if (elements.fleetDronePills) {
            elements.fleetDronePills.innerHTML = '';
        }
    }

    function focusDrone(droneId) {
        if (!activeDrones[droneId]) return;
        activeDroneFocusId = droneId;
        const drone = activeDrones[droneId];
        activeMarker = drone.marker;

        if (drone.lastTelemetry) {
            updateTelemetryCards(drone.lastTelemetry);
            const lat = parseFloat(drone.lastTelemetry.latitude !== undefined ? drone.lastTelemetry.latitude : drone.lastTelemetry.lat);
            const lon = parseFloat(drone.lastTelemetry.longitude !== undefined ? drone.lastTelemetry.longitude : drone.lastTelemetry.lon);
            if (map && !isNaN(lat) && !isNaN(lon)) {
                map.panTo([lat, lon], { animate: true });
            }
            if (elements.hudDroneId) {
                elements.hudDroneId.textContent = `${droneId}`;
                elements.hudDroneId.style.color = drone.color;
            }
            if (elements.mapRouteHud) {
                elements.mapRouteHud.textContent = `Target: ${droneId}`;
                elements.mapRouteHud.style.borderColor = drone.color;
                elements.mapRouteHud.style.color = drone.color;
            }
        }
        updateFleetSelectorUI();
    }

    function fitAllDrones() {
        const droneIds = Object.keys(activeDrones);
        if (!map || droneIds.length === 0) return;

        const latlngs = [];
        droneIds.forEach(id => {
            const drone = activeDrones[id];
            if (drone.marker) {
                latlngs.push(drone.marker.getLatLng());
            }
        });

        if (latlngs.length === 1) {
            map.setView(latlngs[0], 17, { animate: true });
        } else if (latlngs.length > 1) {
            map.fitBounds(L.latLngBounds(latlngs), { padding: [60, 60], maxZoom: 18, animate: true });
        }
    }

    function updateDroneUI(telemetryData, apiState) {
        if (!telemetryData) return;

        const lat = parseFloat(telemetryData.latitude !== undefined ? telemetryData.latitude : telemetryData.lat);
        const lon = parseFloat(telemetryData.longitude !== undefined ? telemetryData.longitude : telemetryData.lon);
        const alt = parseFloat(telemetryData.altitude !== undefined ? telemetryData.altitude : (telemetryData.alt !== undefined ? telemetryData.alt : 0));
        const rawHdg = parseFloat(telemetryData.heading !== undefined ? telemetryData.heading : (telemetryData.hdg !== undefined ? telemetryData.hdg : 0));
        const hdg = (isNaN(rawHdg) || rawHdg > 360 || rawHdg < 0) ? 0 : rawHdg;
        const timeStr = formatTime(telemetryData.timestamp || telemetryData.received_at || new Date().toISOString());
        const droneId = telemetryData.drone_id || telemetryData.id || 'DRONE-ALPHA';
        const color = getDroneColor(droneId);
        const sanitizedId = droneId.replace(/[^a-zA-Z0-9_-]/g, '_');

        if (isNaN(lat) || isNaN(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) {
            console.warn('[UTM] Out-of-bounds or NaN coordinates received:', lat, lon);
            return;
        }

        // Handle indoor bench test GPS fix (0, 0) gracefully
        const isBenchTest = (lat === 0 && lon === 0);
        const effectiveLat = isBenchTest ? lastKnownLat : lat;
        const effectiveLon = isBenchTest ? lastKnownLon : lon;

        if (isBenchTest) {
            if (elements.mapCoordinatesHud) {
                elements.mapCoordinatesHud.textContent = `Coordinates: Bench Test (${droneId}) - Indoors / Acquiring Sats`;
            }
            if (elements.hudAccuracy) elements.hudAccuracy.textContent = 'Indoors (Fix Pending)';
            if (elements.valAccuracy) elements.valAccuracy.innerHTML = '<span style="color: #f59e0b; font-weight: 700;">Acquiring Sats</span>';
            if (elements.subAccuracy) elements.subAccuracy.textContent = `Hardware Connected (${droneId} Bench Test)`;
        }

        // Auto-center map on first valid drone GPS fix
        if (!hasReceivedFirstDroneFix && map) {
            map.setView([effectiveLat, effectiveLon], 16, { animate: true });
            hasReceivedFirstDroneFix = true;
        }

        // 1. Manage Multi-Drone Marker & Trail
        const hasValidCoord = (!isBenchTest && lat !== 0 && lon !== 0 && !(Math.abs(lat - 30.9010) < 0.0001 && Math.abs(lon - 75.8573) < 0.0001));

        if (!activeDrones[droneId]) {
            const marker = L.marker([effectiveLat, effectiveLon], {
                icon: createMultiDroneIcon(hdg, droneId, color, alt),
                title: `${droneId} (Live UAV)`,
                zIndexOffset: 1000
            });

            const initialTrailCoords = hasValidCoord ? [[lat, lon]] : [];
            const trail = L.polyline(initialTrailCoords, {
                color: color,
                weight: 3.5,
                opacity: 0.85,
                dashArray: '6, 6'
            });

            if (map && (activeMode === 'drone' || activeMode === 'main')) {
                marker.addTo(map);
                if (isTrailVisible && initialTrailCoords.length > 0) trail.addTo(map);
            }

            marker.on('click', () => {
                focusDrone(droneId);
            });

            activeDrones[droneId] = {
                id: droneId,
                marker: marker,
                trail: trail,
                trailCoords: initialTrailCoords,
                color: color,
                lastTelemetry: telemetryData,
                lastSeen: Date.now()
            };

            // Backwards compatibility pointer
            droneMarker = marker;

            if (!activeDroneFocusId) {
                activeDroneFocusId = droneId;
            }
        } else {
            const drone = activeDrones[droneId];
            drone.marker.setLatLng([effectiveLat, effectiveLon]);

            if (map && (activeMode === 'drone' || activeMode === 'main') && !map.hasLayer(drone.marker)) {
                drone.marker.addTo(map);
            }

            const rotatorEl = document.getElementById(`droneRotator_${sanitizedId}`);
            if (rotatorEl) {
                rotatorEl.style.transform = `rotate(${hdg}deg)`;
            } else {
                drone.marker.setIcon(createMultiDroneIcon(hdg, droneId, color, alt));
            }

            if (hasValidCoord) {
                // Remove any accidental (0,0) or bench test default coordinates
                drone.trailCoords = drone.trailCoords.filter(pt => {
                    const ptLat = Array.isArray(pt) ? pt[0] : pt.lat;
                    const ptLon = Array.isArray(pt) ? pt[1] : pt.lng;
                    return Math.abs(ptLat) > 0.01 && Math.abs(ptLon) > 0.01 && !(Math.abs(ptLat - 30.9010) < 0.0001 && Math.abs(ptLon - 75.8573) < 0.0001);
                });

                drone.trailCoords.push([lat, lon]);
                if (drone.trailCoords.length > 300) drone.trailCoords.shift();
                if (drone.trail) {
                    if (isTrailVisible && !map.hasLayer(drone.trail) && map && (activeMode === 'drone' || activeMode === 'main')) {
                        drone.trail.addTo(map);
                    }
                    drone.trail.setLatLngs(drone.trailCoords);
                }
            }

            drone.lastTelemetry = telemetryData;
            drone.lastSeen = Date.now();
        }

        // Dynamic Popup for this Drone
        const unitName = telemetryData.unit_name || '';
        const groupName = telemetryData.group_name || '';
        const dteName = telemetryData.dte_name || '';
        const regName = telemetryData.registered_name || droneId;

        let popupContent = `
            <div style="font-family: inherit; font-size: 13px; line-height: 1.5; min-width: 220px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px;">
                    <strong style="color: ${color}; font-size: 14px;">🛸 ${regName}</strong>
                    <span style="font-size: 10px; padding: 1px 6px; border-radius: 4px; background: #e0f2fe; color: ${color}; font-weight: 700;">${telemetryData.category || 'UAV'}</span>
                </div>
                ${unitName && unitName !== 'NCC Unit' ? `<span style="font-size: 11px; font-weight: 600; color: #1e293b;">🎖️ ${unitName}</span><br>` : ''}
                ${groupName && groupName !== 'Group HQ' ? `<span style="font-size: 11px; color: #64748b;">${groupName} &bull; ${dteName}</span><br>` : ''}
                <span style="color: #64748b; font-size: 11px;">ID: <code>${droneId}</code></span><br>
                <div style="margin-top: 4px; padding: 4px 8px; background: #f8fafc; border-left: 3px solid ${color}; border-radius: 2px;">
                    <span>Alt: <strong>${alt.toFixed(1)} m</strong> | Hdg: <strong>${Math.round(hdg)}°</strong></span>
        `;
        if (telemetryData.batt_v !== undefined && telemetryData.batt_v !== null) {
            const bV = parseFloat(telemetryData.batt_v).toFixed(1) + 'V';
            const bP = (telemetryData.batt_pct !== undefined && telemetryData.batt_pct !== null) ? `(${telemetryData.batt_pct}%)` : '';
            popupContent += `<br><span>Battery: <strong>${bV} ${bP}</strong></span>`;
        }
        if (telemetryData.roll !== undefined && telemetryData.roll !== null) {
            const r = parseFloat(telemetryData.roll).toFixed(1) + '°';
            const p = (telemetryData.pitch !== undefined && telemetryData.pitch !== null) ? parseFloat(telemetryData.pitch).toFixed(1) + '°' : '0°';
            popupContent += `<br><span>Attitude: Roll ${r} | Pitch ${p}</span>`;
        }
        popupContent += `</div></div>`;
        activeDrones[droneId].marker.setPopupContent(popupContent);

        // Update Fleet Selector Badges
        updateFleetSelectorUI();

        // 2. If this drone is currently focused (or only 1 drone exists), update HUD & Cards
        const isFocused = (activeDroneFocusId === droneId || Object.keys(activeDrones).length === 1);
        if (isFocused) {
            activeMarker = activeDrones[droneId].marker;
            lastKnownLat = lat;
            lastKnownLon = lon;
            lastKnownHeading = hdg;

            // Update Map HUD
            if (elements.mapCoordinatesHud) {
                elements.mapCoordinatesHud.textContent = `Coordinates: ${lat.toFixed(6)}°, ${lon.toFixed(6)}°`;
            }
            if (elements.mapRouteHud) {
                elements.mapRouteHud.textContent = `Target: ${droneId}`;
                elements.mapRouteHud.style.background = '#e0f2fe';
                elements.mapRouteHud.style.borderColor = color;
                elements.mapRouteHud.style.color = color;
            }
            if (elements.hudAlt) elements.hudAlt.textContent = `${alt.toFixed(1)} m`;
            if (elements.hudHdg) elements.hudHdg.textContent = `${Math.round(hdg)}°`;

            const rawSpeed = telemetryData.speed !== undefined ? parseFloat(telemetryData.speed) : null;
            const spdText = (rawSpeed !== null && !isNaN(rawSpeed)) ? `${rawSpeed.toFixed(1)} m/s` : 'Stationary';
            if (elements.hudSpeed) elements.hudSpeed.textContent = spdText;
            if (elements.hudAccuracy) elements.hudAccuracy.textContent = 'Hardware Fix';
            evaluateAirspaceZone(lat, lon, alt);

            // Update Telemetry Cards
            updateTelemetryCards(telemetryData);
            if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;

            // Update banner badges
            if (elements.esp32BattBadge && (telemetryData.batt_v !== undefined || telemetryData.batt_pct !== undefined)) {
                elements.esp32BattBadge.style.display = 'inline-flex';
                if (elements.esp32BattText) {
                    const bV = telemetryData.batt_v ? parseFloat(telemetryData.batt_v).toFixed(1) + 'V' : '';
                    const bP = telemetryData.batt_pct !== undefined && telemetryData.batt_pct !== null ? telemetryData.batt_pct + '%' : '';
                    elements.esp32BattText.textContent = `${bV} ${bP ? '(' + bP + ')' : ''}`.trim();
                }
            }
            if (elements.esp32AttitudeBadge && (telemetryData.roll !== undefined || telemetryData.pitch !== undefined)) {
                elements.esp32AttitudeBadge.style.display = 'inline-flex';
                if (elements.esp32AttitudeText) {
                    const r = telemetryData.roll !== undefined && telemetryData.roll !== null ? parseFloat(telemetryData.roll).toFixed(1) : 0;
                    const p = telemetryData.pitch !== undefined && telemetryData.pitch !== null ? parseFloat(telemetryData.pitch).toFixed(1) : 0;
                    elements.esp32AttitudeText.textContent = `R: ${r}° | P: ${p}°`;
                }
            }

            const isHw = apiState ? apiState.hardware_connected : true;
            const secondsAgo = (apiState && typeof apiState.seconds_since_update === 'number') ? apiState.seconds_since_update : 0;
            updateConnectionStatus(isHw, secondsAgo, apiState ? apiState.status_label : null);
            if (isHw && (secondsAgo === null || secondsAgo < 30)) {
                updateEsp32MqttStatus('connected', `🟢 4G Live (${droneId})`);
                if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
            }
        }
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
                if (elements.statusLabel) elements.statusLabel.textContent = customLabel || 'Drone Connected (ESP32 Live)';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill pill-green';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-green';
                if (elements.statusConnText) elements.statusConnText.textContent = '🟢 ESP32 4G Connected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = 'Hardware online & streaming';
                if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
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
            const activeIds = new Set();
            if (data.status === 'success' && data.results && data.results.length > 0) {
                data.results.forEach(telemetry => {
                    const secAgo = (typeof telemetry.seconds_since_received === 'number') ? telemetry.seconds_since_received : 0.1;
                    if (secAgo <= droneTimeoutSeconds) {
                        activeIds.add(telemetry.drone_id);
                        updateDroneUI(telemetry, {
                            hardware_connected: true,
                            is_connected: true,
                            seconds_since_update: secAgo,
                            status_label: 'Hardware Online (4G LTE)'
                        });
                    }
                });
            }

            // Prune any drone from map that is no longer broadcasting (check both API and direct MQTT lastSeen)
            const now = Date.now();
            Object.keys(activeDrones).forEach(dId => {
                const drone = activeDrones[dId];
                const msSinceSeen = now - (drone.lastSeen || 0);
                if (!activeIds.has(dId) && msSinceSeen > (droneTimeoutSeconds * 1000)) {
                    removeDroneFromMap(dId);
                }
            });

            if (activeIds.size > 0 || Object.keys(activeDrones).length > 0) {
                if (activeIds.size > 0) totalPacketCount += activeIds.size;
                if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                lastReceivedTimestamp = Date.now();
                if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
                updateConnectionStatus(true, 0.1, 'Drone Connected (4G LTE Live)');
            } else {
                if (Object.keys(activeDrones).length === 0) {
                    resetTelemetryUI();
                    updateConnectionStatus(false, null, 'Drone Not Connected');
                }
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
                if (phoneMarker && !map.hasLayer(phoneMarker)) {
                    phoneMarker.addTo(map);
                    activeMarker = phoneMarker;
                }
                resetTelemetryUI();
            }
        } catch (err) {
            console.warn('[UTM] Phone telemetry fetch error:', err.message);
        }
    }

    async function fetchDroneTelemetry() {
        try {
            // First fetch latest telemetry for all active drones in the fleet
            const allResponse = await fetch('/api/drones/all/');
            if (allResponse.ok) {
                const allData = await allResponse.json();
                const activeIds = new Set();
                if (allData.status === 'success' && allData.results && allData.results.length > 0) {
                    allData.results.forEach(d => {
                        const secAgo = (typeof d.seconds_since_received === 'number') ? d.seconds_since_received : 0.1;
                        if (secAgo <= droneTimeoutSeconds) {
                            activeIds.add(d.drone_id);
                            updateDroneUI(d, {
                                hardware_connected: true,
                                is_connected: true,
                                seconds_since_update: secAgo,
                                status_label: 'Hardware Online (4G LTE)'
                            });
                        }
                    });
                }

                // Prune disconnected drones from map and state (check both API and direct MQTT lastSeen)
                const now = Date.now();
                Object.keys(activeDrones).forEach(dId => {
                    const drone = activeDrones[dId];
                    const msSinceSeen = now - (drone.lastSeen || 0);
                    if (!activeIds.has(dId) && msSinceSeen > (droneTimeoutSeconds * 1000)) {
                        removeDroneFromMap(dId);
                    }
                });

                if (activeIds.size > 0) {
                    totalPacketCount += activeIds.size;
                    if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                    lastReceivedTimestamp = Date.now();
                    if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
                    return;
                } else {
                    if (Object.keys(activeDrones).length === 0) {
                        resetTelemetryUI();
                        updateConnectionStatus(false, null, 'Drone Not Connected');
                    }
                }
            }

            // Fallback to single drone query
            const response = await fetch(`/api/telemetry/latest/?drone_id=${targetDroneId}`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.status === 'success' && data.telemetry && data.hardware_connected) {
                totalPacketCount++;
                if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                lastReceivedTimestamp = Date.now();
                updateDroneUI(data.telemetry, data);
            } else {
                removeDroneFromMap(targetDroneId);
                if (Object.keys(activeDrones).length === 0) {
                    resetTelemetryUI();
                    updateConnectionStatus(false, null, data.status_label || 'Drone Not Connected');
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
                        trailCoordinates = data.results
                            .filter(r => r.latitude && r.longitude && Math.abs(r.latitude) > 0.01 && Math.abs(r.longitude) > 0.01 && !(Math.abs(r.latitude - 30.9010) < 0.0001 && Math.abs(r.longitude - 75.8573) < 0.0001))
                            .map(r => [r.latitude, r.longitude]);
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
        if (!map) return;
        if (activeMode === 'main') {
            const droneList = Object.values(activeDrones);
            if (droneList.length === 1 && droneList[0].marker) {
                map.setView(droneList[0].marker.getLatLng(), 16, { animate: true });
            } else if (droneList.length > 1) {
                const group = L.featureGroup(droneList.map(d => d.marker));
                map.fitBounds(group.getBounds().pad(0.2), { animate: true });
            } else if (activeMarker) {
                map.setView(activeMarker.getLatLng(), 16, { animate: true });
            } else if (lastKnownLat && lastKnownLon) {
                map.setView([lastKnownLat, lastKnownLon], 16, { animate: true });
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
    }

    function clearMovementTrail() {
        // Clear global movement trail
        trailCoordinates = [];
        if (movementTrail) {
            movementTrail.setLatLngs([]);
        }

        // Clear trails for all active drones in fleet completely
        Object.values(activeDrones).forEach(d => {
            d.trailCoords = [];
            if (d.trail) {
                d.trail.setLatLngs([]);
            }
        });

        // Clear simulator paths if in simulator mode
        if (typeof simulatorState !== 'undefined' && simulatorState.markers) {
            simulatorState.markers.forEach(d => {
                d.pathCoords = [];
                if (d.path) {
                    d.path.setLatLngs([]);
                }
            });
        }
        console.log('[UTM] Movement trail cleared completely.');
    }

    function toggleTrailVisibility() {
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
            // Toggle trails for all active drones in fleet
            Object.values(activeDrones).forEach(d => {
                if (d.trail && map) {
                    if (isTrailVisible) {
                        map.addLayer(d.trail);
                    } else {
                        map.removeLayer(d.trail);
                    }
                }
            });
        }
        if (elements.trailButtonText) {
            elements.trailButtonText.textContent = isTrailVisible ? 'Hide Trail' : 'Show Trail';
        }
    }

    function resetMapView() {
        if (!map) return;
        let zoom = (activeMode === 'main' || activeMode === 'simulator') ? 5 : 16;
        if (lastKnownLat && lastKnownLon) {
            map.setView([lastKnownLat, lastKnownLon], zoom, { animate: true });
        } else {
            map.setView([28.6139, 77.2090], zoom, { animate: true });
        }
    }

    // -------------------------------------------------------------------------
    // Client-side Heartbeat Counter
    // -------------------------------------------------------------------------
    function startHeartbeatCounter() {
        heartbeatTimer = setInterval(() => {
            const now = Date.now();
            const timeout = activeMode === 'phone' ? phoneTimeoutSeconds : droneTimeoutSeconds;

            if (activeMode === 'drone' || activeMode === 'main') {
                Object.keys(activeDrones).forEach(dId => {
                    const drone = activeDrones[dId];
                    const droneSecAgo = (now - drone.lastSeen) / 1000;
                    if (droneSecAgo > timeout) {
                        removeDroneFromMap(dId);
                    }
                });

                if (Object.keys(activeDrones).length === 0) {
                    if (droneMarker && map && map.hasLayer(droneMarker)) {
                        map.removeLayer(droneMarker);
                    }
                    resetTelemetryUI();
                    if (lastReceivedTimestamp) {
                        const secAgo = (now - lastReceivedTimestamp) / 1000;
                        updateConnectionStatus(false, secAgo, 'Drone Not Connected');
                    } else {
                        updateConnectionStatus(false, null, 'Drone Not Connected');
                    }
                }
            } else if (activeMode === 'phone') {
                if (lastReceivedTimestamp) {
                    const secondsAgo = (now - lastReceivedTimestamp) / 1000;
                    if (secondsAgo > timeout) {
                        updateConnectionStatus(false, secondsAgo);
                        resetTelemetryUI();
                    }
                }
            }

            if (!lastReceivedTimestamp) return;
            const secondsAgo = (now - lastReceivedTimestamp) / 1000;

            if (elements.statusHeartbeatSec) {
                elements.statusHeartbeatSec.textContent = secondsAgo.toFixed(1);
            }
            if (elements.subLastUpdate && Object.keys(activeDrones).length > 0) {
                elements.subLastUpdate.textContent = `Last update: ${secondsAgo.toFixed(1)}s ago`;
            }

            if (secondsAgo > timeout && Object.keys(activeDrones).length === 0) {
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
                }).catch(() => { });
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
    // ESP32 4G LTE Cloud MQTT Bridge Client (HiveMQ)
    // -------------------------------------------------------------------------
    const lastMqttRenderPerDrone = {};
    const pendingMqttTimeoutPerDrone = {};
    const MQTT_RENDER_THROTTLE_MS = 2000; // 2 seconds delay per drone to prevent UI flickering

    function connectEsp32Mqtt() {
        const topic = (elements.esp32MqttTopic ? elements.esp32MqttTopic.value.trim() : '') || 'utm/drone-alpha/telemetry';
        const brokerHost = 'broker.hivemq.com';
        const useSSL = (location.protocol === 'https:');
        const brokerPort = useSSL ? 8884 : 8000; // 8000 on http, 8884 on https

        if (esp32MqttClient && esp32MqttClient.isConnected()) {
            console.log('[UTM] MQTT already connected to HiveMQ.');
            return;
        }

        if (typeof Paho === 'undefined' || !Paho.MQTT) {
            console.warn('[UTM] Paho MQTT library not ready, retrying in 500ms...');
            setTimeout(connectEsp32Mqtt, 500);
            return;
        }

        updateEsp32MqttStatus('connecting', 'Connecting HiveMQ...');

        const clientId = 'utm_web_' + Math.random().toString(16).substr(2, 8);
        esp32MqttClient = new Paho.MQTT.Client(brokerHost, brokerPort, '/mqtt', clientId);

        esp32MqttClient.onConnectionLost = (responseObject) => {
            console.warn('[UTM] MQTT connection lost:', responseObject ? responseObject.errorMessage : 'Unknown');
            updateEsp32MqttStatus('disconnected', 'MQTT Disconnected');
            if (elements.btnConnectEspMqtt) elements.btnConnectEspMqtt.style.display = 'inline-block';
            if (elements.btnDisconnectEspMqtt) elements.btnDisconnectEspMqtt.style.display = 'none';

            // Auto-reconnect if user is still actively monitoring drone mode
            if (activeMode === 'drone') {
                setTimeout(connectEsp32Mqtt, 3000);
            }
        };

        function processMqttTelemetry(telemetryObj, apiState) {
            updateDroneUI(telemetryObj, apiState);
            updateEsp32MqttStatus('connected', `🟢 4G Live (${telemetryObj.drone_id})`);

            // Update banner badges
            if (elements.esp32BattBadge && (telemetryObj.batt_v !== null || telemetryObj.batt_pct !== null)) {
                elements.esp32BattBadge.style.display = 'inline-flex';
                if (elements.esp32BattText) {
                    elements.esp32BattText.textContent = `${telemetryObj.batt_v ? telemetryObj.batt_v.toFixed(1) + 'V' : ''} ${telemetryObj.batt_pct !== null ? '(' + telemetryObj.batt_pct + '%)' : ''}`.trim();
                }
            }
            if (elements.esp32AttitudeBadge && (telemetryObj.roll !== null || telemetryObj.pitch !== null)) {
                elements.esp32AttitudeBadge.style.display = 'inline-flex';
                if (elements.esp32AttitudeText) {
                    elements.esp32AttitudeText.textContent = `Roll: ${telemetryObj.roll !== null ? telemetryObj.roll.toFixed(1) : 0}° | Pitch: ${telemetryObj.pitch !== null ? telemetryObj.pitch.toFixed(1) : 0}°`;
                }
            }

            // Forward to Django backend asynchronously with 2s interval
            fetch('/api/telemetry/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(telemetryObj)
            }).catch(() => { });
        }

        esp32MqttClient.onMessageArrived = (message) => {
            try {
                // Drop stale broker-retained packets from past sessions (strict 15-second freshness rule)
                if (message.retained) {
                    return;
                }

                const data = JSON.parse(message.payloadString);

                // Extract drone_id from packet payload or fallback to topic regex (e.g. utm/drones/DRONE-40573255F188/telemetry)
                let droneId = data.drone_id || data.id;
                if (!droneId && message.destinationName) {
                    const match = message.destinationName.match(/utm\/drones\/([^\/]+)/);
                    if (match && match[1] && match[1] !== '+') {
                        droneId = match[1];
                    }
                }
                if (!droneId) {
                    droneId = 'DRONE-ALPHA';
                }

                // If drone reported offline, prune immediately
                if (data.status === 'offline') {
                    removeDroneFromMap(droneId);
                    return;
                }

                // If live status online heartbeat
                if (data.status === 'online') {
                    const existing = activeDrones[droneId];
                    const existingLat = existing ? existing.lat : lastKnownLat;
                    const existingLon = existing ? existing.lon : lastKnownLon;
                    updateDroneUI({
                        drone_id: droneId,
                        latitude: existingLat,
                        longitude: existingLon,
                        altitude: existing ? existing.alt : 0,
                        heading: existing ? existing.heading : 0,
                        batt_v: 15.8,
                        batt_pct: 95,
                        flight_mode: 'ONLINE',
                        speed: 0,
                        timestamp: new Date().toISOString()
                    }, {
                        hardware_connected: true,
                        is_connected: true,
                        seconds_since_update: 0.1,
                        status_label: 'Hardware Online (ESP32 Stream)'
                    });
                    return;
                }

                // Handle esp 32 New.txt format:
                // {"lat":30.98,"lon":76.52,"alt":15.4,"hdg":142.5,"roll":1.2,"pitch":-0.8,"batt_v":15.8,"batt_pct":85}
                const lat = parseFloat(data.lat !== undefined ? data.lat : data.latitude);
                const lon = parseFloat(data.lon !== undefined ? data.lon : data.longitude);
                const alt = parseFloat(data.alt !== undefined ? data.alt : (data.altitude || 0));
                const hdg = parseFloat(data.hdg !== undefined ? data.hdg : (data.heading || 0));
                const roll = data.roll !== undefined ? parseFloat(data.roll) : null;
                const pitch = data.pitch !== undefined ? parseFloat(data.pitch) : null;
                const battV = data.batt_v !== undefined ? parseFloat(data.batt_v) : null;
                const battPct = data.batt_pct !== undefined ? parseInt(data.batt_pct) : null;

                if (isNaN(lat) || isNaN(lon)) return;

                totalPacketCount++;
                if (elements.statusMetaPkt) elements.statusMetaPkt.textContent = `Packets Received: ${totalPacketCount}`;
                lastReceivedTimestamp = Date.now();

                const speed = (data.speed !== undefined && data.speed !== null) ? parseFloat(data.speed) : ((data.spd !== undefined && data.spd !== null) ? parseFloat(data.spd) : null);
                const flightMode = data.flight_mode || data.mode || 'POSHOLD';

                const telemetryObj = {
                    drone_id: droneId,
                    latitude: lat,
                    longitude: lon,
                    altitude: alt,
                    heading: hdg,
                    speed: speed,
                    flight_mode: flightMode,
                    roll: roll,
                    pitch: pitch,
                    batt_v: battV,
                    batt_pct: battPct,
                    timestamp: new Date().toISOString(),
                    received_at: new Date().toISOString(),
                    is_simulated: false
                };

                const apiState = {
                    hardware_connected: true,
                    is_connected: true,
                    seconds_since_update: 0.1,
                    status_label: 'Drone Connected (4G LTE Live)',
                    hardware_status_label: 'Hardware Online (ESP32 4G HiveMQ Stream)'
                };

                // Apply 2-second rate-limiting delay per drone to eliminate UI flickering
                const now = Date.now();
                const lastRender = lastMqttRenderPerDrone[droneId] || 0;
                if (now - lastRender >= MQTT_RENDER_THROTTLE_MS) {
                    lastMqttRenderPerDrone[droneId] = now;
                    if (pendingMqttTimeoutPerDrone[droneId]) {
                        clearTimeout(pendingMqttTimeoutPerDrone[droneId]);
                        delete pendingMqttTimeoutPerDrone[droneId];
                    }
                    processMqttTelemetry(telemetryObj, apiState);
                } else if (!pendingMqttTimeoutPerDrone[droneId]) {
                    const waitTime = MQTT_RENDER_THROTTLE_MS - (now - lastRender);
                    pendingMqttTimeoutPerDrone[droneId] = setTimeout(() => {
                        delete pendingMqttTimeoutPerDrone[droneId];
                        lastMqttRenderPerDrone[droneId] = Date.now();
                        processMqttTelemetry(telemetryObj, apiState);
                    }, waitTime);
                }

            } catch (parseErr) {
                console.warn('[UTM] Error parsing 4G MQTT packet:', parseErr);
            }
        };

        const connectOptions = {
            timeout: 10,
            useSSL: useSSL,
            cleanSession: true,
            onSuccess: () => {
                console.log('[UTM] Connected to HiveMQ MQTT Broker!');
                updateEsp32MqttStatus('connected', '🟢 HiveMQ Connected');
                if (elements.btnConnectEspMqtt) elements.btnConnectEspMqtt.style.display = 'none';
                if (elements.btnDisconnectEspMqtt) elements.btnDisconnectEspMqtt.style.display = 'inline-block';

                const subscribeTopics = [
                    topic,
                    'utm/drones/+/telemetry',
                    'utm/drones/+/status',
                    'utm/drones/DRONE-3894D4BD2A58/telemetry',
                    'utm/drones/DRONE-3894D4BD2A58/status',
                    'utm/drones/DRONE-40573255F188/telemetry',
                    'utm/drones/DRONE-40573255F188/status',
                    'utm/drone-alpha/telemetry',
                    'utm/+/telemetry',
                    'utm/#'
                ];
                [...new Set(subscribeTopics)].forEach(subTopic => {
                    esp32MqttClient.subscribe(subTopic, {
                        qos: 0,
                        onSuccess: () => {
                            console.log(`[UTM] Subscribed to topic: ${subTopic}`);
                        },
                        onFailure: (err) => {
                            console.warn(`[UTM] Subscribe failure for ${subTopic}:`, err);
                        }
                    });
                });
                updateEsp32MqttStatus('connected', `🟢 Listening: Fleet Telemetry`);
            },
            onFailure: (err) => {
                console.warn('[UTM] HiveMQ connection failed:', err);
                if (Date.now() - lastReceivedTimestamp > 15000) {
                    updateEsp32MqttStatus('disconnected', 'MQTT Connect Failed');
                }
                if (elements.btnConnectEspMqtt) elements.btnConnectEspMqtt.style.display = 'inline-block';
                if (elements.btnDisconnectEspMqtt) elements.btnDisconnectEspMqtt.style.display = 'none';
            }
        };

        try {
            esp32MqttClient.connect(connectOptions);
        } catch (err) {
            console.error('[UTM] MQTT Client error:', err);
            updateEsp32MqttStatus('disconnected', 'MQTT Error');
        }
    }

    function disconnectEsp32Mqtt() {
        if (esp32MqttClient) {
            try { esp32MqttClient.disconnect(); } catch (e) { }
            esp32MqttClient = null;
        }
        updateEsp32MqttStatus('disconnected', 'MQTT Disconnected');
        if (elements.btnConnectEspMqtt) elements.btnConnectEspMqtt.style.display = 'inline-block';
        if (elements.btnDisconnectEspMqtt) elements.btnDisconnectEspMqtt.style.display = 'none';
    }

    function updateEsp32MqttStatus(state, text) {
        if (!elements.esp32MqttStatusBadge || !elements.esp32MqttDot || !elements.esp32MqttStatusText) return;
        if (elements.esp32MqttStatusText) elements.esp32MqttStatusText.textContent = text;
        if (state === 'connected') {
            elements.esp32MqttStatusBadge.style.background = '#ecfdf5';
            elements.esp32MqttStatusBadge.style.color = '#065f46';
            elements.esp32MqttStatusBadge.style.borderColor = '#a7f3d0';
            elements.esp32MqttDot.className = 'status-indicator-dot dot-green';
            if (elements.hardwareOfflineAlert) elements.hardwareOfflineAlert.style.display = 'none';
        } else if (state === 'connecting') {
            elements.esp32MqttStatusBadge.style.background = '#fffbeb';
            elements.esp32MqttStatusBadge.style.color = '#b45309';
            elements.esp32MqttStatusBadge.style.borderColor = '#fde68a';
            elements.esp32MqttDot.className = 'status-indicator-dot dot-amber';
        } else {
            elements.esp32MqttStatusBadge.style.background = '#fef2f2';
            elements.esp32MqttStatusBadge.style.color = '#b91c1c';
            elements.esp32MqttStatusBadge.style.borderColor = '#fecaca';
            elements.esp32MqttDot.className = 'status-indicator-dot dot-red';
        }
    }

    // -------------------------------------------------------------------------
    // Legacy ESP32 Direct WebSocket Bridge Client
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
        } catch (e) { }

        if (esp32WebSocket) {
            try { esp32WebSocket.close(); } catch (e) { }
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
                    const lat = parseFloat(data.lat !== undefined ? data.lat : data.latitude);
                    const lon = parseFloat(data.lon !== undefined ? data.lon : data.longitude);
                    const alt = parseFloat(data.alt !== undefined ? data.alt : (data.altitude || 0));
                    const hdg = parseFloat(data.heading !== undefined ? data.heading : (data.hdg || 0));
                    const droneId = data.id || data.drone_id || 'DRONE-ALPHA';

                    if (isNaN(lat) || isNaN(lon)) return;

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

                    updateDroneUI(telemetryObj, apiState);

                    fetch('/api/telemetry/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(telemetryObj)
                    }).catch(() => { });

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
            try { esp32WebSocket.close(); } catch (e) { }
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

        // ESP32 4G LTE MQTT Controls
        if (elements.btnConnectEspMqtt) elements.btnConnectEspMqtt.addEventListener('click', connectEsp32Mqtt);
        if (elements.btnDisconnectEspMqtt) elements.btnDisconnectEspMqtt.addEventListener('click', disconnectEsp32Mqtt);
        if (elements.esp32MqttTopic) {
            elements.esp32MqttTopic.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') connectEsp32Mqtt();
            });
        }

        // Legacy ESP32 WebSocket Bridge Controls
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
        if (elements.btnToggleDigitalSky) elements.btnToggleDigitalSky.addEventListener('click', toggleDigitalSkyMap);
        if (elements.btnCloseLegend) elements.btnCloseLegend.addEventListener('click', () => showDigitalSkyLegend(false));
        if (elements.btnFitFleet) elements.btnFitFleet.addEventListener('click', fitAllDrones);

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
                if (skeleton) skeleton.style.opacity = '1';
                if (actual) {
                    actual.style.display = 'none';
                    actual.style.opacity = '0';
                }
                if (gradientBg) gradientBg.style.opacity = '0';

                // Sequence
                setTimeout(() => {
                    if (gradientBg) gradientBg.style.opacity = '1';
                    setTimeout(() => {
                        if (skeleton) skeleton.style.opacity = '0';
                        setTimeout(() => {
                            if (actual) {
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

    window.startSimulator = function () {
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
            marker.on('click', function () {
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

        map.setView([startLat, startLng], 14, { animate: true });

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
                    d.speed = Math.sqrt(dx * dx + dy * dy) * 111320; // roughly meters/sec
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

    window.stopSimulator = function () {
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
        } catch (e) { }

        const urlParams = new URLSearchParams(window.location.search);
        const requestedMode = urlParams.get('mode') || (function () {
            try { return localStorage.getItem('utm_active_mode'); } catch (e) { return null; }
        })();

        if (requestedMode === 'drone') {
            setDashboardMode('drone');
        }

        // Polling interval set to 2000ms (2 seconds delay to eliminate UI flickering)
        pollTimer = setInterval(fetchActiveTelemetry, 2000);
        fetchActiveTelemetry();

        // Auto-connect to 4G LTE HiveMQ MQTT broker for real-time fleet stream
        connectEsp32Mqtt();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.setDashboardMode = setDashboardMode;
    window.clearMapHistory = function () {
        trailCoordinates = [];
        if (movementTrail) movementTrail.setLatLngs([]);

        // Clear all main mode markers
        for (let id in mainModeMarkers) {
            if (mainModeMarkers[id]) map.removeLayer(mainModeMarkers[id]);
        }
        mainModeMarkers = {};

        // Clear simulator markers
        if (typeof simulatorState !== 'undefined' && simulatorState.markers) {
            simulatorState.markers.forEach(m => {
                if (m.marker) map.removeLayer(m.marker);
                if (m.circle) map.removeLayer(m.circle);
                if (m.path) map.removeLayer(m.path);
            });
            simulatorState.markers = [];
        }

        // Only reset telemetry UI and active marker if in simulator or phone mode
        if (activeMode === 'simulator' || activeMode === 'phone') {
            activeMarker = null;
            resetTelemetryUI();
        }
    };
})();

