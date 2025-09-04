#include "main_controller.h"
#include <Arduino.h>
#include <esp_now.h>
#include "messages.h"

uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

esp_now_peer_info_t peerInfo;

MainController mainController;

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

// callback when data is sent
void OnSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void MainController::init()
{
  // Register peer(s)
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK)
  {
    Serial.println("Failed to add peer");
    return;
  }

  esp_now_register_recv_cb(OnRecv);
  esp_now_register_send_cb(OnSent);
}

void MainController::update()
{
  // Create a struct_message called myData
  Heartbeat msg;

  // Set values to send
  strcpy(msg.msg, "THIS IS A HEARTBEAT");
  msg.src = ControllerType::RearCamera;
  msg.dest = ControllerType::Main;
  msg.msgType = MessageType::Heartbeat;

  // Send message via ESP-NOW
  esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)&msg, sizeof(msg));

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
