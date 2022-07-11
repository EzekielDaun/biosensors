close all;
clear;
clc;


%Add as many files as needed: in this case two file names have been
%allocated. The longer the experiment, the more log files generated. 
filename1= ".csv"; 
filename2= ".csv"; 
T1 = readtable(filename1); 
T2= readtable(filename2);

%Channel 1: 
%Channel 2:

T_all= [T1; T2];

T= cell2mat(T_all.Time);
numH=0;
Time=1:2:2*length(T);
Time=Time/60;

figure(1)
t=tiledlayout(3,2)

nexttile
plot(Time,T_all.FlowEZ_1_13109_Q)
title('Set Fluigent Channel 1 Flow Rate (uL/min)')

nexttile
plot(Time,T_all.FlowEZ_2_13110_Q)
title('Set Fluigent Channel 2 Flow Rate (uL/min)')

nexttile
plot(Time,T_all.FlowEZ_1_13109_)
title('Fluigent Channel 1 Pressure (mBar)')

nexttile
plot(Time,T_all.FlowEZ_2_13110_)
title('Fluigent Channel 2 Pressure (mBar)')

nexttile
plot(Time,T_all.M_Switch_1_SwitchEZ_3_10535__)
title('Fluigent Channel 1 Reservoir')

nexttile
plot(Time,T_all.M_Switch_4_SwitchEZ_3_10535__)
title('Fluigent Channel 2 Reservoir')

sgtitle('Fluigent Log Analysis','FontSize', 20)
xlabel(t,'Time (hrs)','FontSize', 14)

figure(2)
t=tiledlayout(1,2)

nexttile
plot(Time,T_all.FlowEZ_1_13109_Q)
title('Set Fluigent Channel 1 Flow Rate (uL/min)')

nexttile
plot(Time,T_all.FlowEZ_2_13110_Q)
title('Set Fluigent Channel 2 Flow Rate (uL/min)')

xlabel(t,'Time (hrs)','FontSize', 14)

flow1= smoothdata(T_all.FlowEZ_1_13109_Q);
flow2= smoothdata(T_all.FlowEZ_2_13110_Q);

figure(3)
t=tiledlayout(1,2)

nexttile
plot(Time,flow1)
title(' Smoothened Set Fluigent Channel 1 Flow Rate (uL/min)')

nexttile
plot(Time,flow2)
title('Smoothened Set Fluigent Channel 2 Flow Rate (uL/min)')

xlabel(t,'Time (hrs)','FontSize', 14)






