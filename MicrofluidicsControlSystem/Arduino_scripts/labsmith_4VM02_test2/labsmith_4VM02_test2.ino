#include <Wire.h>
#include "SerialTransfer.h"

#define LS_4VM02_ADDR 0x6A // Labsmith 4VM02 I2C Address 41 60 70 6A 7E
#define CV_SETVALVES 0x07 // Set Valve Command

uint8_t checksum;

void StartXmit(uint8_t addr) //should return an error int?
{
       checksum = -addr;
}

void Xmit(uint8_t tbyte) //should return an error int?
{
       Wire.write(tbyte);
       checksum -= tbyte;
}

int EndXmit()
{
       Wire.write(checksum);
       return Wire.endTransmission();
}

void setup()
{
    
    Serial.begin(9600);
    Serial.println("Hello!");
    Wire.begin();
}

// Settings for AV801
// For position Y; we send 0xY3
// VXSet starts with V4 and finishes with V1

int SetValveSelect8881()
{
       StartXmit(LS_4VM02_ADDR);  //address<<1. Initialize checksum. You might want to check that the addressed device acked
//and if not, call wire.EndTransmission() and return an error code
       Xmit(0x06);  //Count       
       Xmit(CV_SETVALVES);   // Command 
       Xmit(0x83); //V4Set - Position 8 You may want to check that each byte of the packet was acked.
       Xmit(0x83); //V3Set - Position 8
       Xmit(0x83); //V2Set - Position 8
       Xmit(0x13); //V1Set - Position 1
       return EndXmit(); //send checksum and I2C stop.
}

void loop()
{
    int ret;
    ret = SetValveSelect8881();
    if (ret != 0) {
      Serial.println("Error during write measurement mode command");
    } else {
    delay(1000);
    }
}
