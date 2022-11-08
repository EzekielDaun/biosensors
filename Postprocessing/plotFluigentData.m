%*************************************************************************%
%**                                                                     **%
%**                   Plotting the Resonance Shifts                     **%
%**                                                                     **%
%**                             2021-10-30                              **%
%**                         Mohammed Al-Qadasi                          **%
%**                                                                     **%
%*************************************************************************%
% This script prompts the user to select the Fluigent log files, then plots
% the flow rates, pressure and switch positions. The user will also be
% prompt to select "Reservoir Solutions.csv" file if exists to map the
% reservoir contents to some concentration values. The file needs to have
% the following format: 
%Reservoir	Solution _ Switch1	Concentration _ Switch 1	Solution _ Switch2	Concentration _ Switch 2	Unit
%1	NaCl	0	NaCl	0	mM
%2	NaCl	0	NaCl	0	mM
%3	NaCl	10	NaCl	10	mM
%4	NaCl	20	NaCl	20	mM
%5	NaCl	30	NaCl	30	mM
%6	NaCl	60	NaCl	60	mM
%7	NaCl	125	NaCl	125	mM
%8	NaCl	250	NaCl	250	mM
%9	NaCl	375	NaCl	375	mM
%10	NaCl	0	NaCl	0	mM


clear all
close all
clc
set(0,'DefaultFigureWindowStyle','docked')
warning('off','all');

time_axis_format  = 1; %0: absolute, 1:mins
plot_switch1_data = 1; 
plot_switch2_data = 1;
overlay_plots     = 1;
save_plots        = 1;
outputPath        = ""; % '.': Same as Fluigent log path

% Reservoir Concentrations, {Concentration,Unit,Solvent}
Switch1_Res1 = {'0', 'mM', 'NaCl'}; 
Switch1_Res2 = {'0', 'mM', 'NaCl'}; 
Switch1_Res3 = {'62.5', 'mM', 'NaCl'}; 
Switch1_Res4 = {'125', 'mM', 'NaCl'}; 
Switch1_Res5 = {'250', 'mM', 'NaCl'}; 
Switch1_Res6 = {'375', 'mM', 'NaCl'}; 
Switch1_Res7 = {'125', 'mM', 'NaCl'}; 
Switch1_Res8 = {'0', 'mM', 'NaCl'}; 
Switch1_Res9 = {'0', 'mM', 'NaCl'}; 

Switch2_Res1 = {'0', 'mM', 'NaCl'}; 
Switch2_Res2 = {'0', 'mM', 'NaCl'}; 
Switch2_Res3 = {'62.5', 'mM', 'NaCl'}; 
Switch2_Res4 = {'125', 'mM', 'NaCl'}; 
Switch2_Res5 = {'250', 'mM', 'NaCl'}; 
Switch2_Res6 = {'375', 'mM', 'NaCl'}; 
Switch2_Res7 = {'125', 'mM', 'NaCl'}; 
Switch2_Res8 = {'0', 'mM', 'NaCl'}; 
Switch2_Res9 = {'0', 'mM', 'NaCl'}; 


% Prompt the user to select Fluigent log files 
disp('Select all the Fluigent log "*.csv" files!')
[filename filepath] = uigetfile({'*.csv','Excel Files(*.csv)';'*.xlsx','Excel Files(*.xlsx)'; '*.txt','Txt Files(*.txt)'}, 'Pick a file','MultiSelect','on');
filename = string(filepath) + string(filename); filename=natsortfiles(filename);
if(outputPath == "") outputPath=filepath; end

FluigentData=[];
for i=1:length(filename)
    tmp= readtable(filename(i));
    FluigentData=[FluigentData; tmp];
end

absoluttime = FluigentData.Time;
Switch1     = FluigentData.M_Switch_1_SwitchEZ_3_10535__;
Switch2     = FluigentData.M_Switch_4_SwitchEZ_3_10535__;
Flowrate1   = FluigentData.FlowEZ_1_13109_Q;
Flowrate2   = FluigentData.FlowEZ_2_13110_Q;
Pressure1   = FluigentData.FlowEZ_1_13109_;
Pressure2   = FluigentData.FlowEZ_2_13110_;

if(time_axis_format==1)
time_axis = month(absoluttime).*(30*24*60) + day(absoluttime).*(24*60) + hour(absoluttime).*60 + minute(absoluttime) + second(absoluttime)./60; 
time_axis = time_axis - time_axis(1);
end

% Remove empty transitions in switching
[NaNindices1 NaNvalues1] = find(isnan(Switch1)); 
Switch1(NaNindices1)=Switch1(NaNindices1-1);
[NaNindices2 NaNvalues2] = find(isnan(Switch2)); 
Switch2(NaNindices2)=Switch2(NaNindices2-1);

% Construct Concentration Axis
% Prompt the user to select Fluigent log files 
disp('Select the "Reservoirs Solutions.csv/xlsx" file if exists, otherwise cancel the window!')
[solutionsFileName solutionsFilePath] = uigetfile({'*.csv','Excel Files(*.csv)';'*.xlsx','Excel Files(*.xlsx)'; '*.txt','Txt Files(*.txt)'}, 'Pick a file','MultiSelect','on');
solutionsFileName = string(solutionsFilePath) + string(solutionsFileName);
if(solutionsFilePath==0)
    disp("File not selected! Default script concentrations will be used!");
    for i=1:9
    Switch1_Concentrations(Switch1==i) =eval(['double(string(cell2mat(Switch1_Res',num2str(i),'(1))))']);
    Switch2_Concentrations(Switch2==i) =eval(['double(string(cell2mat(Switch2_Res',num2str(i),'(1))))']);
    end
else
    x=readtable(solutionsFileName); disp(x);
    for i=1:9
    Switch1_Concentrations(Switch1==i) =x.Concentration_Switch1(i);
    Switch2_Concentrations(Switch2==i) =x.Concentration_Switch2(i);
    end
end


if (overlay_plots==1)
LegendStr1 = ["Switch1","Switch2"];LegendStr2 = ["Switch1","Switch2"];
else
LegendStr1 = "Switch1";LegendStr2 = "Switch2";
end

% Plot figures
if(plot_switch1_data==1)
h1=figure(1);
plot(time_axis, Switch1, 'k', 'linewidth', 2); hold on;
xlim('tight'); legend(LegendStr1);
ylim([0.5 9.5]); 
xlabel('Time (min)'); ylabel('Switch Position')
set(gca, 'fontsize', 16)

h2=figure(2);
plot(time_axis, Switch1_Concentrations, 'k', 'linewidth', 2); hold on;
xlim('tight');legend(LegendStr1);
% ylim([0.5 9.5]); 
xlabel('Time (min)'); ylabel('Concentration')
set(gca, 'fontsize', 16)

h3=figure(3);
plot(time_axis, Flowrate1, 'k', 'linewidth', 2); hold on;
xlim('tight');  legend(LegendStr1);
%ylim([0.5 9.5]);
xlabel('Time (min)'); ylabel('Flow Rate (\muL/min)')
set(gca, 'fontsize', 16)

h4=figure(4);
plot(time_axis, Pressure1, 'k', 'linewidth', 2); hold on;
xlim('tight');  legend(LegendStr1);
%ylim([0.5 9.5]);
xlabel('Time (min)'); ylabel('Pressure (mBar)')
set(gca, 'fontsize', 16)

% Saving plots to Fluigent log directory
if(save_plots==1 && overlay_plots==0)
    saveas(h1, [outputPath, '/Switch1_ReservoirNumbers.png']);
    saveas(h2, [outputPath, '/Switch1_Concentrations.png']);
    saveas(h3, [outputPath, '/Switch1_FlowRate.png']);
    saveas(h4, [outputPath, '/Switch1_Pressure.png']);
end

end

if(plot_switch2_data==1)
h5=figure(4*abs(overlay_plots-1) +1);
plot(time_axis, Switch2, 'b','linewidth', 2); 
xlim('tight');ylim([0.5 9.5]); legend(LegendStr2);
xlabel('Time (min)'); ylabel('Switch Position')
set(gca, 'fontsize', 16)

h6=figure(4*abs(overlay_plots-1) +2);
plot(time_axis, Switch2_Concentrations, 'b','linewidth', 2); 
xlim('tight');legend(LegendStr2);
% ylim([0.5 9.5]); 
xlabel('Time (min)'); ylabel('Concentration')
set(gca, 'fontsize', 16)

h7=figure(4*abs(overlay_plots-1) +3);
plot(time_axis, Flowrate2, 'b','linewidth', 2); 
xlim('tight'); legend(LegendStr2);
%ylim([0.5 9.5]);
xlabel('Time (min)'); ylabel('Flow Rate (\muL/min)')
set(gca, 'fontsize', 16)

h8=figure(4*abs(overlay_plots-1) +4);
plot(time_axis, Pressure2, 'b','linewidth', 2); 
xlim('tight'); legend(LegendStr2);
%ylim([0.5 9.5]);
xlabel('Time (min)'); ylabel('Pressure (mBar)')
set(gca, 'fontsize', 16)

if(save_plots==1)
    if(overlay_plots==1)
    saveas(h5, [outputPath, '/Switch1_Switch2_ReservoirNumbers.png']);
    saveas(h6, [outputPath, '/Switch1_Switch2_Concentrations.png']);
    saveas(h7, [outputPath, '/Switch1_Switch2_FlowRate.png']);
    saveas(h8, [outputPath, '/Switch1_Switch2_Pressure.png']);
    else
    saveas(h5, [outputPath, '/Switch2_ReservoirNumbers.png']);
    saveas(h6, [outputPath, '/Switch2_Concentrations.png']);
    saveas(h7, [outputPath, '/Switch2_FlowRate.png']);
    saveas(h8, [outputPath, '/Switch2_Pressure.png']);
    end
end

end


