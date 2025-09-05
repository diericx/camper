#include <Arduino.h>
#include <WiFi.h>
#include "esp_now.h"
#include "messages.h"

// Include role-specific headers
#ifdef DEVICE_ROLE_MAIN_CONTROLLER
#include "controllers/main_controller.h"
#elif defined(DEVICE_ROLE_REAR_CAMERA_CONTROLLER)
#include "controllers/rear_camera_controller.h"
#else
#error "No device role defined! Use -DDEVICE_ROLE_MAIN_CONTROLLER or similar"
#endif

// TODO: Controller -> Dev
// TODO: Rearcameracontroller -> rearcam

uint8_t devMacAddress[6];

void OnRecv(const uint8_t *mac, const uint8_t *incomingData, int len)
{
  if (memcmp(mac, devMacAddress, 6) == 0)
  {
    return; // Ignore broadcasts from self
  }

  Header header;
  memcpy(&header, incomingData, sizeof(header));

  controller.onRecv(header, mac, incomingData, len);
}

void OnSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  controller.onSent(mac_addr, status);
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

  controller.init();

  esp_now_register_recv_cb(OnRecv);
  esp_now_register_send_cb(OnSent);
}

void loop()
{
  controller.update();
}