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
filepath = fullfile(uigetdir, filesep);
fileExtension = '.jpg';
fileList = dir([filepath, '*', fileExtension]);

% check that we find enough .jpgs and throw an error if not
if length(fileList < 2)
    error(['Error: Less than two ', fileExtension, ' files were found in ', filepath, '.']);
end
% Assume filename format like "Image1.jpg", where "Image" is filenameBase
% and "1" is the index.  Assume no numbers in the filename base
for fileIdx = 1:length(fileList)
    % split out the text and the numbers from the string
    fileListNum(fileIdx) = str2double(regexp(fileList(fileIdx).name,'[\d.]+','match')); % get the number out of the string
    if fileIdx == 1 % get the base of the filename
        filenameBase = strrep(fileList(fileIdx).name, num2str(fileListNum(fileIdx)), ''); % remove the number from the string
        filenameBase = strrep(filenameBase, fileExtension, ''); % remove the extension from the string
    end
end
% sort the filenames
fileListNum = sort(fileListNum, 'ascend');

% remake the list of filenames in the correct numerical order
for fileIdx = 1:length(fileList)
    % combine the filename base, new sorted list of numbers, and file
    % extension to make the new list of filenames
    fileList(fileIdx).name = [filenameBase, num2str(fileListNum(fileIdx)), fileExtension];
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