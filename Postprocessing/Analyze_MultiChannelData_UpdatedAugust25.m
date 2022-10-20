%*************************************************************************%
%**                                                                     **%
%**         Collate 6-detector measurements into one MATLAB data        **%
%**    file and plot (stopgap until RetrospectiveAnalysis is updated)   **%
%**                                                                     **%
%**                             2022-02-04                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%
clear;
clc;
close all; 

% figure position and size
figPos = [900, 1200, 500, 200];

% folders to collate
%analysisDirs = [{'Analysis_ch1-2'}, {'Analysis_ch3-4'}, {'Analysis_ch5-6'}]; %% (1) from RA

% detector channels corresponding to the 'power_1' and 'power_2' in each
% directory (first index is for 'power_1'; second index is for 'power_2'
channelIndices = [{[1,2]}, {[3,4]}, {[5,6]}, {[7,8]}]; %% (2) need go fix this as well: power that was analyzed in each directory

% conditions tested
conditionNames = [{'Microfluidic Channel 1: Bottom'}, {'Microfluidic Channel 2: Top'}]; %% (3) need to fix this as well
%protein A was in channel 1 (bottom/edged), gemina was in channel 2 (top/flat)

% colours to plot for each condition, e.g., 'kb' plots the first conidtion
% in black and the second in blue
conditionColours = 'km';

% channels in each condition
conditionChannels = [{[1,3,5,7]}, {[2,4,6,8]}]; % (4) need to fix this as well
%fluigent channel 1, protein A, was detector 1,3, and 4

% import all the data and organize into a data structure
load('peak_shifts.mat');


collatedOffsets{1, :} = power_1_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{2, :} = power_2_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{3, :} = power_3_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{4, :} = power_4_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{5, :} = power_5_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{6, :} = power_6_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{7, :} = power_7_peakWL_list-power_1_peakWL_list(1);
collatedOffsets{8, :} = power_8_peakWL_list-power_1_peakWL_list(1);





% 
% for iDir = 1:length(analysisDirs)
%     %load([analysisDirs{iDir}, '/matlab_matrix.mat'])
%     load('peak_shifts.mat');
%     indices = channelIndices{iDir};
%     
% %     collatedOffsets{indices(1), :} = power_1_offset_list;
% %     collatedOffsets{indices(2), :} = power_2_offset_list;
% 
%     collatedOffsets{indices(1), :} = power_1_unknown;
%     collatedOffsets{indices(2), :} = power_2_offset_list;
% end


filename1= "timeSteps.csv"; 
time_table = readtable(filename1);
timeAll = time_table.Var3;
time=zeros(1,length(timeAll)-1);
for i=2:length(timeAll)
    time(i-1)= timeAll(i)-timeAll(1);
end

time=time/60;

% plot the data on the same axis
h = figure; hold on;
set(h, 'Position', figPos)
xlabel('Time (minutes)')
ylabel('Resonance peak shift (nm)')
%unitScale= 1*10^9;
unitScale= 1;
collatedOffsets=cellfun(@(x) x*unitScale,collatedOffsets,'un',0);
for condIdx = 1:length(conditionNames) %loop channel 1, channel 2
    for chIdx = conditionChannels{condIdx} %channel1: 1,3,4 ; channel 2: 2,5,6
        disp(['condIdx = ',num2str(condIdx)])
        disp(['chIdx = ',num2str(chIdx)])
        hx = plot(time(1:size(collatedOffsets{chIdx, :},2) ), collatedOffsets{chIdx, :}, conditionColours(condIdx),'DisplayName',conditionNames{condIdx});
        %hx = plot(time, collatedOffsets(chIdx, :)*1e9, conditionColours(condIdx),'DisplayName',conditionNames{condIdx});
        
        % If this is the first channel of this condition, display in legend
         if chIdx == conditionChannels{condIdx}(1)
             toPlotLeg(condIdx) = hx;
         end
         clear hx
    end
end

grid on
title("Spike Protein Assay Trial 3")
legend(toPlotLeg, 'Location', 'Northwest')
savefig(h, 'CollatedOverlaidPkShifts.fig');
saveas(h, 'CollatedOverlaidPkShifts.svg');
saveas(h, 'CollatedOverlaidPkShifts.jpeg');
save('CollatedDetectorData.mat')