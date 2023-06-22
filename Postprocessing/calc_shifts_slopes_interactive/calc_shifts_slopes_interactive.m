%*************************************************************************%
%**                                                                     **%
%**                  Calculate peak shift information                   **%
%**                                                                     **%
%**                             2023-06-10                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%

% This script postprocesses binding assay files, and allows the user to
% input a series of assay results, and then perform interactive
% calculations of peak shifts and linear fit regions, to be output to a data file.
% it uses the perceptually uniform colormaps created by Ander Biguri. https://www.mathworks.com/matlabcentral/fileexchange/51986-perceptually-uniform-colormaps

clear; close all; clc;

% number of datapoints to average for each measurement
num_avg = 10;
% figure positions
fig1Pos = [103 490 392 195];

% what is the expected format of the data (all channels in
% 'collatedOffsets' or individual 'power_x_peakWL_list' variables?
offsetCollation = 0;

% are the input data units in nm or in m?  Set to 1 if data are in nm.
data_nm = 1;

% make sure the colormaps are accessible
mfilepath=fileparts(which('calculate_shifts_slopes_interactive.m'));
if exist(fullfile(mfilepath,'Colormaps'), 'dir')
    addpath(fullfile(mfilepath,'Colormaps'));
else
    error(['Error: Colormap not found. Please ensure that the Colormaps folder', ...
        'is in the same directory as the calc_shifts_slopes_interactive.m script.'])
end

% read in the config file get the number of files through which to loop
configFile = 'Config.xlsx';
disp(['Please navigate to the directory containing the configuration file ', configFile])
selpath = uigetdir;
if ~exist(fullfile(selpath, configFile), 'file')
    error(['Error: a folder containing a config file with filename ', configFile, ' was not selected.'])
end
cd(selpath);
tbl = readtable(configFile);
numFiles = height(tbl);

% loop through the files to do the analysis
for fileIdx = 1:numFiles
    % set up all the parameters for each file
    filePath = cell2mat(tbl{fileIdx, 1});
    outputPath = cell2mat(tbl{fileIdx, 2});
    regionFile = cell2mat(tbl{fileIdx, 3});
    numSensors = tbl{fileIdx, 4};
    newcolors = inferno(numSensors);
    
    % read in the different regions to be quantified for shifts or slopes
    if exist(regionFile, 'file')
        tbl2 = readtable(regionFile);
    else
        error(['Error: the regions file ', regionFile, ' was not found.  Please ensure this is correctly defined in the configuration file.'])
    end
    numFields = height(tbl2);
    for fieldIdx = 1:numFields
        regionName{fieldIdx} = cell2mat(tbl2{fieldIdx, 1});
        opType(fieldIdx) = tbl2{fieldIdx, 2}; % 1 for shift calculations, 2 for slope calculations
    end
    
    % load in the data file
    load(fullfile(filePath, 'peak_shifts.mat'))
    close all;
    
    % load in and plot the peak shift data
    h1 = figure(fileIdx); 
    
    clear legendStr;
    
    plottedSensors = 0;
    for sensorIdx = 1:numSensors
        % if the variable name exists, add the data to an array.  If not,
        % make warning
        if ~offsetCollation
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
        
        if chExist
            hold on;
            plottedSensors = plottedSensors+1;
            if ~data_nm
                plot(powArray{fileIdx, sensorIdx}*1e9, 'Color', newcolors(sensorIdx, :));  % convert to nm
            else
                plot(powArray{fileIdx, sensorIdx}, 'Color', newcolors(sensorIdx, :));
            end

            legendStr{plottedSensors} = ['Ch. ', num2str(sensorIdx)];
        end
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
                    if ~isempty(temp)
                        startPkPos(fileIdx, sensorIdx, regionIdx) = mean(temp(startLoc(fileIdx, regionIdx)-num_avg/2:startLoc(fileIdx, regionIdx)+num_avg/2));
                        startShiftErrs(fileIdx, sensorIdx, regionIdx) = 3*std(temp(startLoc(fileIdx, regionIdx)-num_avg/2:startLoc(fileIdx, regionIdx)+num_avg/2));
                    end
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
                    if ~isempty(temp)
                        endPkPos(fileIdx, sensorIdx, regionIdx) = mean(temp(endLoc(fileIdx, regionIdx)-num_avg/2:endLoc(fileIdx, regionIdx)+num_avg/2));
                        endShiftErrs(fileIdx, sensorIdx, regionIdx) = 3*std(temp(endLoc(fileIdx, regionIdx)-num_avg/2:endLoc(fileIdx, regionIdx)+num_avg/2));
                    end
                end

                % calculate the peak shifts for this region
                for sensorIdx = 1:numSensors
                    if ~isempty(powArray{fileIdx, sensorIdx})
                        if ~data_nm  % convert to nm
                            pkShift(fileIdx, sensorIdx, regionIdx) = 1e9*(endPkPos(fileIdx, sensorIdx, regionIdx) - startPkPos(fileIdx, sensorIdx, regionIdx));
                            pkShiftErrs(fileIdx, sensorIdx, regionIdx) = 1e9*(endShiftErrs(fileIdx, sensorIdx, regionIdx) + startShiftErrs(fileIdx, sensorIdx, regionIdx));
                        else
                            pkShift(fileIdx, sensorIdx, regionIdx) = (endPkPos(fileIdx, sensorIdx, regionIdx) - startPkPos(fileIdx, sensorIdx, regionIdx));
                            pkShiftErrs(fileIdx, sensorIdx, regionIdx) = (endShiftErrs(fileIdx, sensorIdx, regionIdx) + startShiftErrs(fileIdx, sensorIdx, regionIdx));
                        end

                        % output the data to a data output file
                        % add the peak shift and error to the output table
                        varName = ['Ch.', num2str(sensorIdx), '_Shift (nm)/Slope (pm/min)'];
                            tbl2.(varName)(regionIdx) = squeeze(pkShift(fileIdx, sensorIdx, regionIdx));
                        varName = ['Ch.', num2str(sensorIdx), '_Err/Rsq'];
                            tbl2.(varName)(regionIdx) = squeeze(pkShiftErrs(fileIdx, sensorIdx, regionIdx));
                    end
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
                    if ~isempty(temp) 
                        y2 = temp(startLoc(fileIdx, regionIdx):endLoc(fileIdx, regionIdx));
                        y = y2(~isnan(y2));
                        x = x(~isnan(y2));
                        X = [ones(length(x),1) x'];



                        B = X\y';
                        intercept(fileIdx, regionIdx, sensorIdx) = B(1);
                        if ~data_nm
                            slope(fileIdx, regionIdx, sensorIdx) = B(2)*1e12; % convert from m to pm
                        else
                            slope(fileIdx, regionIdx, sensorIdx) = B(2)*1e3; % convert from nm to pm
                        end
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
                        if ~data_nm % convert to nm
                            figure(fileIdx); hold on; plot(plotIdxArray, y_fit{fileIdx, regionIdx, sensorIdx}*1e9, 'k','HandleVisibility','off');
                        else
                            figure(fileIdx); hold on; plot(plotIdxArray, y_fit{fileIdx, regionIdx, sensorIdx}, 'k','HandleVisibility','off');
                        end
                    end
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






