#include <Wire.h>
#include <Adafruit_MCP4725.h>

#define MCP4725_ADDR 0x60
int output_code = 0; // 12 bit DAC code to control pressure sensor - //4095
int sensorValue = 0;

void setup()
{
    Wire.begin();
    Serial.begin(9600);
    Serial.println("Starting");
    Serial.println("Hello!");

    // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
    // For MCP4725A0 the address is 0x60 or 0x61
    // For MCP4725A2 the address is 0x64 or 0x65 
    // Serial.println("Generating a triangle wave");
}

void loop()
{
    if (Serial.available()) //at least one data item is in the buffer/array
    {
    output_code = Serial.read(); //read 8-bit ASCII code of character from the 16-bit item of buffer
    }
    Wire.beginTransmission(MCP4725_ADDR);
    Wire.write(64);                     // cmd to update the DAC
    Wire.write(output_code >> 4);        // the 8 most significant bits...
    Wire.write((output_code & 15) << 4); // the 4 least significant bits...
    Wire.endTransmission();
    Serial.println((char)output_code); //show the character on Serial Monitor
}
