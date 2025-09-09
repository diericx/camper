#ifndef DEV_BASE_H
#define DEV_BASE_H

#include <esp_now.h>
#include "messages.h"

namespace Dev
{
  class Base
  {
  protected:
    esp_now_peer_info_t broadcastPeerInfo;

  public:
    virtual ~Base() = default;
    virtual void init()
    {
      // Register broadcast peer(s)
      memcpy(broadcastPeerInfo.peer_addr, BROADCAST_ADDR, 6);
      broadcastPeerInfo.channel = 0;
      broadcastPeerInfo.encrypt = false;
      if (esp_now_add_peer(&this->broadcastPeerInfo) != ESP_OK)
      {
        Serial.println("Failed to add peer");
        return;
      }
    };
    virtual void update() = 0;
    virtual void onRecv(Header header, const uint8_t *mac, const uint8_t *incomingData, int len) = 0;
    virtual void onSent(const uint8_t *mac_addr, esp_now_send_status_t status) = 0;
    virtual DevType getDevType() const = 0;
  };
};

#endif