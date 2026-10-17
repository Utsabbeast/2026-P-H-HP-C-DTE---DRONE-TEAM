/**
 * UTM - Unified Telemetry Monitor: ESP32 Hardware Bridge
 * =======================================================
 * Connects Cube Orange+ (ArduPilot / PX4) to UTM Dashboard over Wi-Fi.
 *
 * WIRING GUIDE (Cube Orange+ TELEM1/TELEM2 to ESP32):
 * ----------------------------------------------------
 *  Cube Orange+ Pin 2 (TX)  -->  ESP32 GPIO 16 (RX2)
 *  Cube Orange+ Pin 3 (RX)  -->  ESP32 GPIO 17 (TX2)
 *  Cube Orange+ Pin 6 (GND) -->  ESP32 GND
 *  Power: 5V from BEC or USB to ESP32 VIN / 5V
 *
 * ARDUPILOT (Mission Planner) PARAMETERS:
 * ---------------------------------------
 *  SERIAL1_PROTOCOL = 2      (MAVLink2)
 *  SERIAL1_BAUD     = 57     (57600 baud)
 *  SR1_POSITION     = 5      (5 Hz GPS telemetry stream)
 */

#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// Wi-Fi Access Point / Hotspot Credentials
const char* ssid = "Galaxy A27 5G CB9A";
const char* password = "nitin6789";

// Optional: HTTP POST telemetry directly to your Render cloud server!
// When set, telemetry is pushed to Render every 1s so https://drone-375d.onrender.com works live anywhere!
// Leave empty "" if you only want local WebSocket (http://localhost:8000/dashboard/).
const char* utmServerUrl = "https://drone-375d.onrender.com/api/telemetry/";

// Hardware Serial2: RX = GPIO 16, TX = GPIO 17
HardwareSerial MavSerial(2);

// WebSocket server running on port 81
WebSocketsServer webSocket = WebSocketsServer(81);

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
    Serial.printf("[%u] Dashboard Client connected!\n", num);
  } else if (type == WStype_DISCONNECTED) {
    Serial.printf("[%u] Dashboard Client disconnected!\n", num);
  }
}

void parseMavlinkByte(uint8_t c) {
  static uint8_t state = 0;
  static uint8_t proto_ver = 2; // 1 = MAVLink v1 (0xFE), 2 = MAVLink v2 (0xFD)
  static uint8_t length = 0;
  static uint32_t msgid = 0;
  static uint8_t msgid_0 = 0;
  static uint8_t msgid_1 = 0;
  static uint8_t payload[256];
  static uint8_t idx = 0;

  switch (state) {
    case 0: // Sync byte detection
      if (c == 0xFD) { proto_ver = 2; state = 1; }      // MAVLink v2 start byte
      else if (c == 0xFE) { proto_ver = 1; state = 1; } // MAVLink v1 start byte
      break;

    case 1: // Payload length
      length = c;
      idx = 0;
      if (proto_ver == 2) {
        state = 2; // MAVLink 2 has incompatibility/compatibility flags next
      } else {
        state = 4; // MAVLink 1 jumps straight to sequence number
      }
      break;

    case 2: state = 3; break; // MAVLink 2: Incompatibility flags
    case 3: state = 4; break; // MAVLink 2: Compatibility flags
    case 4: state = 5; break; // Packet sequence number
    case 5: state = 6; break; // System ID
    case 6: state = 7; break; // Component ID

    case 7: // Message ID byte 0 (Bits 0-7)
      if (proto_ver == 2) {
        msgid_0 = c;
        state = 8;
      } else {
        // MAVLink 1 Message ID is 1 byte only
        msgid = c;
        idx = 0;
        state = (length > 0) ? 10 : 0;
      }
      break;

    case 8: // MAVLink 2: Message ID byte 1 (Bits 8-15)
      msgid_1 = c;
      state = 9;
      break;

    case 9: // MAVLink 2: Message ID byte 2 (Bits 16-23)
      msgid = (uint32_t)msgid_0 | ((uint32_t)msgid_1 << 8) | ((uint32_t)c << 16);
      idx = 0;
      state = (length > 0) ? 10 : 0;
      break;

    case 10: // Payload data bytes
      payload[idx++] = c;
      if (idx >= length) {
        state = 0; // Payload complete, ready for next packet
        if (msgid == 33 && length >= 28) { // GLOBAL_POSITION_INT (#33)
          int32_t lat = *(int32_t*)&payload[4];
          int32_t lon = *(int32_t*)&payload[8];
          int32_t relative_alt = *(int32_t*)&payload[16]; // AGL in mm
          uint16_t hdg = *(uint16_t*)&payload[26];        // cdeg (0..35999, 65535 if unknown)

          // 1. Convert to human-readable units
          float latitude = lat / 1e7;
          float longitude = lon / 1e7;
          float altitude_m = relative_alt / 1000.0;
          // ArduPilot sends 65535 (UINT16_MAX) if compass heading is unknown/uncalibrated
          float heading_deg = (hdg == 65535 || hdg > 36000) ? 0.0 : (hdg / 100.0);

          // 2. Format as JSON for Wi-Fi transmission (supports both short & full keys)
          StaticJsonDocument<256> doc;
          doc["id"] = "DRONE-ALPHA";
          doc["drone_id"] = "DRONE-ALPHA";
          doc["lat"] = latitude;
          doc["latitude"] = latitude;
          doc["lon"] = longitude;
          doc["longitude"] = longitude;
          doc["alt"] = altitude_m;
          doc["altitude"] = altitude_m;
          doc["heading"] = heading_deg;

          char jsonBuffer[256];
          serializeJson(doc, jsonBuffer);

          // 3. Broadcast over Wi-Fi WebSocket (sub-10ms latency)
          webSocket.broadcastTXT(jsonBuffer);

          // 4. (Optional) Forward via HTTP POST to cloud / server
          static unsigned long lastHttpSend = 0;
          if (strlen(utmServerUrl) > 0 && (millis() - lastHttpSend >= 1000) && WiFi.status() == WL_CONNECTED) {
            lastHttpSend = millis();
            if (strncmp(utmServerUrl, "https://", 8) == 0) {
              WiFiClientSecure secureClient;
              secureClient.setInsecure(); // Skip TLS certificate verification on ESP32
              HTTPClient http;
              if (http.begin(secureClient, utmServerUrl)) {
                http.addHeader("Content-Type", "application/json");
                http.setTimeout(1500);
                int code = http.POST(jsonBuffer);
                if (code > 0) {
                  Serial.printf("[CLOUD] Pushed to Render: HTTP %d\n", code);
                } else {
                  Serial.printf("[CLOUD] Push error: %s\n", http.errorToString(code).c_str());
                }
                http.end();
              }
            } else {
              HTTPClient http;
              if (http.begin(utmServerUrl)) {
                http.addHeader("Content-Type", "application/json");
                http.setTimeout(1200);
                int code = http.POST(jsonBuffer);
                if (code > 0) {
                  Serial.printf("[LOCAL API] Pushed: HTTP %d\n", code);
                }
                http.end();
              }
            }
          }

          // ================= PRINT TO SERIAL MONITOR (USB) =================
          Serial.println("---------- TELEMETRY PACKET ----------");
          Serial.println("ID:       DRONE-ALPHA");
          if (lat == 0 && lon == 0) {
            Serial.println("GPS:      NO SATELLITE LOCK YET (lat=0, lon=0 - test near window/outdoors)");
          } else {
            Serial.printf("Lat/Lon:  %.7f, %.7f\n", latitude, longitude);
          }
          Serial.printf("Alt(AGL): %.2f m\n", altitude_m);
          if (hdg == 65535 || hdg > 36000) {
            Serial.println("Heading:  Compass Calibrating / Waiting for Lock");
          } else {
            Serial.printf("Heading:  %.1f deg\n", heading_deg);
          }
          Serial.print("Payload:  ");
          Serial.println(jsonBuffer);
          Serial.println("--------------------------------------\n");
        }
      }
      break;

    default:
      state = 0;
      break;
  }
}

void setup() {
  Serial.begin(115200);
  MavSerial.begin(57600, SERIAL_8N1, 16, 17);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n\n========================================");
  Serial.println("  ESP32 TELEMETRY BRIDGE CONNECTED!     ");
  Serial.println("========================================");
  Serial.print("ESP32 IP Address:        ");
  Serial.println(WiFi.localIP());
  Serial.print("Dashboard WebSocket URL: ws://");
  Serial.print(WiFi.localIP());
  Serial.println(":81");
  Serial.println("========================================\n");

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();

  while (MavSerial.available()) {
    parseMavlinkByte(MavSerial.read());
  }
}
