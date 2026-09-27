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


const char* ssid = "Galaxy A27 5G CB9A";
const char* password = "nitin6789";

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
  static uint8_t length = 0;
  static uint8_t msgid = 0;
  static uint8_t payload[64];
  static uint8_t idx = 0;

  switch (state) {
    case 0: if (c == 0xFD) state = 1; break; // MAVLink v2 packet start
    case 1: length = c; state = 2; break;
    case 2: state = 3; break;
    case 3: state = 4; break;
    case 4: state = 5; break;
    case 5: state = 6; break;
    case 6: state = 7; break;
    case 7: msgid = c; idx = 0; state = (length > 0) ? 8 : 0; break;
    case 8:
      payload[idx++] = c;
      if (idx >= length) {
        if (msgid == 33 && length >= 28) { // GLOBAL_POSITION_INT (#33)
          int32_t lat = *(int32_t*)&payload[4];
          int32_t lon = *(int32_t*)&payload[8];
          int32_t relative_alt = *(int32_t*)&payload[16]; // AGL in mm
          uint16_t hdg = *(uint16_t*)&payload[26];        // cdeg (0..35999)

          // 1. Convert to human-readable units
          float latitude = lat / 1e7;
          float longitude = lon / 1e7;
          float altitude_m = relative_alt / 1000.0;
          float heading_deg = hdg / 100.0;

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

          // 3. Broadcast over Wi-Fi
          webSocket.broadcastTXT(jsonBuffer);

          // ================= MODIFICATION START =================
          // Print formatted telemetry to the Arduino Serial Monitor (USB)
          Serial.println("---------- TELEMETRY PACKET ----------");
          Serial.print("ID:       DRONE-ALPHA\n");
          Serial.printf("Lat/Lon:  %.7f, %.7f\n", latitude, longitude);
          Serial.printf("Alt(AGL): %.2f m\n", altitude_m);
          Serial.printf("Heading:  %.1f deg\n", heading_deg);
          Serial.print("Payload:  ");
          Serial.println(jsonBuffer);
          Serial.println("--------------------------------------\n");
          // ================== MODIFICATION END ==================
        }
        state = 0;
      }
      break;
    default: state = 0; break;
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

  Serial.println("\n--- CONNECTED ---");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP()); // <-- Copy this IP address for your HTML dashboard

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();

  while (MavSerial.available()) {
    parseMavlinkByte(MavSerial.read());
  }
}
