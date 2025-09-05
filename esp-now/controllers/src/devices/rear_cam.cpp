#include "rear_cam.h"
#include "esp_now.h"
#include <WiFi.h>
#include "messages.h"

DevType Dev::RearCam::getDevType() const
{
  return DevType::RearCam;
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
    break;
  }
  default:
    Serial.println("WARNING: Unrecognized message type.");
    break;
  }
}
