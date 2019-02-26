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
[filename, pathname]= uigetfile(['/Volumes/GRAVMACH1/GravityMachine/HopkinsEmbryologyCourse/*'])
if isequal(filename,0)
   disp('User selected Cancel')
else
   disp(['User selected ', fullfile(pathname, filename)])
end

ResultFolder = fullfile(pathname,'Plots');
if (~exist(ResultFolder,'dir'))
    mkdir(ResultFolder)
end
%%------------------------------------------------------------------------
%% Conversion of Raw data to Physical units
% ------------------------------------------------------------------------
% Z axis
% ------------------------------------------------------------------------
gearRatio = 99 + (1044/2057);
encoderCountPerRev_motor = 600;
encoderCountPerRev_output = gearRatio*encoderCountPerRev_motor;
annulusDia = 175;                       % Wheel 15 centerline dia in mm
annulusPer = pi*annulusDia;             % Perimeter of the annulus in mm.
mmPercount_Z = annulusPer/encoderCountPerRev_output; 
% ------------------------------------------------------------------------
% Y axis
% ------------------------------------------------------------------------
% StepsPerRev_Y = 200;
% mmPerStep_Y = 0.001524;
StepsPerRev_Y = 20;
mmPerRev_Y = 0.5;
mmPerStep_Y = mmPerRev_Y/StepsPerRev_Y;

% ------------------------------------------------------------------------
% X axis
% ------------------------------------------------------------------------
StepsPerRev_X = 20;
mmPerRev_X = 0.5;
mmPerStep_X = mmPerRev_X/StepsPerRev_X;
% ------------------------------------------------------------------------
% Chamber dimensions
% ------------------------------------------------------------------------
chamberW = 20;      % in mm
chamberT = 3;       % in mm
Xcenterline = 87.5;          % Centerline of the wheel in mm
%[Time, Xpos, Ypos, Zpos,ImageZcoord, ImageXcoord, ManualTracking] = csvimport(strcat(pathname,filename),'columns',{'Time','Xpos','Ypos','Zpos',	'Image Z coord','Image X coord','Manual Tracking'});

[Time, Xpos, Ypos, Zpos,ThetaWheel, ZobjWheel, ManualTracking, ImageName, FocusMeasure, LensPhase, YmaxFM] = csvimport(strcat(pathname,filename),'columns',{'Time','Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum'});

% try
%     [Time, Xpos, Ypos, Zpos,ThetaWheel, ZobjWheel, ManualTracking, ImageName, FocusMeasure, LensPhase, YmaxFM, R, G , B] = csvimport(strcat(pathname,filename),'columns',{'Time','Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum','LED Panel color R','LED Panel color G','LED Panel color B'});
% catch
%     [Time, Xpos, Ypos, Zpos,ThetaWheel, ZobjWheel, ManualTracking, ImageName, FocusMeasure, LensPhase, YmaxFM, R, G , B] = csvimport(strcat(pathname,filename),'columns',{'Time','Xobjet','Yobjet','Zobjet','ThetaWheel','ZobjWheel','Manual Tracking','Image name','Focus Measure','Liquid Lens Phase','Y FM maximum','LEDPanel color R','LEDPanel color G','LEDPanel color B'});
% 
%     
% end 

% Time stored is in milliseconds
%------------------------------------------------------------------------
% Find the start of the track. i.e the first instance where the tracking
% switches from manual to automatic.
%------------------------------------------------------------------------
startIndex = find(~ManualTracking,1);
%------------------------------------------------------------------------
% Restrict the arrays to start from the index where Automated tracking
% starts
%------------------------------------------------------------------------
Zpos = ZobjWheel;
Time = Time(startIndex:end,1); % Time in seconds
Xpos = Xpos(startIndex:end,1);
Ypos = Ypos(startIndex:end,1);
Zpos = Zpos(startIndex:end,1);
% Zhome = Zhome(startIndex:end,1);
ManualTracking = ManualTracking(startIndex:end,1);

Time = Time;
Xdisp = Xpos;
Ydisp = Ypos;
Zdisp = Zpos ;

wheelRotation = Zdisp./encoderCountPerRev_output;

% Converting to Physical Units
% TrackDisp_mm = [Xdisp*mmPerStep_X, Ydisp*mmPerStep_Y, Zdisp*mmPercount_Z] ; 

TrackDisp_mm = [Xdisp, Ydisp, Zdisp] ; 


TimeDiff = Time(2:end) - Time(1:end-1);
disp('Mean time difference: ')
disp(mean(TimeDiff))
disp('Standard deviation in time difference: ')
disp(std(TimeDiff))

TrackVel = (TrackDisp_mm(2:end,:) - TrackDisp_mm(1:end-1,:))./repmat(TimeDiff, [1 3]);     % Intantaneous velocity of the track.
TrackSpeed = dot(TrackVel,TrackVel,2).^(1/2);

TimeAuto = Time(ManualTracking==0,:);
TrackSpeedAuto = TrackSpeed(ManualTracking(1:end-1)==0,:);

fftPlot(Time,Ydisp);

%% PLOTS
f0= figure, hold on;
plot(Time(1:end-1), TimeDiff,'r.','LineWidth',2);
xlabel('Time (s)','FontSize',20);
ylabel('X displacement (mm)','FontSize',20);
set(gca,'FontName','Arial','FontSize',20);
box on


%--------------------------------------------------------------------------
% Track displacements
%--------------------------------------------------------------------------
figName = 'DisplacementvsTime';
f1= figure, hold on;
subplot(131), hold on
plot(Time, TrackDisp_mm(:,1),'r-','LineWidth',1);
xlabel('Time (s)','FontSize',20);
ylabel('X displacement (mm)','FontSize',20);
set(gca,'FontName','Arial','FontSize',20);
box on
subplot(132), hold on
plot(Time, TrackDisp_mm(:,2),'g--','LineWidth',1);
xlabel('Time (s)','FontSize',20);
ylabel('Y displacement (mm)','FontSize',20);
set(gca,'FontName','Arial','FontSize',20);
box on
subplot(133), hold on
plot(Time, TrackDisp_mm(:,3),'b-.','LineWidth',1);
xlabel('Time (s)','FontSize',20);
ylabel('Z displacement (mm)','FontSize',20);
set(gca,'FontName','Arial','FontSize',20);
box on
saveas(gcf,fullfile(ResultFolder,figName));

figName = 'TracksSpeedvsWheelRotation';
f1= figure, hold on;
plot(wheelRotation(1:end-1), TrackSpeed(:,1),'k--','LineWidth',1);
xlabel('Wheel rotation (revolutions)','FontSize',20);
ylabel('Track speed (mm/s)','FontSize',20);
set(gca,'FontName','Arial','FontSize',20);
box on
saveas(gcf,fullfile(ResultFolder,figName));
%--------------------------------------------------------------------------
% Track instataneous speed
%--------------------------------------------------------------------------
% figName = 'TrackSpeedVstime';
% f2 = figure, hold on;
% plot(Time(1:end-1),TrackSpeed,'r-','LineWidth',1);
% xlabel('Time (s)','FontSize',20);
% ylabel('TrackSpeed (mm/s)','FontSize',20);
% set(gca,'FontName','Arial','FontSize',20);
% box on
% saveas(gcf,fullfile(ResultFolder,figName));

%--------------------------------------------------------------------------
% Plot of track Speed restricted to the automated tracking segments
%--------------------------------------------------------------------------
% figName = 'TrackSpeedVsTime_AutomaticOnly';
% figure, hold on;
% % plot3(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),TrackDisp_mm(1:end-1,3),'k-','LineWidth',2)
% plot(TimeAuto(1:end-1),TrackSpeedAuto,'r--','LineWidth',1);
% colormap(cmap)
% c1 = colorbar;
% xlabel('Time (s)','FontSize',14);
% ylabel('Track Speed(mm/s)','FontSize',14);
% title('Track Speed vs Time (auto only)');
% set(gca,'FontName','Arial','FontSize',14);
% box on
% saveas(gcf,fullfile(ResultFolder,figName));
%--------------------------------------------------------------------------
% XZ Plot of the track.
%--------------------------------------------------------------------------
figName = 'TrackXZPlot';
figure, hold on;
% plot3(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),TrackDisp_mm(1:end-1,3),'k-','LineWidth',2)
scatter(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,3),20,TrackSpeed,'filled');
colormap(cmap)
c1 = colorbar;
xlabel('X displacement (mm)','FontSize',14);
ylabel('Z displacement (mm)','FontSize',14);
title('Track');
ylabel(c1,'Track Speed (mm/s)');
set(gca,'FontName','Arial','FontSize',14);
axis equal
axis vis3d
box on
saveas(gcf,fullfile(ResultFolder,figName));

%--------------------------------------------------------------------------
% XY Plot of the track.
%--------------------------------------------------------------------------
figName = 'TrackXYPlot';
figure, hold on;
% plot3(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),TrackDisp_mm(1:end-1,3),'k-','LineWidth',2)
scatter(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),20,TrackSpeed,'filled');
line([-chamberW/2,chamberW/2,chamberW/2,-chamberW/2],[0,0,chamberT,chamberT]);
colormap(cmap)
c1 = colorbar;
xlabel('X displacement (mm)','FontSize',14);
ylabel('Y displacement (mm)','FontSize',14);
title('Track');
ylabel(c1,'Track Speed (mm/s)');
set(gca,'FontName','Arial','FontSize',14);
axis equal
axis vis3d
box on
saveas(gcf,fullfile(ResultFolder,figName));

%--------------------------------------------------------------------------
% 3D plot of the track.
%--------------------------------------------------------------------------
figName = 'Track3DPlot';
figure, hold on;
% plot3(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),TrackDisp_mm(1:end-1,3),'k-','LineWidth',2)
scatter3(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),TrackDisp_mm(1:end-1,3),20,TrackSpeed,'filled');
colormap(cmap)
c1 = colorbar;
xlabel('X displacement (mm)','FontSize',14);
ylabel('Y displacement (mm)','FontSize',14);
zlabel('Z displacement (mm)','FontSize',14);
title('Track');
ylabel(c1,'Track Speed (mm/s)');
set(gca,'FontName','Arial','FontSize',14);
caxis([0 5]);
axis vis3d
axis equal
box on
saveas(gcf,fullfile(ResultFolder,figName));

% figName = 'ZhomePlot';
% figure, hold on;
% % plot3(TrackDisp_mm(1:end-1,1),TrackDisp_mm(1:end-1,2),TrackDisp_mm(1:end-1,3),'k-','LineWidth',2)
% scatter(Time,Zhome * mmPerStep_Y,20,'filled');
% colormap(cmap)
% c1 = colorbar;
% xlabel('Time (s)','FontSize',14);
% ylabel('Focus offset','FontSize',14);
% 
% title('Focus offset update');
% set(gca,'FontName','Arial','FontSize',14);
% box on
% saveas(gcf,fullfile(ResultFolder,figName));












