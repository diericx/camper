#ifndef CAMERASERVO_H
#define CAMERASERVO_H

#include <ESP32Servo.h>

class CameraServo {
private:
    Servo s;
    int pos;

public:
    CameraServo(int pin);
    void moveSlowlyTo(int newPos);
};

#endif // CAMERASERVO_H