char receivedChar;
boolean newData = false;
#include<Servo.h>
Servo servo1;     // Servo 1 = door1
#include<Servo.h>
Servo servo2;     // Servo 2 = door2
#include<Servo.h>
Servo servo3;     // Servo 3 = door3
#include<Servo.h>
Servo servo4;     // 
#include<Servo.h>
Servo servo5;     // 
#include<Servo.h>
Servo servo6;     // 
#include<Servo.h>
Servo servo7;     // 
#include<Servo.h>
Servo servo8;     // 
#include<Servo.h>
Servo servo9;     // 
#include<Servo.h>
Servo servo10;     // 
#include<Servo.h>
Servo servo11;     // 
#include<Servo.h>
Servo servo12;     // 
#include<Servo.h>
Servo servo13;     // Servo 13 = running-wheel brake
#include<Servo.h>
Servo servo14;     // Servo 14 = social hatch

const int slowness = 6;   //slowness factor, ms wait between 1deg movements, change to set speed
const int social_slowness = 20;

const int servoPin1 = 2;// door servos 1-12
const int servoPin2 = 3;
const int servoPin3 = 4;
const int servoPin4 = 5;
const int servoPin5 = 6;
const int servoPin6 = 7;// 
const int servoPin7 = 8;
const int servoPin8 = 9;
const int servoPin9 = 10;
const int servoPin10 = 11;
const int servoPin11 = 12;//
const int servoPin12 = 13;
const int servoPin13 = 14;//run wheel
const int servoPin14 = 15;//social

//door angles
const int CLOSE_DOOR1 = 80;
const int OPEN_DOOR1 = 145;
const int CLOSE_DOOR2 = 70;
const int OPEN_DOOR2 = 142;
const int CLOSE_DOOR3 = 60;
const int OPEN_DOOR3 = 135;
const int CLOSE_DOOR4 = 110;
const int OPEN_DOOR4 = 38;
const int CLOSE_DOOR5 = 125;
const int OPEN_DOOR5 = 54;
const int CLOSE_DOOR6 = 125;
const int OPEN_DOOR6 = 52;
const int CLOSE_DOOR7 = 70;
const int OPEN_DOOR7 = 141;
const int CLOSE_DOOR8 = 110;
const int OPEN_DOOR8 = 38;
const int CLOSE_DOOR9 = 145;
const int OPEN_DOOR9 = 78;
const int CLOSE_DOOR10 = 112;
const int OPEN_DOOR10 = 53;
const int CLOSE_DOOR11 = 120;
const int OPEN_DOOR11 = 67;
const int CLOSE_DOOR12 = 105;
const int OPEN_DOOR12 = 40;
const int CLOSE_DOOR13 = 10;
const int OPEN_DOOR13 = 40;
const int CLOSE_DOOR14 = 115;
const int OPEN_DOOR14 = 60;

int pos1_current = OPEN_DOOR1; //initial position variables for servos
int pos1_target = OPEN_DOOR1;
int pos2_current = OPEN_DOOR2; //initial position variables for servos
int pos2_target = OPEN_DOOR2;
int pos3_current = OPEN_DOOR3; //initial position variables for servos  >
int pos3_target = OPEN_DOOR3;
int pos4_current = OPEN_DOOR4; //initial position variables for servos
int pos4_target = OPEN_DOOR4;
int pos5_current = OPEN_DOOR5; //initial position variables for servos
int pos5_target = OPEN_DOOR5;
int pos6_current = OPEN_DOOR6; //initial position variables for servos
int pos6_target = OPEN_DOOR6;
int pos7_current = OPEN_DOOR7; //initial position variables for servos  >
int pos7_target = OPEN_DOOR7;
int pos8_current = OPEN_DOOR8; //initial position variables for servos
int pos8_target = OPEN_DOOR8;
int pos9_current = OPEN_DOOR9; //initial position variables for servos
int pos9_target = OPEN_DOOR9;
int pos10_current = OPEN_DOOR10; //initial position variables for servos
int pos10_target = OPEN_DOOR10;
int pos11_current = OPEN_DOOR11; //initial position variables for servos  >
int pos11_target = OPEN_DOOR11;
int pos12_current = OPEN_DOOR12; //initial position variables for servos
int pos12_target = OPEN_DOOR12;
int pos13_current = OPEN_DOOR13; //initial position variables for servos
int pos13_target = OPEN_DOOR13;
int pos14_current = OPEN_DOOR14; //initial position variables for servos
int pos14_target = OPEN_DOOR14;

void setup() 
{
  Serial.begin(9600);
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);
  servo5.attach(servoPin5);
  servo6.attach(servoPin6);
  servo7.attach(servoPin7);
  servo8.attach(servoPin8);
  servo9.attach(servoPin9);
  servo10.attach(servoPin10);
  servo11.attach(servoPin11);
  servo12.attach(servoPin12);
  servo13.attach(servoPin13);
  servo14.attach(servoPin14);
}

void loop() 
{
  recvInfo();
  moveServo();
}

void recvInfo() 
{
  if (Serial.available() > 0) 
  {
    receivedChar = Serial.read();
    Serial.println(receivedChar);    
  }  
}

void moveServo() 
{
  //target commands
  if (receivedChar=='a')
  {
    pos1_target=OPEN_DOOR1;
  }
  if (receivedChar=='b') 
  {
    pos1_target=CLOSE_DOOR1;
  }
  if (receivedChar=='c')
  {
    pos2_target=OPEN_DOOR2;
  }
  if (receivedChar=='d') 
  {
    pos2_target=CLOSE_DOOR2;
  }
  if (receivedChar=='e')
  {
    pos3_target=OPEN_DOOR3;
  }
  if (receivedChar=='f') 
  {
    pos3_target=CLOSE_DOOR3;
  }
  if (receivedChar=='g')
  {
    pos4_target=OPEN_DOOR4;
  }
  if (receivedChar=='h') 
  {
    pos4_target=CLOSE_DOOR4;
  }  
    if (receivedChar=='i')
  {
    pos5_target=OPEN_DOOR5;
  }
  if (receivedChar=='j') 
  {
    pos5_target=CLOSE_DOOR5;
  }
  if (receivedChar=='k')
  {
    pos6_target=OPEN_DOOR6;
  }
  if (receivedChar=='l') 
  {
    pos6_target=CLOSE_DOOR6;
  }
  if (receivedChar=='m')
  {
    pos7_target=OPEN_DOOR7;
  }
  if (receivedChar=='n') 
  {
    pos7_target=CLOSE_DOOR7;
  }
  if (receivedChar=='o')
  {
    pos8_target=OPEN_DOOR8;
  }
  if (receivedChar=='p') 
  {
    pos8_target=CLOSE_DOOR8;
  } 
    if (receivedChar=='q')
  {
    pos9_target=OPEN_DOOR9;
  }
  if (receivedChar=='r') 
  {
    pos9_target=CLOSE_DOOR9;
  }
  if (receivedChar=='s')
  {
    pos10_target=OPEN_DOOR10;
  }
  if (receivedChar=='t') 
  {
    pos10_target=CLOSE_DOOR10;
  }
  if (receivedChar=='u')
  {
    pos11_target=OPEN_DOOR11;
  }
  if (receivedChar=='v') 
  {
    pos11_target=CLOSE_DOOR11;
  }
  if (receivedChar=='w')
  {
    pos12_target=OPEN_DOOR12;
  }
  if (receivedChar=='x') 
  {
    pos12_target=CLOSE_DOOR12;
  } 
    if (receivedChar=='y')
  {
    pos13_target=OPEN_DOOR13;
  }
  if (receivedChar=='z') 
  {
    pos13_target=CLOSE_DOOR13;
  }
  if (receivedChar=='1')
  {
    pos14_target=OPEN_DOOR14;
  }
  if (receivedChar=='2') 
  {
    pos14_target=CLOSE_DOOR14;
  } 
  
  //movement
  if (pos1_current<pos1_target) //SERVO 1
  {
    pos1_current=pos1_current+1;
    servo1.write(pos1_current);     
    delay(slowness); 
  }
  if (pos1_current>pos1_target)
  {
    pos1_current=pos1_current-1;
    servo1.write(pos1_current);     
    delay(slowness); 
  }
  if (pos2_current<pos2_target) //SERVO 2
  {
    pos2_current=pos2_current+1;
    servo2.write(pos2_current);     
    delay(slowness); 
  }
  if (pos2_current>pos2_target)
  {
    pos2_current=pos2_current-1;
    servo2.write(pos2_current);     
    delay(slowness); 
  }
  if (pos3_current<pos3_target) //SERVO 3
  {
    pos3_current=pos3_current+1;
    servo3.write(pos3_current);     
    delay(slowness); 
  }
  if (pos3_current>pos3_target)
  {
    pos3_current=pos3_current-1;
    servo3.write(pos3_current);     
    delay(slowness); 
  }
  if (pos4_current<pos4_target) //SERVO 4
  {
    pos4_current=pos4_current+1;
    servo4.write(pos4_current);     
    delay(slowness); 
  }
  if (pos4_current>pos4_target)
  {
    pos4_current=pos4_current-1;
    servo4.write(pos4_current);     
    delay(slowness); 
  }
    if (pos5_current<pos5_target) //SERVO 5
  {
    pos5_current=pos5_current+1;
    servo5.write(pos5_current);     
    delay(slowness); 
  }
  if (pos5_current>pos5_target)
  {
    pos5_current=pos5_current-1;
    servo5.write(pos5_current);     
    delay(slowness); 
  }
  if (pos6_current<pos6_target) //SERVO 6
  {
    pos6_current=pos6_current+1;
    servo6.write(pos6_current);     
    delay(slowness); 
  }
  if (pos6_current>pos6_target)
  {
    pos6_current=pos6_current-1;
    servo6.write(pos6_current);     
    delay(slowness); 
  }
  if (pos7_current<pos7_target) //SERVO 7
  {
    pos7_current=pos7_current+1;
    servo7.write(pos7_current);     
    delay(slowness); 
  }
  if (pos7_current>pos7_target)
  {
    pos7_current=pos7_current-1;
    servo7.write(pos7_current);     
    delay(slowness); 
  }
  if (pos8_current<pos8_target) //SERVO 8
  {
    pos8_current=pos8_current+1;
    servo8.write(pos8_current);     
    delay(slowness); 
  }
  if (pos8_current>pos8_target)
  {
    pos8_current=pos8_current-1;
    servo8.write(pos8_current);     
    delay(slowness); 
  }
    if (pos9_current<pos9_target) //SERVO 9
  {
    pos9_current=pos9_current+1;
    servo9.write(pos9_current);     
    delay(slowness); 
  }
  if (pos9_current>pos9_target)
  {
    pos9_current=pos9_current-1;
    servo9.write(pos9_current);     
    delay(slowness); 
  }
  if (pos10_current<pos10_target) //SERVO 10
  {
    pos10_current=pos10_current+1;
    servo10.write(pos10_current);     
    delay(slowness); 
  }
  if (pos10_current>pos10_target)
  {
    pos10_current=pos10_current-1;
    servo10.write(pos10_current);     
    delay(slowness); 
  }
  if (pos11_current<pos11_target) //SERVO 11
  {
    pos11_current=pos11_current+1;
    servo11.write(pos11_current);     
    delay(slowness); 
  }
  if (pos11_current>pos11_target)
  {
    pos11_current=pos11_current-1;
    servo11.write(pos11_current);     
    delay(slowness); 
  }
  if (pos12_current<pos12_target) //SERVO 12
  {
    pos12_current=pos12_current+1;
    servo12.write(pos12_current);     
    delay(slowness); 
  }
  if (pos12_current>pos12_target)
  {
    pos12_current=pos12_current-1;
    servo12.write(pos12_current);     
    delay(slowness); 
  }
    if (pos13_current<pos13_target) //SERVO 13
  {
    pos13_current=pos13_current+1;
    servo13.write(pos13_current);     
    delay(slowness); 
  }
  if (pos13_current>pos13_target)
  {
    pos13_current=pos13_current-1;
    servo13.write(pos13_current);     
    delay(slowness); 
  }
  if (pos14_current<pos14_target) //SERVO 14
  {
    pos14_current=pos14_current+1;
    servo14.write(pos14_current);     
    delay(social_slowness); 
  }
  if (pos14_current>pos14_target)
  {
    pos14_current=pos14_current-1;
    servo14.write(pos14_current);     
    delay(social_slowness); 
  }
}
