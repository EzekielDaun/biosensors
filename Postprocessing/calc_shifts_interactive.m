%*************************************************************************%
%**                                                                     **%
%**                  Calculate peak shift information                   **%
%**                                                                     **%
%**                             2021-08-11                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%

% This script postprocesses binding assay files, and allows the user to
% input a series of assay results, and then perform interactive
% calculations of peak shifts and linear fit regions, to be output to a data file.


clear; close all; clc;

% read in the config file get the number of files through which to loop
configFile = '/Users/sgrist/Dropbox/UBC_DP_Biosensor/2021-2/Data/2021-08-17_Detergent_Regen_Test/ShiftQuantification/Config.xlsx';
outputFile = '/Users/sgrist/Dropbox/UBC_DP_Biosensor/2021-2/Data/2021-08-17_Detergent_Regen_Test/ShiftQuantification/Output.xlsx';

tbl = readtable(configFile);
numFiles = height(tbl);
numFields = width(tbl);

% number of datapoints to average for each measurement
num_avg = 5;
% figure positions
fig1Pos = [103 490 392 195];
fig2Pos = [103 490 392 195];
newcolors = [{[0 0 1]},{[1 0 0]},{[0.8 0 1]},{[0 0.8 0.2]},{[1 0.5 0]},{[0.7 0.7 0]},{[0 0.4 0.1]},{[0.2 0 0.8]}];

% loop through the files to do the analysis
for fileIdx = 1:numFiles
    % set up all the parameters for each file
    filePath = cell2mat(tbl{fileIdx, 1});
    outputPath = cell2mat(tbl{fileIdx, 2});
    numSensors = tbl{fileIdx, 3};
    for fieldIdx = 4:numFields
        regionName{fieldIdx-3} = cell2mat(tbl{fileIdx, fieldIdx});
    end
    
    % load in the data file
    load([filePath, '/matlab_matrix.mat'])
    
    % load in and plot the peak shift data
    h1 = figure(fileIdx); 
    %colororder(newcolors)
    
    clear legendStr;
    
    for sensorIdx = 1:numSensors
        % if the variable name exists, add the data to an array.  If not,
        % make warning
        chExist = evalin( 'base', ['exist(', '''power_', num2str(sensorIdx), '_offset_list''',',''var'') == 1'] );
        if chExist
            evalin('base', ['powArray{fileIdx, sensorIdx} = ', 'power_', num2str(sensorIdx), '_offset_list;']);       
        else
            warning(['Warning: no data for sensor ', num2str(sensorIdx)])
        end
        
        hold on;
        plot(powArray{fileIdx, sensorIdx}*1e9, 'Color', newcolors{sensorIdx});
        
        legendStr{sensorIdx} = ['Ch. ', num2str(sensorIdx)];
    end
    
    title(['File ', num2str(fileIdx)]);
    xlabel('Measurement number');
    ylabel('Peak shift (nm)');
    legend(legendStr)
    set(h1, 'Position', fig1Pos)
    
    % now request the user to click on the correct regions to average in
    % each bulk RI region
    for regionIdx = 1:length(regionName)
        % get the user input for the start of this region
        title(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ': click on the start x-location']);
        [x,y,button] = ginput(1);
        startLoc(fileIdx, regionIdx) = uint16(x);
        % check that we have enough data on both sides of the click to do
        % the averaging, and correct and warn if not.
        if startLoc(fileIdx, regionIdx) < num_avg/2+1
            startLoc(fileIdx, regionIdx) = num_avg/2+1;
            warning(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ':click too close to start of data to average.  Corrected.'])
        end
        if startLoc(fileIdx, regionIdx) > (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1))
            startLoc(fileIdx, regionIdx) = (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1));
            warning(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ':click too close to end of data to average.  Corrected.'])
        end
        
        % plot lines showing the averaged region
        figure(fileIdx); hold on; xline(startLoc(fileIdx, regionIdx)-num_avg/2, ':k','HandleVisibility','off'); 
        xline(startLoc(fileIdx, regionIdx)+num_avg/2, ':k','HandleVisibility','off');
        
        % calculate the average peak position in this region, for each
        % sensor
        for sensorIdx = 1:numSensors
            temp = powArray{fileIdx, sensorIdx};
            startPkPos(fileIdx, sensorIdx, regionIdx) = mean(temp(startLoc(fileIdx, regionIdx)-num_avg/2:startLoc(fileIdx, regionIdx)+num_avg/2));
            startShiftErrs(fileIdx, sensorIdx, regionIdx) = 3*std(temp(startLoc(fileIdx, regionIdx)-num_avg/2:startLoc(fileIdx, regionIdx)+num_avg/2));
        end
        
        % get the user input for the end of this region
        title(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ': click on the end x-location']);
        [x,y,button] = ginput(1);
        endLoc(fileIdx, regionIdx) = uint16(x);
        % check that we have enough data on both sides of the click to do
        % the averaging, and correct and warn if not.
        if endLoc(fileIdx, regionIdx) < num_avg/2+1
            endLoc(fileIdx, regionIdx) = num_avg/2+1;
            warning(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ':click too close to start of data to average.  Corrected.'])
        end
        if endLoc(fileIdx, regionIdx) > (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1))
            endLoc(fileIdx, regionIdx) = (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1));
            warning(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ':click too close to end of data to average.  Corrected.'])
        end
        
        % plot lines showing the averaged region
        figure(fileIdx); hold on; xline(endLoc(fileIdx, regionIdx)-num_avg/2, ':k','HandleVisibility','off'); 
        xline(endLoc(fileIdx, regionIdx)+num_avg/2, ':k','HandleVisibility','off');
        
        % calculate the average peak position in this region, for each
        % sensor
        for sensorIdx = 1:numSensors
            temp = powArray{fileIdx, sensorIdx};
            endPkPos(fileIdx, sensorIdx, regionIdx) = mean(temp(endLoc(fileIdx, regionIdx)-num_avg/2:endLoc(fileIdx, regionIdx)+num_avg/2));
            endShiftErrs(fileIdx, sensorIdx, regionIdx) = 3*std(temp(endLoc(fileIdx, regionIdx)-num_avg/2:endLoc(fileIdx, regionIdx)+num_avg/2));
        end
        
        % calculate the peak shifts for this region
        for sensorIdx = 1:numSensors
            pkShift(fileIdx, sensorIdx, regionIdx) = 1e9*(endPkPos(fileIdx, sensorIdx, regionIdx) - startPkPos(fileIdx, sensorIdx, regionIdx));
            pkShiftErrs(fileIdx, sensorIdx, regionIdx) = 1e9*(endShiftErrs(fileIdx, sensorIdx, regionIdx) + startShiftErrs(fileIdx, sensorIdx, regionIdx));
        end
    end
    
   

    figure(h1); title(['File ', num2str(fileIdx)]);
    saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.fig'])
    saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.svg'])
    saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.png'])
   
end

% output the data to a data output file
% add all the peak shifts and errors
for regionIdx = 1:length(regionName)
    for sensorIdx = 1:numSensors
        varName = ['Ch.', num2str(sensorIdx), '_', strrep(regionName{regionIdx}, ' ', '_'), '_Shift'];
        tbl.(varName) = squeeze(pkShift(:, sensorIdx, regionIdx));
        varName = ['Ch.', num2str(sensorIdx), '_', strrep(regionName{regionIdx}, ' ', '_'), '_Err'];
        tbl.(varName) = squeeze(pkShiftErrs(:, sensorIdx, regionIdx));
    end
end

writetable(tbl, outputFile)



