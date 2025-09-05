#ifndef REAR_CAM_CONTROLLER_H

#define REAR_CAM_CONTROLLER_H

#include <esp_now.h>
#include "messages.h"
#include "base.h"

namespace Dev
{
  class RearCam : public Base
  {
  private:
  public:
    void init();
    void update();
    void onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len);
    void onSent(const uint8_t *mac_addr, esp_now_send_status_t status);
    DevType getDevType() const;
  };

}

#endif