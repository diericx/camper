#ifndef BUTTON_H
#define BUTTON_H

#include <functional>

class Button
{
private:
  std::function<void()> onPressedCallback;

public:
  void init(int pin, int debounceMs, std::function<void()> onPressCallback);
  void update();
};

#endif