# Installation instructions for packages for gravity machine data analysis.

# First install Anaconda 

# Open Anaconda prompt (on Windows)

# Create a new environment for gravity machine (if it doesnt exist)

# If an environment exists, activate by using

	activate envName

# Else create a new environment
	conda create --name envName python=3.5 (choose the correct python version so it's compatible with opencv
	activate envName

# Install scipy
	conda install scipy

# Install the Python Imaging Library
	conda install PIL

# Install pyqtgraph
	conda install pyqtgraph

# Install OpenPIV



# Install OpenCV and Dependencies
	Install this directly using the Anaconda environment (installing through terminal doesnt seem to work) 

# Check if OpenCv installation worked by opening python in the command prompt
	python

	>> import cv2

# If the install works OpenCv should now be imported

# Install pandas
	conda install pandas

# Install seaborn
	conda install seaborn