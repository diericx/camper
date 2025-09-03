#ifndef CAMERASERVO_H
#define CAMERASERVO_H

#include <ESP32Servo.h>

class CameraServo
{
private:
    Servo s;
    int pos;
    void savePosition();
    void loadPosition();

public:
    CameraServo(int pin);
    void moveSlowlyTo(int newPos);
    int getCurrentPosition();
};

#endif // CAMERASERVO_H