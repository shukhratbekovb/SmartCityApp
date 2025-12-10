#include <WiFi.h>
#include <HTTPClient.h>
#include <WebSocketsClient.h>

// ================= WIFI =================
const char* WIFI_SSID = "IT911";
const char* WIFI_PASSWORD = "OsamaBenLaden2011";

// ================= BACKEND =================
const char* IRRIGATION_ENDPOINT = "http://192.168.0.200:8000/api/irrigation";
const char* SOIL_ENDPOINT       = "http://192.168.0.200:8000/api/soil";

// ================= WEBSOCKET =================
WebSocketsClient webSocket;
const char* WS_HOST = "192.168.0.200";
const int   WS_PORT = 8000;
const char* WS_PATH = "/ws/";

bool autoMode = true;
bool isWater = false;

const long SOIL_INTERVAL = 5000;     // каждые 5 сек
const long PUMP_DURATION = 1000;    // 1 секунда помпа
const long AUTO_DELAY    = 30000;   // защита от частых автополивов

unsigned long lastSOILTime = 0;
unsigned long pumpStartTime = 0;
unsigned long lastAutoWaterTime = 0;

// ================= PINS =================
#define RELAY_PIN 17
#define SOIL_PIN 34

// ================= FUNCTIONS =================

void sendHTTP(const char* url, String payload) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);

    Serial.println("POST -> " + String(url));
    Serial.println("Payload: " + payload);
    Serial.println("Response: " + String(httpResponseCode));

    http.end();
  }
}

void turnOnPump() {
  if (!isWater) {
    digitalWrite(RELAY_PIN, HIGH);
    isWater = true;
    pumpStartTime = millis();
    sendIrrigation();
    Serial.println("✅ PUMP ON");
  }
}

void turnOffPump() {
  digitalWrite(RELAY_PIN, LOW);
  isWater = false;
  Serial.println("🛑 PUMP OFF");
}

void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected");
  Serial.println(WiFi.localIP());
}

int getSoil() {
  return analogRead(SOIL_PIN);
}

void sendSoil(int soil) {
  String payload = "{\"value\":" + String(soil) + "}";
  sendHTTP(SOIL_ENDPOINT, payload);
}

void sendIrrigation() {
  String payload = "{}";
  sendHTTP(IRRIGATION_ENDPOINT, payload);
}

void sendStatusWS() {
  String status = isWater ? "ON" : "OFF";
  String mode   = autoMode ? "AUTO" : "MANUAL";
  String msg = "STATUS:" + status + ":" + mode;
  webSocket.sendTXT(msg);
}

// ================= WEBSOCKET =================

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String msg = String((char*)payload);
    Serial.println("WS -> " + msg);

    // Режим
    if (msg == "WATER:MODE") {
      webSocket.sendTXT(autoMode ? "WATER:AUTO" : "WATER:MANUAL");
    }

    if (msg == "WATER:AUTO")   autoMode = true;
    if (msg == "WATER:MANUAL") autoMode = false;

    // Ручной полив (1 секунда)
    if (msg == "START") {
      turnOnPump();
    }

    // Статус
    if (msg == "get_status") sendStatusWS();
  }
}

void startWebSocket() {
  webSocket.begin(WS_HOST, WS_PORT, WS_PATH);
  webSocket.onEvent(webSocketEvent);
}

// ================= SETUP =================

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  connectToWiFi();
  startWebSocket();
}

// ================= LOOP =================

void loop() {
  webSocket.loop();
  unsigned long currentMillis = millis();

  // ===== ОТПРАВКА SOIL КАЖДЫЕ 5 СЕК =====
  if (currentMillis - lastSOILTime >= SOIL_INTERVAL) {
    lastSOILTime = currentMillis;

    int soil = getSoil();
    Serial.println("Soil: " + String(soil));
    sendSoil(soil);

    // ===== АВТО ПОЛИВ ПРИ SOIL > 3000 =====
    if (autoMode && soil > 3000 && currentMillis - lastAutoWaterTime > AUTO_DELAY) {
      lastAutoWaterTime = currentMillis;
      turnOnPump();
      sendIrrigation();
    }
  }

  // ===== АВТО ВЫКЛЮЧЕНИЕ ПОМПЫ ЧЕРЕЗ 1 СЕК =====
  if (isWater && currentMillis - pumpStartTime >= PUMP_DURATION) {
    turnOffPump();
  }
}
