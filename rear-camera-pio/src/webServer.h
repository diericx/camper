#ifndef WEBSERVER_H
#define WEBSERVER_H

#include <WiFi.h>
#include <map>
#include <functional>

using RequestHandlerFunc = std::function<std::string(const std::string &verb, const std::string &path, const std::string &inputBody)>;

class WebServer
{
private:
  WiFiServer server;
  std::map<std::string, RequestHandlerFunc> handlers;

public:
  WebServer(int port);
  void begin();
  void handleHTTPRequest();
  void addRoute(std::string verb, std::string path, RequestHandlerFunc func);
};

#endif