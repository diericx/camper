#include <WiFi.h>
#include <HTTPClient.h>
#include <Servo.h>
#include "secrets.h"

unsigned long heartbeatLastSent = 0;
const long heartbeatInterval = 5000; // 5 seconds in milliseconds
const long timeoutTime = 2000;
WiFiServer server(8080);

Servo myservo = Servo();
int servoPin = 9; // D9

void setup() {
  Serial.begin(115200); // Initialize serial communication for debugging
  delay(10); // Small delay for serial port initialization

  myservo.write(servoPin, 90);

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

  // Start http server
  // TODO: reconnect below?
  server.begin();
}

// Sends a heartbeat to the api server periodically
void handleHeartbeat() {
  unsigned long currentMillis = millis();
  if (currentMillis - heartbeatLastSent >= heartbeatInterval) {
    heartbeatLastSent = currentMillis;
    
    HTTPClient http;
    http.begin("http://"+WiFi.gatewayIP().toString() + ":8080/api/v1/device/rear-camera");
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"device-type\":\"REAR_CAMERA\"}";

    int httpResponseCode = http.PUT(payload); // Or http.POST() for POST requests

    if (httpResponseCode > 0) {
      // Serial.printf("HTTP Response code: %d\n", httpResponseCode);
      String payload = http.getString();
      // Serial.println(payload);
    } else {
      Serial.printf("Heartbeat Error code: %d\n", httpResponseCode);
    }
    http.end(); // Free resources
  }
}

void handleHTTPRequests() {
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  unsigned long currentTime = millis();
  unsigned long startTime = currentTime;
  Serial.println("New Client.");          // print a message out in the serial port
  String currentLine = "";                // make a String to hold incoming data from the client
  String header = "";

  while (client.connected() && currentTime - startTime <= timeoutTime) {  // loop while the client's connected
    currentTime = millis();
    if (client.available()) {             // if there's bytes to read from the client,
      char c = client.read();             // read a byte, then
      Serial.write(c);                    // print it out the serial monitor
      header += c;
      if (c == '\n') {                    // if the byte is a newline character
        // if the current line is blank, you got two newline characters in a row.
        // that's the end of the client HTTP request, so send a response:
        if (currentLine.length() == 0) {
          // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
          // and a content-type so the client knows what's coming, then a blank line:
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type:application/json");
          client.println("Connection: close");
          client.println();

          // Basic routing
          if (header.indexOf("POST /api/v1/action/up") >= 0) {
            myservo.write(servoPin, 180);
          }else if (header.indexOf("POST /api/v1/action/down") >= 0) {
            myservo.write(servoPin, 0);
          }

          client.println("{\"status\": \"ok\"}");
          
          break;
        } else { // if you got a newline, then clear currentLine
          currentLine = "";
        }
      } else if (c != '\r') {  // if you got anything else but a carriage return character,
        currentLine += c;      // add it to the end of the currentLine
      }
    }
  }

  // Close the connection
  client.stop();
  Serial.println("Client disconnected.");
  Serial.println("");
}

void loop() {
  // Only continue this loop if we are connected to the wifi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi Disconnected. Attempting to reconnect...");
    uint8_t status = WiFi.begin(SECRET_SSID, SECRET_PASS); // Attempt to reconnect

    if (status != WL_CONNECTED) {
      Serial.println("Unable to connect. Waiting 5 seconds before attempting to reconnect...");
      delay(5000);
      return;
    }
  }

  handleHeartbeat();
  handleHTTPRequests();
}
