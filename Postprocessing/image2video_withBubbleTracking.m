%*************************************************************************%
%**                                                                     **%
%**               Create a video from the captured images               **%
%**           and track intensity changes in user-selected regions      **%
%**                                                                     **%
%**                             2021-05-13                              **%
%**                         Mohammed Al-Qadasi                          **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%
%
% This script prompts the user to :
% 1- select a folder that contains .jpg images. Based on the settings
% listed in this script, the images will be sorted, animated with the
% desired settings and saved as an .avi format.  
% 2- select a region where intensity can be tracked. This is helpful to
% inspect the changes due to bubble formations.

warning('off','all')
clear
clc
save_vid            = 1; % 1: save
outputVid_filename  = 'vid3';
FrameRate           = 32; % images per second (output video frame rate)
image_timelapse_sec = 10; % timelapse of original camera capture
pause_time          = 0.0000001; % pause for visualization when the script is running
file_selection      = 1   ; % 0:select files , 1:select a folder with files
brightness_gain     = 1;  % increase/decrease the brightness of  the image
useImageTimeStamps  = 1;  % 1:obtain timestamp of image file to get the absolute time
trackBubbles        = 1;  % 0: Convert image to video without tracking bubbles
numChannels         = 2;  % Number of tracking windows
showTrackBoundries  = 1;  % Show selected region boundries in the video
Figure_number       = 10; % number of figure in matlab to avoid clearing other figures
Detection_algorithm = 2;  
% Detection Algorithm: 
% 1:Average of window intensities, 
% 2(default):Maximum value in the chosen window, 
% 3:average change in consecuetive window intensities, 
% 4:Maximum change in consecuetive window intensities 
% 5:average change between the current window frame and very first window 
% 6:Maximum change between the current window frame and very first window  

% File Selection
if(file_selection==0)
[filename_array,path] = uigetfile('*.jpg','Select One or More Files', 'MultiSelect', 'on');
filename_array = string(filename_array);
filename_array = sort(filename_array);
filename_arrayx = path + filename_array;
elseif(file_selection==1)
disp("Select the folder that includes the list of images!");
path = uigetdir('');
FilesMetaData = dir([path,'/*.jpg']);% selects all jpg files in the directory
for i =0:length(FilesMetaData)-1
    filename_array(i+1)=string(FilesMetaData(i+1).folder)+'/'+string(FilesMetaData(i+1).name);
end
filename_array = natsortfiles(filename_array); %sort
end
if(endsWith(path,'/')==0)
    path=[path '/'];
end
addpath(path);

%path= '/Users/mohammedalqadasi/Downloads/';
video_filename = [path outputVid_filename];file_number=1;
while(exist([video_filename '.avi'], 'file')) % Avoiding video overwrite
   video_filename = [video_filename '_' char(string(file_number)) '.avi']; 
   file_number=file_number+1;
end 
bubbles_filename = [path 'detected_bubbles'];file_number=1;
while(exist([bubbles_filename '.mat'], 'file')) % Avoiding file overwrite
   bubbles_filename = [bubbles_filename '_' char(string(file_number)) '.mat']; 
   file_number=file_number+1;
end 

if (save_vid==1)
% To create .avi file for moving plot
myVideo = VideoWriter(video_filename); %open video file
myVideo.FrameRate = FrameRate;  %can adjust this, 5 - 10 works well for me
open(myVideo)
end

figure(Figure_number)
clf
subplot(2,numChannels,[1,1+2*(numChannels-1)])
imshow(brightness_gain*imread(filename_array(1)))
pause(pause_time); axis off;
subplot(2,numChannels,2)
xline(0); hold on; ylim([0 256]);xlim([1 length(filename_array)]);
xlabel('Data points'); ylabel({'Window#1','Pixel Intensity'})
set(gca,'fontsize', 14)
if(numChannels==2)
subplot(2,numChannels,4)
xline(0); hold on; ylim([0 256]);xlim([1 length(filename_array)]);
xlabel('Data points'); ylabel({'Window#2','Pixel Intensity'})
set(gca,'fontsize', 14)
end
subplot(2,numChannels,[1,1+2*(numChannels-1)])

if(useImageTimeStamps==1)
    fileList = dir([path,'/*.jpg']);% selects all jpg files in the directory
    x=struct2table(fileList); fileListName=natsort(table2array(x(:,1)));
    for i =1:length(fileList)
%         Image_Suffix=strip(extractBetween(fileList(1).name,"",".jpg"));
%         Image_Suffix=char(regexprep(Image_Suffix,'\d+$',''));
%         fileList(i).name = [Image_Suffix, num2str(i), '.jpg'];
        fileList(i).name = char(fileListName(i));
    end
    % get the initial time (time of first image)
    info = imfinfo([path, fileList(1).name]);
    initTimeStr = info.FileModDate;
    t0 = datetime(initTimeStr);
end

if(trackBubbles==1) % Prompt the user to select a region in the image to track intensity
    for i=1:numChannels
title({['Window #' char(string(i))],'Select a rectangular region where bubbles are expected to pass!','Click on the Upper Left corner!'});
[x1(i),y1(i),button] = ginput(1)
title({'Select a rectangular region where bubbles are expected to pass!','Click on the Lower Right corner!'});
[x2(i),y2(i),button] = ginput(1)
title(['Window1: Blue, Window2: Red']);
x1(i) = uint32(x1(i)); x2(i) = uint32(x2(i)); y1(i) = uint32(y1(i)); y2(i) = uint32(y2(i));
hold on; fill([x1(i) x2(i) x2(i) x1(i)],[y1(i) y1(i) y2(i) y2(i)],'red','facealpha',0.25);
%xline(x1,'w');xline(x2,'w');yline(y1,'w');yline(y2,'w');pause(0.1)

box=plot([x1(i) x1(i)],[y1(i) y2(i)],'-w',[x2(i) x2(i)],[y1(i) y2(i)],'-w',[x1(i) x2(i)],[y1(i) y1(i)],'-w',[x1(i) x2(i)],[y2(i) y2(i)],'-w');pause(0.1)
    end
end

ImageMagnitude1=nan*zeros(1,length(filename_array));
ImageMagnitude2=nan*zeros(1,length(filename_array));

startTime=datetime;
for i=1:length(filename_array)-1
    disp("Processing image: "+ string(fileList(i).name) + ", from a pool of "+string(length(fileList))+" images.")
    I =brightness_gain*imread(filename_array(i));

    if(useImageTimeStamps==1)
        info = imfinfo([path, fileList(i).name]);
        t{i} = datetime(info.FileModDate);
        videoTime{i} = t{i} - t0;
        timeStr = char(videoTime{i});
    else
        timeStr = ['Time = ' char(string(round(image_timelapse_sec*i/60,0))) 'min'];
    end    

    annotationPos = [0, 120, 150, 0];  %[0, 120, 400, 0]  
    IAnnotated = insertObjectAnnotation(I,'rectangle',annotationPos,timeStr,...
    'Color', 'yellow', 'TextBoxOpacity',0.6,'FontSize',60);
    imshow(IAnnotated);
    
    if(trackBubbles)         
        ImageWindow1= I([y1(1):y2(1)],[x1(1):x2(1)],:); 
        if(Detection_algorithm==1)
            ImageMagnitude1(i) = sum(sum(sum(ImageWindow1)))/((x2(1)-x1(1))*(y2(1)-y1(1))*3); %(Sum of pixel values)/(# of pixels) 
        elseif(Detection_algorithm==2)
            ImageMagnitude1(i) = max(max(max(ImageWindow1)));  % Max. value in the window
        elseif(Detection_algorithm==3)
            NextImageWindow1 =brightness_gain*imread(filename_array(i+1));
            NextImageWindow1 = NextImageWindow1([y1(1):y2(1)],[x1(1):x2(1)],:);
            ImageMagnitude1(i)  = sum(sum(sum(NextImageWindow1-ImageWindow1)))/((x2(1)-x1(1))*(y2(1)-y1(1))*3); 
        elseif(Detection_algorithm==4)
            NextImageWindow1 =brightness_gain*imread(filename_array(i+1));
            NextImageWindow1 = NextImageWindow1([y1(1):y2(1)],[x1(1):x2(1)],:); 
            ImageMagnitude1(i)  = max(max(max((NextImageWindow1-ImageWindow1)))); 
        elseif(Detection_algorithm==5)
            FirstImageWindow1 =brightness_gain*imread(filename_array(1));
            FirstImageWindow1 = FirstImageWindow1([y1(1):y2(1)],[x1(1):x2(1)],:); 
            ImageMagnitude1(i)  =  sum(sum(sum(ImageWindow1-FirstImageWindow1)))/((x2(1)-x1(1))*(y2(1)-y1(1))*3);  
        elseif(Detection_algorithm==6)
            FirstImageWindow1 =brightness_gain*imread(filename_array(1));
            FirstImageWindow1 = FirstImageWindow1([y1(1):y2(1)],[x1(1):x2(1)],:); 
            ImageMagnitude1(i)  = max(max(max((ImageWindow1-FirstImageWindow1)))); 
        else
            ImageMagnitude1(i) = max(max(max(ImageWindow1)));  % Max. value in the window
        end

        if(numChannels==2)
        ImageWindow2 = I([y1(2):y2(2)],[x1(2):x2(2)],:); 
        if(Detection_algorithm==1)
            ImageMagnitude2(i) = sum(sum(sum(ImageWindow2)))/((x2(2)-x1(2))*(y2(2)-y1(2))*3); %(Sum of pixel values)/(# of pixels) 
        elseif(Detection_algorithm==2)
            ImageMagnitude2(i) = max(max(max(ImageWindow2)));  % Max. value in the window
        elseif(Detection_algorithm==3)
            NextImageWindow2 =brightness_gain*imread(filename_array(i+1));
            NextImageWindow2 = NextImageWindow2([y1(2):y2(2)],[x1(2):x2(2)],:);
            ImageMagnitude2(i)  = sum(sum(sum(NextImageWindow2-ImageWindow2)))/((x2(2)-x1(2))*(y2(2)-y1(2))*3); 
        elseif(Detection_algorithm==4)
            NextImageWindow2 =brightness_gain*imread(filename_array(i+1));
            NextImageWindow2 = NextImageWindow2([y1(2):y2(2)],[x1(2):x2(2)],:); 
            ImageMagnitude2(i)  = max(max(max((NextImageWindow2-ImageWindow2)))); 
        elseif(Detection_algorithm==5)
            FirstImageWindow2 =brightness_gain*imread(filename_array(1));
            FirstImageWindow2 = FirstImageWindow2([y1(2):y2(2)],[x1(2):x2(2)],:); 
            ImageMagnitude2(i)  =  sum(sum(sum(ImageWindow2-FirstImageWindow2)))/((x2(2)-x1(2))*(y2(2)-y1(2))*3);  
        elseif(Detection_algorithm==6)
            FirstImageWindow2 =brightness_gain*imread(filename_array(1));
            FirstImageWindow2 = FirstImageWindow2([y1(2):y2(2)],[x1(2):x2(2)],:); 
            ImageMagnitude2(i)  = max(max(max((ImageWindow2-FirstImageWindow2)))); 
        else
            ImageMagnitude2(i) = max(max(max(ImageWindow2)));  % Max. value in the window
        end

        end
    end
    if(showTrackBoundries==1) 
        %uistack(box,'top'); 
        box=plot([x1(1) x1(1)],[y1(1) y2(1)],'-b',[x2(1) x2(1)],[y1(1) y2(1)],'-b',[x1(1) x2(1)],[y1(1) y1(1)],'-b',[x1(1) x2(1)],[y2(1) y2(1)],'-b');
        hold on
        if(numChannels==2)
        box=plot([x1(2) x1(2)],[y1(2) y2(2)],'-r',[x2(2) x2(2)],[y1(2) y2(2)],'-r',[x1(2) x2(2)],[y1(2) y1(2)],'-r',[x1(2) x2(2)],[y2(2) y2(2)],'-r');pause(0.1);
        end
    end
    
    subplot(2,numChannels,2)
    plot([1:length(filename_array)],ImageMagnitude1, 'b','linewidth',0.5, 'MarkerFaceColor','k','MarkerSize',3)
    if(Detection_algorithm>2) ylim('tight');  end
    if(numChannels==2)
    subplot(2,numChannels,4)
    plot([1:length(filename_array)],ImageMagnitude2, 'r','linewidth',0.5, 'MarkerFaceColor','r','MarkerSize',3)
    if(Detection_algorithm>2) ylim('tight');  end
    end
    subplot(2,numChannels,[1,1+2*(numChannels-1)])
ylim('tight')



    if(save_vid ==1)
    frame = getframe(gcf); %get frame
    writeVideo(myVideo, frame);
    end
end
elapsedTime= datetime - startTime;

if(save_vid==1)
%Close video file
close(myVideo)
end
disp("image2video_withBubbleTracking, Done!"+", Script runtime="+string(elapsedTime))
commandwindow;
t_array = table2array(cell2table(t));
time_axis_mins = month(t_array).*(30*24*60) + day(t_array).*(24*60) + hour(t_array).*60 + minute(t_array) + second(t_array)./60; 
time_axis_mins = time_axis_mins - time_axis_mins(1);
interpolated_time_axis_mins = [1:length(ImageMagnitude1)]*image_timelapse_sec/60;
save(bubbles_filename ,'ImageMagnitude1','ImageMagnitude2' ,'interpolated_time_axis_mins','time_axis_mins','videoTime','-v7.3');
