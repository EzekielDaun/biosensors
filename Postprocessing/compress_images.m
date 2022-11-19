%*************************************************************************%
%**                                                                     **%
%**                           Compress Images                           **%
%**                                                                     **%
%**                                                                     **%
%**                             2022-11-09                              **%
%**                         Mohammed Al-Qadasi                          **%
%**                                                                     **%
%*************************************************************************%
% This script prompts the user to select a folder that contains some images
% and an output folder where the compressed images are to be saved.
% If the selected input and output folders are the same, the images will be
% replaced with their compressed versions. 

function []=compress_images()

warning('off', 'all');
imageCompressionThreshold_Mb = 1;
CompressionRatio             = 1/4;

disp(">>Select the folder that includes the images to be compressed!");
imagesFolder = uigetdir(''); addpath(imagesFolder);
imageList=[imagesFolder '\*jpg']; imageList = dir(imageList);
disp("Selected input images folder: "+imagesFolder);

disp(">>Select the output folder where the compressed images are to be saved!");
outputFolder = uigetdir(''); addpath(imagesFolder);
disp("Selected output images folder: "+imagesFolder);

c=struct2cell(imageList)'; c=table2array(cell2table(c(:,4))); largeImages=sum((c/1024/1024)>imageCompressionThreshold_Mb);
disp(string(size(imageList,1))+" images found!")
disp("Large image files (>1MB) = "+string(largeImages)+" images!");

compressedImages=1;
for i=1:size(imageList,1)
    if(imageList(i).bytes/(1024*1024)>imageCompressionThreshold_Mb)
        image = imread(imageList(i).name);
        image_compressed=imresize(image,CompressionRatio);
        compressedFileName =[outputFolder '\' imageList(i).name];
        if(string(imagesFolder)==string(outputFolder))
            tmp = strrep(compressedFileName, '.jpg', '_delete.jpg');
            eval(['delete ' tmp]); 
            imwrite(image_compressed,compressedFileName);
            disp("("+string(compressedImages)+"/"+string(largeImages)+"): Replacing " + string(imageList(i).name) + " with its compressed version!");
        else
            imwrite(image_compressed,compressedFileName);
            disp("Compressing " + string(imageList(i).name));
        end
        compressedImages = compressedImages+1;
    end
end

disp('Image Compression, Done!');

end