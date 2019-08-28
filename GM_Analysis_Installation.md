# Installation instructions for packages for gravity machine data analysis.

## First install Anaconda 

https://docs.anaconda.com/anaconda/install/
Follow all the steps including answering "YES" to "Do you wish the installer to initialize Anaconda3
by running conda init"

## Open Anaconda prompt (on Windows) or terminal on MacOS or Linux machines

## Create a new environment for gravity machine projects (if it doesn't exist)

### If an environment exists, activate by using

	conda activate envName

### Else create a new environment
#### (choose the correct python version so it's compatible with opencv 4.0, in this case this is python 3.6)
	conda create --name envName python=3.6 
	conda activate envName

## Ensure that at this stage you are inside the conda environment. You can check this by seeing a `(envName)Joes-MacBook-Pro:` in your terminal prompt

## Install pip
	conda install pip

## Install numpy
	conda install numpy

## Install OpenCV and OpenCV-contrib

	pip install opencv-python
	pip install opencv-contrib-python
	

## Check if OpenCv installation worked by opening python in the command prompt
	python

	>> import cv2

### If the install works OpenCv should now be imported

## Install scipy
	conda install scipy

## Install the Python Imaging Library
	conda install pillow

## Install pyqtgraph
	conda install pyqtgraph

## Install OpenPIV

	conda install -c conda-forge openpiv

## Install Matplotlib

	conda install matplotlib

## Install pandas
	conda install pandas

## Install seaborn
	conda install seaborn

## Install cmocean 
	pip install cmocean

## Install opengl python

	pip install PyOpenGL