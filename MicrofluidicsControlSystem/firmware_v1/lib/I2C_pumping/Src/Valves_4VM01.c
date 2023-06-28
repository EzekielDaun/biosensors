/*
 * Valves_4VM01.c
 *
 *  Created on: Feb 28, 2018
 *      Author: Ed Yoshi Hirata
 */
#include <stdlib.h>
#include "main.h"
#include "stm32f3xx_hal.h"
#include "I2C_Control.h"
#include "Valves_4VM01.h"

/*
 * Pos_A=1
 * Pos_B=3
 * Closed=2
 */
void Valve_Position(I2C_HandleTypeDef *hi2c, uint8_t devAddr, uint8_t pos_valve1,
		uint8_t pos_valve2, uint8_t pos_valve3, uint8_t pos_valve4) {
	uint8_t tData[1];
	uint8_t rData[9] = { 0 };
	tData[0] = 0x07;
	if (pos_valve1 < 4 && pos_valve2 < 4 && pos_valve3 < 4 && pos_valve4 < 4) {
		tData[1] = ((pos_valve1 & 0x03) << 6) | ((pos_valve2 & 0x03) << 4)
				| ((pos_valve3 & 0x03) << 2) | (pos_valve4 & 0x03);
		SendToSlave(hi2c, devAddr, 2, tData);
		RecFromSlave(hi2c, devAddr, 2, 8, tData, &rData);
//		for (int i = 0; i < 8; i++) {
//			printf("------>%x\n", rData[i]);
//		}
	} else {
//		printf("INVALID Valve Input");
	}

}
