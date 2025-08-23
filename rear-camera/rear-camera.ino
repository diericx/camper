#include <WiFi.h>
#include <HTTPClient.h>
#include "secrets.h"

void setup() {
  Serial.begin(115200); // Initialize serial communication for debugging
  delay(10); // Small delay for serial port initialization

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(SECRET_SSID);

  // Set ESP32-C3 to Station mode
  WiFi.mode(WIFI_STA); 

  // Start the connection to the Wi-Fi network
  WiFi.begin(SECRET_SSID, SECRET_PASS); 

  // Wait for the connection to establish
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); // Wait for half a second
    Serial.print("."); // Print a dot to indicate connection progress
  }

  // Connection successful
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP()); // Print the assigned IP address
  Serial.print("Gateway IP address: ");
  Serial.println(WiFi.gatewayIP());
}

unsigned long previousMillis = 0;
const long interval = 5000; // 5 seconds in milliseconds

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis; // Update the last time the request was sent

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin("http://"+WiFi.gatewayIP().toString() + "/api/v1/device/rear-camera");
      http.addHeader("Content-Type", "application/json");

      String payload = "{\"device-type\":\"REAR_CAMERA\"}";

      int httpResponseCode = http.PUT(payload); // Or http.POST() for POST requests

      if (httpResponseCode > 0) {
        Serial.printf("HTTP Response code: %d\n", httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
      } else {
        Serial.printf("Error code: %d\n", httpResponseCode);
      }
      http.end(); // Free resources
    } else {
      Serial.println("WiFi Disconnected. Attempting to reconnect...");
      WiFi.begin(SECRET_SSID, SECRET_PASS); // Attempt to reconnect
    }
  }
}
