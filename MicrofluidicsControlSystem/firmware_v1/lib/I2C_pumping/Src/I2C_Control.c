/*
 * I2C_Control.c
 *
 *  Created on: Feb 27, 2018
 *      Author: Ed Yoshi Hirata
 */
#include <stdlib.h>
#include "main.h"
#include "stm32f3xx_hal.h"
#include "I2C_Control.h"

/*******************************************************************************
 * PRIVATE #DEFINES                                                            *
 ******************************************************************************/


//*************************************************************************************************
/**
 * @function
 * @param 	I2C address
 * @param	address- I2C slave address
 * @param	numBytesRec- Bytes Received
 * @param	pDataSend- ptr to data array
 * @return	HAL_I2C_Master->Slave Transmit
 * @brief  This function writes the I2C packet sequence
 * @note    Packet Sequence : Start sequence / Addr<<1 | 0 <Ack>/ NumBytesSend <Ack> / Command <Ack> /{optional data block
 *			Data1/<Ack>…DataN<Ack>}/Chksum<Ack>/ STOP */
uint8_t SendToSlave(I2C_HandleTypeDef *hi2c, uint8_t address, uint8_t numBytesSent, uint8_t *pDataSend) {
	uint8_t tData[128];
	if (numBytesSent > 125)
		return 'M';
	tData[0] = numBytesSent + 1;
	tData[numBytesSent + 1] = 0;
	tData[numBytesSent + 1] -= (address << 1);
	tData[numBytesSent + 1] -= tData[0];
	for (int i = 0; i < numBytesSent; i++) {
		tData[i + 1] = pDataSend[i];
		tData[numBytesSent + 1] -= tData[i + 1];
//		printf("tData: %x\n", tData[i + 1]);
	}
//	printf("checksum: %x\n", tData[numBytesSent + 1]);
	return HAL_I2C_Master_Transmit( hi2c, address << 1, tData, numBytesSent + 2, STD_TIMEOUT);
}

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

uint8_t RecFromSlave(I2C_HandleTypeDef *hi2c, uint8_t address, uint8_t numBytesSent, uint8_t numBytesRec,
		uint8_t * pDataSend, uint8_t * pDataRec) {
	if (SendToSlave(hi2c,address, numBytesSent, pDataSend) == 'M')
		return 0;
	return HAL_I2C_Master_Receive(hi2c, address << 1, pDataRec, numBytesRec, STD_TIMEOUT);
}
