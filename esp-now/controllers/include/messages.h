#ifndef MESSAGES_H
#define MESSAGES_H

#include "Arduino.h"

enum ControllerType : uint8_t
{
  Main,
  RearCamera,
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