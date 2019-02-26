import os, shutil
import numpy as numpy
def sort_list(list1, list2): 
  
	zipped_pairs = zip(list2, list1) 
  
	z = [x for _, x in sorted(zipped_pairs)] 
	  
	return z 


dataFolder = '/home/prakashlab/GravityMachine/Results/PuertoRico/2018_11_06/Tow_1/Centric_diatom_3_Good/images_new'

destFolder = '/home/prakashlab/GravityMachine/Results/PuertoRico/2018_11_06/Tow_1/Centric_diatom_3_Good/images'


FileList = os.listdir(dataFolder)

FileList.sort()

fileNumber = []

for ii,fileName in enumerate(FileList):
	print('{}: File Name: {}'.format(ii, fileName[4:-4]))
	
	if(ii is not 0):
		
		fileNumber_curr = int(fileName[4:-4])

		# print(fileNumber_curr)

		fileNumber.append(fileNumber_curr)
	else:
		fileNumber.append(0)



FileList_sorted = sort_list(FileList, fileNumber)

subDir = 0

fileCounter = 0
maxFiles = 3000


subFolder_path = os.path.join(destFolder, '{%03d}'.format(subDir))

if(not os.path.exist(subFolder_path)):
	os.makedirs(subFolder_path)

for fileName in FileList_sorted:
	
	print('Copying filename: {}'.format(fileName))
	FilePath_old = os.path.join(dataFolder, fileName)
	FilePath_new = os.path.join(subFolder_path, fileName)
	
	shutil.copy(FilePath_old, FilePath_new)
	
	fileCounter += 1
	
	if(fileCounter >= maxFiles):
		subDir += 1
		subFolder_path = os.path.join(destFolder, '{%03d}'.format(subDir))
		if(not os.path.exist(subFolder_path)):
			os.makedirs(subFolder_path)
			print('Created new directory at {}'.format(subFolder_path))
			
		fileCounter = 0
		
			
		
	
	

	






