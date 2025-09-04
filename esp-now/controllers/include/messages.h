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
  Heartbeat
};

inline String MessageTypeToString(MessageType t)
{
  switch (t)
  {
  case MessageType::Heartbeat:
    return "HeartBeat";
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

struct Heartbeat : Header
{
  char msg[32];
};

#endif