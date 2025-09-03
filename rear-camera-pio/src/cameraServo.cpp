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

  // Load the last saved position from NVS
  loadPosition();

  // Ensure we are at the correct position
  s.write(pos);
}

void CameraServo::moveSlowlyTo(int newPos)
{
  // Only save if the position actually changes
  if (pos != newPos)
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

    // Save the final position to NVS only once after movement is complete
    savePosition();
  }
}

void CameraServo::savePosition()
{
  Preferences preferences;
  preferences.begin(NVS_NAMESPACE, RW_MODE);
  preferences.putInt("servoPos", pos);
  preferences.end();
}

void CameraServo::loadPosition()
{
  Preferences preferences;
  preferences.begin(NVS_NAMESPACE, RO_MODE);
  pos = preferences.getInt("servoPos", 0);
  preferences.end();
}

int CameraServo::getCurrentPosition()
{
  return pos;
}