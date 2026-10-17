// =========================================================================
// ESP32 + A7670C 4G LTE TELEMETRY BRIDGE FOR CUBE ORANGE+ (MAVLINK TO HIVEMQ)
// Dynamic Hardware-bound Drone ID (ESP.getEfuseMac) & Multi-UAV Cloud Mesh
// =========================================================================

// 1. Define the modem type BEFORE including TinyGSM
#define TINY_GSM_MODEM_SIM7600

#include <TinyGsmClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==========================================
// CELLULAR NETWORK CREDENTIALS (JIO 4G)
// ==========================================
const char apn[] = "jionet"; 
const char gprsUser[] = "";
const char gprsPass[] = "";

// ==========================================
// MQTT CLOUD SETTINGS
// ==========================================
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;

// Dynamic Identity & Topics (Populated in setup())
char drone_id[24];
char mqtt_topic_telemetry[64];
char mqtt_topic_status[64];
char mqtt_client_id[32];

// ==========================================
// HARDWARE SERIAL PORTS
// ==========================================
HardwareSerial ModemSerial(1); // A7670C (RX=18, TX=19)
HardwareSerial MavSerial(2);   // Cube Orange+ TELEM2 (RX=16, TX=17)

TinyGsm modem(ModemSerial);
TinyGsmClient espClient(modem);
PubSubClient client(espClient);

// ==========================================
float current_lat = 0, current_lon = 0, current_alt = 0, current_hdg = 0;
float current_roll = 0, current_pitch = 0;
float current_speed = 0.0;
char current_flight_mode[16] = "POSHOLD";
float current_batt_v = 0;
int current_batt_pct = 0;

unsigned long last_mqtt_publish = 0;
unsigned long last_mqtt_reconnect = 0;
unsigned long last_stream_request = 0;
unsigned long last_diagnostic_print = 0;

// === DIAGNOSTIC VARIABLES ===
int bytes_received = 0;
int valid_mavlink_packets = 0;
int total_publishes = 0;

// ==========================================
// UNIQUE DEVICE IDENTITY INITIALIZATION
// ==========================================
void init_drone_identity() {
  uint64_t chipid = ESP.getEfuseMac();
  // Formats to 12-character uppercase Hex MAC (e.g., DRONE-40573255F188)
  snprintf(drone_id, sizeof(drone_id), "DRONE-%04X%08X", (uint16_t)(chipid >> 32), (uint32_t)chipid);
  
  snprintf(mqtt_client_id, sizeof(mqtt_client_id), "ESP32-%s", drone_id);
  snprintf(mqtt_topic_telemetry, sizeof(mqtt_topic_telemetry), "utm/drones/%s/telemetry", drone_id);
  snprintf(mqtt_topic_status, sizeof(mqtt_topic_status), "utm/drones/%s/status", drone_id);

  Serial.println("\n----------------------------------------");
  Serial.print("   ASSIGNED DRONE ID : "); Serial.println(drone_id);
  Serial.print("   TELEMETRY TOPIC   : "); Serial.println(mqtt_topic_telemetry);
  Serial.print("   STATUS TOPIC      : "); Serial.println(mqtt_topic_status);
  Serial.println("----------------------------------------\n");
}

// ==========================================
// ROBUST JIO APN CONNECTION
// ==========================================
void connect_gprs() {
  Serial.print("5. Connecting to APN: ");
  Serial.println(apn);

  modem.sendAT(GF("+CGDCONT=1,\"IP\",\"jionet\""));
  modem.waitResponse();
  modem.sendAT(GF("+CGAUTH=1,0"));
  modem.waitResponse();
  modem.sendAT(GF("+CGATT=1"));
  modem.waitResponse(5000L);
  modem.sendAT(GF("+CGACT=1,1"));
  modem.waitResponse(10000L);

  if (modem.isGprsConnected()) {
    Serial.println("   [OK] 4G INTERNET CONNECTED SUCCESSFULLY!");
  } else {
    Serial.println("   [WARNING] Manual activation timed out. Attempting TinyGSM fallback...");
    if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
      Serial.println("   [ERROR] APN Connection Failed.");
    } else {
      Serial.println("   [OK] 4G INTERNET CONNECTED via TinyGSM!");
    }
  }
}

void setup_modem() {
  Serial.println("\n--- STARTING A7670C LTE MODULE (JIO CONFIG) ---");
  ModemSerial.begin(115200, SERIAL_8N1, 18, 19);
  delay(3000); 

  Serial.println("1. Initializing AT Commands...");
  if (!modem.init()) {
    Serial.println("   [ERROR] Cannot communicate with A7670C.");
    return;
  }
  Serial.println("   [OK] Modem responding.");

  Serial.println("2. Checking SIM Card Status...");
  if (modem.getSimStatus() != SIM_READY) return;
  Serial.println("   [OK] SIM Card is READY.");

  Serial.println("   [INFO] Forcing 4G LTE-Only Mode...");
  modem.sendAT(GF("+CNMP=38")); 
  modem.waitResponse();

  Serial.println("3. Waiting for Jio Cell Tower Network...");
  if (!modem.waitForNetwork(60000L)) return;
  Serial.println("   [OK] Registered on Cellular Network.");
  delay(3000); 

  Serial.println("4. Checking Signal Quality...");
  Serial.print("   [INFO] Signal Quality (CSQ 0-31): ");
  Serial.println(modem.getSignalQuality());

  connect_gprs();
}

void reconnect() {
  if (millis() - last_mqtt_reconnect > 5000) {
    last_mqtt_reconnect = millis();
    Serial.print("Attempting MQTT connection via 4G as [");
    Serial.print(mqtt_client_id);
    Serial.print("]... ");

    // Last Will and Testament: Informs broker if connection drops ungracefully
    const char* willTopic = mqtt_topic_status;
    int willQos = 1;
    bool willRetain = true;
    const char* willMessage = "{\"status\":\"offline\"}";

    if (client.connect(mqtt_client_id, NULL, NULL, willTopic, willQos, willRetain, willMessage)) {
      Serial.println("connected to HiveMQ!");
      // Publish online status upon successful connection (retained)
      client.publish(mqtt_topic_status, "{\"status\":\"online\"}", true);
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
    }
  }
}

// =========================================================================
// MAVLINK PROTOCOL ENGINE (STREAM REQUESTS & DUAL PARSER)
// =========================================================================

// Sends Companion Heartbeat + Request Data Streams to Cube Orange+
void send_mavlink_request_streams() {
  // 1. MAVLink v1 Heartbeat (Msg #0, Type 18 = ONBOARD_CONTROLLER)
  static uint8_t hb_msg[] = {
    0xFE, 0x09, 0x01, 0xFF, 0xBE, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x12, 0x00, 0x00, 0x04, 0x03,
    0xEE, 0x7E
  };
  MavSerial.write(hb_msg, sizeof(hb_msg));

  // 2. MAVLink v1 REQUEST_DATA_STREAM (Msg #66, Stream ALL @ 4Hz)
  static uint8_t req_msg[] = {
    0xFE, 0x06, 0x01, 0xFF, 0xBE, 0x42,
    0x04, 0x00, 0x01, 0x01, 0x00, 0x01,
    0x4A, 0x6E
  };
  MavSerial.write(req_msg, sizeof(req_msg));
}

// Decodes MAVLink v1 (0xFE) and MAVLink v2 (0xFD) packets on the fly
void parseMavlinkByte(uint8_t c) {
  static uint8_t state = 0;
  static uint8_t proto_ver = 2; 
  static uint8_t length = 0;
  static uint32_t msgid = 0;
  static uint8_t msgid_0 = 0, msgid_1 = 0;
  static uint8_t payload[256];
  static uint8_t idx = 0;

  switch (state) {
    case 0: 
      if (c == 0xFD) { proto_ver = 2; state = 1; }      
      else if (c == 0xFE) { proto_ver = 1; state = 1; } 
      break;
    case 1: 
      length = c; idx = 0;
      state = (proto_ver == 2) ? 2 : 4; 
      break;
    case 2: state = 3; break; 
    case 3: state = 4; break; 
    case 4: state = 5; break; 
    case 5: state = 6; break; 
    case 6: state = 7; break; 
    case 7: 
      if (proto_ver == 2) { msgid_0 = c; state = 8; } 
      else { msgid = c; idx = 0; state = (length > 0) ? 10 : 0; }
      break;
    case 8: msgid_1 = c; state = 9; break;
    case 9: 
      msgid = (uint32_t)msgid_0 | ((uint32_t)msgid_1 << 8) | ((uint32_t)c << 16);
      idx = 0;
      state = (length > 0) ? 10 : 0;
      break;
    case 10: 
      payload[idx++] = c;
      if (idx >= length) {
        state = 0; 
        valid_mavlink_packets++; // Track successful packet decodes
        
        // MAVLINK MSG #33: GLOBAL_POSITION_INT
        if (msgid == 33 && length >= 28) { 
          current_lat = *(int32_t*)&payload[4] / 1e7;
          current_lon = *(int32_t*)&payload[8] / 1e7;
          current_alt = *(int32_t*)&payload[16] / 1000.0; 
          int16_t vx = *(int16_t*)&payload[20];
          int16_t vy = *(int16_t*)&payload[22];
          current_speed = sqrt((float)vx * vx + (float)vy * vy) / 100.0; // Ground speed in m/s
          uint16_t hdg = *(uint16_t*)&payload[26];        
          current_hdg = (hdg == 65535 || hdg > 36000) ? 0.0 : (hdg / 100.0);
        }
        // MAVLINK MSG #0: HEARTBEAT (Flight Mode)
        else if (msgid == 0 && length >= 9) {
          uint32_t custom_mode = *(uint32_t*)&payload[0];
          switch(custom_mode) {
            case 0:  strncpy(current_flight_mode, "STABILIZE", sizeof(current_flight_mode)); break;
            case 2:  strncpy(current_flight_mode, "ALT_HOLD", sizeof(current_flight_mode)); break;
            case 3:  strncpy(current_flight_mode, "AUTO", sizeof(current_flight_mode)); break;
            case 4:  strncpy(current_flight_mode, "GUIDED", sizeof(current_flight_mode)); break;
            case 5:  strncpy(current_flight_mode, "LOITER", sizeof(current_flight_mode)); break;
            case 6:  strncpy(current_flight_mode, "RTL", sizeof(current_flight_mode)); break;
            case 9:  strncpy(current_flight_mode, "LAND", sizeof(current_flight_mode)); break;
            case 16: strncpy(current_flight_mode, "POSHOLD", sizeof(current_flight_mode)); break;
            case 17: strncpy(current_flight_mode, "BRAKE", sizeof(current_flight_mode)); break;
            default: strncpy(current_flight_mode, "POSHOLD", sizeof(current_flight_mode)); break;
          }
        }
        // MAVLINK MSG #30: ATTITUDE
        else if (msgid == 30 && length >= 28) {
          current_roll = *(float*)&payload[4] * (180.0 / PI); 
          current_pitch = *(float*)&payload[8] * (180.0 / PI);
        }
        // MAVLINK MSG #1: SYS_STATUS
        else if (msgid == 1 && length >= 31) {
          current_batt_v = *(uint16_t*)&payload[14] / 1000.0; 
          current_batt_pct = *(int8_t*)&payload[30]; 
        }
      }
      break;
    default: state = 0; break;
  }
}

// ==========================================
// TELEMETRY PUBLISH HANDLER (INDEPENDENT)
// ==========================================
void publish_telemetry() {
  if (!client.connected()) return;

  StaticJsonDocument<512> doc;
  doc["drone_id"] = drone_id;
  doc["timestamp"] = millis();
  doc["lat"] = current_lat;
  doc["lon"] = current_lon;
  doc["alt"] = current_alt;
  doc["hdg"] = current_hdg;
  doc["spd"] = current_speed;
  doc["flight_mode"] = current_flight_mode;
  doc["roll"] = current_roll;
  doc["pitch"] = current_pitch;
  doc["batt_v"] = current_batt_v;
  doc["batt_pct"] = current_batt_pct;

  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);

  total_publishes++;
  Serial.print("[MQTT PUB #");
  Serial.print(total_publishes);
  Serial.print("] ");
  Serial.println(jsonBuffer); 

  bool ok = client.publish(mqtt_topic_telemetry, jsonBuffer);
  if (!ok) {
    Serial.println("   [MQTT ERROR] Failed to publish telemetry! Check buffer size or connection.");
  }
}

// ==========================================
// MAIN SETUP
// ==========================================
void setup() {
  Serial.begin(115200);
  MavSerial.begin(57600, SERIAL_8N1, 16, 17); // Cube Orange+ TELEM2 (RX=16, TX=17)

  Serial.println("\n\n========================================");
  Serial.println("  ESP32 + A7670C MULTI-UAV BRIDGE BOOTING ");
  Serial.println("========================================\n");

  // Derive unique MAC identity before network connections
  init_drone_identity();

  setup_modem();
  client.setServer(mqtt_server, mqtt_port);
  client.setKeepAlive(60); 
  client.setBufferSize(512); // Increase PubSubClient buffer from 128 to 512 bytes for full telemetry JSON
}

// ==========================================
// MAIN LOOP
// ==========================================
void loop() {
  // 1. Maintain MQTT Broker Connection
  if (!client.connected()) {
    reconnect();
  } else {
    client.loop();
  }

  // 2. Ingest and parse MAVLink telemetry from Cube Orange+
  while (MavSerial.available()) {
    bytes_received++;
    parseMavlinkByte(MavSerial.read());
  }

  // 3. Command Cube Orange to output telemetry streams every 2 seconds
  if (millis() - last_stream_request > 2000) {
    last_stream_request = millis();
    send_mavlink_request_streams();
  }

  // 4. Reliable Telemetry Publish every 2 seconds (Anti-flicker rate)
  if (millis() - last_mqtt_publish > 2000) {
    last_mqtt_publish = millis();
    publish_telemetry();
  }

  // 5. Periodic Diagnostics to USB Serial (every 3 seconds)
  if (millis() - last_diagnostic_print > 3000) {
    last_diagnostic_print = millis();
    
    Serial.println("\n--- [ESP32 HEALTH MONITOR] ---");
    Serial.print("Cellular Network : "); Serial.println(modem.isGprsConnected() ? "CONNECTED (4G)" : "DISCONNECTED");
    Serial.print("HiveMQ MQTT      : "); Serial.println(client.connected() ? "CONNECTED" : "DISCONNECTED");
    Serial.print("Cube MAVLink Rx  : "); Serial.print(bytes_received); Serial.print(" bytes received (");
    Serial.print(valid_mavlink_packets); Serial.println(" packets decoded)");
    Serial.print("Current GPS Pos  : "); Serial.print(current_lat, 6); Serial.print(", "); Serial.println(current_lon, 6);
    Serial.print("Battery & Att    : "); Serial.print(current_batt_v); Serial.print("V (");
    Serial.print(current_batt_pct); Serial.print("%) | Roll: "); Serial.print(current_roll);
    Serial.print(" | Pitch: "); Serial.println(current_pitch);

    if (bytes_received == 0) {
      Serial.println("[NOTE] 0 bytes from Cube Orange yet. Verify:");
      Serial.println("  1. Cube Orange TELEM2 TX -> ESP32 GPIO 16 (RX)");
      Serial.println("  2. Cube Orange TELEM2 RX -> ESP32 GPIO 17 (TX)");
      Serial.println("  3. Common GND connected between Cube and ESP32");
      Serial.println("  4. Cube Orange SERIAL2_BAUD = 57 (57600)");
    }
    Serial.println("-------------------------------\n");

    bytes_received = 0;
    valid_mavlink_packets = 0;
  }
}