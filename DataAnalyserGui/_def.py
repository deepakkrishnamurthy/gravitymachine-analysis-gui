import glob
import os

##########################################################
#### start of loading machine specific configurations ####
##########################################################
config_files = glob.glob('..' + '/' + 'configuration*.txt')
print(config_files)
if config_files:
    if len(config_files) > 1:
        print('multiple data configuration files found, the program will exit')
        exit()
    print('load data-specific configuration')
    exec(open(config_files[0]).read())
else:
    print('data configuration file not present, the program will exit')
    exit()
##########################################################
##### end of loading machine specific configurations #####
##########################################################

class Chamber:

	WIDTH = 5
	LENGTH = 30
	def __init__(self):
		pass

		

