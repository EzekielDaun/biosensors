%arduinosetup()
clear all;
close all;

% User Defined Properties 
plotTitle = 'Microfluidic Control System Data Log';  % plot title
xLabel = 'Elapsed Time (s)';     % x-axis label
yLabel = 'Sensor Data';      % y-axis label
legend1 = 'Pressure Code';
legend2 = 'Flow Sensor';
legend3 = 'Pressure Sensor';
plotGrid = 'on';                 % 'off' to turn off grid
yMin  = 0;                       %y minimum Value
yMax  = 220;                      %y Maximum Value
delay = .01;                     % make sure sample faster than resolution 

%Define Function Variables
time = 0;
data = 0;
data1 = 0;
data2 = 0;
count = 0;

%Set up Plot
figure;
subplot(3,1,1);
plotGraph = plot(time,data,'-r',LineWidth=2); 
title(plotTitle,'FontSize',11);
legend(legend1)
axis([yMin yMax 0 800]);
grid(plotGrid);
subplot(3,1,2);
plotGraph1 = plot(time,data1,'-b',LineWidth=2);
ylabel(yLabel,'FontSize',11);
legend(legend2)
axis([yMin yMax 0 90]);
grid(plotGrid);
subplot(3,1,3);
plotGraph2 = plot(time,data2,'-k',LineWidth=2);
xlabel(xLabel,'FontSize',11);
legend(legend3)
axis([yMin yMax 0 400]);
grid(plotGrid);

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
outputcode2 = 0;
flag1 = 0;
flag2 = 1;

tic
% Arduino Loop
while (1)
    count = count + 1;
    if (mod(round(toc,0),20)==0)&&(flag1==1)
        outputcode = 0;
        flag2 = 1;
        flag1 = 0;
        if (mod(round(toc,0),10)==0)
            flag1 = 1;
        end
    elseif (mod(round(toc,0),10)==0)&&(flag2==1)
        outputcode2 = outputcode2 + 50;
        if outputcode2 > 800
            outputcode2 = 800;
        end
        outputcode = outputcode2;
        flag2 = 0;
        flag1 = 1;
    end

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

    %fprintf("PressureCode: %d | Flow: %.2f | Pressure: %.2f\n", outputcode, flow, rawpressure);
    
    dat = outputcode;
    dat1 = flow;
    dat2 = rawpressure;

    time(count) = toc;
    data(count) = dat(1);         
    data1(count) = dat1(1);
    data2(count) = dat2(1);

    set(plotGraph,'XData',time,'YData',data);
    set(plotGraph1,'XData',time,'YData',data1);
    set(plotGraph2,'XData',time,'YData',data2);

    if toc>220
        code1 = bitshift(0,-4);
        code2 = bitshift(bitand(0,15),4);
        write(pressure_controller,[64 code1 code2],'uint8');
        break
    end
end
