# Microfluidics control system for EvalBox // ESP32 code

Code for the microcontroller-side of the microfluidics control system.

## Install

If you have PlatformIO already, all you need to do is import the project, plug in your ESP32 and hit Upload. If not, you can obtain it [here](https://platformio.org/platformio-ide).


## Customizing the code to your hardware setup

The hardware is modular, and different valves, pumps and pressure regulators can be used. The main things you may need to specify is which valves are normally-open and which are normally-closed, as well as what types of pressure regulators are connected and where.


