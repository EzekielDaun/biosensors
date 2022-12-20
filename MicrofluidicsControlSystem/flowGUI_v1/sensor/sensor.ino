#include "SerialTransfer.h"
#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 DAC1;
Adafruit_MCP4725 DAC2;

const int ADDRESS = 0x40; // Standard address for Liquid Flow Sensors

SerialTransfer pc;

struct RX {
  float chan1;
  float chan2;
} pressure;

struct TX {
  float chan1;
  float chan2;
} flow;


void setup()
{
//  pinMode(A2,OUTPUT);
//  pinMode(A3,OUTPUT); 
//  digitalWrite(A2,HIGH);
//  digitalWrite(A3,LOW);

  DAC1.begin(0x60);
  
  int ret;
    
  Serial.begin(115200);

  Wire.begin();       // join i2c bus

  do {
    delay(1000); // Error handling for example: wait a second, then try again

    // Soft reset the sensor
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xFE);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.println("Error while sending soft reset command, retrying...");
      continue;
    }
    delay(50); // wait long enough for reset

    // Switch to measurement mode
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xF1);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.println("Error during write measurement mode command");
    }
  } while (ret != 0);
  Serial.println("Starting");
  
  pc.begin(Serial);
}

int pressureCode = 0; // 12 bit code to control pressure sensor

void loop()
{
  if(pc.available())
  {
    pc.rxObj(pressure, 0);
    DAC1.setVoltage(pressure.chan1, false);

    int ret;
    uint16_t raw_sensor_value;
  
    Wire.requestFrom(ADDRESS, 2); // reading 2 bytes ignores the CRC byte
    if (Wire.available() < 2) {
      Serial.println("Error while reading flow measurement");
    } else {
      raw_sensor_value  = Wire.read() << 8; // read the MSB from the sensor
      raw_sensor_value |= Wire.read();      // read the LSB from the sensor
      flow.chan1 = (float) ((int16_t) raw_sensor_value) / 270;  
    }
    
    uint16_t sendSize = pc.txObj(flow, 0);
    pc.sendData(sendSize);
  }
}
