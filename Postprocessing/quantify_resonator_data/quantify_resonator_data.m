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
waitBetweenDets = 0; % flag to choose whether to wait for user to confirm in between analysis of different detector data
restartAnalysis = 0; % set to 0 to resume previous analysis of this folder, or 1 to redo
figPos = [0 350 1080 450]; % sets the default position of the figure windows [x, y, width, height]

% allow user to select the analysis directory, and generate the file list
selpath = uigetdir;
cd(selpath);
fileList = dir('*.mat');

% create the output directory if it does not already exist
if ~exist(outPath, 'dir')
    mkdir(outPath);
    startFile = 1; % start at the beginning of the dataset
else
    if exist([outPath, '/', dataFilename], 'file') && ~restartAnalysis
        load([outPath, '/', dataFilename]);
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
    
    % if we have not already set the bounds in the loaded-in data
    if length(start_idx) < fileIdx && length(end_idx) < fileIdx
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
    
    % loop through all of the power datasets (corresponding to the
    % different detectors with measurements saved in this .mat file)
    for detIdx = 1:size(power, 2)
        disp(['Analyzing data for detector ', num2str(detIdx), '.']);
        % do the peakfinding and Lorentzian fit to quantify resonator performance
        [numPeaks, avg_ER, avg_Q, detFSR, detFSR_err, resFinesse, resLocs, resERs, resFWHMs, resQs, resfitParams, resGofs] = analyze_resonance(wavelength, power(:,detIdx)');
        % save the figure and wait for user input to continue
        h2 = figure(2);
        set(h2, 'Position', figPos);
        fname = strrep(fileList(fileIdx).name, '.mat', '');
        title([fname, ' detector ', num2str(detIdx), ' peaks']);
        saveas(h2, [outPath, '/', fname, '_det', num2str(detIdx), '_fitPlot.fig']);
        saveas(h2, [outPath, '/', fname, '_det', num2str(detIdx), '_fitPlot.svg']);
        saveas(h2, [outPath, '/', fname, '_det', num2str(detIdx), '_fitPlot.png']);
        commandwindow
        if waitBetweenDets
            input('Press return to continue')
        end
    
        % organize the data to prepare to be stored in a table
        Filename{spectrumNum} = fname;
        Detector(spectrumNum) = detIdx;
        numResonances(spectrumNum) = numPeaks;
        avgER(spectrumNum) = avg_ER;
        avgQ(spectrumNum) = avg_Q;
        FSR(spectrumNum) = detFSR;
        FSR_err(spectrumNum) = detFSR_err;
        Finesse(spectrumNum) = resFinesse;
        Resonance_WL{spectrumNum} = resLocs;
        ERs{spectrumNum} = resERs;
        FWHMs{spectrumNum} = resFWHMs;
        Qs{spectrumNum} = resQs;
        fitParams{spectrumNum} = resfitParams;
        GOFs{spectrumNum} = resGofs;
        if isstruct(resGofs)
            Rsq{spectrumNum} = [resGofs.rsq];
        else
            Rsq{spectrumNum} = NaN;
        end
        
        spectrumNum = spectrumNum+1;
    end
    
    % organize and save the data in a table format
    T = table(Filename',Detector',numResonances',avgER',avgQ',FSR',FSR_err',Finesse',Resonance_WL',ERs',FWHMs',Qs',Rsq');
    T.Properties.VariableNames = [{'Filename'},{'Detector'},{'Number of Resonances'},{'Average ER'},{'Average Q'},{'FSR'},{'FSR Error'},{'Finesse'},{'Resonance Wavelengths'},{'ERs'},{'FWHMs'},{'Qs'},{'R-squareds'}];
    writetable(T, [outPath, '/quantifiedResonatorData.xlsx']);
    startFile = fileIdx+1;
    save([outPath, '/', dataFilename])
    
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
%   - avg_Q: a double containing the average quality factor of the peaks
%   - FSR: a double containing the average FSR measured from the peaks
%   - FSR_err: a double containing the std of the resonance spacings
%   - finesse: a double containing the resonator finesse
%   - resLocs: a double array containing the measured extinction ratios of the peaks
%   - FWHMs: a double array containing the measured full-width at half max of the peaks
%   - Qs: a double array containing the measured quality factors of the peaks
%   - fitParams: a structure containing fit parameters and fitted curves
%     for each peak
%   - gofs: a structure containing the goodness of fit parameters for each
%     peak

function [numPeaks, avg_ER, avg_Q, FSR, FSR_err, finesse, resLocs, ERs, FWHMs, Qs, fitParams, gofs] = analyze_resonance(wavelength, power)
    minProminence = 2; % min 2 dB ER
    minDistance = 2; % min 1 nm FSR
    fitWidthMult = 7; % multiplier for the width of the fit window.  E.g., if fitWidthMult is 2, include datapoints encomopassing 2X the estimated peak width on either side of the centre.
    resampleFactor = 50; % factor by which to increase the wavelength sampling frequency in the fit
    RsqThresh = 0.8; % threshold for Rsq goodness of fit to decide if it is "good enough" to use for subsequent calculations
    linearizeFit = 1; % set to 0 to run the Lorentzian fit on the decibel (dBm) data; set to 0 to linearize before fitting
    dBThresh = [2,5]; % Extinction Ratio threshold for calculating FWHM and Q from fit.  
                      % First element is the dB-scale ER threshold if we are fitting linearized power; 
                      %second element is the dB-scale ER threshold if we are fitting dB scale power. 
                      %Can only calculate FWHM and Q in dB scale if ER > 3; choose 5 here for safety for dB scale

    % plot the data
    wavelength = wavelength*1e9; % convert to nm
    if linearizeFit
        figure(2); clf; plot(wavelength, 10.^(power./10), '.k'); % plot on linearized scale
        xlabel('Wavelength (nm)'); ylabel('Power (mW)')
    else
        figure(2); clf; plot(wavelength, power, '.k'); % plot on dB scale
        xlabel('Wavelength (nm)'); ylabel('Power (dBm)')
    end
    
    % find the peaks (median filter the data to remove some of the noise
    % for peak finding only, not subsequent fitting)
    [pks, locs, w, ERs] = findpeaks(medfilt1(-power, 5), wavelength, 'MinPeakProminence', minProminence, 'MinPeakDistance', minDistance);
    % do not do further processing if we did not find any peaks
    if length(pks) < 1
        disp('***Warning: No peaks found in spectrum.');
        numPeaks = 0;
        avg_ER = NaN;
        avg_Q = NaN;
        FSR = NaN;
        FSR_err = NaN;
        finesse = NaN;
        resLocs = NaN;
        ERs = NaN;
        FWHMs = NaN;
        Qs = NaN;
        fitParams = NaN;
        gofs = NaN;
        return
    end
    % overlay the plotted peaks and start assigning the parameters to be
    % returned
    if linearizeFit
        hold on; plot(locs, 10.^(-pks./10), 'm^')
    else
        hold on; plot(locs, -pks, 'm^')
    end
    numPeaks = length(pks);
    avg_ER = mean(ERs);
    
    % Lorentzian-fit each peak and then plot and strore the fitted parameters
    for pkIdx = 1:numPeaks
        % get the x- and y-data around the peak to be fitted
        [~, pkCentreIdx] = min(abs(wavelength - locs(pkIdx)));
        xdiff = mean(diff(wavelength));
        fitWidth = ceil(w(pkIdx)*fitWidthMult/xdiff); % start at the first element of the arrays if we don't have enough room for full fit window
        startIdx = max([1, pkCentreIdx-fitWidth]); % end at the last element of the arrays if we don't have enough room for full fit window
        endIdx = min([length(wavelength), pkCentreIdx+fitWidth]);
        x = wavelength((startIdx):(endIdx));
        y = -power((startIdx):(endIdx));
        
        % fit the data using the lorentzfit() file exchange function by
        % Jared Wells https://www.mathworks.com/matlabcentral/fileexchange/33775-lorentzfit-x-y-varargin
        % either linearize the data or run the fit directly on the
        % decibel-scale (dBm) power, depending on our flag.
        if linearizeFit
            % linearize and normalize the power data
            y = 10.^(-y./10); % linearize the power data
            ymax = max(y);
            y = 1-y/ymax; % normalize the power data and turn it into a positive peak
            % set up the linearized starting values and bounds and run the
            % fit
            p0 = [1, locs(pkIdx), w(pkIdx), mean(y)]; % starting values for the fit
            bounds = [0, min(x), 0, 0; inf, max(x), 10*w(pkIdx), 10*mean(y)]; % bounds for the fit parameters
            [~, fitpar, resnorm, res, jacobian] = lorentzfit(x,y,p0,bounds);
        else
            p0 = [-ERs(pkIdx), locs(pkIdx), w(pkIdx), mean(y)]; % starting values for the fit
            bounds = [0, min(x), 0, 0; inf, max(x), 10*w(pkIdx), 10*mean(y)]; % bounds for the fit parameters
            [~, fitpar, resnorm, res, jacobian] = lorentzfit(x,y,p0,bounds);
        end
        
        
        % get higher-res yfit data and plot overlay
        xfit = min(x):xdiff/resampleFactor:max(x);
        yfit = -(fitpar(1)./((xfit - fitpar(2)).^2 + fitpar(3)) + fitpar(4));
        if linearizeFit
            yfit = (1+yfit); % convert back to a negative peak in linear normalized scale and plot
            plot(xfit, yfit*ymax, 'm'); 
        else
            plot(xfit, yfit, 'm');
        end
        
        % compute the R^2, store in gof alongside other gof parameters
        gofs(pkIdx).res = res;
        gofs(pkIdx).jac = jacobian;
        gofs(pkIdx).resnorm = resnorm;
        gofs(pkIdx).rsq = 1-sum(res.^2)/sum((y-mean(y)).^2);
        
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
                    line([xfit(temp(1)),xfit(temp(end))],[(mean([max(yfit),min(yfit)])*ymax),(mean([max(yfit),min(yfit)])*ymax)], 'Color', 'm', 'LineStyle', ':', 'LineWidth', 3); % draw the FWHM on the axis
                else
                    temp = find(yfit < -(fitpar(4)+3)); % find array indices where yfit is < 3 dB below baseline
                    FWHMs(pkIdx) = abs(xfit(temp(1))-xfit(temp(end))); % FWHM is the wavelength difference between the first and last element
                    line([xfit(temp(1)),xfit(temp(end))],[(-fitpar(4)-3),(-fitpar(4)-3)], 'Color', 'm', 'LineStyle', ':', 'LineWidth', 3); % draw the FWHM on the axis
                end
                
                Qs(pkIdx) = resLocs(pkIdx)/FWHMs(pkIdx); % Q is approx. by res wavelength divided by FWHM wavelength diff
            else
                disp(['***Peak ', num2str(pkIdx), ' warning: could not calculate FWHM and Q due to low ER.']);
                FWHMs(pkIdx) = NaN;
                Qs(pkIdx) = NaN;
            end
        else
            disp(['***Peak ', num2str(pkIdx), ' warning: could not calculate FWHM and Q due to low R^2 of fit.']);
            FWHMs(pkIdx) = NaN;
            Qs(pkIdx) = NaN;
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
end
