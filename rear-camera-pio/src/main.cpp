#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

#include <cameraServo.h>
#include <secrets.h>

CameraServo cameraServo(9);

AsyncWebServer server(8080);

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

void setup()
{
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(SECRET_SSID, SECRET_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED)
  {
    Serial.printf("WiFi Failed!\n");
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

              cameraServo.moveSlowlyTo(pos.toInt());

              request->send(200, "text/plain", "OK");
            });

  server.begin();
}

void loop()
{
}
