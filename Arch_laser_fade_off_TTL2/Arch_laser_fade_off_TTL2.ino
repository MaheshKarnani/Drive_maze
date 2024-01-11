int LASERpin = 9;         // the PWM pin the Laser is attached to
int TTLpin = 2;         // the digital pin the TTL input is attached to
int brightness = 0;  // how bright the Laser is at each iteration
int base_brightness = 0;  // how bright the Laser is by default. Range is 0-255
int high_brightness = 255;  // how bright the Laser is at peak. Range is 0-255
int fadeAmount = 1;  // how many points to fade the LED by. Range is 0-255.

// the setup routine runs once when you press reset:
void setup() 
{
  pinMode(LASERpin, OUTPUT); // declare LASERpin to be an output
  pinMode(TTLpin, INPUT); // declare TTLpin to be an input
}

// the loop routine runs over and over again forever:
void loop() 
{
  if (digitalRead(TTLpin)==HIGH)
  {
    brightness = high_brightness;
  }
  else
  {
    if (brightness>base_brightness)
    {
      brightness = brightness - fadeAmount;
    }
  }
  analogWrite(LASERpin, brightness);
  delay(2);// wait for 2 milliseconds to see the dimming effect. CHANGE RAMP DURATION HERE. 3ms=800ms, 2ms=500ms.
}
