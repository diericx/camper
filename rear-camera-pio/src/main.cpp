#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <cameraServo.h>
#include <secrets.h>

unsigned long heartbeatLastSent = 0;
const long HEARTBEAT_INTERVAL = 5000; // 5 seconds in milliseconds
bool redraw = false;

CameraServo cameraServo(9);

AsyncWebServer server(8080);

Adafruit_SSD1306 display(128, 64, &Wire, -1);

class MoveHandler
{
public:
  static void handleRequest(AsyncWebServerRequest *request)
  {
    if (request->hasParam("who", true))
    {
      String pos = request->getParam("pos", true)->value();
      Serial.println(pos);
    }
    request->send(200, "text/plain", "OK");
  }
};

void draw()
{
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.drawRoundRect(10, 10, 10, 10, 2, WHITE);
  // display.fillRoundRect(22, 22, 6, 6, 2, WHITE);
  display.setCursor(25, 11);
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.print("Pos: ");
  display.println(cameraServo.getCurrentPosition());
  display.display();
}

void setup()
{
  Serial.begin(115200);

  draw();

  WiFi.mode(WIFI_STA);
  WiFi.begin(SECRET_SSID, SECRET_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED)
  {
    Serial.printf("WiFi Failed!\n");
    ESP.restart();
    return;
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP()); // Print the assigned IP address
  Serial.print("Gateway IP address: ");
  Serial.println(WiFi.gatewayIP());

  server.on("/api/v1/move", HTTP_POST,
            [](AsyncWebServerRequest *request)
            {
              if (!request->hasParam("pos"))
              {
                request->send(400, "text/plain", "pos param required");
                return;
              }

              String pos = request->getParam("pos")->value();

              cameraServo.moveSlowlyTo(pos.toInt(), display);

              request->send(200, "text/plain", "OK");
            });

  server.begin();
}

// Sends a heartbeat to the api server periodically
void handleHeartbeat()
{
  unsigned long currentMillis = millis();
  if (currentMillis - heartbeatLastSent >= HEARTBEAT_INTERVAL)
  {
    heartbeatLastSent = currentMillis;

    HTTPClient http;
    http.begin("http://" + WiFi.gatewayIP().toString() + ":8080/api/v1/device/rear-camera");
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"device-type\":\"REAR_CAMERA\"}";

    int httpResponseCode = http.PUT(payload);

    if (httpResponseCode > 0)
    {
      String payload = http.getString();
    }
    else
    {
      Serial.printf("Heartbeat Error code: %d\n", httpResponseCode);
    }
    http.end(); // Free resources
  }
}

void loop()
{
  // Only continue this loop if we are connected to the wifi
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi Disconnected. Waiting 5 seconds before trying again...");
    delay(5000);
    return;
  }

  handleHeartbeat();
}
