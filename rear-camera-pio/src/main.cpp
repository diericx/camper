#include <Arduino.h>
#include <WiFi.h>

#include <cameraServo.h>
#include <webServer.h>
#include <secrets.h>

CameraServo cameraServo(9);
WebServer webServer(8080);

std::string handleHello(const std::string &verb, const std::string &path, const std::string &body)
{
  Serial.println(verb.c_str());
  Serial.println(verb.c_str());
  Serial.println(body.c_str());
  return "{\"status\":\"success\"}";
}

void setup()
{
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(SECRET_SSID, SECRET_PASS);

  webServer.addRoute("POST", "/hello", handleHello);
  webServer.begin();
}

void loop()
{
  webServer.handleHTTPRequest();
}
