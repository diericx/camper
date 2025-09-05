#include "rear_cam.h"
#include "esp_now.h"
#include <WiFi.h>
#include "messages.h"

Dev::RearCam dev;

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

  RearCam_MoveTo msg;
  memcpy(&msg, incomingData, sizeof(msg));
  Serial.print("MoveTo Pos: ");
  Serial.println(msg.pos);
  Serial.println();
}

void Dev::RearCam::onSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
}

void Dev::RearCam::init()
{
}

void Dev::RearCam::update()
{
}