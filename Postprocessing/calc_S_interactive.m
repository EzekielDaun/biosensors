%*************************************************************************%
%**                                                                     **%
%**                   Calculate bulk RI sensitivity                     **%
%**                                                                     **%
%**                             2021-08-11                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%

% This script postprocesses bulk RI data files, and allows the user to
% input a series of bulk RI experimental results and RI sequences, and then
% select the appropriate regions to quantify from the peak shift plots.
% The script then creates sensitivity plots and linear fits for each 
% channel measured in each file and writes the data to an output file.

% disk paper 2013 RIs: [1.3330 1.3336 1.3343 1.3355 1.3378 1.3426 1.3522]
% (for salt concentrations [0 62.5 125 250 500 1000 2000] mM)

clear; close all; clc;

% read in the config file get the number of files through which to loop
configFile = '/Users/sgrist/Dropbox/UBC_DP_Biosensor/2022-1/Results/2022-03-05_AIM_BulkRI_IPA_EtOH/Quantification/Config.xlsx';
outputFile = '/Users/sgrist/Dropbox/UBC_DP_Biosensor/2022-1/Results/2022-03-05_AIM_BulkRI_IPA_EtOH/Quantification/Output.xlsx';

solutionUnits = '% IPA';
%solutionUnits = 'M NaCl';

tbl = readtable(configFile);
numFiles = height(tbl);

% number of datapoints to average for each measurement
num_avg = 100;
% figure positions
fig1Pos = [103 490 392 195];
fig2Pos = [103 490 392 195];
newcolors = [{[1 0 0]},{[0 0 1]},{[0.8 0 1]},{[0 0.8 0.2]},{[1 0.5 0]},{[0.7 0.7 0]},{[0 0.4 0.1]},{[0.2 0 0.8]}];

% loop through the files to do the analysis
for fileIdx = 1:numFiles
    % set up all the parameters for each file
    filePath = cell2mat(tbl{fileIdx, 1});
    saltConc = cell2mat(cellfun(@str2num,tbl{1,2},'uniform',0));
    RIs = cell2mat(cellfun(@str2num,tbl{1,3},'uniform',0));
    outputPath = cell2mat(tbl{fileIdx, 4});
    numSensors = tbl{fileIdx, 5};
    
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
    for RIidx = 1:length(RIs)
        % get the user input for this region
        title(['File ', num2str(fileIdx), ': RI region ', num2str(RIidx), ': click on the centre of the ', ...
                num2str(saltConc(RIidx)), solutionUnits, ' region.']);
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
            RIloc(fileIdx, RIidx) = (length(powArray{fileIdx, sensorIdx}) - (num_avg/2+1))
            warning(['File ', num2str(fileIdx), ': RI region', num2str(RIidx), ...
                'click too close to end of data to average.  Corrected.'])
        end
        
        % plot lines showing the averaged region
        figure(fileIdx); hold on; xline(RIloc(fileIdx, RIidx)-num_avg/2, ':k','HandleVisibility','off'); 
        xline(RIloc(fileIdx, RIidx)+num_avg/2, ':k','HandleVisibility','off');
        
        % calculate the average peak position in this region, for each
        % sensor
        for sensorIdx = 1:numSensors
            temp = powArray{fileIdx, sensorIdx};
            pkPos(fileIdx, sensorIdx, RIidx) = mean(temp(RIloc(fileIdx, RIidx)-num_avg/2:RIloc(fileIdx, RIidx)+num_avg/2));
            shiftErrs(fileIdx, sensorIdx, RIidx) = 3*std(temp(RIloc(fileIdx, RIidx)-num_avg/2:RIloc(fileIdx, RIidx)+num_avg/2));
        end
        
    end
    
    % plot the shifts and save
    h2 = figure(2*numFiles + fileIdx); 
    [RImin, idx] = min(RIs);
    RI_shift = RIs - RImin;
    for sensorIdx = 1:numSensors
        pkShift(fileIdx, sensorIdx, :) = (pkPos(fileIdx, sensorIdx, :) - pkPos(fileIdx, sensorIdx, idx))*1e9;
        hold on;
        errorbar(RI_shift', squeeze(pkShift(fileIdx, sensorIdx, :)), (squeeze(shiftErrs(fileIdx, sensorIdx, :)+shiftErrs(fileIdx, sensorIdx, idx))), '.', 'Color', newcolors{sensorIdx});
    end
   
    set(h2, 'Position', fig2Pos)

    % fit the data with a linear regression (forcing zero intercept)
    for sensorIdx = 1:numSensors
        S(fileIdx, sensorIdx) = RI_shift'\squeeze(pkShift(fileIdx, sensorIdx, :));
        pkShift_fit(fileIdx, sensorIdx, :) = S(fileIdx, sensorIdx)*RI_shift;
        Rsq(fileIdx, sensorIdx) = 1 - sum((pkShift(fileIdx, sensorIdx, :) - pkShift_fit(fileIdx, sensorIdx, :)).^2) ...
            /sum((pkShift(fileIdx, sensorIdx, :) - mean(pkShift(fileIdx, sensorIdx, :))).^2);
    end

    hold on; 
    for sensorIdx = 1:numSensors
        plot(RI_shift', squeeze(pkShift_fit(fileIdx, sensorIdx, :)), ':', 'Color', newcolors{sensorIdx}, 'HandleVisibility','off'); 
    
        legendStr2{sensorIdx} = ['Ch. ', num2str(sensorIdx), ': S=', num2str(S(fileIdx, sensorIdx)), ' nm/RIU', ...
            ', R^2=', num2str(Rsq(fileIdx, sensorIdx))];
    end

    xlabel('RI shift');
    ylabel('Peak shift (nm)')
    legend(legendStr2, 'Location', 'Southeast');

    figure(h1); title(['File ', num2str(fileIdx)]);
    saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.fig'])
    saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.svg'])
    saveas(h1, [outputPath, '/pkShiftPlot_file', num2str(fileIdx), '.png'])
    saveas(h2, [outputPath, '/sensitivityPlot_file', num2str(fileIdx), '.fig'])
    saveas(h2, [outputPath, '/sensitivityPlot_file', num2str(fileIdx), '.svg'])
    saveas(h2, [outputPath, '/sensitivityPlot_file', num2str(fileIdx), '.png'])

end

% output the data to a data output file
% add the sensitivities
for sensorIdx = 1:numSensors
    varName = ['Ch.', num2str(sensorIdx), '_S'];
    tbl.(varName) = squeeze(S(:, sensorIdx));
end
for sensorIdx = 1:numSensors
    varName = ['Ch.', num2str(sensorIdx), '_Rsq'];
    tbl.(varName) = squeeze(Rsq(:, sensorIdx));
end

writetable(tbl, outputFile)



