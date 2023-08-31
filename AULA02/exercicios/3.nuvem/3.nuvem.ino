/*************************************************************
  This is a simple demo of sending and receiving some data.
  Be sure to check out other examples!
 *************************************************************/
// Template ID, Device Name and Auth Token are provided by the Blynk.Cloud
// See the Device Info tab, or Template settings
#define BLYNK_TEMPLATE_ID           "TMPLxxxxxx"
#define BLYNK_DEVICE_NAME           "Device"
#define BLYNK_AUTH_TOKEN            "YourAuthToken"

// Comment this out to disable prints and save space
#define BLYNK_PRINT Serial

#include <SPI.h>
#include <Ethernet.h>
#include <BlynkSimpleEthernet.h>

char auth[] = BLYNK_AUTH_TOKEN;

#define W5100_CS  10
#define SDCARD_CS 4

//STATIC IP
// Mac address should be different for each device in your LAN
//byte arduino_mac[] = { 0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xED };
//IPAddress arduino_ip ( 10,   0,   0,  20);
//IPAddress dns_ip     (  8,   8,   8,   8);
//IPAddress gateway_ip ( 10,   0,   0,   1);
//IPAddress subnet_mask(255, 255, 255,   0);

BlynkTimer timer;

// This function is called every time the Virtual Pin 0 state changes
BLYNK_WRITE(V0)
{
  // Set incoming value from pin V0 to a variable
  int value = param.asInt();

  Serial.println(value);

  // Update state
  Blynk.virtualWrite(V1, value);
}

// This function is called every time the device is connected to the Blynk.Cloud
BLYNK_CONNECTED()
{
  // Change Web Link Button message to "Congratulations!"
  Blynk.setProperty(V3, "offImageUrl", "https://static-image.nyc3.cdn.digitaloceanspaces.com/general/fte/congratulations.png");
  Blynk.setProperty(V3, "onImageUrl",  "https://static-image.nyc3.cdn.digitaloceanspaces.com/general/fte/congratulations_pressed.png");
  Blynk.setProperty(V3, "url", "https://docs.blynk.io/en/getting-started/what-do-i-need-to-blynk/how-quickstart-device-was-made");
}

// This function sends Arduino's uptime every second to Virtual Pin 2.
void myTimerEvent()
{
  // You can send any value at any time.
  // Please don't send more that 10 values per second.
  Blynk.virtualWrite(V2, millis() / 1000);
}

void setup()
{
  // Debug console
  Serial.begin(115200);

  pinMode(SDCARD_CS, OUTPUT);
  digitalWrite(SDCARD_CS, HIGH); // Deselect the SD card

  Blynk.begin(auth);
  // You can also specify static IP:
  //Blynk.begin(BLYNK_AUTH_TOKEN, "blynk.cloud", 80, arduino_ip, dns_ip, gateway_ip, subnet_mask, arduino_mac);
  //or
  //Blynk.begin(BLYNK_AUTH_TOKEN, "cloud.blynk.cc", 8443, arduino_ip, dns_ip, gateway_ip, subnet_mask, arduino_mac);

  // Setup a function to be called every second
  timer.setInterval(1000L, myTimerEvent);

}

void loop()
{
  Blynk.run();
  timer.run();
  // You can inject your own code or combine it with other sketches.
  // Check other examples on how to communicate with Blynk. Remember
  // to avoid delay() function!
}
