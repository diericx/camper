#include <Arduino.h>
#include <cameraServo.h>
#include <secrets.h>

CameraServo cameraServo(9);
int cameraServoPos = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
}
