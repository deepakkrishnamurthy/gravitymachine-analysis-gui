import trackpy
import cv2
from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
import argparse
import imutils
import time
import cv2
import numpy as np
import os, sys
import trackpy as tp
import pims
import matplotlib.pyplot as plt
import imageio
import roipoly
import cmocean
import pandas as pd
import pickle
imageio.plugins.ffmpeg.download()
plt.close("all")

pixelPermm = 37/0.5

particleSize = 37 
#==============================================================================
#                              Plot Parameters   
#==============================================================================
from matplotlib import rcParams
from matplotlib import rc
#rcParams['axes.titlepad'] = 20 
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
### for Palatino and other serif fonts use:
##rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=False)
#plt.rc('font', family='serif')

rc('font', family='sans-serif') 
rc('font', serif='Helvetica') 
rc('text', usetex='false') 
rcParams.update({'font.size': 20})
class particleTrack:
    
    def __init__(self,frames, positionX, positionY, FPS, pixelPermm):
        
        self.frames = np.array(frames)
        
        self.X = np.array(positionX)
        
        self.Y = np.array(positionY)
        
        index = np.argsort(self.frames)
        
        self.frames = self.frames[index]
        self.X = self.X[index]
        self.Y = self.Y[index]
        
        self.fps = FPS
        
        self.pixelPermm = pixelPermm
        
        self.computeSpeed()
        
    
    def computeSpeed(self):
        
        self.velocity_x = (self.X[1:] - self.X[:-1])*(1/pixelPermm)*(self.fps)
        self.velocity_y = (self.Y[1:] - self.Y[:-1])*(1/pixelPermm)*(self.fps)
        
        self.Speed = (self.velocity_x**2 + self.velocity_y**2)**(1/2)
        
#        self.Speed = self.smoothSignal(self.Speed, window_time = 1)
        
    def smoothSignal(self, data, window_time):      # Window is given in seconds
        
        avgWindow = int(window_time*self.fps)

        return pd.rolling_mean(data, avgWindow, min_periods = 1, center = True)
        
        

        

#VideoFolder = '/Users/deepak/Dropbox/GravityMachine/ExperimentResults/AbioticExperiments'
VideoFolder = '/Volumes/DEEPAK-SSD/GravityMachine/AbioticExperiments'

#VideoFile = 'kiss_tumble_1214_1343'
VideoFile = 'kiss_tumble'


DestinationFolder = os.path.join(VideoFolder, 'TrackImages')

if(not os.path.exists(DestinationFolder)):
    os.makedirs(DestinationFolder)
    
    

VideoPath = os.path.join(VideoFolder, VideoFile)

frames = pims.ImageSequence(VideoPath, as_grey=True)

#frames_video = pims.Video(os.path.join(VideoFolder, 'InfiniteBeadDance.mov'))
#
#totalFrames = len(frames_video)
#
#videoDuration = 2*60 + 18
#
#FPS = totalFrames/videoDuration

FPS = 60

#print('Total number of frames in the Folder : {}'.format(totalFrames))
print('Video frame rate: {} fps'.format(FPS))

computeNew = 1

startFrame = 0

nFrames = len(frames)
 
FileName = 'track.pkl'

FilePath = os.path.join(VideoFolder, FileName)


frameNum = 0

flag = 0

blobSize = 51
minMass = 10000

while(flag == 0):
    features = tp.locate(frames[frameNum], particleSize, invert=False)
    
    features.head() # shows the first few rows of data
    
    plt.figure(2)  # make a new figure
    tp.annotate(features, frames[frameNum]);
    
    fig, ax = plt.subplots()
    ax.hist(features['mass'], bins=20)
    
    # Optionally, label the axes.
    ax.set(xlabel='mass', ylabel='count');
    
    plt.figure(3)
    tp.subpx_bias(features);
    
    flag = int(input('Press 1 to use these settings, Press 0 to Enter new settings'))
    
    if(flag==0):
        frameNum = int(input('Enter new frame number. Prev value : {}'.format(frameNum)))
        minMass = int(input('Enter new min mass. Prev value: {}'.format(minMass)))
        blobSize = int(input('Enter new blob size (odd integer). Prev value: {}'.format(blobSize)))
    


if(not os.path.exists(FilePath) or computeNew == 1):
    
    
    # Extract the location of features in each frame
    features = tp.batch(frames[startFrame:startFrame + nFrames], blobSize, minmass = minMass, invert=False, engine='numba', characterize = False);
    
#    pred = tp.predict.NearestVelocityPredict()
    # Link the features in each frame to make tracks
    tracks = tp.link_df(features, particleSize*5, memory = 5)
#    tracks = pred.link_df(pd.concat(frames), 0.5)
    
    # Remove tracks which are lesser than 1 s in length
    tracks1 = tp.filter_stubs(tracks,60)
    
    # Generate tracks from the Frames
    # For each unique particle store all the information corresponding to the particle
    
    nTracks = max(tracks1['particle'])+1
    
    print('Total number of tracks in this dataset: {}'.format(nTracks))
    
    Tracks = []
    # Create a datastructure storing the track of each particle
    for ii in range(nTracks):
    
        particleFrames = tracks1[tracks1['particle']==ii]['frame']
        particleX = tracks1[tracks1['particle']==ii]['x']
        particleY = tracks1[tracks1['particle']==ii]['y']
        Tracks.append(particleTrack(particleFrames, particleX, particleY, pixelPermm=pixelPermm, FPS = FPS))
    

   
#    for ii in range(nTracks): 
#        
#        plt.figure()
#        plt.scatter(Tracks[ii].X, Tracks[ii].Y,20,color='r') 

    # Save the data so it can be extracted and replotted
    with open(FilePath, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump((features, tracks1, Tracks), f)


else:
    
    if(os.path.exists(FilePath)):
        with open(FilePath, 'rb') as f:
            features, tracks1, Tracks = pickle.load(f)
    


 
nTracks = len(Tracks) 
    
# Save the data so it can be replotted again

def press(event):
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'q':
        sys.exit('User stopped the program')
    else:
        pass
  
    
    
plt.close("all")

Umin = 0
Umax = 0

frame_depth = 120
trackSpeedThresh = 10
fig = plt.figure(1)
fig.canvas.mpl_connect('key_press_event', press)

for ii in range(startFrame,startFrame+nFrames):
    
    plt.clf()
    plt.imshow(frames[ii],cmap = cmocean.cm.gray)
    
    
    
    for jj in range(nTracks):
        
        localIndex = next((i for i, x in enumerate(Tracks[jj].frames == ii) if x), None)
        
        
        meanTrackSpeed = np.mean(Tracks[jj].Speed)
       
       
        
        if(localIndex and meanTrackSpeed < trackSpeedThresh):
#            print(localIndex)
            startIndex = localIndex - frame_depth
            if(startIndex < 0):
                startIndex = 0
            ax1 = plt.scatter(Tracks[jj].X[startIndex:localIndex], Tracks[jj].Y[startIndex:localIndex],s = 10, c=Tracks[jj].Speed[startIndex:localIndex], cmap = plt.cm.plasma, vmin=0, vmax = 5)
            Umax = max(Umax, max(Tracks[jj].Speed))

    
#    plt.savefig(os.path.join(DestinationFolder,'IMG'+'{:03d}'.format(ii)+'.png'), dpi=300)
    plt.pause(0.001)
    
    
    
cbar = plt.colorbar(ax1)
cbar.ax.set_ylabel('Particle speed (mm/s)')
#
            
print('Maximum speed: {}'.format(Umax))
    

#for ii in range(nFrames):
#    
##    plt.clf()
##    tp.annotate(t1[t1['frame'] == ii], frames[ii]);
#    
##    plt.pause(0.001)
#    nParticles = len(t1[t1['frame']==ii]['particle'])
#    print('No:of particles in frame : {}'.format(nParticles))
    
    

# Show the particle traces on the original Video files
    
    
    
    
    
