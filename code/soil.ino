#include <WiFi.h>
#include <HTTPClient.h>
#include <WebSocketsClient.h>

// ================= WIFI =================
const char* WIFI_SSID = "IT911";
const char* WIFI_PASSWORD = "OsamaBenLaden2011";

// ================= BACKEND =================
const char* IRRIGATION_ENDPOINT = "http://95.182.118.204:8000/api/irrigation";
const char* SOIL_ENDPOINT       = "http://95.182.118.204:8000/api/soil";

// ================= WEBSOCKET =================
WebSocketsClient webSocket;
const char* WS_HOST = "95.182.118.204";
const int   WS_PORT = 8000;
const char* WS_PATH = "/ws/water";

// ================= PINS =================
#define RELAY_PIN 17
#define ECHO_PIN 16
#define TRIG_PIN 27
#define SOIL_PIN 34

// ================= CONSTANTS =================
#define CUP_HEIGHT_CM 6.0
const long SOIL_INTERVAL = 5000;
const long ULTRASONIC_INTERVAL = 3000;

// ================= GLOBALS =================
unsigned long lastSOILTime = 0;
unsigned long lastUltrasonicTime = 0;

bool waterState = false;
bool autoMode = false;

int soilValue = 0;
int waterPercent = 0;

// ================= WIFI =================
void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected");
}

// ================= HTTP SEND =================
void sendHTTP(const char* url, String payload) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    int code = http.POST(payload);

    Serial.println("POST -> " + String(url));
    Serial.println("Payload: " + payload);
    Serial.println("Response: " + String(code));

    http.end();
  }
}

// ================= WATER PUMP =================
void setWaterPump(bool state) {
  if (state) {
    waterState = true;
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("💧 Pump ON");

    sendHTTP(IRRIGATION_ENDPOINT, "{}");

    delay(1000);  // ✅ 1 СЕКУНДА

    waterState = false;
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println("🛑 Pump OFF");
  }
  else {
    waterState = false;
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println("🛑 Pump OFF");
  }
}

// ================= SOIL SENSOR =================
void readSoil() {
  if (millis() - lastSOILTime >= SOIL_INTERVAL) {
    lastSOILTime = millis();

    soilValue = analogRead(SOIL_PIN);
    Serial.println("🌱 Soil: " + String(soilValue));

    // ✅ отправка soil
    String payload = "{\"value\":" + String(soilValue) + "}";
    sendHTTP(SOIL_ENDPOINT, payload);

    // ✅ AutoMode
    if (autoMode) {
      if (soilValue > 3000) setWaterPump(true);
      else setWaterPump(false);
    }
  }
}

// ================= ULTRASONIC =================
float readUltrasonicCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;
  return duration * 0.034 / 2;
}

void readWaterLevel() {
  if (millis() - lastUltrasonicTime >= ULTRASONIC_INTERVAL) {
    lastUltrasonicTime = millis();

    float distance = readUltrasonicCM();
    if (distance == -1) return;

    float level = CUP_HEIGHT_CM - distance;
    if (level < 0) level = 0;
    if (level > CUP_HEIGHT_CM) level = CUP_HEIGHT_CM;

    waterPercent = (level / CUP_HEIGHT_CM) * 100;

    Serial.println("🧪 Water: " + String(waterPercent) + "%");
  }
}

// ================= SEND STATUS WS =================
void sendStatusWS() {
  String json = "{";
  json += "\"soil\":" + String(soilValue) + ",";
  json += "\"water_percent\":" + String(waterPercent) + ",";
  json += "\"pump\":" + String(waterState ? 1 : 0) + ",";
  json += "\"auto\":" + String(autoMode ? 1 : 0);
  json += "}";

  webSocket.sendTXT(json);
}

// ================= WEBSOCKET =================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String msg = String((char*)payload);
    Serial.println("WS -> " + msg);

    if (msg == "water_on") {
      autoMode = false;
      setWaterPump(true);
    }

    if (msg == "water_off") {
      autoMode = false;
      setWaterPump(false);
    }

    if (msg == "auto_on") autoMode = true;
    if (msg == "auto_off") {
      autoMode = false;
      setWaterPump(false);
    }

    if (msg == "get_status") sendStatusWS();
  }
}

// ================= START WS =================
void startWebSocket() {
  webSocket.begin(WS_HOST, WS_PORT, WS_PATH);
  webSocket.onEvent(webSocketEvent);
}

// ================= SETUP =================
void setup() {
  Serial.begin(9600);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  setWaterPump(false);
  connectToWiFi();
  startWebSocket();
}

// ================= LOOP =================
void loop() {
  webSocket.loop();
  readSoil();
  readWaterLevel();
}
