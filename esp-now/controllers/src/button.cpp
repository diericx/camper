#include "button.h"
#include <Arduino.h>

void Button::init(int pin, int debounceMs, std::function<void()> onPressCallback, std::function<void()> onReleaseCallback)
{
  this->pin = pin;
  this->debounceMs = debounceMs;
  this->onPressCallback = onPressCallback;
  this->onReleaseCallback = onReleaseCallback;

  // Configure pin as input with internal pull-up resistor
  pinMode(pin, INPUT_PULLUP);

  // Initialize state variables
  this->currentState = HIGH; // Pull-up means HIGH when not pressed
  this->lastState = HIGH;
  this->lastDebounceTime = 0;
  this->buttonPressed = false;

  Serial.print("Button initialized on pin ");
  Serial.print(pin);
  Serial.print(" with debounce ");
  Serial.print(debounceMs);
  Serial.println("ms");
}

void Button::update()
{
  // Read the current state of the button
  int reading = digitalRead(pin);

  // Check if the button state has changed
  if (reading != lastState)
  {
    // Reset the debounce timer
    lastDebounceTime = millis();
    Serial.print("Button state change detected: ");
    Serial.println(reading == HIGH ? "HIGH" : "LOW");
  }

  // Check if enough time has passed since the last state change
  if ((millis() - lastDebounceTime) > debounceMs)
  {
    // If the button state has changed after debounce period
    if (reading != currentState)
    {
      currentState = reading;
      Serial.print("Button state confirmed after debounce: ");
      Serial.println(currentState == HIGH ? "HIGH" : "LOW");

      // Button is pressed when it goes from HIGH to LOW (pull-up configuration)
      if (currentState == LOW && !buttonPressed)
      {
        buttonPressed = true;
        Serial.println("Button press detected");
        if (onPressCallback)
        {
          onPressCallback();
        }
      }
      // Button is released when it goes from LOW to HIGH
      else if (currentState == HIGH && buttonPressed)
      {
        buttonPressed = false;
        Serial.println("Button release detected");
        if (onReleaseCallback)
        {
          onReleaseCallback();
        }
      }
    }
  }

  // Save the current reading for next iteration
  lastState = reading;
}