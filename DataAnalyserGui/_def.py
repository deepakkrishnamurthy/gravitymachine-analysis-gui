# Definitions and constants
# Map between CSV headers and internal state variables of the GUI

# Newer variable mappings (For GM codebase >= v2.0)
# VARIABLE_HEADER_MAPPING = {'Time':'Time', 'X_obj':'X_objStage','Y_obj':'Y_objStage','Z_obj':'Z_objStage','Image name':'DF1', 'X_image':'X_image', 'Z_image':'Z_image'}

# Older variable mappings (For GM codebase < v2.0)
VARIABLE_HEADER_MAPPING = {'Time':'Time', 'X_obj':'Xobj','Y_obj':'Yobj','Z_obj':'ZobjWheel','Image name':'Image name', 'X_image':'Xobj_image', 'Z_image':'Zobj'}

class Chamber:

	WIDTH = 5
	LENGTH = 30
	def __init__(self):
		pass

		

