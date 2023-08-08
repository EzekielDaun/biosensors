%*************************************************************************%
%**                                                                     **%
%**                   Calculate bulk RI sensitivity                     **%
%**                                                                     **%
%**                             2023-06-10                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%

% This script postprocesses bulk RI data files, and allows the user to
% input a series of bulk RI experimental results and RI sequences, and then
% select the appropriate regions to quantify from the peak shift plots.
% The script then creates sensitivity plots and linear fits for each 
% channel measured in each file and writes the data to an output file.
% it uses the perceptually uniform colormaps created by Ander Biguri. https://www.mathworks.com/matlabcentral/fileexchange/51986-perceptually-uniform-colormaps

clear; 
close all; 
clc;

% what is the expected format of the data (all channels in
% 'collatedOffsets' or individual 'power_x_peakWL_list' variables?
offsetCollation = 0;

% are the input data units in nm or in m?  Set to 1 if data are in nm.
data_nm = 1;

% figure positions [x loc, y loc, width, height]
fig1Pos = [103 490 450 200];
fig2Pos = [103 490 600 400];
fig3Pos = [103 490 900 400];


% load in the colormap file path
mfilepath=fileparts(which('calc_S_interactive.m'));
addpath(fullfile(mfilepath,'Colormaps'));

% read in the config file get the number of files through which to loop
configFile = 'Config.xlsx';
disp(['Please navigate to the directory containing the configuration file ', configFile])
selpath = uigetdir;
if ~exist(fullfile(selpath, configFile), 'file')
    error(['Error: a folder containing a config file with filename ', configFile, ' was not selected.'])
end
cd(selpath);

opts = detectImportOptions(configFile);
opts = setvartype(opts, "Device_", 'string');
opts = setvartype(opts, "NumAvg", 'double'); 
tbl = readtable(configFile, opts);

numFiles = height(tbl);
initWidth = width(tbl);

% set up the framework for our collated dataframe output (first store all
% values in arrays then convert to a table at the end)
collFilePath = []; % the file analyzed
collSensorNum = []; % the sensor number
collBulkRIConc = []; % the bulk RI concentrations used
collBulkRIUnits = []; % the units for the bulk RI concentrations
collBulkRIs = []; % the bulk RI values
collSensitivity = []; % the bulk RI sensitivities
collR2 = []; % the collated R^2 of our S_bulk fits

% check whether our additional parameters have been added
if initWidth > 6
    collNum_Avg = []; % the number of datapoints averaged to calculate peak shift at each RI
    collFluidicChannel = []; % the fluidic channel
    collTapeout = []; % the photonic tapeout (for tracking)
    collBoxNum = []; % the box number
    collChip = []; % the chip # (for tracking)
    collDevice = []; % the device # (for tracking)
    collExptName = []; % the experiment name (for tracking)        
    sensorTypeThresh = 14; % sets the number of columns expected before the sensor type field of the config file
    if initWidth > sensorTypeThresh
        collSensorType = []; % the type of sensor
        collRampNum = []; % the replicate ramp number
    end
end

% loop through the files to do the analysis
for fileIdx = 1:numFiles
    % set up all the parameters for each file
    filePath = cell2mat(tbl{fileIdx, 1});
    bulkConc = cell2mat(cellfun(@str2num,tbl{fileIdx,2},'uniform',0));
    solutionUnits = cell2mat(tbl{fileIdx, 3});
    RIs = cell2mat(cellfun(@str2num,tbl{fileIdx,4},'uniform',0));
    outputPath = cell2mat(tbl{fileIdx, 5});
    numSensors = tbl{fileIdx, 6};
    if width(tbl) > 6 
        num_avg = tbl{fileIdx, 7}; % number of datapoints to average for each measurement
        channel1Sensors = cell2mat(cellfun(@str2num,tbl{fileIdx,8},'uniform',0)); % the sensors in fluidic channel 1
        channel2Sensors = cell2mat(cellfun(@str2num,tbl{fileIdx,9},'uniform',0)); % the sensors in fluidic channel 2
        tapeout = cell2mat(tbl{fileIdx, 10}); % the photonic tapeout (for tracking)
        boxNum = tbl{fileIdx, 11}; % the box # (for tracking)
        chip = tbl{fileIdx, 12}; % the chip # (for tracking)
        device = string(cell2mat(tbl{fileIdx, 13})); % the device # (for tracking)
        exptName = cell2mat(tbl{fileIdx, 14}); % the name of the experiment (for tracking)
        if width(tbl) > sensorTypeThresh
            sensorType = string(tbl{fileIdx,15}); % the type of sensor
            sensorType = split(sensorType, ',');
            rampNum = tbl{fileIdx, 16}; % the ramp number for this ramp (to keep track of the replicate # when multiple ramps are run in a single experiment)
        end
    end
    outputFile = fullfile(outputPath,'Output.xlsx');
    newcolors = inferno(numSensors);
    % set up the two colourmaps for the fluidic channels
    ch1Map = gray(length(channel1Sensors)+1); % gray map
    ch2Map = winter(length(channel2Sensors)+1);
    
    if length(bulkConc) ~= length(RIs)
        error('The number of Bulk RI concentrations and RI values specified in the configuration file do not match.')
    end
    
    % load in the data file
    if exist(fullfile(filePath, 'peak_shifts.mat'), 'file')
        load(fullfile(filePath, 'peak_shifts.mat'))
    elseif exist(fullfile(filePath, 'peak_shift.mat'), 'file')
        load(fullfile(filePath, 'peak_shift.mat'))
    else
        error(['No data file found at: ', fullfile(filePath, 'peak_shift.mat')]);
    end
    close all;
    
    % load in and plot the peak shift data
    h1 = figure(fileIdx); 
    
    clear legendStr;
    legendStr2 = [];
    
    plottedSensors = 0;
    for sensorIdx = 1:numSensors
        % figure out what channel the sensor is in
        if width(tbl) > 6
            if any(channel1Sensors == sensorIdx)
                fluidicChannel(sensorIdx) = 1;
            elseif any(channel2Sensors == sensorIdx)
                fluidicChannel(sensorIdx) = 2;
            else
                warning(['No fluidic channel found for sensor ', num2str(sensorIdx), '!']);
                fluidicChannel(sensorIdx) = NaN;
            end
        else
            warning(['No fluidic channel found for sensor ', num2str(sensorIdx), '!']);
            fluidicChannel(sensorIdx) = NaN;
        end
            
        % if the variable name exists, add the data to an array.  If not,
        % make warning
        if ~offsetCollation
            chExist = evalin( 'base', ['exist(', '''power_', num2str(sensorIdx), '_peakWL_list''',',''var'') == 1'] );
            if chExist
                evalin('base', ['powArray{fileIdx, sensorIdx} = ', 'power_', num2str(sensorIdx), '_peakWL_list;']);       
            else
                warning(['Warning: no data for sensor ', num2str(sensorIdx)])
                powArray{fileIdx, sensorIdx} = [];
            end
        else
            if size(collatedOffsets, 1) >= sensorIdx
                powArray{fileIdx, sensorIdx} = collatedOffsets(sensorIdx, :);
            else 
                warning(['Warning: no data for sensor ', num2str(sensorIdx)])
                powArray{fileIdx, sensorIdx} = [];
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

            legendStr{plottedSensors} = ['Det. ', num2str(sensorIdx)];
        end
    end
    
    title(['File ', num2str(fileIdx)]);
    xlabel('Measurement number');
    ylabel('Peak shift (nm)');
    legend(legendStr)
    set(h1, 'Position', fig1Pos)
    
    % now request the user to click on the correct regions to average in
    % each bulk RI region
    
    % now request the user to click on the correct regions to average in
    % each bulk RI region
    for RIidx = 1:length(RIs)
        % get the user input for the start of this region
        title(['File ', num2str(fileIdx), ': RI region for ', num2str(bulkConc(RIidx)), ' ', solutionUnits, ': click on the x-location at the centre of the region to analyze']);
        [x,y,button] = ginput(1);
        RIloc(fileIdx, RIidx) = uint16(x);
        disp(['Click RIloc = ', num2str(RIloc(fileIdx, RIidx))])
        % check that we have enough data on both sides of the click to do
        % the averaging, and correct and warn if not.
        if RIloc(fileIdx, RIidx) < num_avg/2+1
            RIloc(fileIdx, RIidx) = num_avg/2+1;
            warning(['File ', num2str(fileIdx), ': RI region', num2str(RIidx), ...
                 'click too close to start of data to average.  Corrected.'])  
        end
        for sensorIdx = 1:numSensors
            if ~isempty(powArray{fileIdx, sensorIdx})
                dataLength = length(powArray{fileIdx, sensorIdx});
                disp(['Using detector ', num2str(sensorIdx), ' to calculate data length.']);
                break
            end
        end
        if RIloc(fileIdx, RIidx) > (dataLength - (num_avg/2+1))
            RIloc(fileIdx, RIidx) = (dataLength - (num_avg/2+1));
            warning(['File ', num2str(fileIdx), ': RI region', num2str(RIidx), ...
                 'click too close to end of data to average.  Corrected.'])
        end
        disp(['Final RIloc = ', num2str(RIloc(fileIdx, RIidx))])

        % plot lines showing the averaged region
        figure(fileIdx); hold on; xline(double(RIloc(fileIdx, RIidx)-num_avg/2), ':k','HandleVisibility','off'); 
        xline(double(RIloc(fileIdx, RIidx)+num_avg/2), ':k','HandleVisibility','off');

        % calculate the average peak position in this region, for each
        % sensor
        for sensorIdx = 1:numSensors
            temp = powArray{fileIdx, sensorIdx};
            if ~isempty(temp)
                tempPkPos(sensorIdx, RIidx) = mean(temp(RIloc(fileIdx, RIidx)-num_avg/2:RIloc(fileIdx, RIidx)+num_avg/2));
                tempShiftErrs(sensorIdx, RIidx) = 3*std(temp(RIloc(fileIdx, RIidx)-num_avg/2:RIloc(fileIdx, RIidx)+num_avg/2));
            end
        end
    end
    
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            pkPos{fileIdx, sensorIdx} = tempPkPos(sensorIdx, :);
            shiftErrs{fileIdx, sensorIdx} = tempShiftErrs(sensorIdx, :);
        end
    end
    
    % plot the shifts and save
    h2 = figure(2*numFiles + fileIdx); 
    [RImin, idx] = min(RIs);
    RI_shift = RIs - RImin;
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            pkPos_temp = pkPos{fileIdx, sensorIdx};
            if ~data_nm
                pkShift{fileIdx, sensorIdx} = (pkPos{fileIdx, sensorIdx} - pkPos_temp(idx))*1e9;
            else
                pkShift{fileIdx, sensorIdx} = (pkPos{fileIdx, sensorIdx} - pkPos_temp(idx));
            end
            hold on;
            errorbar(RI_shift', squeeze(pkShift{fileIdx, sensorIdx}), (squeeze(shiftErrs{fileIdx, sensorIdx}+shiftErrs{fileIdx, sensorIdx})), '.', 'Color', newcolors(sensorIdx, :));
        end
    end
   
    set(h2, 'Position', fig2Pos)

    % fit the data with a linear regression (forcing zero intercept)
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            S(fileIdx, sensorIdx) = RI_shift'\squeeze(pkShift{fileIdx, sensorIdx})';
            pkShift_fit{fileIdx, sensorIdx} = S(fileIdx, sensorIdx)*RI_shift;
            Rsq(fileIdx, sensorIdx) = 1 - sum((pkShift{fileIdx, sensorIdx} - pkShift_fit{fileIdx, sensorIdx}).^2) ...
                /sum((pkShift{fileIdx, sensorIdx} - mean(pkShift{fileIdx, sensorIdx})).^2);
        end
    end

    hold on; 
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            plot(RI_shift', squeeze(pkShift_fit{fileIdx, sensorIdx}), ':', 'Color', newcolors(sensorIdx, :), 'HandleVisibility','off'); 

            legendStr2 = [legendStr2; {['Ch. ', num2str(sensorIdx), ': S=', num2str(S(fileIdx, sensorIdx)), ' nm/RIU', ...
                ', R^2=', num2str(Rsq(fileIdx, sensorIdx))]}];
        end
    end

    xlabel('RI shift');
    ylabel('Peak shift (nm)')
    legend(legendStr2, 'Location', 'Southeast');
    
    % plot the peak shift data with colour dependent on channel and more
    % descriptive legend, if the additional data were provided
    if initWidth > sensorTypeThresh
        h3 = figure(3*numFiles + fileIdx); 
        clear legendStr3;
        plottedSensors = 0;
        for sensorIdx = 1:numSensors
            if ~isempty(powArray{fileIdx, sensorIdx})
                hold on;
                plottedSensors = plottedSensors+1;
                % plot the data with colour dependent on sensor and channel
                if fluidicChannel(sensorIdx) == 1
                    if ~data_nm
                        plot(powArray{fileIdx, sensorIdx}*1e9, 'Color', ch1Map(ceil(sensorIdx/2), :));  % convert to nm
                    else
                        plot(powArray{fileIdx, sensorIdx}, 'Color', ch1Map(ceil(sensorIdx/2), :));
                    end
                else
                    if fluidicChannel(sensorIdx) == 2
                        if ~data_nm
                            plot(powArray{fileIdx, sensorIdx}*1e9, 'Color', ch2Map(ceil(sensorIdx/2), :));  % convert to nm
                        else
                            plot(powArray{fileIdx, sensorIdx}, 'Color', ch2Map(ceil(sensorIdx/2), :));
                        end
                    end
                end
                legendStr3{plottedSensors} = ['Det. ', num2str(sensorIdx), ', Ch. ', num2str(fluidicChannel(sensorIdx)), ', ', sensorType{sensorIdx}];
            end
        end

        title(['File ', num2str(fileIdx)]);
        xlabel('Measurement number');
        ylabel('Peak shift (nm)');
        legend(legendStr3)
        set(h1, 'Position', fig3Pos)
        saveas(h3, fullfile(outputPath, ['pkShiftColourPlot_file', num2str(fileIdx), '.fig']))
        saveas(h3, fullfile(outputPath, ['pkShiftColourPlot_file', num2str(fileIdx), '.svg']))
        saveas(h3, fullfile(outputPath, ['pkShiftColourPlot_file', num2str(fileIdx), '.png']))
    end

    % save the figures
    figure(h1); title(['File ', num2str(fileIdx)]);
    saveas(h1, fullfile(outputPath, ['pkShiftPlot_file', num2str(fileIdx), '.fig']))
    saveas(h1, fullfile(outputPath, ['pkShiftPlot_file', num2str(fileIdx), '.svg']))
    saveas(h1, fullfile(outputPath, ['pkShiftPlot_file', num2str(fileIdx), '.png']))
    saveas(h2, fullfile(outputPath, ['sensitivityPlot_file', num2str(fileIdx), '.fig']))
    saveas(h2, fullfile(outputPath, ['sensitivityPlot_file', num2str(fileIdx), '.svg']))
    saveas(h2, fullfile(outputPath, ['sensitivityPlot_file', num2str(fileIdx), '.png']))

    % add to our arrays for another output file that is more readily postprocessed, with one row
    % for each sensor measurement
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            collFilePath = [collFilePath; string(filePath)]; % the file analyzed
            collSensorNum = [collSensorNum; sensorIdx]; % the sensor number
            collBulkRIConc = [collBulkRIConc; {bulkConc}]; % the bulk RI concentrations used
            collBulkRIUnits = [collBulkRIUnits; string(solutionUnits)]; % the units for the bulk RI concentrations
            collBulkRIs = [collBulkRIs; {RIs}]; % the bulk RI values
            collSensitivity = [collSensitivity; S(fileIdx, sensorIdx)]; % the bulk RI sensitivities
            collR2 = [collR2; Rsq(fileIdx, sensorIdx)]; % the collated R^2 of our S_bulk fits

            % check whether our additional parameters have been added
            if initWidth > 6
                collNum_Avg = [collNum_Avg; num_avg]; % number of averaged datapoints
                collFluidicChannel = [collFluidicChannel; fluidicChannel(sensorIdx)]; % the fluidic channel
                collTapeout = [collTapeout; string(tapeout)]; % the photonic tapeout (for tracking)
                collBoxNum = [collBoxNum; boxNum]; % the box # (for tracking)
                collChip = [collChip; chip]; % the chip # (for tracking)
                collDevice = [collDevice; device]; % the device # (for tracking)
                collExptName = [collExptName; string(exptName)]; % the experiment name (for tracking)
                if initWidth > sensorTypeThresh
                    collSensorType = [collSensorType; sensorType(sensorIdx)]; % the type of sensor
                end
            end
            
        end
        
        % clear the data before moving to the next file
        if ~offsetCollation
            chExist = evalin( 'base', ['exist(', '''power_', num2str(sensorIdx), '_peakWL_list''',',''var'') == 1'] );
            if chExist
                evalin('base', ['clear ', 'power_', num2str(sensorIdx), '_peakWL_list;']);       
            else
                warning(['Warning: no data for sensor ', num2str(sensorIdx)])
            end
        else
            clear collatedOffsets
        end
    end
    
    clear RI_shift tempPkPos tempShiftErrs
end
    
% output the data to a data output file
% add the sensitivities
for sensorIdx = 1:numSensors
    if ~isempty(powArray{fileIdx, sensorIdx})
        varName = ['Ch.', num2str(sensorIdx), '_S'];
        tbl.(varName) = squeeze(S(:, sensorIdx));
    end
end
for sensorIdx = 1:numSensors
    if ~isempty(powArray{fileIdx, sensorIdx})
        varName = ['Ch.', num2str(sensorIdx), '_Rsq'];
        tbl.(varName) = squeeze(Rsq(:, sensorIdx));
    end
end
writetable(tbl, outputFile)


% save another output file in a dataframe format that is more readily 
% postprocessed, with one row for each sensor measurement
% make the table (can also be postprocessed in MATLAB)
varNames = {'Detector Number','Bulk Sensitivity','Sensitivity fit R^2', ...
    'Analyzed file path', 'Bulk RI solution concentrations', 'Concentration units', ...
    'Bulk RI values'};
T2 = table(collSensorNum, collSensitivity, collR2, collFilePath, collBulkRIConc, ...
    collBulkRIUnits, collBulkRIs,'VariableNames',varNames);

if initWidth > 6
    T2 = addvars(T2, collNum_Avg, collExptName, collTapeout, collBoxNum, collChip, collDevice, collFluidicChannel, ...
        'Before', 'Detector Number', 'NewVariableNames', {'# Datapoints Averaged', 'Experiment Name', ...
        'Tapeout Name', 'Box #', 'Chip #', 'Device #', 'Fluidic channel'});
    if initWidth > sensorTypeThresh
        T2 = addvars(T2, collSensorType, 'NewVariableNames', 'Sensor type');
    end
end

% make another table to avoid splitting columns in Excel, then output the
% file
T3 = T2;
T3.("Bulk RI solution concentrations") = cellfun(@num2str, T3.("Bulk RI solution concentrations"), 'UniformOutput', false); 
T3.("Bulk RI values") = cellfun(@num2str, T3.("Bulk RI values"), 'UniformOutput', false); 
writetable(T3, strrep(outputFile, '.xlsx', '_dataFrame.xlsx'));

% clear the duplicate table and save the workspace in MATLAB format
clear T3
save(strrep(outputFile, '.xlsx', '.mat'))