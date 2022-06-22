%*************************************************************************%
%**                                                                     **%
%**      Prepare video from time-lapse microscope acquisition images    **%
%**                                                                     **%
%**                                                                     **%
%**                             2022-02-23                              **%
%**                         Samantha M. Grist                           **%
%**                                                                     **%
%*************************************************************************%

% find the list of files in the working directory
filepath = '/Users/sgrist/Dropbox/UBC_DP_Biosensor/2022-1/Data/2022-03-14_Silanization_Phase_0_Trial_4/Timelapse/second try/';
fileList = dir([filepath, '*.jpg']);
% for now, force natural order due to the filename format
%fileList(1).name = 'Image.jpg';
% for fileIdx = 2:length(fileList)
%     fileList(fileIdx).name = ['Image', num2str(fileIdx-1), '.jpg'];
% end
for fileIdx = 1:length(fileList)
    fileList(fileIdx).name = ['Image', num2str(fileIdx), '.jpg'];
end
imgScale = 0.25; % how much smaller do we want to make the images for the video?

% set up the video writer
outputVideo = VideoWriter(fullfile(filepath,'timelapse'), 'MPEG-4');
outputVideo.FrameRate = 10; % choose 10 fps
open(outputVideo)

% get the initial time (time of first image)
info = imfinfo([filepath, fileList(1).name]);
initTimeStr = info.FileModDate;
t0 = datetime(initTimeStr);


% loop through all the images in the directory (assume video should be
% ordered by filename, which works by default for our )
for fileIdx = 1:length(fileList)
    disp(fileList(fileIdx).name);
    % read in the image metadata to find the file modification date, and
    % compute elapsed time since the initial time
    info = imfinfo([filepath, fileList(fileIdx).name]);
    t{fileIdx} = datetime(info.FileModDate);
    videoTime{fileIdx} = t{fileIdx} - t0;
    timeStr = char(videoTime{fileIdx});
    
    % read in the image, adjust its size, and annotate with the time
    I = imread([filepath, fileList(fileIdx).name]);
    ISmall = imresize(I, imgScale);
    imgSz = size(ISmall);
    annotationPos = [0, 60, 200, 0];
    
    IAnnotated = insertObjectAnnotation(ISmall,'rectangle',annotationPos,timeStr,...
    'Color', 'cyan', 'TextBoxOpacity',0.6,'FontSize',36);
    
    writeVideo(outputVideo,IAnnotated)
end
close(outputVideo)