# UTM — Unified Telemetry Monitor

**UTM (Unified Telemetry Monitor)** is a clean, professional drone location tracking web application and backend system. It displays real-time telemetry and geographic position on an interactive Leaflet/OpenStreetMap tactical map with heading orientation, live connection heartbeat monitoring, breadcrumb movement trails, and readiness for future Cube Orange+ / ESP32 Wi-Fi hardware integration.

This version adds **Phone GPS Test Mode**, allowing an Android smartphone to temporarily act as the drone's live GPS telemetry source over a local Wi-Fi hotspot without physical flight controller hardware.

---

## 1. System Architectures

### A. Phone GPS Test Architecture (Current Testing Mode)

```
       Android Phone
             │
             │ High-Accuracy GPS (navigator.geolocation.watchPosition)
             │ Wi-Fi Mobile Hotspot
             ▼
   Laptop running Django (0.0.0.0:8000)
             │
             ▼ POST /api/phone-location/
       UTM Backend (SQLite)
             │
             ▼ Polling / REST API
       UTM Dashboard (/dashboard/)
             │
             ▼ Leaflet.js + OpenStreetMap
       📱 Phone Location Marker & Movement Trail
```

The laptop connects to the Android phone's mobile hotspot. The phone opens the dedicated mobile tracking page (`/mobile/`), requests browser GPS permissions, and streams location updates to the Django backend immediately upon every position change.

---

### B. Future Drone Hardware Architecture (Production Architecture)

```
┌─────────────────────────────────┐
│   Cube Orange+ Flight Controller│
│   (Running ArduPilot / PX4)     │
└────────────────┬────────────────┘
                 │ MAVLink Telemetry (UART)
                 ▼
       ┌──────────────────┐
       │   TELEM Port 1/2 │
       └─────────┬────────┘
                 │ Serial (RX/TX, GND, 5V)
                 ▼
       ┌──────────────────┐
       │   ESP32 Module   │ (Wi-Fi Microcontroller)
       └─────────┬────────┘
                 │ HTTP POST JSON over Wi-Fi
                 ▼
┌─────────────────────────────────┐
│     Django Backend (UTM)        │
│   - POST /api/telemetry/        │
│   - SQLite Persistence          │
│   - Heartbeat & Health Check    │
└────────────────┬────────────────┘
                 │ Polling / REST API (1 Hz)
                 ▼
┌─────────────────────────────────┐
│     UTM Web Dashboard           │
│   - Interactive Leaflet Map     │
│   - Heading Rotating Drone Icon │
│   - Live Flight Metrics         │
│   - Breadcrumb Flight Path      │
└─────────────────────────────────┘
```

> **Design Note:** The phone test endpoint (`/api/phone-location/`) and future drone endpoint (`/api/telemetry/`) are kept **logically separate**. Test phone data (`source = "phone_test"`) is isolated in its own `PhoneTelemetry` model, preventing test runs from mixing with real drone flight history.

---

## 2. Phone GPS Test Mode — Hotspot Testing Instructions

Follow this exact step-by-step workflow to test with an Android phone:

### Step 1
Turn on the Android phone's **Mobile Hotspot**.

### Step 2
Connect your laptop's Wi-Fi to the Android phone's hotspot.

### Step 3
Find your laptop's local IP address on the hotspot network:
* **macOS:** Run `ipconfig getifaddr en0` (or `ifconfig | grep "inet "`)
* **Linux:** Run `hostname -I` (or `ip addr show`)
* **Windows:** Run `ipconfig` and look for the IPv4 Address under the active Wi-Fi adapter.
*(Example IP: `192.168.43.100` — do not hardcode, use your laptop's actual IP).*

### Step 4
Start the Django server bound to all interfaces:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 5
On the Android phone's browser, open:
```text
http://<LAPTOP-IP>:8000/mobile/
```
*(Example: `http://192.168.43.100:8000/mobile/`)*

### Step 6
Press **Start GPS Tracking**.

### Step 7
Allow location permission when prompted by the browser.

### Step 8
Walk or move with the phone. The phone screen will immediately display:
* 🟢 GPS Tracking Active
* Live Latitude, Longitude, Altitude, Heading, Speed, and Accuracy
* Transmitted packet count and delivery confirmations

### Step 9
Open the UTM dashboard on the laptop:
```text
http://<LAPTOP-IP>:8000/dashboard/
```
*(or `http://localhost:8000/dashboard/`)*

### Step 10
Observe the real-time tracking:
* The dedicated **Smartphone SVG marker** moves on the Leaflet map.
* The emerald **GPS movement trail** is drawn behind the phone.
* All 7 telemetry cards update live without page reload.
* Connection status reports **🟢 Phone Connected** (`Last update: X seconds ago`).
* Click **Clear Trail** to reset the visual polyline at any time (historical database records are preserved).
* Click **Center Phone** to snap the map view directly onto the phone's coordinates.

---

## 3. Browser Security & HTTPS for Android Chrome

Modern Android Chrome requires a **Secure Context** (HTTPS) to allow the browser Geolocation API (`navigator.geolocation`) on non-localhost IP addresses (`192.168.x.x`).

If Android Chrome blocks location permissions on plain HTTP, use the built-in development HTTPS runner:

```bash
python manage.py run_https --port 8443
```

1. **Auto-Certificate Generation:** The command automatically generates self-signed certificates in `ssl/cert.pem` and `ssl/key.pem` using `openssl`.
2. **Open on Laptop:**
   ```text
   https://localhost:8443/dashboard/
   ```
3. **Open on Android Phone:**
   ```text
   https://<LAPTOP-IP>:8443/mobile/
   ```
4. **Android Chrome Notice:** Because a self-signed certificate is used, Chrome will display *"Your connection is not private"*. Tap **Advanced** &rarr; **Proceed to \<LAPTOP-IP\> (unsafe)**.
5. Android Chrome will now grant full high-accuracy GPS hardware permissions!

---

## 4. Phone GPS API Specification

### Endpoint: Telemetry Ingest

* **URL:** `POST /api/phone-location/`
* **Content-Type:** `application/json`

#### Expected JSON Payload

```json
{
    "device_id": "phone_test_01",
    "latitude": 30.9010,
    "longitude": 75.8573,
    "altitude": 125.4,
    "heading": 142,
    "accuracy": 8.5,
    "speed": 4.2,
    "timestamp": "2026-09-26T12:45:32Z",
    "source": "phone_test"
}
```

#### Field Details

| Field | Type | Description |
|---|---|---|
| `device_id` | String | Identifier of testing phone (e.g. `"phone_test_01"`) |
| `latitude` | Float | Decimal degrees (`-90.0` to `90.0`) |
| `longitude` | Float | Decimal degrees (`-180.0` to `180.0`) |
| `altitude` | Float / Null | Altitude in meters above sea level (`null` if unavailable) |
| `heading` | Float / Null | Degrees (`0.0` to `360.0`, `null` if unavailable) |
| `accuracy` | Float / Null | Horizontal GPS accuracy radius in meters (`null` if unavailable) |
| `speed` | Float / Null | Velocity in meters/second (`null` if unavailable) |
| `timestamp` | String | ISO-8601 UTC timestamp from device clock |
| `source` | String | Telemetry origin tag (`"phone_test"`) |

*Note: If the mobile browser sensor does not provide altitude, heading, or speed, it sends `null` instead of inventing dummy values. The dashboard displays `N/A` for missing metrics.*

#### Success Response (HTTP 201 Created)

```json
{
    "status": "success",
    "id": 1,
    "device_id": "phone_test_01"
}
```

---

### Endpoint: Latest Phone Location

* **URL:** `GET /api/phone-location/latest/?device_id=phone_test_01`
* **Response:** Returns the most recent phone GPS packet, freshness age, and connectivity status (`🟢 Phone Connected` / `🔴 Phone Disconnected`).

---

### Endpoint: Phone Movement Trail History

* **URL:** `GET /api/phone-location/history/?device_id=phone_test_01&limit=100`
* **Response:** Chronological coordinate list used to draw the Leaflet polyline breadcrumb trail.

---

## 5. Main Dashboard Features

* **🟢 TEST MODE — PHONE GPS:** Prominent mode indicator and badge.
* **Mode Switcher:** Seamlessly toggle between:
  * **📱 Phone GPS Test Mode** (default testing mode)
  * **🚁 Drone (ESP32 / Simulation)** (preserves all drone features)
* **Dedicated Phone SVG Marker:** A smartphone icon with illuminated radar screen, top heading notch, and dynamic rotation aligned with user direction. Visually distinct from the future quadcopter drone marker.
* **GPS Movement Trail:** Live polyline that extends as the phone moves.
* **Clear Trail Button:** Removes the displayed trail from the map and starts a fresh path from the current position without deleting historical records from SQLite.
* **Center Phone Button:** Instantly centers the Leaflet tactical map onto the phone's current GPS location.
* **7 Live Telemetry Cards:**
  1. Latitude (Live coordinates)
  2. Longitude (Live coordinates)
  3. Altitude (Live meters MSL or `N/A`)
  4. Heading (Live degrees with mini compass needle or `N/A`)
  5. Speed (Live m/s and km/h or `N/A`)
  6. Accuracy (Live precision in meters or `N/A`)
  7. Last Update (Live time string and relative age `"X seconds ago"`)
* **Connection Status:** Evaluates telemetry freshness against `PHONE_TIMEOUT_SECONDS = 10`.

---

## 6. Installation & Quickstart

### A. Clone and Activate Virtualenv

```bash
cd /path/to/utm
source venv/bin/activate  # macOS / Linux
# or .\venv\Scripts\Activate.ps1 on Windows
```

### B. Install Dependencies

```bash
pip install -r requirements.txt
```

### C. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### D. Run the Server

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 7. Running Tests

Run the full test suite (20 automated unit tests covering phone models, serializers, APIs, simulation engine, and views):

```bash
python manage.py test telemetry
```

Expected output:
```text
Ran 20 tests in 0.026s
OK
```

---

## 8. Summary of URL Endpoints

| Route | Method | Description |
|---|---|---|
| `/dashboard/` | `GET` | Primary UTM tactical monitoring dashboard |
| `/mobile/` | `GET` | Mobile-first Phone GPS streaming portal for Android |
| `/api/phone-location/` | `POST` | Ingests real phone GPS coordinates |
| `/api/phone-location/latest/` | `GET` | Returns latest phone fix & connection state |
| `/api/phone-location/history/` | `GET` | Returns phone movement trail coordinates |
| `/api/telemetry/` | `POST` | Future ESP32 / Cube Orange+ hardware ingest |
| `/api/telemetry/latest/` | `GET` | Returns latest drone telemetry packet |
| `/api/telemetry/history/` | `GET` | Returns drone flight path breadcrumbs |
| `/api/telemetry/status/` | `GET` | Hardware connection & simulation status |
| `/api/simulation/toggle/` | `POST` | Toggles drone simulation mode |
| `/api/simulation/reset/` | `POST` | Generates randomized flight route |
| `/admin/` | `GET` | Django Administration panel |
