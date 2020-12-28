# Image analysis functionalities

import numpy as np
from pyqtgraph.Qt import QtWidgets,QtCore, QtGui
import pyqtgraph as pg


class imageAnalysisWidget(QtWidgets.QWidget):

	show_roi = QtCore.pyqtSignal(bool)

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

		# Labels to display the position at of the ROI center
		self.x_pos_label = QtGui.QLabel('X centroid')
		self.y_pos_label = QtGui.QLabel('Y centroid')

		self.x_pos_value = QtGui.QLabel()
		self.y_pos_value = QtGui.QLabel()
		
		self.x_pos_value.setNum(0)
		self.y_pos_value.setNum(0)

		# ROI size
		self.size_label = QtGui.QLabel('ROI radius')

		self.size_value = QtGui.QLabel()
		self.size_value.setNum(0)

		# Connection

		self.roi_button.clicked.connect(self.handle_roi_button)


		# Layout
		pos_grid_layout = QtGui.QGridLayout()

		pos_grid_layout.addWidget(self.x_pos_label,0,0)
		pos_grid_layout.addWidget(self.y_pos_label,0,1)
		pos_grid_layout.addWidget(self.size_label,0,2)
		pos_grid_layout.addWidget(self.x_pos_value,1,0)
		pos_grid_layout.addWidget(self.y_pos_value,1,1)
		pos_grid_layout.addWidget(self.size_value,1,2)

		overall_layout = QtGui.QVBoxLayout()
		overall_layout.addWidget(self.roi_button)
		overall_layout.addLayout(pos_grid_layout)


		self.setLayout(overall_layout)

	def handle_roi_button(self):

		if(self.roi_button.isChecked()):
			self.show_roi.emit(True)
			print('Send show roi signal')
		else:
			self.show_roi.emit(False)
			print('Sent hide roi signal')

	def update_pos_display(self, xpos, ypos):

		self.x_pos_value.setNum(xpos)
		self.y_pos_value.setNum(ypos)

	def update_size_display(self, size):
		self.size_value.setNum(size)












