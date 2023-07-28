/*
 * pump.c
 *
 *  Created on: Feb 24, 2018
 *      Author: Ed Yoshi Hirata
 */
#include <stdlib.h>
#include "main.h"
#include "stm32f3xx_hal.h"
#include "I2C_Control.h"
#include "SPS01_control.h"

static uint16_t m_position;
static uint16_t pos_volume;
static uint16_t init_syringe;
static uint16_t end_syringe;
static uint8_t status;
/**
 * @brief  This function Sets the Flowrate of SPS01 Pumps
 * @note   The data block for the SetPeriod command is a 24-bit number proportional to the time delay between
 microsteps.
 * @param  dRate - flow rate in ul/min
 * @retval
 */
void SPS01_Init(I2C_HandleTypeDef *hi2c, uint8_t devAddr) {
//	printf("\nGET CAL\n");
	uint8_t tData[1];
	uint8_t rData[9] = { 0 };
	tData[0] = 0x14; // get Status 1 byte for status, 2 byte for measured position, 2 byte for moto micropulse count
	SendToSlave(hi2c, devAddr, 2, tData);
//	HAL_Delay(1000);
	RecFromSlave(hi2c, devAddr, 2, 8, tData, &rData);
//	for (int i = 0; i < 8; i++) {
//		printf("------>%x\n", rData[i]);
//	}
	end_syringe = rData[2] | (rData[3] << 8);
	init_syringe = rData[4] | (rData[5] << 8);
//	printf("Syringe Max= %d  MIN=%d\n", end_syringe, init_syringe);
}

void SPS01_Status(I2C_HandleTypeDef *hi2c, uint8_t devAddr) {
//	printf("\nGET STATUS\n");
	uint8_t tData[1];
	uint8_t rData[9] = { 0 };
	tData[0] = 0x1A; // get Status 1 byte for status, 2 byte for measured position, 2 byte for moto micropulse count
	SendToSlave(hi2c, devAddr, 1, tData);
//	HAL_Delay(1000);
	RecFromSlave(hi2c, devAddr, 1, 8, tData, &rData);
//	for (int i = 0; i < 8; i++) {
//		printf("------>%x\n", rData[i]);
//	}
	status = rData[2];
	m_position = rData[3] | rData[4] << 8;
	pos_volume = (0.7853975 / encoderRange) * diameter_80ul * diameter_80ul * stroke_length
			* (m_position - end_syringe); //volume from pos calc
//	printf("STATUS=%x\n",status);
//	printf("Pos= %d, Volume= %d \n", m_position, pos_volume);
//	HAL_Delay(1000);
}

void SPS01_DEV_NAME(I2C_HandleTypeDef *hi2c, uint8_t devAddr) {
	uint8_t tData[1];
	uint8_t rData[9] = { 0 };
	tData[0] = 0x0B;
	SendToSlave(hi2c, devAddr, 1, tData);
	RecFromSlave(hi2c, devAddr, 1, 7, tData, &rData);
//	for (int i = 0; i < 8; i++) {
//		printf("------>%x\n", rData[i]);
//	}
}

void SPS01_SetSpeed(I2C_HandleTypeDef *hi2c, uint8_t devAddr, double flow_rate) {
//	printf("\nSET SPEED 300\n");
	uint8_t tData[5];
	uint8_t rData[9] = { 0 };
	double cSpeed = (ACTUATION_DIST * CLOCK_FREQ * 0.04908738521234);
	int nPeriod = (cSpeed * diameter_80ul * diameter_80ul / flow_rate + 0.5);
	//			if(nPeriod<MAX_PERIOD){
	//				nPeriod=MIN_PERIOD;
	//			}
	if (nPeriod > 0xFFFFFF) {
		nPeriod = 0xFFFFFF;
	}
//	printf("period:%x Speed:%x\n", nPeriod, cSpeed);
	tData[0] = 0x07;
	tData[1] = nPeriod & 0xFF;
	tData[2] = (nPeriod >> 8) & 0xFF;
	tData[3] = (nPeriod >> 16) & 0xFF;
	SendToSlave(hi2c, devAddr, 4, tData);
	RecFromSlave(hi2c, devAddr, 1, 8, tData, &rData);
//	for (int i = 0; i < 8; i++) {
//		printf("------>%x\n", rData[i]);
//	}
}

void SPS01_SetVolume(I2C_HandleTypeDef *hi2c, uint8_t devAddr, int chosen_volume) {
	uint8_t tData[5];
	uint8_t rData[9] = { 0 };
//	printf("\nSET VOLUME %d\n", chosen_volume);
	int move2pos = ((encoderRange * 1.27324062) * chosen_volume
			/ (diameter_80ul * diameter_80ul * stroke_length) + 0.5) + end_syringe;
//	printf("Position moved %x\n", move2pos);
	tData[0] = 0x08;
	tData[1] = (uint8_t) (move2pos & 0xFF);
	tData[2] = (uint8_t) ((move2pos >> 8) & 0xFF);
	SendToSlave(hi2c, devAddr, 4, tData);
	RecFromSlave(hi2c, devAddr, 4, 8, tData, &rData);
//	for (int i = 0; i < 8; i++) {
//		printf("------>%x\n", rData[i]);
//	}
	SPS01_Status(hi2c, devAddr);
	while (status == (SPS_RUNNING|SPS_MOVING_IN) || status == (SPS_RUNNING|SPS_MOVING_OUT)||status==(SPS_STARTING_MOTION|SPS_MOVING_IN)||status==(SPS_STARTING_MOTION|SPS_MOVING_OUT)) {
		SPS01_Status(hi2c, devAddr);
	}

}
