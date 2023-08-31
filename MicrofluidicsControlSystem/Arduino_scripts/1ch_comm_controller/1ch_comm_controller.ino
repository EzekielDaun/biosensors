#include "SerialTransfer.h"
#include <Wire.h>
#include <Adafruit_MCP4725.h>

// -----------------------------------------------------------------------------
// Objects
// -----------------------------------------------------------------------------

Adafruit_MCP4725 DAC1;
Adafruit_MCP4725 DAC2;

SerialTransfer pc;

// -----------------------------------------------------------------------------
// Sensor specific settings, adjust if needed:
// -----------------------------------------------------------------------------

const float SIGNED_SCALE_FACTOR_FLOW = 270.0; // Scale Factor for flow rate measurement
const float SCALE_FACTOR_TEMP = 200.0; // Scale Factor for temperature measurement
const float SCALE_FACTOR_PRESSURE = 150.0; // Scale Factor for temperature measurement
#define SLI0430_ADDR 0x40
#define MCP4725_ADDR1 0x60
#define MCP4725_ADDR2 0x61

// -----------------------------------------------------------------------------
// Data Structures
// -----------------------------------------------------------------------------

int outputCode = 0; // 12 bit DAC code to control pressure sensor - //4095
int sensorValue = 0;

struct RX {
  int pressureCode1;
  int pressureCode2;
} pressureCodes;

struct TX {
  float flowchan1;
  int pressuresensor1;
  float flowchan2;
  int pressuresensor2;
} sensors;

void setup()
{
  int ret;
  
  // Begin the communication protocols
  Wire.begin();       // join i2c bus - 100kHz
  Serial.begin(115200);
  //DAC1.begin(MCP4725_ADDR1);
  //DAC2.begin(MCP4725_ADDR2);

  do {
    delay(1000); // Error handling for example: wait a second, then try again

    // Soft reset the sensor
    Wire.beginTransmission(SLI0430_ADDR);
    Wire.write(0xFE);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.println("Error while sending soft reset command, retrying...");
      continue;
    }
    Serial.println("Soft reset done");
    delay(50); // wait long enough for reset to complete

    // Switch to measurement mode
    Wire.beginTransmission(SLI0430_ADDR);
    Wire.write(0xF1);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.println("Error during write measurement mode command");
    }
  } while (ret != 0);
  Serial.println("Starting");
  
  pc.begin(Serial);
}

void loop()
{
  int ret;
  uint16_t raw_sensor_value;
  // use this variable to keep track of how many bytes we're stuffing in the transmit buffer
  uint16_t sendSize = 0;

  while(pc.available()>0)
  {
    // use this variable to keep track of how many bytes we've processed from the receive buffer
    uint16_t recSize = 0;
    recSize = pc.rxObj(pressureCodes, 0);
    //DAC1.setVoltage(pressureCodes.pressureCode1, false);
    //DAC2.setVoltage(pressureCodes.pressureCode2, false);
    //String myString = pressureCodes.pressureCode1; // Read as String
    //outputCode = myString.toInt();   // Convert it to float
    outputCode = (int) pressureCodes.pressureCode1;
    Wire.beginTransmission(MCP4725_ADDR1);
    Wire.write(64);                     // cmd to update the DAC
    Wire.write(outputCode >> 4);        // the 8 most significant bits...
    Wire.write((outputCode & 15) << 4); // the 4 least significant bits...
    Wire.endTransmission();

    // To perform a measurement, first send 0xF1 to switch to continuous
    // measurement mode (H20 calibration), then read 3x (2 bytes + 1 CRC byte) from the sensor.
    // To perform a IPA based measurement, send 0x__ instead.
    // Check datasheet for available measurement commands.
    Wire.requestFrom(SLI0430_ADDR, 2); // reading 2 bytes ignores the CRC byte
    if (Wire.available() < 2) {
      Serial.println("Error while reading flow measurement");
    } else {
      raw_sensor_value  = Wire.read() << 8; // read the MSB from the sensor
      raw_sensor_value |= Wire.read();      // read the LSB from the sensor
      sensors.flowchan1 = -(float) ((int16_t) raw_sensor_value) / SIGNED_SCALE_FACTOR_FLOW;  
    }
    
    sensorValue = analogRead(A6);
    sensors.pressuresensor1 = (int) (sensorValue);

    ///////////////////////////////////////// Stuff buffer with struct
    sendSize = pc.txObj(sensors, 0);
    ///////////////////////////////////////// Send buffer
    pc.sendData(sendSize);
  }
  // Serial.println("");
  // Serial.print("Pressure Reg Code: ");
  // Serial.print(outputCode); //show the character on Serial Monitor
  // Serial.println("");
  // Serial.print("Pressure Sensor: ");
  // Serial.print(sensorValue); //show the character on Serial Monitor
  // Serial.println("");
}
