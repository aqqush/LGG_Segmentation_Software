# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 01:18:22 2015

@author: m131199
"""

from PyQt4 import QtGui,QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
 
from matplotlib.figure import Figure
 
class MplCanvas(FigureCanvas):
 
    def __init__(self):
        self.fig = Figure(facecolor='black')
        self.ax = self.fig.add_subplot(111)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.ax.set_axis_bgcolor('black')
#        self.ax.set_aspect('equal')

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    
 
class figure2Widget(QtGui.QWidget):
 
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.canvas.setFocus(QtCore.Qt.MouseFocusReason)
#        self.canvas.focusInEvent(QtCore.Qt.)
        self.canvas.key_press_event(QtCore.Qt.LeftButton)
        self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.canvas.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.canvas.setFocus()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)