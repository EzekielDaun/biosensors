%*************************************************************************%
%**                                                                     **%
%**               `            Detect bubbles                           **%
%**                                                                     **%
%**                                                                     **%
%**                             2022-10-14                              **%
%**                         Mohammed Al-Qadasi                          **%
%**                                                                     **%
%*************************************************************************%
% This function prompts the user to: 
% 1- select a folder that contains .jpg images. 
% 2- select a region where intensity can be tracked. This is helpful to
% inspect the changes due to bubble formations.
% 
% Function: [time_axis_mins, WindowIntensity]=detect_bubbles(ImageList, CaptureTimeLapse_seconds, Detection_algorithm)
% "time_axis_mins": array of time axis [Unit: mins]
% "WindowIntensity": Detected bubbles in the specified window
% "ImageList" : A 4D matrix that represents a series of images.
% "CaptureTimeLapse_seconds": frame rate of the input imageList.
% "Detection_algorithm":  [1:Average of window intensities, 2(default):
% Max. window intensity, 3:Max. change in window intensities]
%
% # Example: 
% ImageList = zeros(256,64,3,'uint8'); ImageList=repmat(ImageList,1 ,1,1,100);
% for(i=1:100) ImageList(100,mod(i,64)+1,:, i) = 255; end 
% figure; for(i=1:100) image(ImageList(:,:,:,i));pause(0.033); end
% [time_axis, detectedBubblePulses] = detect_bubbles(ImageList,30,2);
% figure; plot(time_axis,detectedBubblePulses);xlabel('Time(min));

function [time_axis_mins, WindowIntensity]=detect_bubbles(ImageList, CaptureTimeLapse_seconds, Detection_algorithm)

CaptureTimeLapse_seconds = 30; 
Image = ImageList(:,:,:,1);

% Plot image
figure(1); clf;image(Image); hold on;

% get the user input for this region
title({'Select a rectangular region where bubbles are expected to pass!','Click on the Upper Left corner!'});
[x1,y1,button] = ginput(1);
title({'Select a rectangular region where bubbles are expected to pass!','Click on the Lower Right corner!'});
[x2,y2,button] = ginput(1);
title([]);
x1 = uint32(x1); x2 = uint32(x2); y1 = uint32(y1); y2 = uint32(y2);

figure(1)
fill([x1 x2 x2 x1],[y1 y1 y2 y2],'red','facealpha',0.25);
xline(x1,'w');xline(x2,'w');yline(y1,'w');yline(y2,'w');
pause(0.1)

counter = 1;
for i=1:size(ImageList,4)-1
        Image= ImageList(:,:,:,i);
        ImageWindow = Image([y1:y2],[x1:x2],:);

        % Detection Algorithm: (1:Average of window intensities, 2(default):Max. window intensity, 3:Max. change in window intensities)
        Detection_algorithm=1;
        if(Detection_algorithm==1)
            WindowIntensity(i) = sum(sum(sum(ImageWindow)))/((x2-x1)*(y2-y1)*3);  
        elseif(Detection_algorithm==2)
            WindowIntensity(i) = max(max(max(ImageWindow)));  
        elseif(Detection_algorithm==3)
            Image2= ImageList(:,:,:,i+1);
            ImageWindow2 = Image2([y1:y2],[x1:x2],:);
            WindowIntensity(i)  = sum(sum(sum(ImageWindow2-ImageWindow)))/((x2-x1)*(y2-y1)*3); 
            WindowIntensity(i)  = max(max(max((ImageWindow2-ImageWindow)))); 
        else
            WindowIntensity(i) = max(max(max(ImageWindow)));  
        end
    %else
        %disp("Image: " +['BulkRI' char(string(i)) '.jpg  ->> MISSING !!!!']);
    %end
end

time_axis_mins = [1:size(ImageList,4)-1]*CaptureTimeLapse_seconds/60.0;
disp('Window Detection, Done!')

end