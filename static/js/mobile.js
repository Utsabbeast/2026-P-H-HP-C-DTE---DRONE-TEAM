/**
 * UTM - Unified Telemetry Monitor
 * Phone GPS Test Mode Client (mobile.js)
 *
 * Captures real-time device GPS coordinates via navigator.geolocation.watchPosition()
 * and continuously transmits telemetry packets over Wi-Fi to Django /api/phone-location/.
 */

(function () {
    'use strict';

    // State
    let watchId = null;
    let packetsSentCount = 0;
    let isTracking = false;
    let wakeLock = null;
    let latestCoords = null;
    let lastTransmitTime = 0;
    let heartbeatTimer = null;

    // DOM Elements
    const btnStart = document.getElementById('btnStart');
    const btnStop = document.getElementById('btnStop');
    const btnForceRefresh = document.getElementById('btnForceRefresh');
    const accuracyGuideCard = document.getElementById('accuracyGuideCard');
    const accuracyGuideTitle = document.getElementById('accuracyGuideTitle');
    const statusCard = document.getElementById('statusCard');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const statusDetail = document.getElementById('statusDetail');

    // Telemetry Values
    const valLat = document.getElementById('valLat');
    const valLon = document.getElementById('valLon');
    const valAlt = document.getElementById('valAlt');
    const valHeading = document.getElementById('valHeading');
    const valAccuracy = document.getElementById('valAccuracy');
    const valSpeed = document.getElementById('valSpeed');
    const valTimestamp = document.getElementById('valTimestamp');

    // Diagnostics
    const diagPacketsSent = document.getElementById('diagPacketsSent');
    const diagServerStatus = document.getElementById('diagServerStatus');
    const diagWakeLock = document.getElementById('diagWakeLock');
    const securityBanner = document.getElementById('securityBanner');
    const securityBannerTitle = document.getElementById('securityBannerTitle');
    const securityBannerDesc = document.getElementById('securityBannerDesc');

    // Configuration from body attributes
    const deviceId = document.body.dataset.deviceId || 'phone_test_01';
    const localIp = document.body.dataset.localIp || window.location.hostname;
    const INGEST_API_URL = '/api/phone-location/';

    // Silent Audio Keep-Alive Context (Prevents Android Chrome from freezing background JS)
    let audioKeepAliveCtx = null;
    let audioKeepAliveOsc = null;

    function startKeepAliveAudio() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            if (!audioKeepAliveCtx) {
                audioKeepAliveCtx = new AudioContext();
                audioKeepAliveOsc = audioKeepAliveCtx.createOscillator();
                const gain = audioKeepAliveCtx.createGain();
                gain.gain.value = 0.00001; // Virtually inaudible
                audioKeepAliveOsc.connect(gain);
                gain.connect(audioKeepAliveCtx.destination);
                audioKeepAliveOsc.start();
            }
            if (audioKeepAliveCtx.state === 'suspended') {
                audioKeepAliveCtx.resume();
            }
        } catch (e) {
            console.log('[UTM Mobile] Audio keepalive note:', e);
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
    // Screen Wake Lock API (Keeps phone screen on while streaming)
    // -------------------------------------------------------------------------
    async function requestWakeLock() {
        try {
            if ('wakeLock' in navigator) {
                wakeLock = await navigator.wakeLock.request('screen');
                if (diagWakeLock) {
                    diagWakeLock.textContent = 'Active (Screen On)';
                    diagWakeLock.style.color = '#10b981';
                }
                wakeLock.addEventListener('release', () => {
                    if (isTracking) {
                        // Re-acquire if released due to app switcher
                        requestWakeLock();
                    }
                });
            } else {
                if (diagWakeLock) diagWakeLock.textContent = 'Not supported';
            }
        } catch (err) {
            console.warn('[UTM Mobile] Wake Lock error:', err);
            if (diagWakeLock) diagWakeLock.textContent = 'Unavailable';
        }
    }

    function releaseWakeLock() {
        if (wakeLock !== null) {
            wakeLock.release().catch(() => {});
            wakeLock = null;
            if (diagWakeLock) {
                diagWakeLock.textContent = 'Inactive';
                diagWakeLock.style.color = 'var(--text-muted)';
            }
        }
    }

    // -------------------------------------------------------------------------
    // Initialization & Secure Context Detection
    // -------------------------------------------------------------------------
    function init() {
        // Detect context (Android Chrome requires HTTPS for Geolocation on external domains)
        const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        if (securityBanner) {
            if (window.isSecureContext || window.location.protocol === 'https:' || isLocalhost) {
                securityBanner.classList.add('secure');
                if (securityBannerTitle) securityBannerTitle.textContent = '🔒 Secure HTTPS Context Active';
                if (securityBannerDesc) securityBannerDesc.textContent = 'High-accuracy GPS sensor permission is enabled for cloud streaming.';
                securityBanner.style.display = 'block';
            } else {
                securityBanner.classList.remove('secure');
                if (securityBannerTitle) securityBannerTitle.textContent = '⚠️ Insecure HTTP Context';
                if (securityBannerDesc) securityBannerDesc.textContent = 'Android Chrome requires HTTPS to allow GPS access. Access this site over HTTPS.';
                securityBanner.style.display = 'block';
            }
        }

        // Attach event listeners
        if (btnStart) btnStart.addEventListener('click', startTracking);
        if (btnStop) btnStop.addEventListener('click', stopTracking);
        if (btnForceRefresh) btnForceRefresh.addEventListener('click', forceFreshGpsSync);

        // Resume WakeLock and GPS when returning to tab from background
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && isTracking) {
                requestWakeLock();
                startKeepAliveAudio();
                // If more than 4 seconds elapsed without fix, trigger immediate GPS poll
                if (Date.now() - lastTransmitTime > 4000) {
                    forceFreshGpsSync();
                }
            }
        });

        // Check if Geolocation is supported
        if (!navigator.geolocation) {
            updateStatus('error', '⚠️ Geolocation Unsupported', 'This browser does not support the Geolocation API.');
            if (btnStart) btnStart.disabled = true;
        }
    }

    // -------------------------------------------------------------------------
    // Status Display Helpers
    // -------------------------------------------------------------------------
    function updateStatus(state, mainText, detailText) {
        if (!statusIndicator || !statusText || !statusDetail) return;

        statusIndicator.className = 'status-indicator';
        if (state === 'active') {
            statusIndicator.classList.add('status-active');
        } else if (state === 'warning' || state === 'error') {
            statusIndicator.classList.add('status-warning');
        } else {
            statusIndicator.classList.add('status-stopped');
        }

        statusText.textContent = mainText;
        statusDetail.textContent = detailText;
    }

    // -------------------------------------------------------------------------
    // Start GPS Tracking
    // -------------------------------------------------------------------------
    function startTracking() {
        // Prevent duplicate watchers
        if (watchId !== null || isTracking) {
            console.warn('[UTM Mobile] Tracking is already active. Ignoring start request.');
            return;
        }

        if (!navigator.geolocation) {
            updateStatus('error', '⚠️ Geolocation Unsupported', 'Your browser does not support location services.');
            return;
        }

        // Haptic feedback if supported
        if ('vibrate' in navigator) {
            try { navigator.vibrate(50); } catch (e) {}
        }

        // Request Screen Wake Lock so phone doesn't sleep in hand
        requestWakeLock();

        // Start inaudible audio keepalive so Android Chrome doesn't suspend background JS
        startKeepAliveAudio();

        // Update UI state to starting
        isTracking = true;
        btnStart.disabled = true;
        btnStop.disabled = false;
        if (btnForceRefresh) btnForceRefresh.disabled = false;
        updateStatus('warning', '🟡 Acquiring GPS Satellite Lock...', 'Requesting high-accuracy GPS coordinates directly from GNSS hardware...');

        const geoOptions = {
            enableHighAccuracy: true, // Forces Android to power on raw GNSS satellite receiver
            timeout: 30000,           // 30s timeout allows GNSS hardware time to lock 4+ satellites
            maximumAge: 0             // Strictly 0: Do NOT accept cached cell-tower or network fixes
        };

        try {
            watchId = navigator.geolocation.watchPosition(
                onLocationSuccess,
                onLocationError,
                geoOptions
            );
            console.log(`[UTM Mobile] Geolocation watch initialized with ID: ${watchId}`);

            // Heartbeat fallback: keeps live connection alive even when stationary
            heartbeatTimer = setInterval(() => {
                if (isTracking && latestCoords && (Date.now() - lastTransmitTime >= 2500)) {
                    transmitHeartbeat();
                }
            }, 1000);

        } catch (err) {
            console.error('[UTM Mobile] Failed to start watchPosition:', err);
            handleGeneralError('Failed to initialize GPS watcher: ' + err.message);
        }
    }

    // -------------------------------------------------------------------------
    // Stop GPS Tracking
    // -------------------------------------------------------------------------
    function stopTracking() {
        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
            console.log(`[UTM Mobile] Cleared geolocation watch ID: ${watchId}`);
            watchId = null;
        }

        if (heartbeatTimer !== null) {
            clearInterval(heartbeatTimer);
            heartbeatTimer = null;
        }

        releaseWakeLock();
        stopKeepAliveAudio();
        latestCoords = null;

        isTracking = false;
        btnStart.disabled = false;
        btnStop.disabled = true;
        if (btnForceRefresh) btnForceRefresh.disabled = true;
        if (accuracyGuideCard) accuracyGuideCard.style.display = 'none';

        updateStatus('stopped', '🔴 GPS Tracking Stopped', 'Tracking halted. No location data is being transmitted.');
        if (diagServerStatus) {
            diagServerStatus.textContent = 'Stopped';
            diagServerStatus.style.color = 'var(--text-muted)';
        }
    }

    // -------------------------------------------------------------------------
    // Geolocation Success Callback (Triggered on every native GPS update)
    // -------------------------------------------------------------------------
    function updateAccuracyUI(accuracy) {
        if (!isTracking) return;

        if (accuracy === null || isNaN(accuracy)) {
            updateStatus('active', '🟢 GPS Tracking Active', 'Transmitting coordinates to UTM dashboard...');
            if (accuracyGuideCard) accuracyGuideCard.style.display = 'none';
            return;
        }

        if (accuracy > 100) {
            // Coarse Cell Tower Triangulation (~1400m)
            updateStatus('warning', `⚠️ Coarse Network Fix (±${accuracy.toFixed(0)}m)`, 'Using approximate cell-tower data. Enable "Precise location" in Chrome.');
            if (accuracyGuideCard) {
                accuracyGuideCard.style.display = 'block';
                accuracyGuideCard.classList.remove('success');
            }
            if (accuracyGuideTitle) {
                accuracyGuideTitle.textContent = `⚠️ Cell Tower Fix (±${accuracy.toFixed(0)}m) — Tap Lock Icon 🔒 & Enable "Precise Location"`;
            }
        } else if (accuracy > 25) {
            // Moderate GPS (acquiring satellites)
            updateStatus('warning', `🟡 Acquiring Satellites (±${accuracy.toFixed(1)}m)`, 'Satellite signal found. Move near a window or outdoors for ±3m precision.');
            if (accuracyGuideCard) {
                accuracyGuideCard.style.display = 'block';
                accuracyGuideCard.classList.remove('success');
            }
            if (accuracyGuideTitle) {
                accuracyGuideTitle.textContent = `🟡 Acquiring Full Satellite Lock (±${accuracy.toFixed(1)}m) — Move Outdoors for 3m`;
            }
        } else {
            // High-precision Satellite GPS
            updateStatus('active', `🟢 Real Satellite GPS Locked (±${accuracy.toFixed(1)}m)`, `High-precision GNSS satellite lock active (Packet #${packetsSentCount}).`);
            if (accuracyGuideCard) {
                accuracyGuideCard.style.display = 'none';
            }
        }
    }

    function onLocationSuccess(position) {
        if (!isTracking) {
            // Guard against callbacks queued right before clearWatch
            return;
        }

        const coords = position.coords;
        latestCoords = coords;
        lastTransmitTime = Date.now();
        const now = new Date(position.timestamp || Date.now());

        // Extract values strictly without inventing fake fallbacks
        const lat = coords.latitude;
        const lon = coords.longitude;
        const rawAlt = coords.altitude;
        const rawHdg = coords.heading;
        const rawAcc = coords.accuracy;
        const rawSpd = coords.speed;

        const alt = (rawAlt !== null && !isNaN(rawAlt)) ? Number(rawAlt.toFixed(1)) : null;
        // On Android, negative values (< 0) are sentinel values representing unknown heading/speed
        const heading = (rawHdg !== null && !isNaN(rawHdg) && rawHdg >= 0) ? Number((rawHdg % 360).toFixed(1)) : null;
        const accuracy = (rawAcc !== null && !isNaN(rawAcc) && rawAcc >= 0) ? Number(rawAcc.toFixed(1)) : null;
        const speed = (rawSpd !== null && !isNaN(rawSpd) && rawSpd >= 0) ? Number(rawSpd.toFixed(1)) : null;
        const isoTimestamp = now.toISOString();
        const displayTime = now.toTimeString().split(' ')[0]; // HH:MM:SS

        // Update Phone UI elements immediately
        updateAccuracyUI(accuracy);

        if (valLat) valLat.textContent = lat.toFixed(6) + '°';
        if (valLon) valLon.textContent = lon.toFixed(6) + '°';
        if (valAlt) valAlt.innerHTML = alt !== null ? `${alt} <span class="card-unit">m</span>` : 'N/A';
        if (valHeading) valHeading.innerHTML = heading !== null ? `${heading} <span class="card-unit">°</span>` : 'N/A';
        
        if (valAccuracy) {
            if (accuracy !== null) {
                if (accuracy > 100) {
                    valAccuracy.innerHTML = `<span style="color: #ef4444;">${accuracy.toFixed(0)} <span class="card-unit">m (Coarse)</span></span>`;
                } else if (accuracy > 25) {
                    valAccuracy.innerHTML = `<span style="color: #f59e0b;">${accuracy.toFixed(1)} <span class="card-unit">m</span></span>`;
                } else {
                    valAccuracy.innerHTML = `<span style="color: #10b981;">${accuracy.toFixed(1)} <span class="card-unit">m (High-Acc)</span></span>`;
                }
            } else {
                valAccuracy.textContent = 'N/A';
            }
        }
        
        if (valSpeed) valSpeed.innerHTML = speed !== null ? `${speed} <span class="card-unit">m/s</span>` : 'N/A';
        if (valTimestamp) valTimestamp.textContent = displayTime;

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

        // Dispatch immediately to Django backend
        sendTelemetryToDjango(payload);
    }

    // Transmit heartbeat when stationary to maintain continuous dashboard connection
    function transmitHeartbeat() {
        if (!isTracking || !latestCoords) return;
        lastTransmitTime = Date.now();

        const lat = latestCoords.latitude;
        const lon = latestCoords.longitude;
        const rawAlt = latestCoords.altitude;
        const rawHdg = latestCoords.heading;
        const rawAcc = latestCoords.accuracy;
        const rawSpd = latestCoords.speed;

        const alt = (rawAlt !== null && !isNaN(rawAlt)) ? Number(rawAlt.toFixed(1)) : null;
        const heading = (rawHdg !== null && !isNaN(rawHdg) && rawHdg >= 0) ? Number((rawHdg % 360).toFixed(1)) : null;
        const accuracy = (rawAcc !== null && !isNaN(rawAcc) && rawAcc >= 0) ? Number(rawAcc.toFixed(1)) : null;
        const speed = (rawSpd !== null && !isNaN(rawSpd) && rawSpd >= 0) ? Number(rawSpd.toFixed(1)) : null;

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
    // Geolocation Error Callback
    // -------------------------------------------------------------------------
    function onLocationError(error) {
        console.warn('[UTM Mobile] Geolocation event:', error);

        // If we already have an active fix, do not flash red on intermittent satellite timeouts
        if (error.code === error.TIMEOUT && latestCoords) {
            console.log('[UTM Mobile] Intermittent GPS timeout; retaining active fix.');
            return;
        }

        let headline = '🔴 GPS Error';
        let detail = 'An unknown GPS error occurred.';

        switch (error.code) {
            case error.PERMISSION_DENIED:
                headline = '🔴 Permission Denied';
                detail = 'Location permission required. Please enable location permissions in your browser site settings.';
                break;
            case error.POSITION_UNAVAILABLE:
                headline = '🔴 GPS Signal Unavailable';
                detail = 'Device location is currently unavailable. Ensure GPS / Location is turned ON in Android settings.';
                break;
            case error.TIMEOUT:
                headline = '🟡 GPS Timeout';
                detail = 'GPS fix acquisition timed out. Searching for GPS satellites...';
                break;
            default:
                detail = error.message || detail;
                break;
        }

        if (!latestCoords) {
            updateStatus('error', headline, detail);

            if (diagServerStatus) {
                diagServerStatus.textContent = 'GPS Unavailable';
                diagServerStatus.style.color = '#ef4444';
            }
        }
    }

    function handleGeneralError(message) {
        stopTracking();
        updateStatus('error', '🔴 Error Occurred', message);
    }

    // -------------------------------------------------------------------------
    // Force Fresh GPS Satellite Sync (Bypasses cache with maximumAge: 0)
    // -------------------------------------------------------------------------
    function forceFreshGpsSync() {
        if (!navigator.geolocation) return;
        updateStatus('warning', '🛰️ Polling GNSS Satellites...', 'Requesting fresh hardware satellite coordinates directly from phone GNSS chip...');
        if (btnForceRefresh) {
            btnForceRefresh.disabled = true;
            btnForceRefresh.textContent = '🛰️ Polling Satellites...';
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                onLocationSuccess(pos);
                if (btnForceRefresh) {
                    btnForceRefresh.disabled = false;
                    btnForceRefresh.textContent = '🔄 Force Fresh Satellite GPS Fix';
                }
            },
            (err) => {
                console.warn('[UTM Mobile] Fresh GPS sync warning:', err);
                onLocationError(err);
                if (btnForceRefresh) {
                    btnForceRefresh.disabled = false;
                    btnForceRefresh.textContent = '🔄 Force Fresh Satellite GPS Fix';
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 30000,
                maximumAge: 0
            }
        );
    }

    // -------------------------------------------------------------------------
    // HTTP POST to Django Backend
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
                if (diagServerStatus) {
                    diagServerStatus.textContent = `Streaming Active (HTTP ${response.status} OK)`;
                    diagServerStatus.style.color = '#10b981';
                }
                // Maintain accurate warning/active status without blindly stamping generic green text
                const acc = payload.accuracy;
                if (acc !== null && acc > 100) {
                    updateStatus('warning', `⚠️ Coarse Network Fix (±${acc.toFixed(0)}m)`, `Packet #${packetsSentCount} sent. Follow guide below to enable "Precise location" in Chrome.`);
                } else if (acc !== null && acc > 25) {
                    updateStatus('warning', `🟡 Acquiring Satellites (±${acc.toFixed(1)}m)`, `Packet #${packetsSentCount} sent. Step outdoors for ±3m precision.`);
                } else {
                    updateStatus('active', `🟢 Real Satellite GPS Locked (±${acc !== null ? acc.toFixed(1) + 'm' : 'GNSS fix'})`, `Packet #${packetsSentCount} sent to website. Real-time streaming active.`);
                }
            } else {
                const errData = await response.json().catch(() => ({}));
                console.error('[UTM Mobile] Server error response:', response.status, errData);
                const detailMsg = errData.message || (errData.errors ? JSON.stringify(errData.errors) : `HTTP ${response.status}`);
                if (diagServerStatus) {
                    diagServerStatus.textContent = `Server Error (${response.status}): ${detailMsg}`;
                    diagServerStatus.style.color = '#ef4444';
                }
                updateStatus('warning', '⚠️ Server Rejected Packet', `Server HTTP ${response.status}: ${detailMsg}`);
            }
        } catch (netErr) {
            console.error('[UTM Mobile] Network transmission failure:', netErr);
            if (diagServerStatus) {
                diagServerStatus.textContent = `Network Offline: ${netErr.message}`;
                diagServerStatus.style.color = '#ef4444';
            }
            updateStatus('warning', '⚠️ Network Offline', 'Unable to reach server. Check internet connection.');
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();


// Fingerprint UI Logic
const fpBtn = document.getElementById('btnFingerprintStart');
const fpInst = document.getElementById('fpInstruction');
const fpTime = document.getElementById('fpTime');
const fpDate = document.getElementById('fpDate');

if (fpBtn) {
    fpBtn.addEventListener('click', () => {
        if (!isTracking) {
            startTracking();
            fpBtn.classList.add('active-pulse');
            fpInst.textContent = 'GPS Active - Tracking';
            fpInst.style.color = '#10b981';
        } else {
            stopTracking();
            fpBtn.classList.remove('active-pulse');
            fpInst.textContent = 'Tap to Activate GPS';
            fpInst.style.color = 'rgba(255, 255, 255, 0.8)';
        }
    });
}

// Update clock
setInterval(() => {
    const now = new Date();
    if(fpTime) fpTime.textContent = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false});
    if(fpDate) {
        const options = { weekday: 'short', day: 'numeric', month: 'long' };
        fpDate.textContent = now.toLocaleDateString('en-US', options);
    }
}, 1000);
