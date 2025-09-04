#include "rear_camera_controller.h"
#include "esp_now.h"
#include <WiFi.h>
#include "messages.h"

RearCameraController rearCamController;

// callback function that will be executed when data is received
void OnRecv(const uint8_t *mac, const uint8_t *incomingData, int len)
{
  // Create a struct_message called myData
  Header header;
  memcpy(&header, incomingData, sizeof(header));
  Serial.print("Bytes received: ");
  Serial.println(len);
  Serial.print("Source type: ");
  Serial.println(header.src);
  Serial.print("Dest type: ");
  Serial.println(header.dest);
  Serial.print("Msg type: ");
  Serial.println(MessageTypeToString(header.msgType));

  Heartbeat msg;
  memcpy(&msg, incomingData, sizeof(msg));
  Serial.print("Heartbeat Content: ");
  Serial.println(msg.msg);
  Serial.println();
}

void RearCameraController::init()
{
}

void RearCameraController::update()
{
}