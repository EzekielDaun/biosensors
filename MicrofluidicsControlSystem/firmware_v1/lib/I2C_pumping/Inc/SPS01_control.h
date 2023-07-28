/*
 * pump.h
 *
 *  Created on: Feb 24, 2018
 *      Author: Ed Yoshi Hirata
 */

#ifndef SPS01_CONTROL_H_
#define SPS01_CONTROl_H_

#define ACTUATION_DIST 0.2 //mm per step
#define CLOCK_FREQ 4000000/16*44.59
//#define CLOCK_FREQ 41943040/16*44.59
#define MAX_PERIOD 65536
#define MIN_PERIOD 108
#define diameter_80ul 3.256
#define stroke_length  13.0	//mm
#define encoderRange  65536
/*STATUS */
#define SPS_MOVING_IN 0x01
#define SPS_MOVING_OUT 0x02
#define SPS_RUNNING 0x04
#define SPS_STALLED 0x08
#define SPS_FULLSPEED 0x10
#define SPS_STARTING_MOTION 0x40

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
void SPS01_Init(I2C_HandleTypeDef *hi2c, uint8_t devAddr);
void SPS01_Status(I2C_HandleTypeDef *hi2c, uint8_t devAddr);
void SPS01_DEV_NAME(I2C_HandleTypeDef *hi2c, uint8_t devAddr);
void SPS01_SetSpeed(I2C_HandleTypeDef *hi2c, uint8_t devAddr, double flow_rate);
void SPS01_SetVolume(I2C_HandleTypeDef *hi2c, uint8_t devAddr, int chosen_volume);

#endif /* SPS01__CONTROL_H_ */
