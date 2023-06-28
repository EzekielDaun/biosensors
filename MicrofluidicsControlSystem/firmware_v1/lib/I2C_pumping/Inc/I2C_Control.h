/*
 * I2C_Control.h
 *
 *  Created on: Feb 27, 2018
 *      Author: Ed Yoshi Hirata
 */

#ifndef I2C_CONTROL_H_
#define I2C_CONTROL_H_

/* Commands to control the uDevices through I2C */

//*****************Universal*****************************
#define CB_GETDATABLOCK = 0x00;
#define CB_PING = 0x01;
#define CB_SETDEVADDR = 0x02;
#define DEV_ID_COMMAND = 0x03;	//return (2 byte firmware, 2 byte bootloder version, 2 byte hardware version)
#define CB_RESET = 0x05;
#define CB_STOP = 0x06;
#define CB_SETNAME = 0x0A;		//arg (16 char "name")
#define CB_GETNAME = 0x0B;		//return (16 char "name")
#define CS_SETPOWER = 0x0D;
#define CB_GETCAL = 0x14;		//return (device dependent)
#define CB_GETSTATUS = 0x1A; 	//return (device dependent)

//****************SPS01 Valves****************************
#define CS_SETPERIOD = 0x07;	//arg ( 3 bytes period)
#define CS_MOVETOPOS = 0x08;	//arg (2 byte position)
#define CS_GETMODE = 0x09;
#define CS_SETDIAMETER = 0X15;	//arg(2 byte unsigned int)
#define CS_GETDIAMETER = 0x16;	//arg(2 byte unsigned int)
#define CS_MOVEPERCHANNEL = 0x1C;
//********************4PM01********************************
#define CV_SETVALVES = 0x07;	//Packed target position

//********************I2C**********************************
#define STD_TIMEOUT 1000

/**
 * @function
 * @param	I2C address
 * @param	address- I2C slave address
 * @param	numBytesRec- Bytes Received
 * @param	pDataSend- ptr to data array
 * @return	HAL_I2C_Master->Slave Transmit
 * @brief  	This function writes the I2C packet sequence
 * @note    Packet Sequence : Start sequence / Addr<<1 | 0 <Ack>/ NumBytesSend <Ack> / Command <Ack> /{optional data block
 *			Data1/<Ack>…DataN<Ack>}/Chksum<Ack>/ STOP */

uint8_t SendToSlave(I2C_HandleTypeDef *hi2c,uint8_t address, uint8_t numBytesRec, uint8_t *pDataSend);

/**
 * @function
 * @param	I2C address
 * @param	address- I2C slave address
 * @param	numBytesSent - Total Bytes Sent
 * @param 	numBytesRec	-	Total Bytes to be Received
 * @param	pDataSend- ptr to data to send buffer
 * @param	pDataRec -ptr data to receive buffer
 * @return	HAL_I2C_Master->Slave Receive
 * @brief  	This function writes the I2C packet sequence
 * @note    Packet Sequence : START/ Addr<<1 | 1 <Ack>/ Packet Complete (0xAA or 0xEE) <MAck> / NumReadBytes <MAck> /{data block
 Data1/<MAck>…DataN<MAck>}/Chksum<MAck>/ STOP */

uint8_t RecFromSlave(I2C_HandleTypeDef *hi2c,uint8_t address, uint8_t numBytesSent, uint8_t numBytesRec,
		uint8_t * pDataSend, uint8_t * pDataRec);

#endif /* I2C_CONTROL_H_ */
