#include <cameraServo.h>
#include <ESP32Servo.h>
#include <Preferences.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

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

void CameraServo::moveSlowlyTo(int newPos, Adafruit_SSD1306 &display)
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
      display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
      display.clearDisplay();
      display.drawRoundRect(10, 10, 10, 10, 2, WHITE);
      // display.fillRoundRect(22, 22, 6, 6, 2, WHITE);
      display.setCursor(25, 11);
      display.setTextSize(1);
      display.setTextColor(WHITE);
      display.print("Pos: ");
      display.println(pos);
      display.display();
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