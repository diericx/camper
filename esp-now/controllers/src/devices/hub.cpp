#include "hub.h"
#include <Arduino.h>
#include <esp_now.h>

DevType Dev::Hub::getDevType() const
{
  return DevType::Hub;
}

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

void Dev::Hub::onButtonPressed()
{
  // Function called when button is pressed
  Serial.println("Button pressed!");

  // Create a struct_message called myData
  RearCam_MoveTo msg;
  msg.src = this->getDevType();
  msg.dest = DevType::RearCam;
  msg.pos = 0;

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
}

void Dev::Hub::onButtonReleased()
{
  // Function called when button is pressed
  Serial.println("Button Released!");

  // Create a struct_message called myData
  RearCam_MoveTo msg;
  msg.src = this->getDevType();
  msg.dest = DevType::RearCam;
  msg.pos = 90;

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
}

void Dev::Hub::init()
{
  // Initialize button on pin 9 with 200ms debounce and callback functions
  toggleSwitch.init(TOGGLE_SWITCH_PIN, 200, [this]()
                    { onButtonPressed(); }, [this]()
                    { onButtonReleased(); });

  Serial.println("Toggle switch initialized.");

  if (esp_now_add_peer(&this->broadcastPeerInfo) != ESP_OK)
  {
    Serial.println("Failed to add peer");
    return;
  }
}

void Dev::Hub::update()
{
  toggleSwitch.update();
}
