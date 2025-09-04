#include "rear_camera_controller.h"
#include "esp_now.h"
#include <WiFi.h>
#include "messages.h"

RearCameraController rearCamController;

uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

esp_now_peer_info_t peerInfo;

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void RearCameraController::init()
{
  esp_now_register_send_cb(OnDataSent);

  // Register peer(s)
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK)
  {
    Serial.println("Failed to add peer");
    return;
  }
}

void RearCameraController::update()
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