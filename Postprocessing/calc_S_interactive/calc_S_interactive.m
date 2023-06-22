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

% number of datapoints to average for each measurement
num_avg = 10;
% figure positions [x loc, y loc, width, height]
fig1Pos = [103 490 450 200];
fig2Pos = [103 490 600 400];
legendStr2 = [];

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

tbl = readtable(configFile);
numFiles = height(tbl);

% loop through the files to do the analysis
for fileIdx = 1:numFiles
    % set up all the parameters for each file
    filePath = cell2mat(tbl{fileIdx, 1});
    bulkConc = cell2mat(cellfun(@str2num,tbl{1,2},'uniform',0));
    solutionUnits = cell2mat(tbl{fileIdx, 3});
    RIs = cell2mat(cellfun(@str2num,tbl{1,4},'uniform',0));
    outputPath = cell2mat(tbl{fileIdx, 5});
    numSensors = tbl{fileIdx, 6};
    outputFile = fullfile(outputPath,'Output.xlsx');
    newcolors = inferno(numSensors);
    
    if length(bulkConc) ~= length(RIs)
        error('The number of Bulk RI concentrations and RI values specified in the configuration file do not match.')
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
    
    % now request the user to click on the correct regions to average in
    % each bulk RI region
    for RIidx = 1:length(RIs)
        % get the user input for the start of this region
        title(['File ', num2str(fileIdx), ': RI region for ', num2str(bulkConc(RIidx)), ' ', solutionUnits, ': click on the start x-location']);
        [x,y,button] = ginput(1);
        RIloc(fileIdx, RIidx) = uint16(x);
        % check that we have enough data on both sides of the click to do
        % the averaging, and correct and warn if not.
        if RIloc(fileIdx, RIidx) < num_avg/2+1
            RIloc(fileIdx, RIidx) = num_avg/2+1;
            warning(['File ', num2str(fileIdx), ': RI region', num2str(RIidx), ...
                 'click too close to start of data to average.  Corrected.'])  
        end
        if RIloc(fileIdx, RIidx) > (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1))
            RIloc(fileIdx, RIidx) = (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1));
            warning(['File ', num2str(fileIdx), ': RI region', num2str(RIidx), ...
                 'click too close to end of data to average.  Corrected.'])
        end

        % plot lines showing the averaged region
        figure(fileIdx); hold on; xline(double(RIloc(fileIdx, RIidx)-num_avg/2), ':k','HandleVisibility','off'); 
        xline(double(RIloc(fileIdx, RIidx)+num_avg/2), ':k','HandleVisibility','off');

        % calculate the average peak position in this region, for each
        % sensor
        for sensorIdx = 1:numSensors
            temp = powArray{fileIdx, sensorIdx};
            if ~isempty(temp)
                pkPos(fileIdx, sensorIdx, RIidx) = mean(temp(RIloc(fileIdx, RIidx)-num_avg/2:RIloc(fileIdx, RIidx)+num_avg/2));
                shiftErrs(fileIdx, sensorIdx, RIidx) = 3*std(temp(RIloc(fileIdx, RIidx)-num_avg/2:RIloc(fileIdx, RIidx)+num_avg/2));
            end
        end
    end
    
    % plot the shifts and save
    h2 = figure(2*numFiles + fileIdx); 
    [RImin, idx] = min(RIs);
    RI_shift = RIs - RImin;
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            if ~data_nm
                pkShift(fileIdx, sensorIdx, :) = (pkPos(fileIdx, sensorIdx, :) - pkPos(fileIdx, sensorIdx, idx))*1e9;
            else
                pkShift(fileIdx, sensorIdx, :) = (pkPos(fileIdx, sensorIdx, :) - pkPos(fileIdx, sensorIdx, idx));
            end
            hold on;
            errorbar(RI_shift', squeeze(pkShift(fileIdx, sensorIdx, :)), (squeeze(shiftErrs(fileIdx, sensorIdx, :)+shiftErrs(fileIdx, sensorIdx, idx))), '.', 'Color', newcolors(sensorIdx, :));
        end
    end
   
    set(h2, 'Position', fig2Pos)

    % fit the data with a linear regression (forcing zero intercept)
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            S(fileIdx, sensorIdx) = RI_shift'\squeeze(pkShift(fileIdx, sensorIdx, :));
            pkShift_fit(fileIdx, sensorIdx, :) = S(fileIdx, sensorIdx)*RI_shift;
            Rsq(fileIdx, sensorIdx) = 1 - sum((pkShift(fileIdx, sensorIdx, :) - pkShift_fit(fileIdx, sensorIdx, :)).^2) ...
                /sum((pkShift(fileIdx, sensorIdx, :) - mean(pkShift(fileIdx, sensorIdx, :))).^2);
        end
    end

    hold on; 
    for sensorIdx = 1:numSensors
        if ~isempty(powArray{fileIdx, sensorIdx})
            plot(RI_shift', squeeze(pkShift_fit(fileIdx, sensorIdx, :)), ':', 'Color', newcolors(sensorIdx, :), 'HandleVisibility','off'); 

            legendStr2 = [legendStr2; {['Ch. ', num2str(sensorIdx), ': S=', num2str(S(fileIdx, sensorIdx)), ' nm/RIU', ...
                ', R^2=', num2str(Rsq(fileIdx, sensorIdx))]}];
        end
    end

    xlabel('RI shift');
    ylabel('Peak shift (nm)')
    legend(legendStr2, 'Location', 'Southeast');

    % save the figures
    figure(h1); title(['File ', num2str(fileIdx)]);
    saveas(h1, fullfile(outputPath, ['pkShiftPlot_file', num2str(fileIdx), '.fig']))
    saveas(h1, fullfile(outputPath, ['pkShiftPlot_file', num2str(fileIdx), '.svg']))
    saveas(h1, fullfile(outputPath, ['pkShiftPlot_file', num2str(fileIdx), '.png']))
    saveas(h2, fullfile(outputPath, ['sensitivityPlot_file', num2str(fileIdx), '.fig']))
    saveas(h2, fullfile(outputPath, ['sensitivityPlot_file', num2str(fileIdx), '.svg']))
    saveas(h2, fullfile(outputPath, ['sensitivityPlot_file', num2str(fileIdx), '.png']))

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



