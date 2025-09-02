#include <cameraServo.h>
#include <ESP32Servo.h>
#include <Preferences.h>

#define RW_MODE false
#define RO_MODE true
#define NVS_NAMESPACE "rearCamera"

CameraServo::CameraServo(int pin)
{
  // Allow allocation of all timers (optional, but recommended for multiple servos)
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  s.setPeriodHertz(50); // Standard 50 Hz servo frequency
  s.attach(pin);

  // Ensure we are at the correct position
  s.write(pos);
}

void CameraServo::moveSlowlyTo(int newPos)
{
  while (pos != newPos)
  {
    if (pos < newPos)
    {
      pos += 1;
    }
    if (pos > newPos)
    {
      pos -= 1;
    }
    s.write(pos);
    delay(10);
  }
}