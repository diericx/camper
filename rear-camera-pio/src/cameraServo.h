#ifndef CAMERASERVO_H
#define CAMERASERVO_H

#include <ESP32Servo.h>
#include <Adafruit_SSD1306.h>

class CameraServo
{
private:
    Servo s;
    int pos;
    void savePosition();
    void loadPosition();

public:
    CameraServo(int pin);
    void moveSlowlyTo(int newPos, Adafruit_SSD1306 &display);
    int getCurrentPosition();
};

#endif // CAMERASERVO_H