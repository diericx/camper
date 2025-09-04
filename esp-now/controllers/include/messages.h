enum ControllerType : uint8_t
{
  Main,
  RearCamera,
};

enum class MessageType : uint8_t
{
  Heartbeat
};

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