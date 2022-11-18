%*************************************************************************%
%**                                                                     **%
%**                     BulkRI Baseline Calibration                     **%
%**                                                                     **%
%**                             2021-10-20                              **%
%**                         Mohammed Al-Qadasi                          **%
%**         Inspired from (Samantha M. Grist)'s scripts                 **%
%**                                                                     **%
%*************************************************************************%

% This script prompts the user select a .mat file that includes the
% resonance peak shifts, (typically peakShifts.mat exported from the
% retrospective_analysis_gui.pyw), plots the peak shifts then prompts the
% user to select some points from the resonance shift figure. These points
% will be use to create a baseline for calibration. 

set(0,'DefaultFigureWindowStyle','docked')
set(gca,'fontsize',16)
clc
clear

% allow user to select the peakshifts file
[filename filepath] = uigetfile;
peakShiftsfile = string(filepath) + string(filename);
load(peakShiftsfile);

% Find the number of files with peakshifts, (with prefix "power_*")
NumPeakTracks= who('power_*');
disp("The following "+ length(string(NumPeakTracks)) + " ararys are to be analyzed:")
disp(string(NumPeakTracks));

for j=1:length(string(NumPeakTracks))
    peak_shift_data = eval(cell2mat(NumPeakTracks(j)));
    figure(1); clf
    plot(peak_shift_data, 'linewidth',2); grid on;hold on;pause(0.1);
    xlim('tight'); set(gca, 'fontsize', 14);

    disp("Processing: "+ string(cell2mat(NumPeakTracks(j))));

     title({'Press s to skip analysis of this file.','Click or press any other key to proceed with data calibration.'}); pause(0.01);
     [x,y,button] = ginput(1);
    switch button
        case {'s','S'} % skip the file
            continue
        otherwise % do nothing
    end

    % Prompt user to select points of baseline
    title({'Zoom into the region of interest, then enter the number of points','to be selected from the measured data','for baseline calibration in the Command Window!'})
    prompt = "Enter the number of points to be selected from the measured data for baseline calibration: ";
    NumPoints = input(prompt);
    
    for i=1:NumPoints
        title("Click on point # "+ i);
        [x(i) , y(i), button] = ginput(1);
        x(i) = uint64(x(i));
        plot(x(i), y(i), "r*");
    end
    title([]);
        
    t_array = [1:length(eval(cell2mat(NumPeakTracks(1))))];
    
    % Polynomial fitting 
    [p, S, mu] = polyfit(x, y, 2);
    plot(t_array, polyval(p, t_array, S, mu), ':m');
    % subtract the polynomial fit from the Bulk RI signal
    peak_shift_data_calibrated = peak_shift_data(1) + peak_shift_data - polyval(p, t_array, S, mu);
    % Save data to same variable name
    eval(char([string((cell2mat(NumPeakTracks(j)))) + " = " + "peak_shift_data_calibrated;"]));
    
    figure
    plot(t_array, peak_shift_data_calibrated, 'k','linewidth',2);grid on;hold on; pause(0.1);
    xlim('tight'); set(gca, 'fontsize', 12);

    % Save/append output
    if(j==1) save(strrep(peakShiftsfile, '.mat', '_modified.mat') ,char(string((cell2mat(NumPeakTracks(j))))) ,'t_array');
    else     save(strrep(peakShiftsfile, '.mat', '_modified.mat') ,char(string((cell2mat(NumPeakTracks(j))))) ,'t_array','-v7.3','-append');
    end
end

