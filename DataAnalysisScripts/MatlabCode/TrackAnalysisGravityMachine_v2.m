% Code to Analyze tracks from the Gravity machine
clear variables
close all
%% Preliminaries
cmap = cmocean('matter',32);

% ------------------------------------------------------------------------
% Choose the track file to import
% ------------------------------------------------------------------------
% [filename, pathname] = uigetfile('D:\GravityMachineLocal\*.csv','Select the Tracks to analyze: ');
%[filename, pathname] = uigetfile('Y:\Projects\GravityMachine\*','Select the Tracks to analyze: ');
% [filename, pathname]= uigetfile(['/Volumes/GRAVMACH1/GravityMachine/HopkinsEmbryologyCourse/*'])

[filename, pathname] = uigetfile(['F:\GravityMachineBackup\HopkinsEmbryologyCourse\*'])
if isequal(filename,0)
   disp('User selected Cancel')
else
   disp(['User selected ', fullfile(pathname, filename)])
end

TrackNames = ['SeaCucumber

ResultFolder = fullfile(pathname,'Plots');
if (~exist(ResultFolder,'dir'))
    mkdir(ResultFolder)
end

%[Time, Xpos, Ypos, Zpos,ImageZcoord, ImageXcoord, ManualTracking] = csvimport(strcat(pathname,filename),'columns',{'Time','Xpos','Ypos','Zpos',	'Image Z coord','Image X coord','Manual Tracking'});

[Time, Xobjet, Yobjet, Zobjet, ThetaWheel, ZobjWheel, ManualTracking,	ImageName,	FocusMeasure,	LiquidLensPhase	,YFMmaximum] =  ...
    csvimport(strcat(pathname,filename),'columns',{'Time','Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum'});


figure(1)
plot(Time(ManualTracking), ZobjWheel(ManualTracking))


% Create a msd analyzer object with all the tracks

Tracks = {}
















