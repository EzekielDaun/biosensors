%arduinosetup()
clear all;
close all;

% Arduino Setup
a = arduino('COM14','Nano33IoT','BaudRate',115200,'Libraries','I2C');

% I2C Devices
%addrs = scanI2CBus(a);
pressure_controller = device(a,"I2CAddress",0x60,'bitrate',100000);
flow_sensor = device(a,'I2CAddress',0x40,'bitrate',100000);

% Flow Sensor Reset
write(flow_sensor,0xFE,"uint8");
disp("Soft reset done");
pause(0.05);
write(flow_sensor,0xF1,'uint8');
disp("Starting");

outputcode = 0;

% Arduino Loop
while (1)
    code1 = bitshift(outputcode,-4);
    code2 = bitshift(bitand(outputcode,15),4);
    write(pressure_controller,[64 code1 code2],'uint8');

    flow_data = read(flow_sensor,2,'uint8');
    flow1 = bitshift((flow_data(1)), 8);
    flow2 = bitor(flow1,flow_data(2));
    if flow1 > 30000 
        flow = (65536-flow2)/270;
    else
        flow = (flow2)/270;
    end
    rawpressure = (readVoltage(a,'A6'))*(1023/3.3);

    %fprintf("FlowD1: %3d | FlowD2: %3d ", flow_data(1), flow_data(2));
    %fprintf("Flow1: %6d | Flow2: %6d ", flow1, flow2);
    %pressure = sgolayfilt(rawpressure,3,11);

    fprintf("PressureCode: %d | Flow: %.2f | Pressure: %.2f\n", outputcode, flow, rawpressure);
end

