# Gravity Machine Analysis GUI 

## Introduction
This is a custom GUI-based data analysis tool for visualizing and analyzing gravity machine datasets. Gravity machine is the nickname for Scale-free Vertical Tracking Microscopy, a method developed by [D Krishnamurthy et. al : Scale-free Vertical Tracking Microscopy: Towards Bridging Scales in Biological Oceanography](https://doi.org/10.1101/610246). 

The program has a few run-time dependencies which can be installed by following *GM_Analysis_Installation.md*.

To launch open a terminal, activate the appropriate virtual environment (conda activate ...). After this type:
	
	python DataAnalyser.py

## Basic usage

### Opening a dataset
To open a new dataset, hit *'Ctrl + O'* or click *File > Open*. Then first choose the folder containing the data (.csv track file + folder containing images). In the next dialog, choose the .csv track file you wish to open.

### Changing track parameters
To change track parameters such as Pixel size, chamber dimensions etc., navigate to *Edit > Track* parameters or hit *'Ctrl + T'*. 

### Changing Video Playback speed
To change the playback speed of the video, navigate to *Video > Video Parameters* or hit *'Ctrl + V'*. Use the slider or entry box to enter the playback factor. Playback factor of *'1'* corresponds to real-time playback.


## To cite this tool:

Krishnamurthy, Deepak, Hongquan Li, François Benoit du Rey, Pierre Cambournac, Adam Larson, and Manu Prakash. "Scale-free Vertical Tracking Microscopy: Towards Bridging Scales in Biological Oceanography." bioRxiv (2019): 610246.

## Screenshot


#### Contributors: 
Deepak Krishnamurthy, Francois benoit du Rey and Ethan Li
