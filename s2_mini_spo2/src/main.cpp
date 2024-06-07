// for lolin
// SCL -> pin 35
// sda -> pin 33

#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "MAX30100_PulseOximeter.h"

char ssid[] = "Your SSID";
const char password[] = "Your Password";
const char * udpAddress = "Your PC IP";
const uint16_t multicast_port = 12345;

WiFiUDP udp;
MAX30100 sensor;


//Read the documantation
//configure sensor
void configureMax30100() {
  sensor.setMode(MAX30100_MODE_SPO2_HR);
  sensor.setLedsCurrent(MAX30100_LED_CURR_20_8MA, MAX30100_LED_CURR_20_8MA);
  sensor.setLedsPulseWidth(MAX30100_SPC_PW_400US_14BITS);
  sensor.setSamplingRate(MAX30100_SAMPRATE_100HZ);
  sensor.setHighresModeEnabled(true);
}


void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  //initialize wifi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi!");
  Serial.println();
  Serial.print("IP Address (AP): ");
  Serial.println(WiFi.localIP());
  delay(500);

  //initialize sensor
  if (!sensor.begin()) {
        Serial.println("FAILED");
        for(;;);
    } else {
        Serial.println("SUCCESS");
    }
    
  configureMax30100();
  
}

void loop()
{
  digitalWrite(LED_BUILTIN, HIGH);

  uint16_t ir, red;
  sensor.update();

  if (sensor.getRawValues(&ir, &red)) {
    char packetBuffer[60];
    snprintf(packetBuffer, sizeof(packetBuffer), "%d,%d", red, ir);

    // Send sensor data via UDP multicast
    udp.beginPacket(udpAddress, multicast_port);
    udp.print(packetBuffer);
    udp.endPacket();  
    Serial.println(packetBuffer);
    }
}