# Installation instructions for packages for gravity machine data analysis.

## First install Anaconda (package management)

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

Ensure that at this stage you are inside the conda environment. You can check this by seeing a `(envName)Joes-MacBook-Pro:` in your terminal prompt

## Install the required dependencies
	pip install -r requirements.ext
