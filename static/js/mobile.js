/**
 * UTM - Unified Telemetry Monitor
 * Phone GPS Test Mode Client (mobile.js)
 * 
 * Captures real-time device GPS coordinates via Geolocation API
 * and transmits telemetry packets continuously to Django /api/phone-location/.
 */

(function () {
    'use strict';

    // State Variables
    let watchId = null;
    let packetsSentCount = 0;
    let isTracking = false;
    let wakeLock = null;
    let latestCoords = null;
    let lastTransmitTime = 0;
    let heartbeatTimer = null;

    // DOM Elements - Actions
    const btnMainBroadcast = document.getElementById('btnMainBroadcast');
    const btnStartTracking = document.getElementById('btnStartTracking');
    const btnStartText = document.getElementById('btnStartText');
    const btnForceRefresh = document.getElementById('btnForceRefresh');
    const radarContainer = document.getElementById('radarContainer');
    const iconIdle = document.getElementById('iconIdle');
    const iconActive = document.getElementById('iconActive');

    // DOM Elements - Status & Radar Content
    const radarTitle = document.getElementById('radarTitle');
    const radarSub = document.getElementById('radarSub');
    const statusBadge = document.getElementById('statusBadge');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const rateIndicator = document.getElementById('rateIndicator');

    // DOM Elements - Telemetry Cards
    const valLat = document.getElementById('valLat');
    const subLat = document.getElementById('subLat');
    const valLon = document.getElementById('valLon');
    const subLon = document.getElementById('subLon');
    const valAlt = document.getElementById('valAlt');
    const subAlt = document.getElementById('subAlt');
    const valHeading = document.getElementById('valHeading');
    const subHeading = document.getElementById('subHeading');
    const miniCompassNeedle = document.getElementById('miniCompassNeedle');
    const valSpeed = document.getElementById('valSpeed');
    const subSpeed = document.getElementById('subSpeed');
    const valAccuracy = document.getElementById('valAccuracy');
    const subAccuracy = document.getElementById('subAccuracy');
    const valTimestamp = document.getElementById('valTimestamp');
    const packetBadge = document.getElementById('packetBadge');

    // DOM Elements - Diagnostics
    const diagDeviceId = document.getElementById('diagDeviceId');
    const diagHost = document.getElementById('diagHost');
    const diagWakeLock = document.getElementById('diagWakeLock');
    const diagPacketsSent = document.getElementById('diagPacketsSent');
    const diagServerStatus = document.getElementById('diagServerStatus');
    const accuracyGuideCard = document.getElementById('accuracyGuideCard');
    const accuracyGuideTitle = document.getElementById('accuracyGuideTitle');
    const secureContextTag = document.getElementById('secureContextTag');

    // Configuration from body attributes
    const deviceId = document.body.dataset.deviceId || 'phone_test_01';
    const INGEST_API_URL = '/api/phone-location/';

    // -------------------------------------------------------------------------
    // Silent Audio Keep-Alive Context
    // Prevents mobile browsers (e.g. Android Chrome) from putting background tabs to sleep
    // -------------------------------------------------------------------------
    let audioKeepAliveCtx = null;
    let audioKeepAliveOsc = null;

    function startKeepAliveAudio() {
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            if (!audioKeepAliveCtx) {
                audioKeepAliveCtx = new AudioCtx();
                audioKeepAliveOsc = audioKeepAliveCtx.createOscillator();
                const gain = audioKeepAliveCtx.createGain();
                gain.gain.value = 0.00001; // Inaudible
                audioKeepAliveOsc.connect(gain);
                gain.connect(audioKeepAliveCtx.destination);
                audioKeepAliveOsc.start();
            }
            if (audioKeepAliveCtx.state === 'suspended') {
                audioKeepAliveCtx.resume();
            }
        } catch (e) {
            console.log('[UTM Mobile] Audio keepalive notice:', e);
        }
    }

    function stopKeepAliveAudio() {
        try {
            if (audioKeepAliveCtx && audioKeepAliveCtx.state !== 'closed') {
                audioKeepAliveCtx.suspend().catch(() => {});
            }
        } catch (e) {}
    }

    // -------------------------------------------------------------------------
    // Screen Wake Lock API
    // -------------------------------------------------------------------------
    async function requestWakeLock() {
        try {
            if ('wakeLock' in navigator) {
                wakeLock = await navigator.wakeLock.request('screen');
                if (diagWakeLock) {
                    diagWakeLock.textContent = 'Active (Screen On)';
                    diagWakeLock.style.color = '#16a34a';
                }
                wakeLock.addEventListener('release', () => {
                    if (isTracking) requestWakeLock();
                });
            } else {
                if (diagWakeLock) diagWakeLock.textContent = 'Not Supported';
            }
        } catch (err) {
            console.warn('[UTM Mobile] WakeLock error:', err);
            if (diagWakeLock) diagWakeLock.textContent = 'Unavailable';
        }
    }

    function releaseWakeLock() {
        if (wakeLock !== null) {
            wakeLock.release().catch(() => {});
            wakeLock = null;
            if (diagWakeLock) {
                diagWakeLock.textContent = 'Inactive';
                diagWakeLock.style.color = '';
            }
        }
    }

    // -------------------------------------------------------------------------
    // UI State Helpers
    // -------------------------------------------------------------------------
    function setBadgeState(state, text) {
        if (!statusBadge || !statusText) return;
        statusBadge.className = 'status-badge';
        if (state === 'streaming') {
            statusBadge.classList.add('status-streaming');
        } else if (state === 'acquiring') {
            statusBadge.classList.add('status-acquiring');
        } else if (state === 'stopped') {
            statusBadge.classList.add('status-stopped');
        } else {
            statusBadge.classList.add('status-idle');
        }
        statusText.textContent = text;
    }

    // -------------------------------------------------------------------------
    // Start GPS Tracking
    // -------------------------------------------------------------------------
    function startTracking() {
        if (isTracking) return;

        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your mobile browser. Please use Chrome or Safari.');
            return;
        }

        // Haptic feedback
        if ('vibrate' in navigator) {
            try { navigator.vibrate(60); } catch (e) {}
        }

        // Screen WakeLock
        requestWakeLock();
        startKeepAliveAudio();

        isTracking = true;

        // Visual Updates
        if (radarContainer) radarContainer.classList.add('radar-active');
        if (iconIdle) iconIdle.style.display = 'none';
        if (iconActive) iconActive.style.display = 'block';

        if (radarTitle) radarTitle.textContent = 'Broadcasting GPS Live';
        if (radarSub) radarSub.textContent = 'Streaming coordinates directly to UTM Tactical Map';

        if (btnStartTracking) {
            btnStartTracking.className = 'btn btn-action-stop';
            if (btnStartText) btnStartText.textContent = 'Stop Live Broadcast';
        }
        if (btnForceRefresh) btnForceRefresh.disabled = false;
        if (rateIndicator) {
            rateIndicator.textContent = '● Connecting...';
            rateIndicator.classList.add('live');
        }

        setBadgeState('acquiring', 'Acquiring Satellite Lock...');

        const geoOptions = {
            enableHighAccuracy: true,
            timeout: 25000,
            maximumAge: 0
        };

        // 1. Immediate Initial Query for fastest fix
        navigator.geolocation.getCurrentPosition(
            (pos) => onLocationSuccess(pos),
            (err) => console.log('[UTM Mobile] Initial fix query notice:', err),
            geoOptions
        );

        // 2. Continuous watchPosition
        try {
            watchId = navigator.geolocation.watchPosition(
                onLocationSuccess,
                onLocationError,
                geoOptions
            );
            console.log(`[UTM Mobile] Geolocation watch initialized: ${watchId}`);

            // Heartbeat: keeps stream live even if completely stationary
            heartbeatTimer = setInterval(() => {
                if (isTracking && latestCoords && (Date.now() - lastTransmitTime >= 2000)) {
                    transmitHeartbeat();
                }
            }, 1000);

        } catch (err) {
            console.error('[UTM Mobile] watchPosition failed:', err);
            handleError('Failed to initialize GPS: ' + err.message);
        }
    }

    // -------------------------------------------------------------------------
    // Stop GPS Tracking
    // -------------------------------------------------------------------------
    function stopTracking() {
        if (!isTracking) return;

        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }

        if (heartbeatTimer !== null) {
            clearInterval(heartbeatTimer);
            heartbeatTimer = null;
        }

        releaseWakeLock();
        stopKeepAliveAudio();

        isTracking = false;
        latestCoords = null;

        // Visual Updates
        if (radarContainer) radarContainer.classList.remove('radar-active');
        if (iconIdle) iconIdle.style.display = 'block';
        if (iconActive) iconActive.style.display = 'none';

        if (radarTitle) radarTitle.textContent = 'Tap to Start GPS Broadcast';
        if (radarSub) radarSub.textContent = 'Stream high-precision smartphone GPS to the UTM live map';

        if (btnStartTracking) {
            btnStartTracking.className = 'btn btn-action-start';
            if (btnStartText) btnStartText.textContent = 'Start Live Broadcast';
        }
        if (btnForceRefresh) btnForceRefresh.disabled = true;
        if (rateIndicator) {
            rateIndicator.textContent = '○ Standby';
            rateIndicator.classList.remove('live');
        }
        if (accuracyGuideCard) accuracyGuideCard.style.display = 'none';

        setBadgeState('stopped', 'Broadcast Stopped');

        if (diagServerStatus) {
            diagServerStatus.textContent = 'Stopped';
            diagServerStatus.style.color = 'var(--text-muted)';
        }
    }

    // Toggle Handler
    function toggleTracking() {
        if (isTracking) {
            stopTracking();
        } else {
            startTracking();
        }
    }

    // -------------------------------------------------------------------------
    // Location Success Callback
    // -------------------------------------------------------------------------
    function onLocationSuccess(position) {
        if (!isTracking) return;

        const coords = position.coords;
        latestCoords = coords;
        lastTransmitTime = Date.now();
        const now = new Date(position.timestamp || Date.now());

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
        const isoTimestamp = now.toISOString();
        const displayTime = now.toLocaleTimeString();

        // Accuracy State & Guidance
        if (accuracy !== null) {
            if (accuracy > 80) {
                setBadgeState('acquiring', `Coarse Network (±${accuracy.toFixed(0)}m)`);
                if (accuracyGuideCard) {
                    accuracyGuideCard.style.display = 'block';
                    if (accuracyGuideTitle) accuracyGuideTitle.textContent = `Coarse Fix (±${accuracy.toFixed(0)}m) — Enable "Precise Location" in Chrome`;
                }
            } else if (accuracy > 25) {
                setBadgeState('acquiring', `Acquiring Satellites (±${accuracy.toFixed(1)}m)`);
                if (accuracyGuideCard) {
                    accuracyGuideCard.style.display = 'block';
                    if (accuracyGuideTitle) accuracyGuideTitle.textContent = `Satellite Fix Found (±${accuracy.toFixed(1)}m) — Move outdoors for ±3m`;
                }
            } else {
                setBadgeState('streaming', `3D GNSS Locked (±${accuracy.toFixed(1)}m)`);
                if (accuracyGuideCard) accuracyGuideCard.style.display = 'none';
            }
        } else {
            setBadgeState('streaming', 'GPS Broadcasting');
        }

        // Update Telemetry Cards
        if (valLat) valLat.textContent = `${lat.toFixed(6)}°`;
        if (subLat) subLat.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;

        if (valLon) valLon.textContent = `${lon.toFixed(6)}°`;
        if (subLon) subLon.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;

        if (valAlt) valAlt.textContent = alt !== null ? `${alt} m` : 'N/A';
        if (subAlt) subAlt.textContent = alt !== null ? 'MSL Altitude' : 'Unavailable';

        if (valHeading) valHeading.textContent = heading !== null ? `${Math.round(heading)}°` : 'N/A';
        if (subHeading) subHeading.textContent = heading !== null ? getCardinalDirection(heading) : 'Azimuth Cardinal';
        if (miniCompassNeedle && heading !== null) {
            miniCompassNeedle.style.transform = `rotate(${heading}deg)`;
            miniCompassNeedle.style.transformOrigin = 'center';
        }

        if (valSpeed) valSpeed.textContent = speed !== null ? `${speed.toFixed(1)} m/s` : '0.0 m/s';
        if (subSpeed) subSpeed.textContent = speed !== null ? `${(speed * 3.6).toFixed(1)} km/h` : '0.0 km/h';

        if (valAccuracy) valAccuracy.textContent = accuracy !== null ? `±${accuracy.toFixed(1)} m` : 'N/A';
        if (subAccuracy) {
            if (accuracy !== null) {
                subAccuracy.textContent = accuracy <= 15 ? 'High Satellite Precision' : (accuracy <= 50 ? 'Moderate Satellite Lock' : 'Cell Tower / Coarse');
            }
        }

        if (valTimestamp) valTimestamp.textContent = displayTime;
        if (rateIndicator) rateIndicator.textContent = '● Live 1Hz Stream';

        // Build Payload
        const payload = {
            device_id: deviceId,
            latitude: Number(lat.toFixed(6)),
            longitude: Number(lon.toFixed(6)),
            altitude: alt,
            heading: heading,
            accuracy: accuracy,
            speed: speed,
            timestamp: isoTimestamp,
            source: 'phone_test'
        };

        sendTelemetryToDjango(payload);
    }

    // Helper: Cardinal direction
    function getCardinalDirection(deg) {
        const cardinals = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'];
        const index = Math.round((deg % 360) / 45);
        return cardinals[index];
    }

    // Transmit heartbeat when still
    function transmitHeartbeat() {
        if (!isTracking || !latestCoords) return;
        lastTransmitTime = Date.now();

        const lat = latestCoords.latitude;
        const lon = latestCoords.longitude;
        const alt = latestCoords.altitude !== null ? Number(latestCoords.altitude.toFixed(1)) : null;
        const heading = (latestCoords.heading !== null && latestCoords.heading >= 0) ? Number((latestCoords.heading % 360).toFixed(1)) : null;
        const accuracy = latestCoords.accuracy !== null ? Number(latestCoords.accuracy.toFixed(1)) : null;
        const speed = (latestCoords.speed !== null && latestCoords.speed >= 0) ? Number(latestCoords.speed.toFixed(1)) : null;

        const payload = {
            device_id: deviceId,
            latitude: Number(lat.toFixed(6)),
            longitude: Number(lon.toFixed(6)),
            altitude: alt,
            heading: heading,
            accuracy: accuracy,
            speed: speed,
            timestamp: new Date().toISOString(),
            source: 'phone_test'
        };

        sendTelemetryToDjango(payload);
    }

    // -------------------------------------------------------------------------
    // Location Error Callback
    // -------------------------------------------------------------------------
    function onLocationError(error) {
        console.warn('[UTM Mobile] Geolocation notice:', error);

        if (error.code === error.TIMEOUT && latestCoords) {
            // Keep active fix on intermittent GPS timeout
            return;
        }

        let msg = 'GPS acquisition issue';
        if (error.code === error.PERMISSION_DENIED) {
            msg = 'Location permission denied in browser';
            alert('Location Permission Required: Please tap the lock icon in your address bar and allow Location access.');
        } else if (error.code === error.POSITION_UNAVAILABLE) {
            msg = 'GPS Signal Unavailable (Ensure GPS is turned ON)';
        } else if (error.code === error.TIMEOUT) {
            msg = 'Searching for Satellites...';
        }

        if (!latestCoords) {
            setBadgeState('acquiring', msg);
            if (diagServerStatus) {
                diagServerStatus.textContent = msg;
                diagServerStatus.style.color = '#ef4444';
            }
        }
    }

    function handleError(msg) {
        stopTracking();
        setBadgeState('stopped', msg);
    }

    // -------------------------------------------------------------------------
    // Force Fresh Satellite Sync
    // -------------------------------------------------------------------------
    function forceFreshGpsSync() {
        if (!navigator.geolocation) return;
        setBadgeState('acquiring', 'Polling GNSS Chip...');
        if (btnForceRefresh) btnForceRefresh.textContent = 'Syncing...';

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                onLocationSuccess(pos);
                if (btnForceRefresh) {
                    btnForceRefresh.textContent = 'Instant Satellite Sync';
                }
            },
            (err) => {
                onLocationError(err);
                if (btnForceRefresh) {
                    btnForceRefresh.textContent = 'Instant Satellite Sync';
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 25000,
                maximumAge: 0
            }
        );
    }

    // -------------------------------------------------------------------------
    // POST Telemetry to Django Backend
    // -------------------------------------------------------------------------
    async function sendTelemetryToDjango(payload) {
        try {
            const response = await fetch(INGEST_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                packetsSentCount++;
                if (diagPacketsSent) diagPacketsSent.textContent = packetsSentCount;
                if (packetBadge) packetBadge.textContent = `Packets: ${packetsSentCount}`;
                if (diagServerStatus) {
                    diagServerStatus.textContent = `HTTP ${response.status} OK (Delivered)`;
                    diagServerStatus.style.color = '#16a34a';
                }
            } else {
                const errData = await response.json().catch(() => ({}));
                console.error('[UTM Mobile] Server error:', response.status, errData);
                if (diagServerStatus) {
                    diagServerStatus.textContent = `HTTP ${response.status} Error`;
                    diagServerStatus.style.color = '#ef4444';
                }
            }
        } catch (netErr) {
            console.error('[UTM Mobile] Transmission failure:', netErr);
            if (diagServerStatus) {
                diagServerStatus.textContent = 'Network Offline';
                diagServerStatus.style.color = '#ef4444';
            }
        }
    }

    // -------------------------------------------------------------------------
    // Initialization
    // -------------------------------------------------------------------------
    function init() {
        // Secure context check
        const isSecure = window.isSecureContext || window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        if (secureContextTag) {
            if (isSecure) {
                secureContextTag.textContent = '🔒 SECURE HTTPS';
                secureContextTag.style.background = 'rgba(22, 163, 74, 0.25)';
                secureContextTag.style.color = '#86efac';
            } else {
                secureContextTag.textContent = '⚠️ HTTP';
                secureContextTag.style.background = 'rgba(220, 38, 38, 0.25)';
                secureContextTag.style.color = '#fca5a5';
            }
        }

        // Attach Event Listeners
        if (btnMainBroadcast) btnMainBroadcast.addEventListener('click', toggleTracking);
        if (btnStartTracking) btnStartTracking.addEventListener('click', toggleTracking);
        if (btnForceRefresh) btnForceRefresh.addEventListener('click', forceFreshGpsSync);

        // Resume WakeLock and GPS when returning to tab
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && isTracking) {
                requestWakeLock();
                startKeepAliveAudio();
                if (Date.now() - lastTransmitTime > 3000) {
                    forceFreshGpsSync();
                }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
