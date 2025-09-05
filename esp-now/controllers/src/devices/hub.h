#ifndef DEV_HUB_H

#define DEV_HUB_H
#define DEV_TYPE DevType::Hub

#include <esp_now.h>
#include "messages.h"

namespace Dev
{
  class Hub
  {
  private:
  public:
    void init();
    void update();
    void onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len);
    void onSent(const uint8_t *mac_addr, esp_now_send_status_t status);
  };

}

extern Dev::Hub dev;

#endif