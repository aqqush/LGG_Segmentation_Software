# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 13:04:31 2015

@author: m131199
"""

from PyQt4 import QtGui,QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
 
from matplotlib.figure import Figure
 
class MplCanvas(FigureCanvas):
 
    def __init__(self):
        self.fig = Figure(facecolor='gray')
        self.ax = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    
 
class plotHistWidget(QtGui.QWidget):
 
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
        