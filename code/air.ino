#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT11.h>
#include <WebSocketsClient.h>

// ================= WIFI =================
const char* WIFI_SSID = "IT911";
const char* WIFI_PASSWORD = "OsamaBenLaden2011";

// ================= BACKEND ENDPOINTS =================
const char* TEMP_ENDPOINT = "http://95.182.118.204/api/temperature";
const char* HUM_ENDPOINT  = "http://95.182.118.204/api/humidity";
const char* GAS_ENDPOINT  = "http://95.182.118.204/api/gas";
const char* RAIN_ENDPOINT = "http://95.182.118.204/api/rain";

// Digital Pins 
#define DHTPIN 17
#define MQ2_LED_PIN 16
#define BUZZER_PIN 27
#define PHOTO_PIN  14     
#define LIGHT_LED  12 

// Analog Pins
#define RAIN_PIN 34
#define MQ2_ANALOG_PIN 35

DHT11 dht11(DHTPIN);
WebSocketsClient webSocket;

bool autoMode = true;
bool isLight = false;

// ================= TIMERS =================
unsigned long lastDHTTime = 0;
unsigned long lastGasTime = 0;
unsigned long lastRainTime = 0;
unsigned long lastLightTime = 0;

const long DHT_INTERVAL = 5000;
const long GAS_INTERVAL = 3000;
const long RAIN_INTERVAL = 4000;
const long LIGHT_INTERVAL = 2000;

void turnOnLight() {
    digitalWrite(LIGHT_LED, HIGH);
    isLight = true;
}

void turnOffLight() {
    digitalWrite(LIGHT_LED, LOW);
    isLight = false;
}

int readLightLevel() {
    return digitalRead(PHOTO_PIN);
}

void proccessLight() {
    int lightLevel = readLightLevel();
    Serial.println("Light");
    if (autoMode) {
      Serial.println(lightLevel);
        if (lightLevel == HIGH) {
            turnOnLight();
        } else {
            turnOffLight();
        }
    }

    // sendLightLevel(lightLevel);
    // sendLightStatus();
    // sendLightMode();
}

void sendLightStatus() {
    String payload = "{\"type\":\"light_status\", \"value\":" + String(isLight ? 1 : 0) + "}";
    webSocket.sendTXT(payload);
}
void sendLightMode() {
    String payload = "{\"type\":\"light_mode\", \"value\":" + String(autoMode ? 1 : 0) + "}";
    webSocket.sendTXT(payload);
}
void sendLightLevel(int lightLevel) {
    String payload = "{\"type\":\"light_level\",\"value\":" + String(lightLevel) + "}";
    webSocket.sendTXT(payload);
}

int readHumidity() {
  return dht11.readHumidity();
}

int readTemperature() {
  return dht11.readTemperature();
}

int detectGas() {
  return analogRead(RAIN_PIN);
}

int detectRain() {
  return analogRead(MQ2_ANALOG_PIN);
}

void startBuzzer() {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000); 
    digitalWrite(BUZZER_PIN, LOW);
}

void runGasWarningSystem(int gasValue) {
    if (gasValue > 400) {
        digitalWrite(MQ2_LED_PIN, HIGH);
        startBuzzer();
    } else {
        digitalWrite(MQ2_LED_PIN, LOW);
    }
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

// ================= HTTP SEND =================
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

// ================= SEND FUNCTIONS =================
void sendTemperature() {
  float temp = readTemperature();
  if (isnan(temp)) return;

  String payload = "{\"value\":" + String(temp) + "}";
  sendHTTP(TEMP_ENDPOINT, payload);
}

void sendHumidity() {
  float hum = readHumidity();
  if (isnan(hum)) return;

  String payload = "{\"value\":" + String(hum) + "}";
  sendHTTP(HUM_ENDPOINT, payload);
}

void sendGas(int gas) {
  String payload = "{\"value\":" + String(gas) + "}";
  sendHTTP(GAS_ENDPOINT, payload);
}

void sendRain() {
  int rain = detectRain();
  String payload = "{\"value\":" + String(rain) + "}";
  sendHTTP(RAIN_ENDPOINT, payload);
}
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String msg = String((char*)payload);
    Serial.println("WS -> " + msg);

    // ======== ЗАПРОС РЕЖИМА =========
    if (msg == "LIGHT:MODE") {
      if (autoMode) {
        webSocket.sendTXT("LIGHT:AUTO");
      } else {
        webSocket.sendTXT("LIGHT:MANUAL");
      }
    }

    // ======== УСТАНОВКА РЕЖИМА =========
    if (msg == "LIGHT:AUTO") {
      autoMode = true;
      webSocket.sendTXT("LIGHT:AUTO");
    }

    if (msg == "LIGHT:MANUAL") {
      autoMode = false;
      webSocket.sendTXT("LIGHT:MANUAL");
    }
    if (msg=="LIGHT:INFO"){
      if (isLight) {
        webSocket.sendTXT("LIGHT:ON");
      }
      else {
        webSocket.sendTXT("LIGHT:OFF");
      }
    }
    // ======== УПРАВЛЕНИЕ СВЕТОМ (ТОЛЬКО В MANUAL) =========
    if (!autoMode) {
      if (msg == "LIGHT:ON") {
        turnOnLight();
      }

      if (msg == "LIGHT:OFF") {
        turnOffLight();
      }
    }
  }
}

void startWebSocket() {
  webSocket.begin("95.182.118.204", 8000, "/ws/");
  webSocket.onEvent(webSocketEvent);
}

void setup() {
    Serial.begin(9600);

    pinMode(MQ2_LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
pinMode(PHOTO_PIN, INPUT);
  pinMode(LIGHT_LED, OUTPUT);
    connectToWiFi();
    startWebSocket();
    
}

void loop() {
  
    webSocket.loop();
    unsigned long currentMillis = millis();

    if (currentMillis - lastDHTTime >= DHT_INTERVAL) {
        lastDHTTime = currentMillis;
        sendTemperature();
        sendHumidity();
    }

    if (currentMillis - lastGasTime >= GAS_INTERVAL) {
        lastGasTime = currentMillis;
        int gas = detectGas();
        runGasWarningSystem(gas);
        sendGas(gas);
    }

    if (currentMillis - lastRainTime >= RAIN_INTERVAL) {
        lastRainTime = currentMillis;
        sendRain();
    }
    if (currentMillis - lastLightTime >= LIGHT_INTERVAL) {
        lastLightTime = currentMillis;
        proccessLight();
    }
}