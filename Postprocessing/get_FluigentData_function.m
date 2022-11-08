%*************************************************************************%
%**                                                                     **%
%**                   Plotting the Resonance Shifts                     **%
%**                                                                     **%
%**                             2021-10-30                              **%
%**                         Mohammed Al-Qadasi                          **%
%**                                                                     **%
%*************************************************************************%
% This function takes list of conentrations as inputs, prompts the user to
% select the Fluigent log files, then returns x and y axes for switch
% transitions, concentration transitions, flow rates and pressures.  The
% user will also be prompt to select "Reservoir Solutions.csv" file if
% exists to map the reservoir contents to some concentration values. The
% file needs to have the following format: 
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
%
% Examples of calling this function:
% [time_axis,Res1_array, Conc1_array, flow1_rate, pressure1_array]=get_FluigentData_function([0 0 62.5 125 250 375 0 0 0],[])
% [time_axis, Res2_array, Conc2_array, flow2_rate, pressure2_array]=get_FluigentData_function([],[0 0 62.5 125 250 375 0 0 0])
% [time_axis, Res1_2_array, Conc1_2_array, flow1_2_rate, pressure1_2_array]=get_FluigentData_function([0 0 62.5 125 250 375 0 0 0],[0 0 62.5 125 250 375 0 0 0])

function [time_axis, Res_array, Conc_array, flow_rate, pressure_array]=get_FluigentData_function(concentrations_list1, concentrations_list2)

time_axis_format  = 1; %0: absolute, 1:mins
plot_switch1_data = 1; 
plot_switch2_data = 1;
overlay_plots     = 1;

if (length(concentrations_list1)==0) concentrations_list1=zeros(1,9); end
if (length(concentrations_list2)==0) concentrations_list2=zeros(1,9); end

% Prompt the user to select Fluigent log files 
disp('Select all the Fluigent log "*.csv" files!')
[filename filepath] = uigetfile({'*.csv','Excel Files(*.csv)';'*.xlsx','Excel Files(*.xlsx)'; '*.txt','Txt Files(*.txt)'}, 'Pick a file','MultiSelect','on');
filename = string(filepath) + string(filename);filename=natsortfiles(filename);

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
disp('Select the "Reservoirs Solutions.csv/xlsx" file if exists, otherwise cancel the window to use the default concentrations!')
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

% Reservoir Concentrations, {Concentration,Unit,Solvent}
for i=1:9
eval(['Switch1_Res',num2str(i),' = {concentrations_list1(',num2str(i),char(")', 'mM', 'NaCl'};")]);
eval(['Switch2_Res',num2str(i),' = {concentrations_list2(',num2str(i),char(")', 'mM', 'NaCl'};")]);
end

% Arrange output data
Res_array(:,1)=Switch1;         Res_array(:,2)=Switch2; 
Conc_array(:,1)=Switch1_Concentrations; Conc_array(:,2)=Switch2_Concentrations; 
flow_rate(:,1)=Flowrate1;       flow_rate(:,2)=Flowrate2;
pressure_array(:,1)=Pressure1;  pressure_array(:,2)=Pressure2;

end