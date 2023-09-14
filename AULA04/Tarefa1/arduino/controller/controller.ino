#include "Wire.h"
#include "Servo.h"

#include "DHT.h"
 
#define DHTPIN A1 // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 

#define SERVO_PIN 6 // Digital pin connected to the DHT sensor

#define SAMPLE_TIME 100 // PID interval in miliseconds

#define VALVE_OFFSET 90

#define SLAVE_ADDRESS 0x08 //SLAVE Unique ID in the BUS
 
// Connect pin 1 (on the left) of the sensor to +5V
// NOTE: If using a board with 3.3V logic like an Arduino Due connect pin 1
// to 3.3V instead of 5V!
// Connect pin 2 of the sensor to whatever your DHTPIN is
// Connect pin 3 (on the right) of the sensor to GROUND (if your sensor has 3 pins)
// Connect pin 4 (on the right) of the sensor to GROUND and leave the pin 3 EMPTY (if your sensor has 4 pins)
// Connect a 10K resistor from pin 2 (data) to pin 1 (power) of the sensor
DHT dht(DHTPIN, DHTTYPE);

String inputString = "";//Store i2c data
String outputString = "";//enqueue i2c data
boolean stringComplete = false;  // whether the string is complete
boolean halt = false;

Servo valveServo; // Servo controller
int currentPos = 0; // Servo position 0 = midpoint
int avgCount = 0;

float tSetPoint;

float kp = 10, ki = 5, kd = 0.1;

long time;
long et;

long pTime, lTime, rTime, sampleTime, reportTime;

float dt, error, pError;

float integralError = 0;
float derivativeError = 0;

float h;
float t, avgTemp = 0;


void receiveData(int bytecount)
{
  char inChar;

  for (int i = 0; i < bytecount; i++) {
    inChar = Wire.read();
    inputString += String(inChar);
  }

  stringComplete = true;

}
void sendData()
{
  if ( outputString != "" )
  {
    //Serial.println(outputString);
    Wire.write(outputString.c_str());
    outputString = "";
  }

}
 
void setup() 
{
  Serial.begin(9600);
  while(!Serial);
  Serial.println("SP, PV, CO");

  dht.begin();

  Wire.begin(SLAVE_ADDRESS);

  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  valveServo.attach(SERVO_PIN);
  valveServo.write(VALVE_OFFSET + currentPos); 

  tSetPoint = dht.readTemperature();

  pinMode(LED_BUILTIN, OUTPUT);

  for( int i = 0; i < 3; ++i)
  {
    tSetPoint = max(tSetPoint, dht.readTemperature());
    
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(1000);                       // wait for a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    delay(1000);                       // wait for a second
  }

}
 
void loop() 
{

  if ( stringComplete )
  {
    //Serial.println(inputString);
    if ( inputString == "close")
    {
      halt = true;
      digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
      //Serial.println("Critical stop due to alarm condition. Please, reset manually!");
      valveServo.write(0);
    }
    
    stringComplete = false;
    inputString = "";  
  }
  
  // Reading temperature or humidity takes about 250 milliseconds!
  h = dht.readHumidity();
  t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(t) || isnan(h)) 
  {
    //Serial.println("Failed to read from DHT");
  } 
  else
  {

    et = millis() - sampleTime;

    if ( et > SAMPLE_TIME && avgCount > 0)
    {
      avgTemp = (float)avgTemp/avgCount;

     Serial.print(tSetPoint);
     Serial.print(" ");
     Serial.print(avgTemp);

      sampleTime = millis();
      dt = (float)et/1000;

      error = tSetPoint - avgTemp;

      integralError = integralError + (float)error * dt;
      derivativeError = (float)(error - pError)/dt;

      pError = error;

      currentPos = VALVE_OFFSET + (int)(kp*error + ki * integralError + kd * derivativeError);
      currentPos = constrain(currentPos,0,180); 

      if (!halt)
      {
        valveServo.write(currentPos);
      }else{
        currentPos = 0;
      }
        
     Serial.print(" ");
     Serial.println(currentPos);

      avgTemp = 0;
      avgCount = 0;

    }else{
      avgTemp += t;
      avgCount++;
    }


    //prepare i2c message to master
    outputString = String("{\"t\":"+String(t)+", \"h\":"+String(h)+"}");
    
  }
}
