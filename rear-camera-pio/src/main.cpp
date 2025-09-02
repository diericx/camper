#include <Arduino.h>
#include <ESP32Servo.h>

Servo myservo;

int pos = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Got here!");

  // Allow allocation of all timers (optional, but recommended for multiple servos)
  ESP32PWM::allocateTimer(0); 
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  Serial.println("setup servo");
  myservo.setPeriodHertz(50); // Standard 50 Hz servo frequency
  myservo.attach(9);
}

void loop() {
  Serial.println("Forward...");
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    myservo.write(pos);
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  Serial.println("Backward...");
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);
    delay(15);                       // waits 15ms for the servo to reach the position
  }
}