#ifndef REAR_CAM_CONTROLLER_H

#define REAR_CAM_CONTROLLER_H
#define DEV_TYPE DevType::RearCam

#include <esp_now.h>
#include "messages.h"

namespace Dev
{
  class RearCam
  {
  private:
  public:
    void init();
    void update();
    void onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len);
    void onSent(const uint8_t *mac_addr, esp_now_send_status_t status);
  };

}

extern Dev::RearCam dev;

#endif