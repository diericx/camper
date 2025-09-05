#ifndef DEV_BASE_H
#define DEV_BASE_H

#include <esp_now.h>
#include "messages.h"

namespace Dev
{
  class Base
  {
  public:
    virtual ~Base() = default;
    virtual void init() = 0;
    virtual void update() = 0;
    virtual void onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len) = 0;
    virtual void onSent(const uint8_t *mac_addr, esp_now_send_status_t status) = 0;
    virtual DevType getDevType() const = 0;
  };
};

#endif