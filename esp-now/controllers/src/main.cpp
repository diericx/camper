#include <Arduino.h>
#include <WiFi.h>
#include "esp_now.h"
#include "messages.h"

#include "devices/hub.h"
#include "devices/rear_cam.h"
#include "button.h"

uint8_t devMacAddress[6];
std::unique_ptr<Dev::Base> dev;
Button toggleSwitch;

void OnRecv(const uint8_t *mac, const uint8_t *incomingData, int len)
{
  // Ignore broadcasts from self
  if (memcmp(mac, devMacAddress, 6) == 0)
  {
    return;
  }

  Header header;
  memcpy(&header, incomingData, sizeof(header));

  // Ignore messages directed at another device type
  if (header.dest != dev->getDevType())
  {
    return;
  }

  dev->onRecv(header, mac, incomingData, len);
}

void OnSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  dev->onSent(mac_addr, status);
}

void setup()
{
  // Init Serial Monitor
  Serial.begin(115200);
  delay(1000);

  // Initialize button on pin 9 with 200ms debounce and anonymous callback functions
  toggleSwitch.init(9, 200, []()
                    {
      // Anonymous function called when button is pressed
      Serial.println("Button pressed!"); }, []()
                    {
      // Anonymous function called when button is released
      Serial.println("Button released!"); });

  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);
  WiFi.macAddress(devMacAddress);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK)
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  dev->init();

  esp_now_register_recv_cb(OnRecv);
  esp_now_register_send_cb(OnSent);
}

void loop()
{
  dev->update();
  toggleSwitch.update();
}