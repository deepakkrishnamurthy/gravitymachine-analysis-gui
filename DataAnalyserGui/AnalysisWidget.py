# Image analysis functionalities

import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg


class AnalysisWidget(QtWidgets.QWidget):

	show_roi = QtCore.pyqtSignal(bool)
	save_analysis_data = QtCore.pyqtSignal(str, str, float, float, int)

	def __init__(self):
		super().__init__()
		self.add_components()

	def add_components(self):

		# Widget
		# Button to show or hide the ROI
		self.roi_button = QtGui.QPushButton('Show ROI')

		self.roi_button.setCheckable(True)
		self.roi_button.setChecked(False)
		self.roi_button.setEnabled(True)

		# Button to save the analysis parameters
		self.save_button = QtGui.QPushButton('Save analysis params')
		self.save_button.setChecked(False)
		self.save_button.setEnabled(True)

		# Entry label for Sphere/Organism ID
		self.track_ID_label = QtGui.QLabel('Organism')
		self.track_ID = QtGui.QLineEdit()

		self.track_condition_label = QtGui.QLabel('Condition')
		self.track_condition = QtGui.QLineEdit()

		self.Tmin_label = QtGui.QLabel('T min')
		self.Tmax_label = QtGui.QLabel('T max')
		self.Tmin = QtGui.QLineEdit()
		self.Tmax = QtGui.QLineEdit()
		self.Tmin.setValidator(QtGui.QDoubleValidator(0.00,10000.00,2))
		self.Tmax.setValidator(QtGui.QDoubleValidator(0.00,10000.00,2))

		# Labels to display the position at of the ROI center
		self.x_pos_label = QtGui.QLabel('X centroid')
		self.y_pos_label = QtGui.QLabel('Y centroid')

		self.x_pos_value = QtGui.QLabel()
		self.y_pos_value = QtGui.QLabel()
		
		self.x_pos_value.setNum(0)
		self.y_pos_value.setNum(0)

		# ROI size
		self.size_label = QtGui.QLabel('ROI diameter')

		self.size_value = QtGui.QLabel()
		self.size_value.setNum(0)

		# Connection

		self.roi_button.clicked.connect(self.handle_roi_button)
		self.save_button.clicked.connect(self.handle_save_button)


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
		overall_layout.addWidget(self.track_condition_label,0,2)
		overall_layout.addWidget(self.track_condition,0,3)
		overall_layout.addWidget(self.Tmin_label,1,0)
		overall_layout.addWidget(self.Tmin,1,1)
		overall_layout.addWidget(self.Tmax_label,1,2)
		overall_layout.addWidget(self.Tmax,1,3)
		overall_layout.addLayout(pos_grid_layout,2,0,1,2)
		overall_layout.addWidget(self.roi_button,3,0)
		overall_layout.addWidget(self.save_button,3,1)


		self.setLayout(overall_layout)

	def handle_roi_button(self):

		if(self.roi_button.isChecked()):
			self.show_roi.emit(True)
			print('Send show roi signal')
		else:
			self.show_roi.emit(False)
			print('Sent hide roi signal')

	def handle_save_button(self):

		Tmin = float(self.Tmin.text())
		Tmax = float(self.Tmax.text())
		track_ID = self.track_ID.text()
		track_condition = self.track_condition.text()
		diameter = int(self.size_value.text())
		self.save_analysis_data.emit(track_ID, track_condition, Tmin, Tmax, diameter) 

	def update_pos_display(self, xpos, ypos):

		self.x_pos_value.setNum(xpos)
		self.y_pos_value.setNum(ypos)

	def update_size_display(self, size):
		self.size_value.setNum(size)












