
#ifndef DEV_HUB_H

#define DEV_HUB_H

#include <esp_now.h>
#include "messages.h"
#include "base.h"
#include "button.h"

namespace Dev
{
  class Hub : public Base
  {
  private:
    const int TOGGLE_SWITCH_PIN = 2;
    Button toggleSwitch;

    void onButtonPressed();
    void onButtonReleased();

  public:
    void init();
    void update();
    void onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len);
    void onSent(const uint8_t *mac_addr, esp_now_send_status_t status);
    DevType getDevType() const;
  };
}

#endif