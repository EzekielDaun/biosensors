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
configFile = 'Config.xlsx';
disp(['Please navigate to the directory containing the configuration file ', configFile])
selpath = uigetdir;
cd(selpath);


tbl = readtable(configFile);
numFiles = height(tbl);

% number of datapoints to average for each measurement
num_avg = 10;
% figure positions
fig1Pos = [103 490 392 195];
fig2Pos = [103 490 392 195];
newcolors = [{[0 0 1]},{[1 0 0]},{[0.8 0 1]},{[0 0.8 0.2]},{[1 0.5 0]},{[0.7 0.7 0]},{[0 0.4 0.1]},{[0.2 0 0.8]}];

% what is the expected format of the data (all channels in
% 'collatedOffsets' or individual 'power_x_offset_list' variables?
CollatedOffsets = 0;

% loop through the files to do the analysis
for fileIdx = 1:numFiles
    % set up all the parameters for each file
    filePath = cell2mat(tbl{fileIdx, 1});
    outputPath = cell2mat(tbl{fileIdx, 2});
    regionFile = cell2mat(tbl{fileIdx, 3});
    numSensors = tbl{fileIdx, 4};
    
    % read in the different regions to be quantified for shifts or slopes
    tbl2 = readtable(regionFile);
    numFields = height(tbl2);
    for fieldIdx = 1:numFields
        regionName{fieldIdx} = cell2mat(tbl2{fieldIdx, 1});
        opType(fieldIdx) = tbl2{fieldIdx, 2}; % 1 for shift calculations, 2 for slope calculations
    end
    
    % load in the data file
    if ispc
        load([filePath, '\peak_shifts.mat'])
    else
        load([filePath, '/peak_shifts.mat'])
    end
    close all;
    
    % load in and plot the peak shift data
    h1 = figure(fileIdx); 
    %colororder(newcolors)
    
    clear legendStr;
    
    for sensorIdx = 1:numSensors
        % if the variable name exists, add the data to an array.  If not,
        % make warning
        if ~CollatedOffsets
            chExist = evalin( 'base', ['exist(', '''power_', num2str(sensorIdx), '_peakWL_list''',',''var'') == 1'] );
            if chExist
                evalin('base', ['powArray{fileIdx, sensorIdx} = ', 'power_', num2str(sensorIdx), '_peakWL_list;']);       
            else
                warning(['Warning: no data for sensor ', num2str(sensorIdx)])
            end
        else
            if size(collatedOffsets, 1) >= sensorIdx
                powArray{fileIdx, sensorIdx} = collatedOffsets(sensorIdx, :);
            else 
                warning(['Warning: no data for sensor ', num2str(sensorIdx)])
            end
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
        switch opType(regionIdx)
            case 1 % calculate peak shifts
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
                figure(fileIdx); hold on; xline(double(startLoc(fileIdx, regionIdx)-num_avg/2), ':k','HandleVisibility','off'); 
                xline(double(startLoc(fileIdx, regionIdx)+num_avg/2), ':k','HandleVisibility','off');

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
                figure(fileIdx); hold on; xline(double(endLoc(fileIdx, regionIdx)-num_avg/2), ':k','HandleVisibility','off'); 
                xline(double(endLoc(fileIdx, regionIdx)+num_avg/2), ':k','HandleVisibility','off');

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
                
                    % output the data to a data output file
                    % add the peak shift and error to the output table
                    varName = ['Ch.', num2str(sensorIdx), '_Shift (nm)/Slope (pm/min)'];
                        tbl2.(varName)(regionIdx) = squeeze(pkShift(fileIdx, sensorIdx, regionIdx));
                    varName = ['Ch.', num2str(sensorIdx), '_Err/Rsq'];
                        tbl2.(varName)(regionIdx) = squeeze(pkShiftErrs(fileIdx, sensorIdx, regionIdx));
                end
                
                
            case 2 % calculate slopes
                % get the user input for the start of this region
                title(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ': click on the start x-location for slope calculation']);
                [x,y,button] = ginput(1);
                startLoc(fileIdx, regionIdx) = uint16(x);
                
                % plot line showing the start of the slope-calculation region
                figure(fileIdx); hold on; xline(double(startLoc(fileIdx, regionIdx)), ':k','HandleVisibility','off'); 
                
                % get the user input for the end of this region
                title(['File ', num2str(fileIdx), ' ', regionName{regionIdx}, ': click on the end x-location for slope calculation']);
                [x,y,button] = ginput(1);
                endLoc(fileIdx, regionIdx) = uint16(x);
                
                % plot line showing the end of the slope-calculation region
                figure(fileIdx); hold on; xline(double(endLoc(fileIdx, regionIdx)), ':k','HandleVisibility','off'); 
                
                % calculate the slope in this region, for each sensor
                for sensorIdx = 1:numSensors
                    x = t_array(startLoc(fileIdx, regionIdx):endLoc(fileIdx, regionIdx));
                    temp = powArray{fileIdx, sensorIdx};
                    y2 = temp(startLoc(fileIdx, regionIdx):endLoc(fileIdx, regionIdx));
                    y = y2(~isnan(y2));
                    x = x(~isnan(y2));
                    X = [ones(length(x),1) x'];
                    
                    
                    
                    B = X\y';
                    intercept(fileIdx, regionIdx, sensorIdx) = B(1);
                    slope(fileIdx, regionIdx, sensorIdx) = B(2)*1e12;
                    y_fit{fileIdx, regionIdx, sensorIdx} = X*B;
                    y_fit2 = B(2)*x+B(1);
                    Rsq(fileIdx, regionIdx, sensorIdx) = 1 - sum((y - squeeze(y_fit{fileIdx, regionIdx, sensorIdx})').^2) ...
                        /sum((y - mean(y)).^2);

                    % output the data to a data output file
                    % add the slope and Rsq to the output table
                    varName = ['Ch.', num2str(sensorIdx), '_Shift (nm)/Slope (pm/min)'];
                        tbl2.(varName)(regionIdx) = squeeze(slope(fileIdx, regionIdx, sensorIdx));
                    varName = ['Ch.', num2str(sensorIdx), '_Err/Rsq'];
                        tbl2.(varName)(regionIdx) = squeeze(Rsq(fileIdx, regionIdx, sensorIdx));
                        
                    % plot the fit on the figure
                    plotIdxArray = startLoc(fileIdx, regionIdx):endLoc(fileIdx, regionIdx);
                    plotIdxArray = plotIdxArray(~isnan(y2));
                    figure(fileIdx); hold on; plot(plotIdxArray, y_fit{fileIdx, regionIdx, sensorIdx}*1e9, 'k','HandleVisibility','off'); 
                end
                
            otherwise
               disp('Invalid input for operation type (should be 1 for peak shift calculation, 2 for slope calculation)');

        end
                
    end

           

            writetable(tbl2, [outputPath, '/File ', num2str(fileIdx), '_Output.xlsx'] )

            figure(h1); title(['File ', num2str(fileIdx)]);
            saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.fig'])
            saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.svg'])
            saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.png'])
            
   
    clear regionName
end






