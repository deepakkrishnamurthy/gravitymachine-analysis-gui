# Gravity Machine Analysis GUI 

## Introduction
This is a custom GUI-based data analysis tool for visualizing and analyzing Gravity Machine datasets. Gravity machine is the nickname for Scale-free Vertical Tracking Microscopy, a method developed by [Deepak Krishnamurthy et al.](https://www.nature.com/articles/s41592-020-0924-7) at [Prakash lab, Stanford](https://github.com/prakashlab). 

The dependencies can be installed by following instructions in the *GM_Analysis_Installation.md* file.

To launch the tool, open a terminal, activate the appropriate virtual environment (conda activate ...). After this launch the folowing script:
	
	python DataAnalyser.py
	
## Basic usage

### Opening a dataset
To open a new dataset, hit *'Ctrl + O'* or click *File > Open*. Then first choose the folder containing the data (.csv track file + folder containing images). In the next dialog, choose the .csv track file you wish to open.

### Changing track parameters
To change track parameters such as Pixel size, chamber dimensions etc., navigate to *Edit > Track* parameters or hit *'Ctrl + T'*. 

### Changing Video Playback speed
To change the playback speed of the video, navigate to *Video > Video Parameters* or hit *'Ctrl + V'*. Use the slider or entry box to enter the playback factor. Playback factor of *'1'* corresponds to real-time playback.

### Saving analysis data
Currently a very basic widget allows you to annotate the track ID, condition and also choose the time interval of interest. This widget also allows a simple means to stimate the size of the tracked object. This analysis notes can be saved as a CSV file by clicking *'Save analysis params'*.


## Publications:
1. Krishnamurthy, Deepak, Hongquan Li, François Benoit du Rey, Pierre Cambournac, Adam G. Larson, Ethan Li, and Manu Prakash. "Scale-free vertical tracking microscopy." Nature Methods (2020): 1-12. [Weblink](https://www.nature.com/articles/s41592-020-0924-7)

## To cite this tool
	@article{krishnamurthy2020scale,
	  title={Scale-free vertical tracking microscopy},
	  author={Krishnamurthy, Deepak and Li, Hongquan and du Rey, Fran{\c{c}}ois Benoit and Cambournac, Pierre and Larson, Adam G and Li, Ethan and Prakash, Manu},
	  journal={Nature Methods},
	  volume={17},
	  number={10},
	  pages={1040--1051},
	  year={2020},
	  publisher={Nature Publishing Group}
	}
#### Contributors: 
Deepak Krishnamurthy, Francois benoit du Rey and Ethan Li
