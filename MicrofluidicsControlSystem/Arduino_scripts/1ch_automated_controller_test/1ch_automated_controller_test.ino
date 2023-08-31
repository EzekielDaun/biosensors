#include <Wire.h>
#include <Adafruit_MCP4725.h>
#include "ArduPID.h"

ArduPID myController;

// -----------------------------------------------------------------------------
// PID Settings
// -----------------------------------------------------------------------------

double input;
double output;

// Arbitrary setpoint and gains - adjust these as fit for your project:
double setpoint = 0;
double p = 7;
double i = 1;
double d = 0.1;

// -----------------------------------------------------------------------------
// Sensor specific settings, adjust if needed:
// -----------------------------------------------------------------------------

const int ADDRESS = 0x40; // Sensor I2C Address (this is the default address)
const float SCALE_FACTOR_FLOW = 270.0; // Scale Factor for flow rate measurement
const float SCALE_FACTOR_TEMP = 200.0; // Scale Factor for temperature measurement
const char *UNIT_FLOW = " ul/min"; //physical unit of the flow rate measurement
const char *UNIT_TEMP = " deg C"; //physical unit of the temperature measurement

#define MCP4725_ADDR 0x60
int output_code = 0; // 12 bit DAC code to control pressure sensor - //4095
int sensorValue = 0;

void setup()
{
  int ret;

  Wire.begin();
  Serial.begin(115200);
  Serial.println("Starting");
  Serial.println("Hello!");
  do {
    // Soft reset the sensor
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xFE);
    ret = Wire.endTransmission();
    Serial.println("Soft resetting the sensor");
    if (ret != 0) {
      Serial.println("Error while sending soft reset command, retrying...");
      delay(500); // wait long enough for chip reset to complete
    }
  } while (ret != 0);
  Serial.println("Soft reset done");
  delay(50); // wait long enough for chip reset to complete

  myController.begin(&input, &output, &setpoint, p, i, d);

  // myController.reverse()               // Uncomment if controller output is "reversed"
  // myController.setSampleTime(10);      // OPTIONAL - will ensure at least 10ms have past between successful compute() calls
  myController.setOutputLimits(0, 511);
  myController.setBias(511.0 / 2.0);
  myController.setWindUpLimits(-10, 10); // Groth bounds for the integral term to prevent integral wind-up
  
  myController.start();
  // myController.reset();               // Used for resetting the I and D terms - only use this if you know what you're doing
  // myController.stop();                // Turn off the PID controller (compute() will not do anything until start() is called)
}

void loop()
{
  int ret;
  uint16_t sensor_flow_value;
  int16_t signed_flow_value;
  float scaled_flow_value;

  // To perform a measurement, first send 0xF1 to switch to continuous
  // measurement mode (H20 calibration), then read 3x (2 bytes + 1 CRC byte) from the sensor.
  // To perform a IPA based measurement, send 0x__ instead.
  // Check datasheet for available measurement commands.
  Wire.beginTransmission(ADDRESS);
  Wire.write(0xF1);
  ret = Wire.endTransmission();
  if (ret != 0) {
    Serial.println("Error during write measurement mode command");
  } 
  else {
    uint8_t bytesReceived = Wire.requestFrom(ADDRESS, 2);
    if (Wire.available() < 2) {
      Serial.println("Error while reading flow measurement");
    }
    sensor_flow_value  = Wire.read() << 8; // read the MSB from the sensor
    sensor_flow_value |= Wire.read();      // read the LSB from the sensor
    
    Serial.print("Flow value from Sensor: ");
    Serial.print(sensor_flow_value);

    signed_flow_value = (int16_t) sensor_flow_value;
    Serial.print(", signed value: ");
    Serial.print(signed_flow_value);

    //scaled_signed_flow_value = ((float) signed_flow_value) / SCALE_FACTOR_FLOW;
    scaled_flow_value = -((float) signed_flow_value) / SCALE_FACTOR_FLOW;
    Serial.print(", scaled value: ");
    Serial.print(scaled_flow_value);
    Serial.print(UNIT_FLOW);

    Serial.println("");
    // To stop the continuous measurement, first send 0x3F.
    //Wire.beginTransmission(ADDRESS);
    //Wire.write(0x3F);

    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.println("Error during write measurement mode command");
    }
  }
  input = scaled_flow_value; // sensor feedback

  myController.compute();
  myController.debug(&Serial, "myController", PRINT_INPUT    | // Can include or comment out any of these terms to print
                                              PRINT_OUTPUT   | // in the Serial plotter
                                              PRINT_SETPOINT |
                                              PRINT_BIAS     |
                                              PRINT_P        |
                                              PRINT_I        |
                                              PRINT_D);

  while(Serial.available()>0){
  String myString = Serial.readString(); // Read as String
  setpoint = (myString.toInt());   // Convert it to float
  }
  double temp = setpoint;
  Serial.print("Set point: ");
  Serial.print(temp/2.083); //show the character on Serial Monitor
  Serial.print(UNIT_FLOW);
  Serial.println("");

  output_code = output;
  Wire.beginTransmission(MCP4725_ADDR);
  Wire.write(64);                     // cmd to update the DAC
  Wire.write(output_code >> 4);        // the 8 most significant bits...
  Wire.write((output_code & 15) << 4); // the 4 least significant bits...
  Wire.endTransmission();

  Serial.print("Pressure Reg Code: ");
  Serial.print(output_code); //show the character on Serial Monitor
  Serial.println("");

  sensorValue = analogRead(A6);
  Serial.print("Pressure Sensor: ");
  Serial.print(sensorValue); //show the character on Serial Monitor
  Serial.println("");

  Serial.println("=============================================================================");
  //delay(500); // milliseconds delay between reads (for demo purposes)
}
