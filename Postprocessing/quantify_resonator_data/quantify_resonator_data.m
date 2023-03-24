%*************************************************************************%
%**                                                                     **%
%**                   Quantify Resonator Performance                    **%
%**                                                                     **%
%**                                                                     **%
%**                             2022-07-31                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%

% Quantify resonator performance from a set of .mat files, each containing
% power and wavelength vectors (one wavelength vector, one power matrix
% with the power data for all detectors), such as those exported from
% PyOptomip.  This script allows the user to select an analysis folder,
% then allows the user to select a wavelength range to be analyzed and
% .mat files to skip, then performs peak finding and Lorentzian fitting to
% each peak and saves the resonator performance data.

clear;
close all;

outPath = 'output_resData'; % subfolder name in which to save output data
dataFilename = 'quantifiedResonatorAnalysis.mat'; % filename for the .mat file
wlFilename = 'wavelengthRanges.xlsx'; % filename for the saved or read in file with the wavelength ranges
waitBetweenDets = 0; % flag to choose whether to wait for user to confirm in between analysis of different detector data
restartAnalysis = 1; % set to 0 to resume previous analysis of this folder, or 1 to redo
useWLFilename = 1; % set to 1 to use the wavelength range file instead of interactive input of the wavelength ranges, if the file exists
figPos = [0 350 1080 450]; % sets the default position of the figure windows [x, y, width, height]

% allow user to select the analysis directory, and generate the file list
selpath = uigetdir;
cd(selpath);
fileList = dir('*.mat');

% read in the wavelength range file if it exists
wlRangeDataExists = 0;
if useWLFilename
    wlFile = dir(['*', wlFilename]);
    if ~isempty(wlFile)
        filename = wlFile(1).name; % choose the first file matching the filename pattern
        filename = strrep(filename, '~$', ''); % if we have found the temporary file, remove those characters so we open the real one
        wavelengthData = readtable(filename); % read in the wavelength ranges
        for fileIdx = 1:size(wavelengthData, 1) % go through the table and store the wavelength range data
            filenames_wavelengths{fileIdx} = cell2mat(wavelengthData{fileIdx, 1});
            wavelengthRanges(fileIdx, :) = cell2mat(cellfun(@str2num,wavelengthData{1,2},'uniform',0)); % start wavelength is the first element, end wavlength is the second
        end
        wlRangeDataExists = 1; % set the flag so that we know we have the data
    end
end


% create the output directory if it does not already exist
if ~exist(outPath, 'dir')
    mkdir(outPath);
    startFile = 1; % start at the beginning of the dataset
else
    if exist([outPath, filesep, dataFilename], 'file') && ~restartAnalysis
        load([outPath, filesep, dataFilename]);
    else
        startFile = 1; % start at the beginning of the dataset
    end
end

% create a counter for the datasets (individual spectra from a detector)
% that have been analyzed)
spectrumNum = 1;
start_idx = [];
end_idx = [];

% loop through the file list to select and analyze the data
for fileIdx = startFile:length(fileList)
    disp(['Analyzing file ', num2str(fileIdx), ' (', fileList(fileIdx).name, ').'])
    
    % clear all reused variables
    clear power wavelength
    
    % load in the data and plot
    load(fileList(fileIdx).name)
    h = figure(1); clf; plt = plot(wavelength*1e9, power); 
    set(h, 'Position', figPos);
    xlabel('Wavelength (nm)'); ylabel('Power (dBm)')
    
    % use the wavelength ranges that we have read in from the file, if we
    % have them and if the filename is in the list
    if wlRangeDataExists
        temp = strfind(filenames_wavelengths, strrep(fileList(fileIdx).name, '.mat', '')); % find the filename in the list of names from the wavelength file
        tempIdx = find(~cellfun(@isempty,temp));
        if length(tempIdx)>1 % check for duplicates
            warning('Found two filename matches in the wavelength range file.  Using the first one.');
            tempIdx = tempIdx(1);
        end
        if ~isempty(tempIdx) % if we found a match, use those wavelength ranges
            start_WL(fileIdx) = wavelengthRanges(tempIdx, 1);
            end_WL(fileIdx) = wavelengthRanges(tempIdx, 2);
            
            % get the indices corresponding to the start and end wavelengths
            [~, start_idx(fileIdx)] = min(abs(wavelength - start_WL(fileIdx)*1e-9));
            [~, end_idx(fileIdx)] = min(abs(wavelength - end_WL(fileIdx)*1e-9));
            
            % truncate the data and plot the new data for review
            power = power(start_idx(fileIdx):end_idx(fileIdx), :);
            wavelength = wavelength(start_idx(fileIdx):end_idx(fileIdx));
            figure(1); clf; plt = plot(wavelength*1e9, power); title(['Wavelength data using input file for ', fileList(fileIdx).name]);
            
            useWLFile(fileIdx) = 1;
        else
            warning(['Did not find a filename match in the wavelength range data for ', fileList(fileIdx).name])
            useWLFile(fileIdx) = 0;
        end
    else
        useWLFile(fileIdx) = 0;
    end
    
    % if we have not already set the bounds in the loaded-in data
    if length(start_idx) < fileIdx && length(end_idx) < fileIdx && ~useWLFile(fileIdx)
        % ask the user to select the data range
        doneFlag = 0;
        while ~doneFlag
            % get the start WL
            title(['File ', num2str(fileIdx), ': Select start wavelength range. Press s to skip analysis of this file.'])
            [x,y,button] = ginput(1);
            if button == 's' || button == 'S'
                doneFlag = 2;
                continue
            else
                hold on; xline(x,':k')
                [~, start_idx(fileIdx)] = min(abs(wavelength - x*1e-9));
                start_WL(fileIdx) = x;
            end

            % get the end WL
            title(['\lambda_{start} = ', num2str(start_WL(fileIdx)), '. Select end wavelength range. Press s to skip analysis of this file.'])
            [x,y,button] = ginput(1);
            if button == 's' || button == 'S'
                doneFlag = 2;
                continue
            else
                hold on; xline(x,':k')
                [~, end_idx(fileIdx)] = min(abs(wavelength - x*1e-9));
                end_WL(fileIdx) = x;
            end

            % truncate the data and plot the new data for review
            power = power(start_idx(fileIdx):end_idx(fileIdx), :);
            wavelength = wavelength(start_idx(fileIdx):end_idx(fileIdx));
            figure(1); clf; plt = plot(wavelength*1e9, power);
            title({'Press r to further crop the data. Press u to revert to original.','Press s to skip analysis of this file. Click or press any other key to accept the range.'})
            [x,y,button] = ginput(1);
            switch button
                case {'s','S'} % skip the file
                    doneFlag = 2;
                    continue
                case {'r','R'} % further crop -- loop again through this user input
                    continue   
                case {'u','U'} % revert to the original data and loop again
                    load(fileList(fileIdx).name)
                    figure(1); clf; plt = plot(wavelength*1e9, power); 
                    xlabel('Wavelength (nm)'); ylabel('Power (dBm)')
                    continue
                otherwise % we are done with WL selection
                    doneFlag = 1;
                    continue
            end
        end

        % skip this file, move onto the next iteration of the loop
        if doneFlag == 2
            continue
        end
    end
    
    % prepare the wavelength range data to be saved in the output file
    filename_wlOutput{fileIdx} = fileList(fileIdx).name;
    wlRange_wlOutput{fileIdx} = [num2str(start_WL(fileIdx)), ', ', num2str(end_WL(fileIdx))];
    
    % loop through all of the power datasets (corresponding to the
    % different detectors with measurements saved in this .mat file)
    for detIdx = 1:size(power, 2)
        disp(['Analyzing data for detector ', num2str(detIdx), '.']);
        % do the peakfinding and Lorentzian fit to quantify resonator performance
        [numPeaks, avg_ER, avg_ER_fit, avg_Q, detFSR, detFSR_err, resFinesse, resLocs, resERs, resERs_fit, resFWHMs, resQs, resfitParams, resGofs] = analyze_resonance(wavelength, power(:,detIdx)');
        % save the figure and wait for user input to continue
        h2 = figure(2);
        set(h2, 'Position', figPos);
        fname = strrep(fileList(fileIdx).name, '.mat', '');
        title([fname, ' detector ', num2str(detIdx), ' peaks']);
        saveas(h2, [outPath, filesep, fname, '_det', num2str(detIdx), '_fitPlot.fig']);
        saveas(h2, [outPath, filesep, fname, '_det', num2str(detIdx), '_fitPlot.svg']);
        saveas(h2, [outPath, filesep, fname, '_det', num2str(detIdx), '_fitPlot.png']);
        if numPeaks>0
            h3 = figure(3);
            set(h3, 'Position', figPos);
            fname = strrep(fileList(fileIdx).name, '.mat', '');
            title([fname, ' detector ', num2str(detIdx), ' baseline']);
            saveas(h3, [outPath, filesep, fname, '_det', num2str(detIdx), '_baselinePlot.fig']);
            saveas(h3, [outPath, filesep, fname, '_det', num2str(detIdx), '_baselinePlot.svg']);
            saveas(h3, [outPath, filesep, fname, '_det', num2str(detIdx), '_baselinePlot.png']);
        end
        if numPeaks>0 && ishandle(4)
            h4 = figure(4);
            set(h4, 'Position', figPos);
            fname = strrep(fileList(fileIdx).name, '.mat', '');
            title([fname, ' detector ', num2str(detIdx), ' logPlot']);
            saveas(h4, [outPath, filesep, fname, '_det', num2str(detIdx), '_logPlot.fig']);
            saveas(h4, [outPath, filesep, fname, '_det', num2str(detIdx), '_logPlot.svg']);
            saveas(h4, [outPath, filesep, fname, '_det', num2str(detIdx), '_logPlot.png']);
        end
        commandwindow
        if waitBetweenDets
            input('Press return to continue')
        end
    
        % organize the data to prepare to be stored in a table
        Filename{spectrumNum} = fname;
        Detector(spectrumNum) = detIdx;
        WL_Range{spectrumNum} = [num2str(1e9*min(wavelength)), ', ', num2str(1e9*max(wavelength))];
        numResonances(spectrumNum) = numPeaks;
        avgER(spectrumNum) = avg_ER;
        avgER_fit(spectrumNum) = avg_ER_fit;
        avgQ(spectrumNum) = avg_Q;
        FSR(spectrumNum) = detFSR;
        FSR_err(spectrumNum) = detFSR_err;
        Finesse(spectrumNum) = resFinesse;
        Resonance_WL{spectrumNum} = resLocs;
        ERs{spectrumNum} = resERs;
        ERs_fit{spectrumNum} = resERs_fit;
        FWHMs{spectrumNum} = resFWHMs;
        Qs{spectrumNum} = resQs;
        fitParams{spectrumNum} = resfitParams;
        GOFs{spectrumNum} = resGofs;
        if isstruct(resGofs)
            temp_rsq = [resGofs.rsq];
            temp_rsq_peak = [resGofs.rsq_peak];
            Rsq{spectrumNum} = temp_rsq;
            Rsq_peak{spectrumNum} = temp_rsq_peak;
            Rsq_avg{spectrumNum} = mean(nonzeros(temp_rsq(~isnan(temp_rsq))));
            Rsq_std{spectrumNum} = std(nonzeros(temp_rsq(~isnan(temp_rsq))));
            Rsq_peak_avg{spectrumNum} = mean(nonzeros(temp_rsq_peak(~isnan(temp_rsq_peak))));
            Rsq_peak_std{spectrumNum} = std(nonzeros(temp_rsq_peak(~isnan(temp_rsq_peak))));
        else
            Rsq{spectrumNum} = NaN;
            Rsq_peak{spectrumNum} = NaN;
            Rsq_avg{spectrumNum} = NaN;
            Rsq_std{spectrumNum} = NaN;
            Rsq_peak_avg{spectrumNum} = NaN;
            Rsq_peak_std{spectrumNum} = NaN;
        end
        
        spectrumNum = spectrumNum+1;
    end
    
    % save the wavelength range file
    T_wl = table(Filename',WL_Range');
    T_wl.Properties.VariableNames = [{'Filename'},{'Wavelength Range'}];
    writetable(T_wl, wlFilename);
    
    % organize and save the data in a table format
    T = table(Filename',Detector',WL_Range',numResonances',avgER',avgQ',FSR',FSR_err',Finesse',Rsq_avg',Rsq_std',Rsq_peak_avg',Rsq_peak_std',Resonance_WL',ERs',FWHMs',Qs',Rsq',Rsq_peak', avgER_fit', ERs_fit');
    T.Properties.VariableNames = [{'Filename'},{'Detector'},{'Wavelength Range'},{'Number of Resonances'},{'Average ER'},{'Average Q'},{'FSR'},{'FSR Error'},{'Finesse'},{'Average Rsq'},{'Rsq Stdev'},{'Average Peak Rsq'},{'Peak Rsq Stdev'},{'Resonance Wavelengths'},{'ERs'},{'FWHMs'},{'Qs'},{'R-squareds'},{'Peak region R-squareds'},{'Average ER (from fits)'},{'ERs (from fits)'}];
    writetable(T, [outPath, '/quantifiedResonatorData.xlsx']);
    startFile = fileIdx+1;
    save([outPath, filesep, dataFilename])
    
end

return


%*************************************************************************%
%**                                                                     **%
%**                      Analyze resonances function                    **%
%**                                                                     **%
%*************************************************************************%
%   inputs:
%   - wavelength: a 1D array of wavelengths
%   - power: a 1D array of powers (each power should correspond to a
%     wavelength in wavelengths
%
%   outputs:
%   - numPeaks: an integer containing the number of found resonance peaks
%   - avg_ER: a double containing the average extinction ratio of the peaks
%   - avg_ER_fit: a double containing the average extinction ratio of the
%     peaks, calculated from the Lorentzian fits to the peaks
%   - avg_Q: a double containing the average quality factor of the peaks
%   - FSR: a double containing the average FSR measured from the peaks
%   - FSR_err: a double containing the std of the resonance spacings
%   - finesse: a double containing the resonator finesse
%   - resLocs: a double array containing the measured extinction ratios of the peaks
%   - FWHMs: a double array containing the measured full-width at half max
%     of the peaks from the Lorentzian fits to the peaks
%   - Qs: a double array containing the measured quality factors of the
%     peaks (from Lorentzian fits) 
%   - ERs: a double array containing the measured ERs from the peaks
%   - ERs_fit: a double array containing the measured ERs from the
%     Lorentzian fits to the peaks
%   - fitParams: a structure containing fit parameters and fitted curves
%     for each peak
%   - gofs: a structure containing the goodness of fit parameters for each
%     peak

function [numPeaks, avg_ER, avg_ER_fit, avg_Q, FSR, FSR_err, finesse, resLocs, ERs, ERs_fit, FWHMs, Qs, fitParams, gofs] = analyze_resonance(wavelength, power)
    noiseLevel = -60; % set the threshold for noise: if >half the power values are less than this, don't analyze
    minProminence = 1.5; % min 2 dB ER
    minDistance = 3; % min 1 nm FSR
    useEqualFitWidth = 1; % set to 1 to use a fit window size based on the width of the widest peak in the spectrum.  0 to set per-peak.
    fitWidthMult = 4; % multiplier for the width of the fit window.  E.g., if fitWidthMult is 2, include datapoints encomopassing 2X the estimated peak width on either side of the centre.
    baselineWidthMult = 0.5; % proportion of the peak fitting window to subtract from the spectra for baseline fitting
    resampleFactor = 50; % factor by which to increase the wavelength sampling frequency in the fit
    RsqThresh = 0.7; % threshold for Rsq goodness of fit to decide if it is "good enough" to use for subsequent calculations
    linearizeFit = 1; % set to 0 to run the Lorentzian fit on the decibel (dBm) data; set to 1 to linearize before fitting
    dBThresh = [5,1.5]; % Extinction Ratio threshold for calculating FWHM and Q from fit.  
                      % First element is the dB-scale ER threshold if we are fitting dB scale power; 
                      % Second element is the dB-scale ER threshold if we are fitting linearized power. 
                      % Can only calculate FWHM and Q in dB scale if ER > 3; choose 5 here for safety for dB scale
    useThreshForER = 1; % set to 1 to use the Rsq threshold to determine peaks for ER calculation (peaks with Rsq less than RsqThresh will have their ERs set to NaN)
    use_medFilter = 0; % set to 0 to run peak finder on the raw data. Otherwise, set to a median filter width (e.g., 3 or 5) to median-filter the data prior to peak finding (note that this will reduce ER calculation accuracy).
    correct_powerData.flag = 1; % set to 1 to automatically replace power data in case of anomalous readings
    correct_powerData.badData = -100; % this field holds the anomalous reading to be replaced in the power data
    correct_powerData.repData = -80; % this field holds the new value with which to replace the anomalous reading
    correct_powerData.removeClipping = 0; % set to 1 to remove repeated values in the power matrix corresponding to clipVal
    correct_powerData.clipVal = -80; % this is the power value corresponding to clipped data
    dbg = 0; % plot debug figures of each fit?
    width_scale = 1; % scaling factor to convert from the found peak width (from findpeaks()) to the initial condition for the third Lorentzian fit parameter
    
    % correct the power data for anomalous readings, if we want to do so
    power_pkFind = power;
    if correct_powerData.flag
        power(power == correct_powerData.badData) = correct_powerData.repData;
        power_pkFind = power;
        % if we have clipping (consecutive clipVal floor values), set all
        % of the middle ones to NaNs, leaving the edge ones at clipVal. 
        if correct_powerData.removeClipping 
            duplicateNum = 1;
            dupIndices = [];
            for i=1:length(power)
                if i>1 && i<length(power) && power(i) == correct_powerData.clipVal 
                    % look at the previous and next elements to determine
                    % whether this one should be changed to NaN and store
                    % the index if so
                    if (power(i-1) == correct_powerData.clipVal) && (power(i+1) == correct_powerData.clipVal)
                        dupIndices(duplicateNum) = i;
                        duplicateNum = duplicateNum+1;
                    end
                end
            end
            % now set all consecutive clipVal values to NaN
            power(dupIndices) = NaN;
        end
    end
        
    wavelength = wavelength*1e9; % convert to nm
    
    % find the peaks (median filter the data to remove some of the noise
    % for peak finding only, not subsequent fitting)
    if use_medFilter
        [pks, locs, w, ERs] = findpeaks(medfilt1(-power_pkFind, use_medFilter), wavelength, 'MinPeakProminence', minProminence, 'MinPeakDistance', minDistance, 'WidthReference', 'halfprom');
    else
        [pks, locs, w, ERs] = findpeaks(-power_pkFind, wavelength, 'MinPeakProminence', minProminence, 'MinPeakDistance', minDistance, 'WidthReference', 'halfprom');
    end
    
    % do not do further processing if we did not find any peaks or if
    % spectrum is mostly below the noise threshold
    if length(pks) < 1 || length(find(power<noiseLevel))+length(find(isnan(power))) > length(power)/2 || length(find(isnan(power))) > length(power)/5
        if length(pks) < 1    
            disp('***Warning: No peaks found in spectrum. Skipping analysis.');
        end
        if length(find(power<noiseLevel)) > length(power)/2
            disp('***Warning: Spectrum found to be mostly noise. Skipping analysis.');
        end
        numPeaks = 0;
        avg_ER = NaN;
        avg_ER_fit = NaN;
        avg_Q = NaN;
        FSR = NaN;
        FSR_err = NaN;
        finesse = NaN;
        resLocs = NaN;
        ERs = NaN;
        ERs_fit = NaN;
        FWHMs = NaN;
        Qs = NaN;
        fitParams = NaN;
        gofs = NaN;
        
        % plot the data 
        if linearizeFit
            figure(2); clf; plot(wavelength, 10.^(power./10), '.k'); % plot on linearized scale
            xlabel('Wavelength (nm)'); ylabel('Power (mW)')
        else
            figure(2); clf; plot(wavelength, power, '.k'); % plot on dB scale
            xlabel('Wavelength (nm)'); ylabel('Power (dBm)')
        end
        return
    end
    numPeaks = length(pks);
    
    % polynomial-fit the non-peak data and subtract the polynomial fit to
    % correct for the GC response
    baseline = power;
    % remove the peaks from the power spectrum
    for pkIdx = 1:numPeaks
        % get the x- and y-data around the peak to be fitted
        [~, pkCentreIdx] = min(abs(wavelength - locs(pkIdx)));
        xdiff = mean(diff(wavelength));
        if useEqualFitWidth
            fitWidth = ceil(max(w)*baselineWidthMult*fitWidthMult/xdiff); 
        else
            fitWidth = ceil(w(pkIdx)*baselineWidthMult*fitWidthMult/xdiff); 
        end
        startIdx = max([1, pkCentreIdx-fitWidth]); % start at the first element of the arrays if we don't have enough room for full fit window
        endIdx = min([length(wavelength), pkCentreIdx+fitWidth]); % end at the last element of the arrays if we don't have enough room for full fit window
        baseline((startIdx):(endIdx)) = nan(size(baseline((startIdx):(endIdx))));
        excludeIdx = isnan(baseline);
    end
    
    if length(wavelength(~excludeIdx)) < 5 % if we don't have at least 10 baseline points to fit, write a warning
        warning('***Warning: Not enough non-peak points found to perform baseline correction.');
        baselineCorrected = 0;
    else % else do the baseline correction.
        % do a 3rd degree polynomial fit to the baseline data and subtract it
        % from the power spectrum
        [p, S, mu] = polyfit(wavelength(~excludeIdx), baseline(~excludeIdx), 3);
        figure(3); clf; plot(wavelength, baseline, '.k');
        xlabel('Wavelength (nm)'); ylabel('Baseline Power (dB)')
        hold on; plot(wavelength, polyval(p, wavelength, S, mu), 'c');
        % subtract the polynomial fit from the power
        power = power - polyval(p, wavelength, S, mu);
        baselineCorrected = 1;
    end
    
    % plot the data 
    if linearizeFit
        figure(2); clf; subplot(5, 1, [1 2 3]); plot(wavelength, 10.^(power./10), '.k'); % plot on linearized scale
        xlabel('Wavelength (nm)'); ylabel('Baseline-Subtracted Power (mW)')
    else
        figure(2); clf; subplot(5, 1, [1 2 3]); plot(wavelength, power, '.k'); % plot on dB scale
        xlabel('Wavelength (nm)'); ylabel('Power (dBm)')
    end
    
    % overlay the plotted peaks and start assigning the parameters to be
    % returned (baseline correct plotted peaks with the baseline polynomial fit)
    pks_plot = -pks;
    if baselineCorrected
        pks_plot = pks_plot-polyval(p, locs, S, mu);
    end
    if linearizeFit
        hold on; plot(locs, 10.^(pks_plot./10), 'm^')
        % also plot the dB-scale data for troubleshooting
        figure(4); clf; plot(wavelength, power, '.k'); % plot on dB scale
        xlabel('Wavelength (nm)'); ylabel('Power (dBm)')
        hold on; plot(locs, pks_plot, 'm^'); 
        figure(2);
    else
        hold on; plot(locs, pks_plot, 'm^')
    end
    
    % Lorentzian-fit each peak and then plot and strore the fitted parameters
    for pkIdx = 1:numPeaks
        % get the x- and y-data around the peak to be fitted
        [~, pkCentreIdx] = min(abs(wavelength - locs(pkIdx)));
        xdiff = mean(diff(wavelength));
        if useEqualFitWidth
            fitWidth = ceil(max(w)*0.5*fitWidthMult/xdiff); 
        else
            fitWidth = ceil(w(pkIdx)*0.5*fitWidthMult/xdiff); 
        end
        startIdx = max([1, pkCentreIdx-fitWidth]);  % start at the first element of the arrays if we don't have enough room for full fit window
        endIdx = min([length(wavelength), pkCentreIdx+fitWidth]); % end at the last element of the arrays if we don't have enough room for full fit window
        x = wavelength((startIdx):(endIdx));
        y = -power((startIdx):(endIdx));
        if dbg
            disp(['****** fitting an array of ', num2str(length(y)), ' points with ', num2str(length(nonzeros(isnan(y)))), ' NaNs.']);
        end
        
        
        % fit the data using the lorentzfit() file exchange function by
        % Jared Wells https://www.mathworks.com/matlabcentral/fileexchange/33775-lorentzfit-x-y-varargin
        % either linearize the data or run the fit directly on the
        % decibel-scale (dBm) power, depending on our flag.
        if linearizeFit
            % linearize and normalize the power data
            y = 10.^(-y./10); % linearize the power data
            ymax = max(y);
            y = 1-y/ymax; % normalize the power data and turn it into a positive peak
            % remove the NaNs from the data to be fitted
            x_nonan = x(~isnan(y));
            y_nonan = y(~isnan(y));
            
            if length(y_nonan) < 5 % if we don't have enough datapoints to fit, don't attempt the fit.
                disp(['***Peak ', num2str(pkIdx), ' warning: could not fit the data because there were insufficient non-NaN datapoints.']);
                FWHMs(pkIdx) = NaN;
                Qs(pkIdx) = NaN;
                gofs(pkIdx).rsq_peak = NaN;
                ERs_fit(pkIdx) = NaN;
                if useThreshForER
                    ERs(pkIdx) = NaN;
                end
                continue
            end
            
            % set up the linearized starting values and bounds and run the
            % fit
            p0 = [(max(y_nonan)-min(y_nonan))*w(pkIdx)/width_scale, locs(pkIdx), w(pkIdx)/width_scale, min(y_nonan)]; % starting values for the fit
            bounds = [0, min(x), 0, 0; inf, max(x), 10*w(pkIdx), max([5*max(y_nonan), 10])]; % bounds for the fit parameters
            [~, fitpar, resnorm, res, jacobian] = lorentzfit(x_nonan,y_nonan,p0,bounds);
            if dbg
                xfit = min(x):xdiff/resampleFactor:max(x);
                yfit = (fitpar(1)./((xfit - fitpar(2)).^2 + fitpar(3)) + fitpar(4));
                yfit_start = (p0(1)./((xfit - p0(2)).^2 + p0(3)) + p0(4));
                disp(['****** fitted ', num2str(length(y_nonan)), ' points.   max(y_nonan) = ', num2str(max(y_nonan)), ', min(y_nonan) = ', num2str(min(y_nonan))])
                disp(['****** pkW from peakfinder = ', num2str(w(pkIdx)), ', Lorentzian width = ', num2str(fitpar(3))])

                h_temp = figure(100); set(h_temp, 'Position', [1569 239 560 420]);
                clf; plot(x_nonan, y_nonan, '.k'); hold on; plot(xfit, yfit, 'm'); hold on; plot(xfit, yfit_start, 'g')
                title(['Debug fit plot for peak ', num2str(pkIdx)]); xlabel('Wavelength (nm)'), ylabel('Normalized power');
                legend([{'Data'}, {'Fitted curve'}, {'Fit initial conditions'}])
                figure(2);
            end
        else
            % remove the NaNs from the data to be fitted
            x_nonan = x(~isnan(y));
            y_nonan = y(~isnan(y));
            p0 = [-ERs(pkIdx), locs(pkIdx), w(pkIdx), max(y_nonan)]; % starting values for the fit
            bounds = [0, min(x), 0, 0; inf, max(x), 10*w(pkIdx), max([5*max(y), 10])]; % bounds for the fit parameters
            [~, fitpar, resnorm, res, jacobian] = lorentzfit(x_nonan,y_nonan,p0,bounds);
        end
        
        % get higher-res yfit data and plot overlay, and calculate
        % fit-calculated ERs
        xfit = min(x):xdiff/resampleFactor:max(x);
        yfit = -(fitpar(1)./((xfit - fitpar(2)).^2 + fitpar(3)) + fitpar(4));
        subplot(5, 1, [1 2 3]); 
        if linearizeFit
            yfit = (1+yfit); % convert back to a negative peak in linear normalized scale and plot
            plot(xfit, yfit*ymax, 'm'); 
            figure(4)
            hold on;
            
            yfit_log = 10*log10(yfit*ymax);
            plot(xfit, yfit_log, 'm'); % plot the dB-scale version of the fit as well
            %ERs_fit(pkIdx) = abs(min(yfit_log)-max(yfit_log));
            ERs_fit(pkIdx) = 10*(log10(ymax*(1-fitpar(1)/fitpar(3)-fitpar(4))))-10*log10(ymax*(1-fitpar(4)));
            figure(2);
        else
            plot(xfit, yfit, 'm');
            ERs_fit(pkIdx) = abs(min(yfit)-max(yfit));
        end
        
        % compute the R^2, store in gof alongside other gof parameters
        gofs(pkIdx).res = res;
        gofs(pkIdx).jac = jacobian;
        gofs(pkIdx).resnorm = resnorm;
        gofs(pkIdx).rsq = 1-sum(res.^2)/sum((y_nonan-mean(y_nonan)).^2);
        
        % plot the residuals
        subplot(5, 1, 5); hold on; plot(x_nonan, res, '.k'); 
        if linearizeFit
            xlabel('Wavelength (nm)'); ylabel([{'Lorentzian fit residuals'}; {'(baseline-subtracted mW)'}]);
        else
            xlabel('Wavelength (nm)'); ylabel([{'Lorentzian fit residuals'}; {'(baseline-subtracted dBm)'}]);
        end
        
        %*** compute the resonator properties ***%
        % resonance wavelength
        if gofs(pkIdx).rsq > RsqThresh % only use the Lorentzian data if the fit is good
            [~, minIdx] = min(yfit);
            resLocs(pkIdx) = xfit(minIdx);
        else
            disp(['***Peak ', num2str(pkIdx), ' warning: using raw peak location (no Lorentzian) due to low R^2 of fit.']);
            resLocs(pkIdx) = locs(pkIdx); % otherwise use the found peak from the peakfinder
        end
        
        % quality factor
        % calculate the FWHM (in dBm scale this is calculated at 3 dB below the baseline)
        if gofs(pkIdx).rsq > RsqThresh % only use the Lorentzian data if the fit is good
            if ERs(pkIdx) > dBThresh(linearizeFit+1) % can only calculate FWHM and Q in dB scale if ER > 3.  Test the ER against our defined threshold (defined as an array since different thresholds for linear and dB scale).
                if linearizeFit
                    temp = find(yfit < mean([max(yfit),min(yfit)])); % find array indices where yfit (to the normalized data) is < 0.5
                    FWHMs(pkIdx) = abs(xfit(temp(1))-xfit(temp(end))); % FWHM is the wavelength difference between the first and last element
                    subplot(5, 1, [1 2 3]); line([xfit(temp(1)),xfit(temp(end))],[(mean([max(yfit),min(yfit)])*ymax),(mean([max(yfit),min(yfit)])*ymax)], 'Color', 'm', 'LineStyle', ':', 'LineWidth', 3); % draw the FWHM on the axis
                    yplot = (1-y_nonan)*ymax;
                else
                    temp = find(yfit < -(fitpar(4)+3)); % find array indices where yfit is < 3 dB below baseline
                    FWHMs(pkIdx) = abs(xfit(temp(1))-xfit(temp(end))); % FWHM is the wavelength difference between the first and last element
                    subplot(5, 1, [1 2 3]); line([xfit(temp(1)),xfit(temp(end))],[(-fitpar(4)-3),(-fitpar(4)-3)], 'Color', 'm', 'LineStyle', ':', 'LineWidth', 3); % draw the FWHM on the axis
                    yplot = -y_nonan;
                end
                
                Qs(pkIdx) = resLocs(pkIdx)/FWHMs(pkIdx); % Q is approx. by res wavelength divided by FWHM wavelength diff
                %temp2 = find(yfit < (min(yfit)+0.75*(max(yfit)-min(yfit)))); % find array indices where yfit (to the normalized data) is < 75% of the way to the baseline
                %FWHM_indices = find((x > xfit(temp2(1))) & (x < xfit(temp2(end)))); % turn the fit indices into data indices
                FWHM_indices = find((x_nonan > resLocs(pkIdx)-FWHMs(pkIdx)) & (x_nonan < resLocs(pkIdx)+FWHMs(pkIdx))); % calculate peak R^2 over the region one linewidth on either sideof the FWHM
                gofs(pkIdx).rsq_peak = 1-sum(res(FWHM_indices).^2)/sum((y_nonan(FWHM_indices)-mean(y_nonan(FWHM_indices))).^2); % compute the "peak region R-squared" as the R-squared of the fit in the peak region (one FWHM on either side of the centre)
                subplot(5, 1, 5); hold on; plot(x_nonan(FWHM_indices), res(FWHM_indices), '.b') % plot the residuals used in the peak region R^2 generation as blue
                subplot(5, 1, [1 2 3]); hold on; plot(x_nonan(FWHM_indices), yplot(FWHM_indices), '.b') % plot the datapoints used in the peak region R^2 generation as blue
            else
                disp(['***Peak ', num2str(pkIdx), ' warning: could not calculate FWHM and Q due to low ER.']);
                FWHMs(pkIdx) = NaN;
                Qs(pkIdx) = NaN;
            end
        else
            disp(['***Peak ', num2str(pkIdx), ' warning: could not calculate FWHM and Q due to low R^2 of fit.']);
            FWHMs(pkIdx) = NaN;
            Qs(pkIdx) = NaN;
            gofs(pkIdx).rsq_peak = NaN;
            ERs_fit(pkIdx) = NaN;
            if useThreshForER
                ERs(pkIdx) = NaN;
            end
        end  
       
        % fit parameters
        fitParams{pkIdx} = fitpar;
    end
    
    % calculate the averages
    % Q
    if any(~isnan(Qs))
        avg_Q = mean(Qs, 'omitnan');
    else
        avg_Q = NaN;
    end
    % FSR
    resSpacings = diff(resLocs); % find the difference between neighboring resonances
    resSpacingsTrunc = rmoutliers(resSpacings); % remove outliers (missed peaks or noise peaks)
    FSR = mean(resSpacingsTrunc); % FSR is the average spacing after removing outliers
    FSR_err = std(resSpacingsTrunc); % note the error in FSR as well
    % finesse
    if any(~isnan(Qs))
        finesse = FSR/mean(FWHMs, 'omitnan');
    else
        finesse = NaN;
    end
    % ER
    if any(~isnan(ERs))
        avg_ER = mean(ERs(~isnan(ERs)));
    else
        avg_ER = NaN;
    end
    % ER from fit
    if any(~isnan(ERs_fit))
        avg_ER_fit = mean(ERs_fit(~isnan(ERs_fit)));
    else
        avg_ER_fit = NaN;
    end
    % set the xlims to be the same for plots and residuals.
    subplot(5, 1, [1 2 3]); xlim([min(wavelength), max(wavelength)]);
    subplot(5, 1, 5); xlim([min(wavelength), max(wavelength)]);
end
