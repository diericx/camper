#include "rear_cam.h"
#include "esp_now.h"
#include <WiFi.h>
#include <nvs_flash.h>

#include "messages.h"

DevType Dev::RearCam::getDevType() const
{
  return DevType::RearCam;
}

void Dev::RearCam::init()
{
  // Initialize NVS
  esp_err_t ret = nvs_flash_init();
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
  {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret);

  cameraServo.init(2); // D0
}

// callback function that will be executed when data is received
void Dev::RearCam::onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len)
{
  // Create a struct_message called myData
  Serial.print("Bytes received: ");
  Serial.println(len);
  Serial.print("Source type: ");
  Serial.println(header.src);
  Serial.print("Dest type: ");
  Serial.println(header.dest);
  Serial.print("Msg type: ");
  Serial.println(MessageTypeToString(header.msgType));

  switch (header.msgType)
  {
  case MessageType::RearCam_MoveTo:
  {
    RearCam_MoveTo msg;
    memcpy(&msg, incomingData, sizeof(msg));
    Serial.print("MoveTo Pos: ");
    Serial.println(msg.pos);
    Serial.println();

    cameraServo.moveSlowlyTo(msg.pos);

    break;
  }
  default:
    Serial.println("WARNING: Unrecognized message type.");
    break;
  }
}
