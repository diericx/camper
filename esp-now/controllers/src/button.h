#ifndef BUTTON_H
#define BUTTON_H

#include <functional>

class Button
{
private:
  std::function<void()> onPressCallback;
  std::function<void()> onReleaseCallback;

  // Button state variables
  int pin;
  int debounceMs;
  int currentState;
  int lastState;
  unsigned long lastDebounceTime;
  bool buttonPressed;

public:
  void init(int pin, int debounceMs, std::function<void()> onPressCallback, std::function<void()> onReleaseCallback);
  void update();
};

#endif