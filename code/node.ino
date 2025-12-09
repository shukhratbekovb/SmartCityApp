#include <ESP8266WiFi.h>
#include <WebSocketsClient.h>

#define RED_PIN    D2
#define YELLOW_PIN D3
#define GREEN_PIN  D4

const char* ssid = "IT911";
const char* password = "OsamaBenLaden2011";

const char* ws_host = "192.168.1.200";
const int ws_port = 8000;
const char* ws_path = "/ws/traffic";

WebSocketsClient webSocket;

bool priority = false;

unsigned long lastSwitch = 0;
int state = 0; // 0=R, 1=G, 2=Y

void sendStatus(char c) {
  String msg = "STATUS:";
  msg += c;
  webSocket.sendTXT(msg);
}

void setLight(bool r, bool y, bool g, char s) {
  digitalWrite(RED_PIN, r);
  digitalWrite(YELLOW_PIN, y);
  digitalWrite(GREEN_PIN, g);
  sendStatus(s);
}

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String msg = (char*)payload;

    if (msg == "PRIORITY:ON")  priority = true;
    if (msg == "PRIORITY:OFF") priority = false;
  }
}

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);

  setLight(1, 0, 0, 'R'); // старт с красного

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(300);

  webSocket.begin(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(3000);
}

void loop() {
  webSocket.loop();

  unsigned long now = millis();

  int greenTime = priority ? 6000 : 3000;  // ✅ 6 или 3 сек
  int redTime   = priority ? 3000 : 6000;  
  int yellowTime = 1500;

  int currentDelay = 0;

  if (state == 0) currentDelay = redTime;
  if (state == 1) currentDelay = greenTime;
  if (state == 2) currentDelay = yellowTime;

  if (now - lastSwitch >= currentDelay) {
    lastSwitch = now;
    state++;

    if (state > 2) state = 0;

    if (state == 0) setLight(1, 0, 0, 'R');
    if (state == 1) setLight(0, 0, 1, 'G');
    if (state == 2) setLight(0, 1, 0, 'Y');
  }
}
