#include <Arduino.h>
#include <cameraServo.h>
#include <secrets.h>

CameraServo cameraServo;
int cameraServoPos = 0;
int servoPin = 9;

void setup() {
  Serial.begin(115200);
}

void loop() {
  cameraServo.moveSlowlyTo(0);
  delay(500);
  cameraServo.moveSlowlyTo(180);
  delay(500);
}
