#include "hub.h"
#include <Arduino.h>
#include <esp_now.h>
#include "messages.h"

esp_now_peer_info_t peerInfo;
Dev::Hub dev;

// callback function that will be executed when data is received
void Dev::Hub::onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len)
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
}

// callback when data is sent
void Dev::Hub::onSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void Dev::Hub::init()
{
  // Register peer(s)
  memcpy(peerInfo.peer_addr, BROADCAST_ADDR, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK)
  {
    Serial.println("Failed to add peer");
    return;
  }
}

void Dev::Hub::update()
{
  // Create a struct_message called myData
  RearCam_MoveTo msg;
  msg.src = DEV_TYPE;
  msg.dest = DevType::RearCam;
  msg.pos = 99;

  // Send message via ESP-NOW
  esp_err_t result = esp_now_send(BROADCAST_ADDR, (uint8_t *)&msg, sizeof(msg));

  if (result == ESP_OK)
  {
    Serial.println("Sent with success");
  }
  else
  {
    Serial.println("Error sending the data");
  }
  delay(2000);
}
