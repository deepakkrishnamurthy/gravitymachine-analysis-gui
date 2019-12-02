# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 16:28:46 2019

@author: Deepak
"""

import GravityMachineTrack
import imp
import msdanalyzer
import pandas as pd
import numpy as np
import os
imp.reload(GravityMachineTrack)
imp.reload(msdanalyzer)

import matplotlib.pyplot as plt
# %matplotlib inline

    
#------------------------------------------------------------------------------------------------------------------------------    
# Define some constants for the data analysis:

minTrackDuration = 60
    
    
# Folder in which to save analysis results
saveFolder = 'C:/Users/deepak/Dropbox/GravityMachine/ExperimentResults/MSD_Analysis'
    
analysis_file = 'C:/Users/deepak/Dropbox/GravityMachine/GravityMachineAnalysis_Scripts/AnalyzeTracks_snail.csv'

analysis_df = pd.read_csv(analysis_file)


pairwise_conditions = [(x,y) for x in analysis_df['Organism'] for y in analysis_df['Condition']]


# Create unique pairs between the Organism and Condition columns
used = set()
unique_conditions = [x for x in pairwise_conditions if x not in used and (used.add(x) or True)]
print(50*'-')
print('Unique condition : {}'.format(unique_conditions))
print(50*'-')

ensemble_tracks = []
TrackArray = []

nUniqueConditions = len(unique_conditions)

# Assemble the list of unique conditions i.e unique combinations of Organisms, Condition. Each Unique Condition will in general have several tracks

OrgDims = []

for ii in range(nUniqueConditions):
    
    curr_Organism = unique_conditions[ii][0]
    curr_Condition = unique_conditions[ii][1]
    
    bool_Org = analysis_df['Organism'] == curr_Organism
    bool_Cond = analysis_df['Condition'] == curr_Condition
   
    tracks_sameCondition = analysis_df[bool_Org & bool_Cond]
    
    nTracksSameCondition = len(tracks_sameCondition)
    
    for jj in range(nTracksSameCondition):
        
        Track_df = tracks_sameCondition.iloc[jj]
        
        
        
        print(Track_df)
        full_path = os.path.join(Track_df['rootFolder'],Track_df['trackFolder'], Track_df['trackFile'])

        track = GravityMachineTrack.gravMachineTrack(trackFile = full_path , organism = Track_df['Organism'], condition = Track_df['Condition'], Tmin = Track_df['Tmin'], Tmax = Track_df['Tmax'], findDims = True)
        
        try:
            OrgDims.append(track.OrgDim)
        except:
            temp = float(input('Enter Organism dimensions in mm'))
            track.OrgDim = temp
                
        # Filter tracks based on min Track Duration
        if(track.trackDuration >= minTrackDuration):
            TrackArray.append(track)

    
    
    
    msd1 = msdanalyzer.msdanalyzer(Tracks = TrackArray, ensemble_method = 'subtrack', Organism = curr_Organism, Condition = curr_Condition, savePath = saveFolder)


#    msd1 = msdanalyzer(testFlag=0)

    msd1.computeSqDisp(save = True)
    msd1.computeMSD(save = True, overwrite = False)
    
#     msd1.calculate_velocityDist()