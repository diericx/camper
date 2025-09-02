#include <map>
#include <vector>
#include <string>
#include <sstream>

#include <webServer.h>
#include <WiFi.h>

#define TIMEOUT 10000

WebServer::WebServer(int port)
{
  server = WiFiServer(port);
}

void WebServer::begin()
{
  Serial.println("Waiting for wifi connection before starting web server.");
  // Wait for the connection to establish
  // WARNING: this will hang the entire app...
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);        // Wait for half a second
    Serial.print("."); // Print a dot to indicate connection progress
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP()); // Print the assigned IP address
  Serial.print("Gateway IP address: ");
  Serial.println(WiFi.gatewayIP());

  server.begin();
}

void WebServer::addRoute(std::string verb, std::string path, RequestHandlerFunc func)
{
  handlers[verb + " " + path] = func;
}

void WebServer::handleHTTPRequest()
{
  WiFiClient client = server.available();
  if (!client)
  {
    return;
  }

  unsigned long currentTime = millis();
  unsigned long startTime = currentTime;

  Serial.println("New Client."); // print a message out in the serial port

  String buffer = ""; // make a String to hold incoming data from the client
  String headers = "";
  String requestLine = "";
  String body = "";

  // loop while the client's connected
  while (client.connected() && currentTime - startTime <= TIMEOUT)
  {
    currentTime = millis();
    if (client.available())
    {                         // if there's bytes to read from the client,
      char c = client.read(); // read a byte, then
      Serial.write(c);        // print it out the serial monitor
      buffer += c;

      Serial.println("Request line: ");
      Serial.println(requestLine);
      if (requestLine == "")
      {
        if (c == '\n')
        {
          requestLine = buffer;
          buffer = "";
          continue;
        }
      }

      if (headers == "")
      {
        if (buffer.endsWith("\r\n\r\n") || buffer.endsWith("\n\n"))
        {
          headers = buffer;
          buffer = "";
          continue;
        }
      }
    }
    else
    {
      body = buffer;
      break;
    }
  }

  // Split request line
  std::stringstream rlStringStream(requestLine.c_str());
  std::string segment;
  std::vector<std::string> seglist;
  while (std::getline(rlStringStream, segment, ' '))
  {
    seglist.push_back(segment);
  }

  if (seglist.size() < 3)
  {
    Serial.println("Invalid request line, not enough values parsed out when splitting on space char");
    Serial.println(requestLine);
    client.println("HTTP/1.1 400 Bad Request");
    client.println("Connection: close");
    client.println();
    client.stop();
    return;
  }

  std::string verb, path, protocol, route;
  verb = seglist.at(0);
  path = seglist.at(1);
  protocol = seglist.at(2);
  route = verb + " " + path;

  if (handlers.count(route))
  {
    std::string response = handlers[route](verb, path, body.c_str());
    client.println("HTTP/1.1 200 OK");
    client.println("Content-type:text/plain");
    client.println("Connection: close");
    client.print("Content-Length: ");
    client.println(response.length());
    client.println();
    client.println(response.c_str());
    client.stop();
  }
  else
  {
    Serial.println("NOT Found!");
    client.println("HTTP/1.1 404 Not Found");
    client.println("Connection: close"); // Tell client we're closing
    client.println("Content-Length: 0"); // No body content
    client.println();                    // Empty line to end headers
    client.stop();
  }
}