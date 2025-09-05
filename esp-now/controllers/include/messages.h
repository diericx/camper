#ifndef MESSAGES_H
#define MESSAGES_H

#include "Arduino.h"

const uint8_t BROADCAST_ADDR[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

enum ControllerType : uint8_t
{
  Hub,
  RearCam,
};

enum class MessageType : uint8_t
{
  RearCam_MoveTo
};

inline String MessageTypeToString(MessageType t)
{
  switch (t)
  {
  case MessageType::RearCam_MoveTo:
    return "RearCam_MoveTo";
  default:
    return "UNKNOWN";
  };
}

struct Header
{
  ControllerType src;
  ControllerType dest;
  MessageType msgType;
};

struct RearCam_MoveTo : Header
{
  uint8_t pos;
  MessageType msgType = MessageType::RearCam_MoveTo;
};

#endif