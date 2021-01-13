# Image analysis functionalities

import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg


class imageAnalysisWidget(QtWidgets.QWidget):

	show_circular_roi = QtCore.pyqtSignal(bool)
	show_object_roi = QtCore.pyqtSignal(bool)
	show_feature_roi = QtCore.pyqtSignal(bool)
	track_signal = QtCore.pyqtSignal(bool)
	save_signal = QtCore.pyqtSignal(str, int)
	save_images_signal = QtCore.pyqtSignal(bool)

	def __init__(self):
		super().__init__()
		self.add_components()

	def add_components(self):

		# Widget
		# Button to show or hide the ROI
		self.circular_roi_button = QtGui.QPushButton('Show circle ROI')
		self.circular_roi_button.setCheckable(True)
		self.circular_roi_button.setChecked(False)
		self.circular_roi_button.setEnabled(True)

		# Show/Hide object ROI button
		self.object_roi_button = QtGui.QPushButton('Select object')
		self.object_roi_button.setCheckable(True)
		self.object_roi_button.setChecked(False)
		self.object_roi_button.setEnabled(True)
		# Show/Hide feature ROIs button

		self.feature_roi_button = QtGui.QPushButton('Select features')
		self.feature_roi_button.setCheckable(True)
		self.feature_roi_button.setChecked(False)
		self.feature_roi_button.setEnabled(True)

		# Start/Stop tracking button
		self.track_button = QtGui.QPushButton('Start tracking')
		self.track_button.setCheckable(True)
		self.track_button.setChecked(False)
		self.track_button.setEnabled(True)

		# Save tracking data to File button
		self.save_data_button = QtGui.QPushButton('Save data')
		self.save_data_button.setCheckable(False)
		self.save_data_button.setEnabled(True)

		# Save tracking data to File button
		self.save_images = QtGui.QCheckBox('Save images')
		self.save_images.setChecked(False)


		# Entry label for Sphere/Organism ID
		self.track_ID_label = QtGui.QLabel('track ID')
		self.track_ID = QtGui.QLineEdit()


		# Labels to display the position at of the ROI center
		self.x_pos_label = QtGui.QLabel('X centroid')
		self.y_pos_label = QtGui.QLabel('Y centroid')

		self.x_pos_value = QtGui.QLabel()
		self.y_pos_value = QtGui.QLabel()
		
		self.x_pos_value.setNum(0)
		self.y_pos_value.setNum(0)

		# ROI size
		self.size_label = QtGui.QLabel('Object size (px)')

		self.size_value = QtGui.QLabel()
		self.size_value.setNum(0)

		# Connections

		self.circular_roi_button.clicked.connect(self.handle_circular_roi_button)
		self.object_roi_button.clicked.connect(self.handle_object_roi_button)
		self.feature_roi_button.clicked.connect(self.handle_feature_roi_button)
		self.track_button.clicked.connect(self.handle_track_button)
		self.save_data_button.clicked.connect(self.handle_save_button)
		self.save_images.stateChanged.connect(self.handle_save_images_button)

		# Layout
		pos_grid_layout = QtGui.QGridLayout()

		pos_grid_layout.addWidget(self.x_pos_label,0,0)
		pos_grid_layout.addWidget(self.y_pos_label,0,1)
		pos_grid_layout.addWidget(self.size_label,0,2)
		pos_grid_layout.addWidget(self.x_pos_value,1,0)
		pos_grid_layout.addWidget(self.y_pos_value,1,1)
		pos_grid_layout.addWidget(self.size_value,1,2)

		overall_layout = QtGui.QGridLayout()
		overall_layout.addWidget(self.track_ID_label,0,0)
		overall_layout.addWidget(self.track_ID,0,1)
		overall_layout.addLayout(pos_grid_layout,1,0,1,2)
		overall_layout.addWidget(self.circular_roi_button,2,0)
		overall_layout.addWidget(self.object_roi_button,2,1)
		overall_layout.addWidget(self.feature_roi_button,3,0)
		overall_layout.addWidget(self.track_button,3,1)
		overall_layout.addWidget(self.save_data_button,4,1)
		overall_layout.addWidget(self.save_images,4,0)
		self.setLayout(overall_layout)

	def handle_circular_roi_button(self):

		if(self.circular_roi_button.isChecked()):
			self.show_circular_roi.emit(True)
			print('Send show roi signal')
		else:
			self.show_circular_roi.emit(False)
			print('Sent hide roi signal')

	def handle_object_roi_button(self):

		if(self.object_roi_button.isChecked()):
			self.show_object_roi.emit(True)
		else:
			self.show_object_roi.emit(False)

	def handle_feature_roi_button(self):

		if(self.feature_roi_button.isChecked()):
			self.show_feature_roi.emit(True)
		else:
			self.show_feature_roi.emit(False)

	def handle_track_button(self):

		if(self.track_button.isChecked()):
			self.track_signal.emit(True)
			self.save_data_button.setEnabled(False)
		else:
			self.track_signal.emit(False)
			self.save_data_button.setEnabled(True)

	def handle_save_button(self):
		self.save_signal.emit(self.track_ID.text(), int(self.size_value.text()))

	def handle_save_images_button(self):
		if(self.save_images.isChecked()):
			self.save_images_signal.emit(True)
		else:
			self.save_images_signal.emit(False)

	def update_pos_display(self, xpos, ypos):

		self.x_pos_value.setNum(xpos)
		self.y_pos_value.setNum(ypos)

	def update_size_display(self, size):
		self.size_value.setNum(size)






