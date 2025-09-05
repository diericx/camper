#include <Arduino.h>
#include <WiFi.h>
#include "esp_now.h"
#include "messages.h"

// Include role-specific headers
#ifdef DEVICE_ROLE_HUB
#include "devices/hub.h"
#elif defined(DEVICE_ROLE_REAR_CAM)
#include "devices/rear_cam.h"
#else
#error "No device role defined! Use -DDEVICE_ROLE_HUB or similar"
#endif

uint8_t devMacAddress[6];

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
  if (header.dest != DEV_TYPE)
  {
    return;
  }

  dev.onRecv(header, mac, incomingData, len);
}

void OnSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  dev.onSent(mac_addr, status);
}

void setup()
{
  // Init Serial Monitor
  Serial.begin(115200);
  delay(1000);

  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);
  WiFi.macAddress(devMacAddress);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK)
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  dev.init();

  esp_now_register_recv_cb(OnRecv);
  esp_now_register_send_cb(OnSent);
}

void loop()
{
  dev.update();
}