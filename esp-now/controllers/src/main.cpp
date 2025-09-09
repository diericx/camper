#include <Arduino.h>
#include <WiFi.h>
#include "esp_now.h"
#include "messages.h"
#include <memory>

#include "devices/hub.h"
#include "devices/rear_cam.h"
#include "button.h"

uint8_t devMacAddress[6];
std::unique_ptr<Dev::Base> dev;

void OnRecv(const uint8_t *mac, const uint8_t *incomingData, int len)
{
  // Only process if device is initialized
  if (!dev)
    return;

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
  // Only process if device is initialized
  if (dev)
  {
    dev->onSent(mac_addr, status);
  }
}

void setup()
{
  // Init Serial Monitor
  Serial.begin(115200);
  delay(2000);

  Serial.println("Starting setup...");

  // Initialize the appropriate device based on build flags
#ifdef DEVICE_ROLE_HUB
  dev.reset(new Dev::Hub());
  Serial.println("Initialized as Hub device");
#elif defined(DEVICE_ROLE_REAR_CAM)
  dev.reset(new Dev::RearCam());
  Serial.println("Initialized as RearCam device");
#else
  Serial.println("Warning: No device role defined, running without device functionality");
#endif

  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);
  WiFi.macAddress(devMacAddress);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK)
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Initialize device if it was created
  if (dev)
  {
    dev->init();
    esp_now_register_recv_cb(OnRecv);
    esp_now_register_send_cb(OnSent);
    Serial.println("Device initialized");
  }

  Serial.println("Setup complete");
}

void loop()
{
  // Only update dev if it's been assigned
  if (dev)
  {
    dev->update();
  }
}