#include "main_controller.h"
#include <Arduino.h>
#include <esp_now.h>
#include "messages.h"

MainController mainController;

// callback function that will be executed when data is received
void OnDataRecv(const uint8_t *mac, const uint8_t *incomingData, int len)
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

void MainController::init()
{
  // Init ESP-NOW
  if (esp_now_init() != ESP_OK)
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Once ESPNow is successfully Init, we will register for recv CB to
  // get recv packer info
  esp_now_register_recv_cb(OnDataRecv);
}

void MainController::update()
{
}
