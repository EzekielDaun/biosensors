/*
 * Valves_4VM01.h
 *
 *  Created on: Feb 28, 2018
 *      Author: Ed Yoshi Hirata
 */

#ifndef VALVES_4VM01_H_
#define VALVES_4VM01_H_

void Valve_Position(I2C_HandleTypeDef *hi2c, uint8_t devAddr, uint8_t pos_valve1,
		uint8_t pos_valve2, uint8_t pos_valve3, uint8_t pos_valve4);

#endif /* VALVES_4VM01_H_ */
