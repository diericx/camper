#include <Arduino.h>
#include <WiFi.h>
#include "esp_now.h"

// Include role-specific headers
#ifdef DEVICE_ROLE_MAIN_CONTROLLER
#include "controllers/main_controller.h"
#elif defined(DEVICE_ROLE_REAR_CAMERA_CONTROLLER)
#include "controllers/rear_camera_controller.h"
#else
#error "No device role defined! Use -DDEVICE_ROLE_MAIN_CONTROLLER or similar"
#endif

void setup()
{
  // Init Serial Monitor
  Serial.begin(115200);
  delay(1000);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK)
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

#ifdef DEVICE_ROLE_MAIN_CONTROLLER
  mainController.init();
#elif defined(DEVICE_ROLE_REAR_CAMERA_CONTROLLER)
  rearCamController.init();
#endif
}

void loop()
{
#ifdef DEVICE_ROLE_MAIN_CONTROLLER
  mainController.update();
#elif defined(DEVICE_ROLE_REAR_CAMERA_CONTROLLER)
  rearCamController.update();
#endif
  // put your main code here, to run repeatedly:
}