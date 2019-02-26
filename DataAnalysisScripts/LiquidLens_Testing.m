% File to analyze liquid lens focus tracking performance
clear all
close all
% ------------------------------------------------------------------------
% Choose the track file to import
% ------------------------------------------------------------------------
%[filename, pathname] = uigetfile('Y:\Projects\GravityMachine\Y_Tracking_test_30_05_2018\*','Select the Tracks to analyze: ');
[filename, pathname] = uigetfile('Y:\Projects\GravityMachine\Ytracking_31_05_2018\*','Select the Tracks to analyze: ');

if isequal(filename,0)
   disp('User selected Cancel')
else
   disp(['User selected ', fullfile(pathname, filename)])
end

ResultFolder = fullfile(pathname,'Plots');
if (~exist(ResultFolder,'dir'))
    mkdir(ResultFolder)
end

[Time, Xpos, Ypos, Zpos,ImageZcoord, ImageXcoord, ManualTracking, ImageName, FocusMeasure, LensPhase, YmaxFM] = csvimport(strcat(pathname,filename),'columns',{'Time','Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum'});
% [Time, Xpos, Ypos, Zpos,ImageZcoord, ImageXcoord, ManualTracking, ImageName, FocusMeasure] = csvimport(strcat(pathname,filename),'columns',{'Time','Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure'});


Time = Time - min(Time);
SamplingRate_approx = mean(1./(Time(2:end)-Time(1:end-1)));
SamplingRate_stdev = std(1./(Time(2:end)-Time(1:end-1)));
disp('Sampling Rate mean (Hz)');
disp(SamplingRate_approx)
disp('Sampling Rate standard dev (Hz)');
disp(SamplingRate_stdev)
FocusMeasure= FocusMeasure-mean(FocusMeasure);
FocusMeasure = FocusMeasure./max(FocusMeasure);

figure, hold on;
plot(Time(1:end-1),Time(2:end)-Time(1:end-1),'go','LineWidth',1);
title('Time interval between data points')

figure, hold on;
plot(Time,FocusMeasure,'ro-');
title('Focus Measure vs time');

figure, hold on;
plot(Time,Ypos,'ko-','LineWidth',2)
title('Y position vs time');

figure, hold on;
plot(Time,sin(LensPhase),'ko-','LineWidth',1);
title('Lens Phase sin(\phi) vs time');

windowSize = 35;
lensAmp = 0.05;
movMax = runningExtreme(FocusMeasure,windowSize,'max');

% Moving maximum
figure, hold on;
plot(Time,movMax,'ro-','LineWidth',1)

FocusPosition = (lensAmp/2)*sin(LensPhase); 

indexArray = zeros(1,length(movMax));

Y_maximizesFM_theory = zeros(1,length(movMax));

for ii=1:length(movMax)
    indexArray(1,ii) = find(FocusMeasure == movMax(ii));
    Y_maximizesFM_theory(1,ii) = FocusPosition(indexArray(1,ii));
end

% Moving maximum
figure, hold on;
plot(Time,Y_maximizesFM_theory,'ro-','LineWidth',1)


figure, hold on;
plot(Time,indexArray,'go');





    

figure, hold on;
plot(Time,YmaxFM,'ro','LineWidth',1);
title('Y position that maximizes Focus Measure vs Time')





 





