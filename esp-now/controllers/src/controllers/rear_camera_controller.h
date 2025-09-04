#ifndef REAR_CAMERA_CONTROLLER_H
#define REAR_CAMERA_CONTROLLER_H

#include <esp_now.h>

class RearCameraController
{
private:
public:
  void init();
  void update();
  void onRecv(const uint8_t *mac, const uint8_t *incomingData, int len);
  void onSent(const uint8_t *mac_addr, esp_now_send_status_t status);
};

extern RearCameraController rearCamController;

#endif