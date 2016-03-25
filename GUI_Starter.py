# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 15:43:55 2015

@author: m131199
"""
import time
import matplotlib
matplotlib.use('Qt4Agg', warn=False)
#matplotlib.pyplot.switch_backend('QT4Agg')
import os
#os.chdir('/Users/m131199/Documents/LGG_GUI/LGG') 
#at_auto = 'mainWindow_ui'
import sys
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import QFileDialog
from UI_LGG import Ui_MainWindow
from skullstripping import stripSkull
from registration import rigidRegFunc,affineRegFunc,nonrigidRegFunc,rigid_nonrigidRegFunc,affine_nonrigidRegFunc,atlasRegFunc,atlasRegFunc2
from N4biasFieldC import biasFieldCorrection
import segmentation
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import nibabel as nib
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mplPath
from scipy import ndimage
import nibabel.orientations as orx
from copy import copy, deepcopy
#from skimage.draw import polygon
import json
import os
import random
import roipoly
#import resampleROIVector
import probEstROI,probEstROI3D,probEstROI3DS
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from scipy.ndimage.measurements import label
from scipy.stats import mode
import preProcessing3D
import csv
import scipy.ndimage.interpolation as interp3D
from skimage import feature 
#import nrrd
#import xlsxwriter

try:
    import qin  # qin (image database) library (requires the sys.path.append(...) line above)
    from tactic_client_lib import TacticServerStub  #
except ImportError:
    print 'Error loading libraries'
    

class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.homeDir = os.getcwd()
#        self.homeDir = '/home/m131199/Desktop/LGG_GUI/LGG'
#        print self.homeDir
        self.ui.searchPatientData.clicked.connect(self.searchPatientDataFunc)
        self.ui.imageSeries.currentIndexChanged.connect(self.searchSeriesFunc)
        self.ui.registration.clicked.connect(self.registrationFunc)
        self.ui.testButton.clicked.connect(self.testFunc)
        self.ui.preProcSeg.clicked.connect(self.preProcessing3DFunc)  
        self.ui.segmentation2.clicked.connect(self.segmentationFunc2)
        self.ui.segmentation3.clicked.connect(self.segmentationFunc3)
        self.ui.brushUpdateButton.clicked.connect(self.brushUpdateFunc)
        self.ui.resetSegButton.clicked.connect(self.resetUpdateSeg)
        self.ui.polygon.stateChanged.connect(self.roipolyFunc)
        self.ui.volBrushCB.stateChanged.connect(self.brushEditFunc)
        self.ui.imageSlider.valueChanged.connect(self.imageSliderFunc)
        self.ui.alphaSet.valueChanged.connect(self.alphaSetFunc)
        self.ui.browseT1C.clicked.connect(self.browseT1CFunc)
        self.ui.browseT2.clicked.connect(self.browseT2Func)
        self.ui.loadPatientData.clicked.connect(self.loadDataFunc)
        self.ui.skullStripping.clicked.connect(self.skullStrippingFunc)
        self.ui.biasFieldCorrection.clicked.connect(self.biasFieldCorrFunc)
        self.ui.load3DSeg.clicked.connect(self.load2DSegFunc)
        self.ui.saveROI.clicked.connect(self.saveROIFunc)
        self.ui.loadROI.clicked.connect(self.loadROIFunc)
        self.ui.pushButton_3.clicked.connect(self.deleteROI)
        self.scrolFlag1 = self.ui.figure1.canvas.mpl_connect('scroll_event', self.scrollT1CImage)
        self.scrolFlag2 = self.ui.figure2.canvas.mpl_connect('scroll_event', self.scrollT2WImage)
        self.clickFlag1 = self.ui.figure1.canvas.mpl_connect('button_press_event', self.onclickWidget1)
        self.clickFlag2 = self.ui.figure2.canvas.mpl_connect('button_press_event', self.onclickWidget2)
        self.clickFlag3 = self.ui.figure3.canvas.mpl_connect('button_press_event', self.onclickWidget3)
        self.clickFlag4 = self.ui.figure4.canvas.mpl_connect('button_press_event', self.onclickWidget4)
        
        self.clickFlag5 = self.ui.figure2.canvas.mpl_connect('motion_notify_event', self.onMotion2)
        self.clickFlag6 = self.ui.figure2.canvas.mpl_connect('button_release_event', self.onRelease2)
        self.clickFlag7 = self.ui.figure3.canvas.mpl_connect('motion_notify_event', self.onMotion3)
        self.clickFlag8 = self.ui.figure3.canvas.mpl_connect('button_release_event', self.onRelease3)        
        self.clickFlag9 = self.ui.figure4.canvas.mpl_connect('motion_notify_event', self.onMotion4)
        self.clickFlag10 = self.ui.figure4.canvas.mpl_connect('button_release_event', self.onRelease4)
#        self.clickFlag5 = self.ui.figure2.canvas.mpl_connect('button_press_event', self.__scribble_button_press_callback)
#        self.clickFlag6 = self.ui.figure2.canvas.mpl_connect('motion_notify_event', self.__scribble_motion_notify_callback)
#        self.clickFlag7 = self.ui.figure2.canvas.mpl_connect('button_release_event', self.__scribble_button_release_callback)
        self.ui.useT1.setChecked(True)
        self.ui.useT2.setChecked(True)
        self.ui.tacticCB.setChecked(False)
        #initialize Variables        
        self.thVal = None
#        self.tempBrushImg = []
        self.ui.alphaSet.setMinimum(0)
        self.ui.alphaSet.setMaximum(10)
        self.ui.alphaSet.setSingleStep(1)  
        self.segFlag = '2D'
        self.segCount=0
        self.defaultLGGPath = '/research/projects/jiri/LGG/LGG400/'
        self.defaultLGGPathF = 0
        self.stopEvolving = 0
#        num = [49,57,61,103,106,107,110,113,116,136,138,139,140,141,142,144,146,147,576,582,584,592,594,595,597,631,638,644,651,653]
#        try:        
#            for i in range(len(num)):
#    #            T1Cfname = '/Users/m131199/Documents/testData/testLGGdata/LGG_'+str(num[i])+'_T1C.nii'
#    #            T2Wfname = '/Users/m131199/Documents/testData/testLGGdata/registered'+str(num[i])+'.nii'
#                T1Cfname = '/Users/m131199/Documents/segData/registeredT1C/registeredT1C_'+str(num[i])+'.nii'
#                T2Wfname = '/Users/m131199/Documents/segData/T2/LGG_'+str(num[i])+'_T2.nii'
#                self.ui.T1Contrast.addItem(T1Cfname)   
#                index = self.ui.T1Contrast.findText(str(T1Cfname))
#                self.ui.T1Contrast.setCurrentIndex(index)
#                self.ui.T2Image.addItem(T2Wfname)   
#                index = self.ui.T2Image.findText(str(T2Wfname))
#                self.ui.T2Image.setCurrentIndex(index)
#        except:
#            pass
        

#        num = [49,57,61,103,106,107,110,113,116,136,138,139,140,141,142,144,146,147,576,582,584,592,594,595,597,631,638,644,651,653]      
##        num = [638,644,651,653]      
#
#        for i in range(len(num)):
##            T1Cfname = '/Users/m131199/Documents/testData/testLGGdata/LGG_'+str(num[i])+'_T1C.nii'
##            T2Wfname = '/Users/m131199/Documents/testData/testLGGdata/registered'+str(num[i])+'.nii'
#            T1Cfname = '/Users/m131199/Documents/segData/T2/interpT1Data/LGG_'+str(num[i])+'_T1C.nii'
#            T2Wfname = '/Users/m131199/Documents/segData/T2/interpT2Data/LGG_'+str(num[i])+'_T2.nii'
#            self.ui.T1Contrast.addItem(T1Cfname)   
#            index = self.ui.T1Contrast.findText(str(T1Cfname))
#            self.ui.T1Contrast.setCurrentIndex(index)
#            self.ui.T2Image.addItem(T2Wfname)   
#            index = self.ui.T2Image.findText(str(T2Wfname))
#            self.ui.T2Image.setCurrentIndex(index)
                
#        num = [49,57,61,103,106,107,110,113,116,136,138,139,140,141,142,144,146,147,576,582,584,592,594,595,597,631,638,644,651,653]
#        for i in range(len(num)):
##            T1Cfname = '/Users/m131199/Documents/testData/testLGGdata/LGG_'+str(num[i])+'_T1C.nii'
##            T2Wfname = '/Users/m131199/Documents/testData/testLGGdata/registered'+str(num[i])+'.nii'
#            T1Cfname = '/Volumes/store01/Z_MacBackUps/segData/registeredT1C/registeredT1C_'+str(num[i])+'.nii'
#            T2Wfname = '/Volumes/store01/Z_MacBackUps/segData/T2/LGG_'+str(num[i])+'_T2.nii'
#            self.ui.T1Contrast.addItem(T1Cfname)   
#            index = self.ui.T1Contrast.findText(str(T1Cfname))
#            self.ui.T1Contrast.setCurrentIndex(index)
#            self.ui.T2Image.addItem(T2Wfname)   
#            index = self.ui.T2Image.findText(str(T2Wfname))
#            self.ui.T2Image.setCurrentIndex(index)

#        filenames = ['brats_tcia_pat101_1','brats_tcia_pat141_1','brats_tcia_pat177_1',
#        'brats_tcia_pat202_1','brats_tcia_pat248_1','brats_tcia_pat249_1','brats_tcia_pat254_1',
#        'brats_tcia_pat255_1','brats_tcia_pat266_1','brats_tcia_pat276_2','brats_tcia_pat298_1',
#        'brats_tcia_pat299_1','brats_tcia_pat310_1','brats_tcia_pat312_2','brats_tcia_pat325_1',
#        'brats_tcia_pat351_1','brats_tcia_pat402_1','brats_tcia_pat413_1','brats_tcia_pat428_1',
#        'brats_tcia_pat442_1','brats_tcia_pat449_1','brats_tcia_pat466_1','brats_tcia_pat483_1',
#        'brats_tcia_pat490_1','brats_tcia_pat493_1']

#        os.chdir('/home/m131199/Desktop/') 
#        with open('ExamplesToProcess.csv', 'rb') as csvfile:
#            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#            i=1
#            for row in spamreader:
#                if i%2>0:                
#                    T1Cfname = row[0]
#                    self.ui.T1Contrast.addItem(T1Cfname)   
#                    index = self.ui.T1Contrast.findText(str(T1Cfname))
#                    self.ui.T1Contrast.setCurrentIndex(index)
#                    i=1+1
#                else:                
#                    T2Wfname = row[0]
#                    self.ui.T2Image.addItem(T2Wfname)   
#                    index = self.ui.T2Image.findText(str(T2Wfname))
#                    self.ui.T2Image.setCurrentIndex(index) 
#                    i=i+1
                        
#        self.ui.T1Contrast.addItem('/Users/m131199/Documents/testData/testAtlasReg/registeredT1C_144.nii')   
#        index = self.ui.T1Contrast.findText('/Users/m131199/Documents/testData/testAtlasReg/registeredT1C_144.nii')
#        self.ui.T1Contrast.setCurrentIndex(index)
#        self.ui.T2Image.addItem('/Users/m131199/Documents/testData/testAtlasReg/LGG_144_T2.nii')   
#        index = self.ui.T2Image.findText('/Users/m131199/Documents/testData/testAtlasReg/LGG_144_T2.nii')
#        self.ui.T2Image.setCurrentIndex(index)
#        num2 = [582,138]
                        
        TCGA_LGG = ['TCGA-CS-4938',
                     'TCGA-CS-4941',
                     'TCGA-CS-4942',
                     'TCGA-CS-4943',
                     'TCGA-CS-4944',
                     'TCGA-CS-5390',
                     'TCGA-CS-5393',
                     'TCGA-CS-5394',
                     'TCGA-CS-5395',
                     'TCGA-CS-5396',
                     'TCGA-CS-5397',
                     'TCGA-CS-6186',
                     'TCGA-CS-6188',
                     'TCGA-CS-6290',
                     'TCGA-CS-6665',
                     'TCGA-CS-6666',
                     'TCGA-CS-6667',
                     'TCGA-CS-6668',
                     'TCGA-CS-6669',
                     'TCGA-CS-6670',
                     'TCGA-DU-5849',
                     'TCGA-DU-5851',
                     'TCGA-DU-5852',
                     'TCGA-DU-5853',
                     'TCGA-DU-5854',
                     'TCGA-DU-5855',
                     'TCGA-DU-5871',
                     'TCGA-DU-5872',
                     'TCGA-DU-5874',
                     'TCGA-DU-6395',
                     'TCGA-DU-6397',
                     'TCGA-DU-6399',
                     'TCGA-DU-6400',
                     'TCGA-DU-6401',
                     'TCGA-DU-6402',
                     'TCGA-DU-6404',
                     'TCGA-DU-6405',
                     'TCGA-DU-6407',
                     'TCGA-DU-6408',
                     'TCGA-DU-6410',
                     'TCGA-DU-6542',
                     'TCGA-DU-7008',
                     'TCGA-DU-7010',
                     'TCGA-DU-7013',
                     'TCGA-DU-7014',
                     'TCGA-DU-7015',
                     'TCGA-DU-7018',
                     'TCGA-DU-7019',
                     'TCGA-DU-7294',
                     'TCGA-DU-7298',
                     'TCGA-DU-7299',
                     'TCGA-DU-7300',
                     'TCGA-DU-7301',
                     'TCGA-DU-7302',
                     'TCGA-DU-7304',
                     'TCGA-DU-7306',
                     'TCGA-DU-7309',
                     'TCGA-DU-8158',
                     'TCGA-DU-8162',
                     'TCGA-DU-8163',
                     'TCGA-DU-8164',
                     'TCGA-DU-8165',
                     'TCGA-DU-8166',
                     'TCGA-DU-8167',
                     'TCGA-DU-8168',
                     'TCGA-DU-A5TP',
                     'TCGA-DU-A5TR',
                     'TCGA-DU-A5TS',
                     'TCGA-DU-A5TT',
                     'TCGA-DU-A5TU',
                     'TCGA-DU-A5TW',
                     'TCGA-DU-A5TY',
                     'TCGA-DU-A6S2',
                     'TCGA-DU-A6S3',
                     'TCGA-DU-A6S6',
                     'TCGA-DU-A6S7',
                     'TCGA-DU-A6S8',
                     'TCGA-EZ-7264A',
                     'TCGA-EZ-7265A',
                     'TCGA-FG-5962',
                     'TCGA-FG-5963',
                     'TCGA-FG-5964',
                     'TCGA-FG-5965',
                     'TCGA-FG-6688',
                     'TCGA-FG-6689',
                     'TCGA-FG-6690',
                     'TCGA-FG-6691',
                     'TCGA-FG-6692',
                     'TCGA-FG-7634',
                     'TCGA-FG-7637',
                     'TCGA-FG-7641',
                     'TCGA-FG-7643',
                     'TCGA-FG-8186',
                     'TCGA-FG-8189',
                     'TCGA-FG-A4MT',
                     'TCGA-FG-A4MU',
                     'TCGA-FG-A60K',
                     'TCGA-FG-A6IZ',
                     'TCGA-FG-A6J1',
                     'TCGA-FG-A713',
                     'TCGA-FG-A87N',
                     'TCGA-HT-7467',
                     'TCGA-HT-7468',
                     'TCGA-HT-7469',
                     'TCGA-HT-7470',
                     'TCGA-HT-7471',
                     'TCGA-HT-7472',
                     'TCGA-HT-7473',
                     'TCGA-HT-7474',
                     'TCGA-HT-7475',
                     'TCGA-HT-7476',
                     'TCGA-HT-7477',
                     'TCGA-HT-7478',
                     'TCGA-HT-7479',
                     'TCGA-HT-7480',
                     'TCGA-HT-7481',
                     'TCGA-HT-7482',
                     'TCGA-HT-7483',
                     'TCGA-HT-7485',
                     'TCGA-HT-7601',
                     'TCGA-HT-7602',
                     'TCGA-HT-7603',
                     'TCGA-HT-7604',
                     'TCGA-HT-7605',
                     'TCGA-HT-7606',
                     'TCGA-HT-7607',
                     'TCGA-HT-7608',
                     'TCGA-HT-7609',
                     'TCGA-HT-7610',
                     'TCGA-HT-7611',
                     'TCGA-HT-7616',
                     'TCGA-HT-7620',
                     'TCGA-HT-7676',
                     'TCGA-HT-7677',
                     'TCGA-HT-7680',
                     'TCGA-HT-7681',
                     'TCGA-HT-7684',
                     'TCGA-HT-7686',
                     'TCGA-HT-7687',
                     'TCGA-HT-7688',
                     'TCGA-HT-7689',
                     'TCGA-HT-7690',
                     'TCGA-HT-7691',
                     'TCGA-HT-7692',
                     'TCGA-HT-7693',
                     'TCGA-HT-7694',
                     'TCGA-HT-7695',
                     'TCGA-HT-7854',
                     'TCGA-HT-7855',
                     'TCGA-HT-7856',
                     'TCGA-HT-7857',
                     'TCGA-HT-7858',
                     'TCGA-HT-7860',
                     'TCGA-HT-7873',
                     'TCGA-HT-7874',
                     'TCGA-HT-7875',
                     'TCGA-HT-7877',
                     'TCGA-HT-7879',
                     'TCGA-HT-7880',
                     'TCGA-HT-7881',
                     'TCGA-HT-7882',
                     'TCGA-HT-7884',
                     'TCGA-HT-7902',
                     'TCGA-HT-8010',
                     'TCGA-HT-8011',
                     'TCGA-HT-8012',
                     'TCGA-HT-8013',
                     'TCGA-HT-8015',
                     'TCGA-HT-8018',
                     'TCGA-HT-8019',
                     'TCGA-HT-8104',
                     'TCGA-HT-8105',
                     'TCGA-HT-8106',
                     'TCGA-HT-8107',
                     'TCGA-HT-8108',
                     'TCGA-HT-8109',
                     'TCGA-HT-8110',
                     'TCGA-HT-8111',
                     'TCGA-HT-8113',
                     'TCGA-HT-8114',
                     'TCGA-HT-8558',
                     'TCGA-HT-8563',
                     'TCGA-HT-8564',
                     'TCGA-HT-A4DS',
                     'TCGA-HT-A4DV',
                     'TCGA-HT-A5R5',
                     'TCGA-HT-A5R7',
                     'TCGA-HT-A5RA',
                     'TCGA-HT-A5RB',
                     'TCGA-HT-A5RC',
                     'TCGA-HT-A614',
                     'TCGA-HT-A615',
                     'TCGA-HT-A616',
                     'TCGA-HT-A617',
                     'TCGA-HT-A618',
                     'TCGA-HT-A619',
                     'TCGA-HT-A61A',
                     'TCGA-HT-A61B',
                     'TCGA-HT-A61C']


            
            
#        for i in range(len(TCGA_LGG)):
#            self.ui.patientID.addItem(str(TCGA_LGG[i]))               
#            self.ui.patientID.setCurrentIndex(0)
            
                        
                        
#        for i in range(1):
#            T1Cfname = '/home/m131199/Desktop/testData/Examples/rigid_reg_T1C_ex1.nii'
#            T2Wfname = '/home/m131199/Desktop/testData/Examples/T2_ex1.nii'
#            self.ui.T1Contrast.addItem(T1Cfname)   
#            index = self.ui.T1Contrast.findText(str(T1Cfname))            
#            self.ui.T1Contrast.setCurrentIndex(index)
#            self.ui.T2Image.addItem(T2Wfname)   
#            index = self.ui.T2Image.findText(str(T2Wfname))            
#            self.ui.T2Image.setCurrentIndex(index)
#        self.ui.figure1.canvas.mpl_connect('button_press_event', self.onclickWidget1)  
        
    def testFunc(self):
        path = '/research/projects/jiri/LGG/LGG400/registered_Jay/'
#        path = '/home/m131199/Desktop/testJiri/'
        for each in os.listdir(path):
            path2 = path + each
            for each in os.listdir(path2):
                if each.endswith('.gz'):
                    if each[0:2] == 'T1':
                        T1Cfname = path2 + '/' + each
                    if each[0:2] == 'T2':
                        T2Wfname = path2 + '/' + each
            
            self.ui.T1Contrast.addItem(T1Cfname)   
            index = self.ui.T1Contrast.findText(str(T1Cfname))            
            self.ui.T1Contrast.setCurrentIndex(index)
            self.ui.T2Image.addItem(T2Wfname)   
            index = self.ui.T2Image.findText(str(T2Wfname))            
            self.ui.T2Image.setCurrentIndex(index)            
            self.loadDataFunc()
            plt.pause(1)
            os.chdir(path2)
            self.loadROIFunc()
            plt.pause(1)
            self.stopEvolving = 1
            self.segmentationFunc2()
            
            
                        
                            
            
            
            
#        mask1 = self.getMask(self.img1)
        
#        num = [49,57,61,103,106,107,110,113,116,136,138,139,140,141,142,144,146,147,576,582,584,592,594,595,597,631,638,644,651,653]
##        num = [49,57,61]
#        thVal = np.arange(0.1,0.5,0.1)
#        for j in range(len(thVal)):
#            self.thVal = thVal[j]
#            for i in range(len(num)):
#                self.ui.T1Contrast.setCurrentIndex(i)
#                self.ui.T2Image.setCurrentIndex(i)
#                self.loadDataFunc()
#                self.loadROIFunc()
#                self.segmentationFunc2()
        
#        num = [49,57,61,103,106,107,110,113,116,136,138,139,140,141,142,144,146,147,576,582,584,592,594,595,597,631,638,644,651,653]
#        for i in range(1):
#            self.ui.T1Contrast.setCurrentIndex(i+2)
#            self.ui.T2Image.setCurrentIndex(i+2)
#            
#            self.ui.tacticCB.setChecked(False)
#            self.loadDataFunc()
#            self.ui.rigidCB.setChecked(True)
#            self.registrationFunc()
#            self.ui.rigidCB.setChecked(False)
##            self.ui.atlasCB.setChecked(True)
##            self.registrationFunc()
##            self.ui.atlasCB.setChecked(False)
#            self.preProcessing3DFunc()
                
                
              
                             
        return
   

    def searchPatientDataFunc(self,event):
        # Get ticket for TACTIC (MIRMAID)
        server = TacticServerStub(setup=False)
        server.set_server('')
        server.set_project('')
        ticket = server.get_ticket ('', '')
        server.set_login_ticket(ticket)
        
        fileName = self.ui.patientID.currentText()
        expression = "@SOBJECT(qin/subject['patientname'," + unichr(39) + str(fileName)+ unichr(39) + "])"
        queryDB=qin.Subject.search(expression=expression, server=server)
        self.exams = queryDB[0].getExams()
        self.ui.imageSeries.clear()
        self.ui.tacticCB.setChecked(True)
        
        for i in range(0, len(self.exams)):
            self.ui.imageSeries.addItem(self.exams[i].studydate[0:11])
#            self.ui.imageSeries.addItem(self.exams[i].description)   
#            index = self.ui.imageSeries.findText(str(self.exams[i].description))            
#            self.ui.imageSeries.setCurrentIndex(index)                
            
            
    def searchSeriesFunc(self, event):
        index = self.ui.imageSeries.findText(str(self.ui.imageSeries.currentText()))
#        print index
        self.ui.T1Contrast.clear()                
        self.ui.T2Image.clear()   
        self.ui.tacticCB.setChecked(True)
        self.series = self.exams[index].getSeries()
        for i in range(0, len(self.series)):
            self.ui.T1Contrast.addItem(self.series[i].description)   
            index = self.ui.T1Contrast.findText(str(self.series[i].description))            
            self.ui.T1Contrast.setCurrentIndex(index)
            
            self.ui.T2Image.addItem(self.series[i].description)   
            index = self.ui.T2Image.findText(str(self.series[i].description))            
            self.ui.T2Image.setCurrentIndex(index)
        
    def scrollT1CImage(self, event):
        if (event.step > 0 and self.z1 != 0):
            self.z1 = self.z1 - 1
            self.ui.lineEdit.setText(str(self.z1))
        elif (event.step < 0 and self.z1 < self.sliceNum1):
            self.z1 = self.z1 + 1
            self.ui.lineEdit.setText(str(self.z1))
        self.img1 = self.img_data1[:,:,self.z1]
        self.imshowFunc()  
    
    def scrollT2WImage(self, event): 
        if (event.step > 0 and self.z2 != 0):
            self.z2 = self.z2 - 1
            self.ui.lineEdit.setText(str(self.z2))
        elif (event.step < 0 and self.z2 < self.sliceNum2):
            self.z2 = self.z2 + 1
            self.ui.lineEdit.setText(str(self.z2))
        self.img2 = self.img_data2[:,:,self.z2]
        self.imshowFunc()  
        
    def loadDataFunc(self):
#        path = '/Users/m131199/Documents/testData/testLGGdata/'
#        fixedImg = path + 'LGG_107_T1C.nii'
        self.segCount =0  
        self.useT1CB = self.ui.useT1.isChecked()
        self.useT2CB = self.ui.useT2.isChecked()
        self.ui.label_4.setText("Brain Tumor Segmentation v4.0")
        self.defaultLGGPathF = 0
        
        if  (self.useT1CB and self.useT2CB):
            self.z =0
            self.z1 = 0
            self.z2 = 0
            self.rotD = -90
    #        self.ui.lineEdit.setText(self.ui.T1Contrast.currentText())
            if self.ui.tacticCB.isChecked():              
                T1ContrastName = self.ui.T1Contrast.currentText()
                index = self.ui.T1Contrast.findText(str(T1ContrastName))            
                file1Path = self.series[index].getFilenameForContext('image')[0];
                
                T2ImageName = self.ui.T2Image.currentText()
                index = self.ui.T2Image.findText(str(T2ImageName))            
                file2Path = self.series[index].getFilenameForContext('image')[0]; 
                
                imgObj1 = nib.load(str(file1Path))
                imgObj2= nib.load(str(file2Path))  
                
                self.imageFile1 = file1Path
                self.imageFile2 = file2Path
                indx1 = self.imageFile1.rfind('/')
                indx2 = self.imageFile2.rfind('/')
                self.filePath1 = self.imageFile1[0:indx1+1]
                self.fileName1 = self.imageFile1[indx1+1:]
                self.filePath2 = self.imageFile2[0:indx2+1]
                self.fileName2 = self.imageFile2[indx2+1:]   
                
#                os.chdir('/home/m131199/Desktop/')
#                with open('TCGA_sequenceList.csv', 'a') as csvfile:
#                    fileWriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)                
#                    fileWriter.writerow([str(file1Path)])
#                    fileWriter.writerow([str(file2Path)])
#                self.index = self.index+1
            else:
                imgObj1 = nib.load(str(self.ui.T1Contrast.currentText()))
                imgObj2= nib.load(str(self.ui.T2Image.currentText()))
                
                self.imageFile1 = str(self.ui.T1Contrast.currentText())
                self.imageFile2 = str(self.ui.T2Image.currentText())
                indx1 = self.imageFile1.rfind('/')
                indx2 = self.imageFile2.rfind('/')
                self.filePath1 = self.imageFile1[0:indx1+1]
                self.fileName1 = self.imageFile1[indx1+1:]
                self.filePath2 = self.imageFile2[0:indx2+1]
                self.fileName2 = self.imageFile2[indx2+1:]
#                ind3 = self.fileName2.rfind('_')
#                sliceNum = self.fileName2[ind3+1:ind3+3]
#                self.z = int(sliceNum) 
                
                
                
            self.affine1 = imgObj1.get_affine()  
            self.affine2 = imgObj2.get_affine()     
            
            self.img_data1 = imgObj1.get_data()
            self.img_data2 = imgObj2.get_data()  

            if self.img_data1.ndim == 2:
                temp = np.zeros((self.img_data1.shape[0],self.img_data1.shape[1],1))
                temp[:,:,0] = self.img_data1
                self.img_data1=temp
                temp = np.zeros((self.img_data2.shape[0],self.img_data2.shape[1],1))
                temp[:,:,0] = self.img_data2
                self.img_data2=temp
            
    #        self.shape = imgObj2.shape
#            self.qform2 = imgObj2.get_header()['pixdim'][0]       
#            self.qform2 = imgObj1.get_header()['pixdim'][0] 
            self.PSx = imgObj1.get_header()['pixdim'][1]
            self.PSy = imgObj1.get_header()['pixdim'][2]
            self.PSz = imgObj1.get_header()['pixdim'][3]
            
            (x1,y1,z1) = orx.aff2axcodes(self.affine1)
            self.Orx = x1
            self.Ory = y1
            self.Orz = z1
            ornt = orx.axcodes2ornt((x1,y1,z1))  
            refOrnt = orx.axcodes2ornt(('R','A','S'))
            newOrnt1 = orx.ornt_transform(ornt,refOrnt)
            
            (x2,y2,z2) = orx.aff2axcodes(self.affine2)
            self.Orx = x2
            self.Ory = y2
            self.Orz = z2
            ornt = orx.axcodes2ornt((x2,y2,z2))  
            refOrnt = orx.axcodes2ornt(('R','A','S'))
            newOrnt2 = orx.ornt_transform(ornt,refOrnt)
            
     
    
            self.img_data1 = orx.apply_orientation(self.img_data1,newOrnt1)
            self.img_data2 = orx.apply_orientation(self.img_data2,newOrnt2)
            
            self.img_data1 = np.fliplr(np.rot90(self.img_data1,1))
            self.img_data2 = np.fliplr(np.rot90(self.img_data2,1))
    
            
     
    #        sizeT1C = self.img_data1.shape
            try:
                (x1,y1,z1) = self.img_data1.shape
            except:
                (x1,y1,z1,d1) = self.img_data1.shape
                self.img_data1 = self.img_data1[:,:,:,1]
                
            try:
                (x2,y2,z2) = self.img_data2.shape
            except:
                (x2,y2,z2,d1) = self.img_data2.shape
                self.img_data2 = self.img_data2[:,:,:,1]
                
            self.sliceNum1 = z1
            self.sliceNum2 = z2
            
            self.shape = self.img_data2.shape
    
            self.img1 = self.img_data1[:,:,self.z]
            self.img2 = self.img_data2[:,:,self.z]
            
            
            self.imshowFunc()  
            
            (x,y,z) = self.shape
            
            self.ui.figure3.canvas.ax.clear()
    #        self.ui.figure3.canvas.ax.imshow(((self.img_data2[:,round(x/2),:])),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,int(round(x/2)),:]),1),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[int(round(y/2)),:,:]),1),cmap=plt.cm.gray)
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
            self.ui.figure4.canvas.draw()
            
    #        self.imhistFunc()
            self.ui.imageSlider.setMinimum(0)
            self.ui.imageSlider.setMaximum(z2-1)
            self.ui.imageSlider.setSingleStep(1)
#            self.ui.imageSlider.setValue(int(sliceNum))
            
            
        elif (self.useT2CB and not(self.useT1CB)):
            self.z =0
            self.z1 = 0
            self.z2 = 0
            self.rotD = -90
            imgObj2= nib.load(str(self.ui.T2Image.currentText()))
            imgObj1 = imgObj2
            self.affine2 = imgObj2.get_affine()     
            self.PSx = imgObj1.get_header()['pixdim'][1]
            self.PSy = imgObj1.get_header()['pixdim'][2]
            self.PSz = imgObj1.get_header()['pixdim'][3]
            (x,y,z) = orx.aff2axcodes(self.affine2)
            self.Orx = x
            self.Ory = y
            self.Orz = z
            ornt = orx.axcodes2ornt((x,y,z))  
            refOrnt = orx.axcodes2ornt(('R','A','S'))
            newOrnt = orx.ornt_transform(ornt,refOrnt)
            self.img_data2 = imgObj2.get_data()       
    
            self.img_data2 = orx.apply_orientation(self.img_data2,newOrnt)
            
            self.img_data2 = np.fliplr(np.rot90(self.img_data2,1))
            self.img_data1 = self.img_data2
            
            self.imageFile2 = str(self.ui.T2Image.currentText())
            self.imageFile1 = self.imageFile2
            indx2 = self.imageFile2.rfind('/')
            indx1 = indx2
            self.filePath1 = self.imageFile1[0:indx1+1]
            self.fileName1 = self.imageFile1[indx1+1:]
            self.filePath2 = self.imageFile2[0:indx2+1]
            self.fileName2 = self.imageFile2[indx2+1:]
            
     
    #        sizeT1C = self.img_data1.shape
            try:
                (x2,y2,z2) = self.img_data2.shape
            except:
                (x2,y2,z2,d1) = self.img_data2.shape
                self.img_data2 = self.img_data2[:,:,:,0]
                
            self.sliceNum1 = z1
            self.sliceNum2 = z2
            
            self.shape = self.img_data2.shape
    
            self.img1 = self.img_data1[:,:,self.z]
            self.img2 = self.img_data2[:,:,self.z]
            
            
            self.imshowFunc()  
            
            (x,y,z) = self.shape
    
            self.ui.figure3.canvas.ax.clear()
    #        self.ui.figure3.canvas.ax.imshow(((self.img_data2[:,round(x/2),:])),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(x/2),:]),1),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[round(y/2),:,:]),1),cmap=plt.cm.gray)
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
            self.ui.figure4.canvas.draw()
            
    #        self.imhistFunc()
            self.ui.imageSlider.setMinimum(0)
            self.ui.imageSlider.setMaximum(z2-1)
            self.ui.imageSlider.setSingleStep(1)
            self.ui.imageSlider.setValue(int(sliceNum))
            
        elif (not(self.useT2CB) and self.useT1CB): 
            self.z =0
            self.z1 = 0
            self.z2 = 0
            self.rotD = -90
    #        self.ui.lineEdit.setText(self.ui.T1Contrast.currentText())
            imgObj1 = nib.load(str(self.ui.T1Contrast.currentText()))
            imgObj2 = imgObj1
            self.affine2 = imgObj1.get_affine()     
    #        self.shape = imgObj2.shape
            self.PSx = imgObj1.get_header()['pixdim'][1]
            self.PSy = imgObj1.get_header()['pixdim'][2]
            self.PSz = imgObj1.get_header()['pixdim'][3]
            (x,y,z) = orx.aff2axcodes(self.affine2)
            self.Orx = x
            self.Ory = y
            self.Orz = z
            ornt = orx.axcodes2ornt((x,y,z))  
            refOrnt = orx.axcodes2ornt(('R','A','S'))
            newOrnt = orx.ornt_transform(ornt,refOrnt)
            self.img_data1 = imgObj1.get_data()
    
            self.img_data1 = orx.apply_orientation(self.img_data1,newOrnt)
            
            self.img_data1 = np.fliplr(np.rot90(self.img_data1,1))
            self.img_data2 = self.img_data1
    
            
            self.imageFile1 = str(self.ui.T1Contrast.currentText())
            self.imageFile2 = self.imageFile1
            indx1 = self.imageFile1.rfind('/')
            indx2 = indx1
            self.filePath1 = self.imageFile1[0:indx1+1]
            self.fileName1 = self.imageFile1[indx1+1:]
            self.filePath2 = self.imageFile2[0:indx2+1]
            self.fileName2 = self.imageFile2[indx2+1:]
            
     
    #        sizeT1C = self.img_data1.shape
            try:
                (x1,y1,z1) = self.img_data1.shape
            except:
                (x1,y1,z1,d1) = self.img_data1.shape
                self.img_data1 = self.img_data1[:,:,:,0]
                
            self.sliceNum1 = z1
            self.sliceNum2 = z2
            
            self.shape = self.img_data2.shape
    
            self.img1 = self.img_data1[:,:,self.z]
            self.img2 = self.img_data2[:,:,self.z]
            
            
            self.imshowFunc()  
            
            (x,y,z) = self.shape
    
            self.ui.figure3.canvas.ax.clear()
    #        self.ui.figure3.canvas.ax.imshow(((self.img_data2[:,round(x/2),:])),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(x/2),:]),1),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[round(y/2),:,:]),1),cmap=plt.cm.gray)
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
            self.ui.figure4.canvas.draw()
            
    #        self.imhistFunc()
            self.ui.imageSlider.setMinimum(0)
            self.ui.imageSlider.setMaximum(z2-1)
            self.ui.imageSlider.setSingleStep(1)            
        return
    
    def browseT1CFunc(self):
#        self.fname = []
        if self.defaultLGGPathF == 0:
            self.T1Cfname=QFileDialog.getOpenFileName(self, 'Open file')
            self.defaultLGGPathF = self.defaultLGGPathF + 1
        else:
            self.T1Cfname=QFileDialog.getOpenFileName()
        if self.T1Cfname=='':  
            return
        self.ui.T1Contrast.addItem(self.T1Cfname)   
        index = self.ui.T1Contrast.findText(str(self.T1Cfname))
        self.ui.T1Contrast.setCurrentIndex(index)
        return
        
    def browseT2Func(self):
        if self.defaultLGGPathF == 0:
            self.T2fname=QFileDialog.getOpenFileName(self, 'Open file')
            self.defaultLGGPathF = self.defaultLGGPathF + 1
        else:
            self.T2fname=QFileDialog.getOpenFileName()        
        if self.T2fname=='':  
            return
        self.ui.T2Image.addItem(self.T2fname)  
        index = self.ui.T2Image.findText(str(self.T2fname))
        self.ui.T2Image.setCurrentIndex(index)
        return
       
    def imageSliderFunc(self):
#        self.ui.label_4.setText("Brain Tumor Segmentation v4.0")
        self.ui.lineEdit.setText(str(self.ui.imageSlider.value()))
        self.z = self.ui.imageSlider.value()
        self.img1 =self.img_data1[:,:,self.z]
        self.img2 =self.img_data2[:,:,self.z]
        self.imshowFunc()          
    
    def alphaSetFunc(self):
        self.imshowFunc()
        
    def skullStrippingFunc(self):
        self.ui.tacticCB.setChecked(False)
        stripSkull(self.filePath1,self.filePath2,self.imageFile1,self.imageFile2,self.fileName1,self.fileName2)       
        if self.fileName1.endswith('.nii'):       
            self.ui.T1Contrast.addItem(self.filePath1 + 'SS_' + self.fileName1 + '.gz')   
            index = self.ui.T1Contrast.findText(self.filePath1 + 'SS_' + self.fileName1 + '.gz')
        elif self.fileName1.endswith('.gz'):
            self.ui.T1Contrast.addItem(self.filePath1 + 'SS_' + self.fileName1[:len(self.fileName1)])   
            index = self.ui.T1Contrast.findText(self.filePath1 + 'SS_' + self.fileName1[:len(self.fileName1)])    
        self.ui.T1Contrast.setCurrentIndex(index)
        
        if self.fileName2.endswith('.nii'): 
            self.ui.T2Image.addItem(self.filePath2 + 'SS_' + self.fileName2 + '.gz')   
            index = self.ui.T2Image.findText(self.filePath2 + 'SS_' + self.fileName2 + '.gz')
        elif self.fileName2.endswith('.gz'):
            self.ui.T2Image.addItem(self.filePath2 + 'SS_' + self.fileName2[:len(self.fileName2)])   
            index = self.ui.T2Image.findText(self.filePath2 + 'SS_' + self.fileName2[:len(self.fileName2)])
        self.ui.T2Image.setCurrentIndex(index)
        self.loadDataFunc()    
    
    def biasFieldCorrFunc(self): 
        self.ui.tacticCB.setChecked(False)
        biasFieldCorrection(self.filePath1,self.filePath2,self.imageFile1,self.imageFile2,self.fileName1,self.fileName2)       
        if self.fileName1.endswith('.nii'):        
            self.ui.T1Contrast.addItem(self.filePath1 + self.fileName1[:len(self.fileName1)-4] + '_corrected.nii')   
            index = self.ui.T1Contrast.findText(self.filePath1 + self.fileName1[:len(self.fileName1)-4] + '_corrected.nii')
            self.ui.T1Contrast.setCurrentIndex(index)
        elif self.fileName1.endswith('.gz'):
            self.ui.T1Contrast.addItem(self.filePath1 + self.fileName1[:len(self.fileName1)-7] + '_corrected.nii')   
            index = self.ui.T1Contrast.findText(self.filePath1 + self.fileName1[:len(self.fileName1)-7] + '_corrected.nii')
            self.ui.T1Contrast.setCurrentIndex(index)
        if self.fileName2.endswith('.nii'):        
            self.ui.T2Image.addItem(self.filePath2 + self.fileName2[:len(self.fileName2)-4] + '_corrected.nii')   
            index = self.ui.T2Image.findText(self.filePath2 + self.fileName2[:len(self.fileName2)-4] + '_corrected.nii')
            self.ui.T2Image.setCurrentIndex(index)
        elif self.fileName2.endswith('.gz'):  
            self.ui.T2Image.addItem(self.filePath2 + self.fileName2[:len(self.fileName2)-7] + '_corrected.nii')   
            index = self.ui.T2Image.findText(self.filePath2 + self.fileName2[:len(self.fileName2)-7] + '_corrected.nii')
            self.ui.T2Image.setCurrentIndex(index)
        self.loadDataFunc()                   
 
    def brushEditFunc(self):
        if self.ui.volBrushCB.isChecked()==True:    
            (row,col,dep) = self.img_data2.shape
            self.overlayImgAX = np.zeros((row,col))
            self.overlayImgSAG = np.zeros((dep,row))
            self.overlayImgCOR = np.zeros((dep,col))
            self.colormap = mpl.colors.LinearSegmentedColormap.from_list('mycmap',[(0,0,0,0),(0,1,0,0.6)])
            self.ui.figure2.canvas.mpl_disconnect(self.__ID1)
            self.ui.figure2.canvas.mpl_disconnect(self.__ID2)
            self.ui.figure2.canvas.mpl_disconnect(self.scrolFlag2)
            self.ui.figure1.canvas.mpl_disconnect(self.__ID3)
            self.ui.figure1.canvas.mpl_disconnect(self.__ID4)
            self.ui.figure3.canvas.mpl_disconnect(self.__ID5)
            self.ui.figure3.canvas.mpl_disconnect(self.__ID6)
            self.ui.figure4.canvas.mpl_disconnect(self.__ID7)
            self.ui.figure4.canvas.mpl_disconnect(self.__ID8)
            


    def brushUpdateFunc(self):
        (rows,cols) = np.where(self.overlayImgAX == 1)
        (rows3,cols3) = np.where(self.overlayImgSAG == 1)
        (rows4,cols4) = np.where(self.overlayImgCOR == 1)
#        sizeV = int(self.ui.brushSize.value())
        dep = self.segImg.shape[2]
        sizeZ = 1#int(sizeV/2)
        zVal = self.z
        if len(rows)>0:
            self.segImg[rows,cols,zVal-sizeZ:zVal+sizeZ+1] = 0
        if len(rows3)>0:
            self.segImg[cols3,round(self.coordXPoint)-sizeZ:round(self.coordXPoint)+sizeZ+1,dep-rows3+1] = 0
        if len(rows4)>0:
            self.segImg[round(self.coordYPoint)-sizeZ:round(self.coordYPoint)+sizeZ+1,cols4,dep-rows4+1] = 0
        
        self.refreshSAGCORViews()
#        labelData = label(self.segImg)
#        test = np.multiply(labelData[0][:,:,self.refZ],self.mask)
#        (indX,indY) = np.where(test > 0)
#        labels = mode(test[indX,indY])      
#        tumLabel = labels[0][0]
#        
#        (indX1,indY1,indZ1) = np.where(labelData[0] == tumLabel)
#        self.segImg = np.zeros(self.shape)
#        self.segImg[indX1,indY1,indZ1]=1        
        
        finalROI = np.rot90(np.fliplr(self.segImg),3)
        refOrnt = orx.axcodes2ornt((self.Orx,self.Ory,self.Orz))  
        ornt = orx.axcodes2ornt(('R','A','S')) 
        newOrnt = orx.ornt_transform(ornt,refOrnt)  
        finalROI = orx.apply_orientation(finalROI,newOrnt)
        new_image = nib.Nifti1Image(finalROI, self.affine2)
#        os.chdir(self.filePath2+'automated3DSegmentations/')        
        os.chdir(self.filePath2)
        nib.save(new_image, self.fileName2[:len(self.fileName2)-4] + '_seg3D.nii')  
#        os.chdir(self.filePath2)
#        nib.save(new_image,'current_seg3D') 
        
        self.overlayImgCOR = np.zeros((self.shape[2],self.shape[1]))
        self.overlayImgSAG = np.zeros((self.shape[2],self.shape[0]))
        self.overlayImgAX = np.zeros((self.shape[0],self.shape[1]))
        self.imshowFunc()

    def resetUpdateSeg(self):
        self.segImg = deepcopy(self.original3DSeg)
        self.overlayImgCOR = np.zeros((self.shape[2],self.shape[1]))
        self.overlayImgSAG = np.zeros((self.shape[2],self.shape[0]))
        self.overlayImgAX = np.zeros((self.shape[0],self.shape[1]))
        
    def registrationFunc(self):
        self.ui.tacticCB.setChecked(False)
#        self.ui.lineEdit.setText("zeynettin")  
        rFlag = self.ui.rigidCB.isChecked()
        aFlag = self.ui.affineCB.isChecked()
        nrFlag = self.ui.nonrigidCB.isChecked()
        atFlag = self.ui.atlasCB.isChecked()
        atSFlag = self.ui.atlasCBS.isChecked()
        
        if (rFlag == 1 and aFlag == 0 and nrFlag == 0 and atFlag == 0):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            rigidRegFunc(self.filePath2,self.fileName1,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'rigid_reg_' + self.fileName1)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'rigid_reg_' + self.fileName1)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        elif (rFlag == 0 and aFlag == 1 and nrFlag == 0 and atFlag == 0):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            affineRegFunc(self.filePath2,self.fileName1,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'affine_reg_' + self.fileName1)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'affine_reg_' + self.fileName1)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        elif (rFlag == 0 and aFlag == 0 and nrFlag == 1 and atFlag == 0):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            nonrigidRegFunc(self.filePath2,self.fileName1,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'nonrigid_reg_' + self.fileName1)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'nonrigid_reg_' + self.fileName1)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        elif (rFlag == 0 and aFlag == 0 and nrFlag == 0 and atFlag == 1):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            atlasRegFunc(self.homeDir, self.filePath2,self.fileName2,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'registeredAtlas_' + self.fileName2)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'registeredAtlas_' + self.fileName2)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        elif (rFlag == 0 and aFlag == 0 and nrFlag == 0 and atSFlag == 1):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            atlasRegFunc2(self.homeDir, self.filePath2,self.fileName2,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'registeredAtlas_' + self.fileName2)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'registeredAtlas_' + self.fileName2)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        elif (rFlag == 0 and aFlag == 1 and nrFlag == 1 and atFlag == 0):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            affine_nonrigidRegFunc(self.filePath2,self.fileName1,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'affine_nonrigid_reg_' + self.fileName1)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'affine_nonrigid_reg_' + self.fileName1)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        elif (rFlag == 1 and aFlag == 0 and nrFlag == 1 and atFlag == 0):
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            rigid_nonrigidRegFunc(self.filePath2,self.fileName1,fixedImg,movingImg)
            self.ui.T1Contrast.addItem(self.filePath2 + 'rigid_nonrigid_reg_' + self.fileName1)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'rigid_nonrigid_reg_' + self.fileName1)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
        else:
            fixedImg = self.filePath2 + self.fileName2
            movingImg = self.filePath1 + self.fileName1
            affineRegFunc(self.filePath2,self.fileName1,fixedImg,movingImg)   
            self.ui.T1Contrast.addItem(self.filePath2 + 'affine_nonrigid_reg_' + self.fileName1)   
            index = self.ui.T1Contrast.findText(self.filePath2 + 'affine_nonrigid_reg_' + self.fileName1)
            self.ui.T1Contrast.setCurrentIndex(index)
            self.loadDataFunc()
    
    def segmentationFunc(self):
        
        self.segFlag == '2D'
        self.mask = self.getMask(self.img1)
        os.chdir(self.filePath2)
        
        if self.segCount != 0:
            self.loadROIFunc()
            
        if self.fileName2.endswith('.nii'):
            pmapWMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[:len(self.fileName2)-4] +'/deformed_pbmap_WM.nii'
            pmapGMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[:len(self.fileName2)-4] + '/deformed_pbmap_GM.nii'
            pmapCSFpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[:len(self.fileName2)-4] + '/deformed_pbmap_CSF.nii'
        elif self.fileName2.endswith('.gz'):        
            pmapWMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[:len(self.fileName2)-7] +'/deformed_pbmap_WM.nii'
            pmapGMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[:len(self.fileName2)-7] + '/deformed_pbmap_GM.nii'
            pmapCSFpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[:len(self.fileName2)-7] + '/deformed_pbmap_CSF.nii'        
        
        pmapWM = nib.load(pmapWMpath)
        pmapWM_data = pmapWM.get_data()
        pmapGM = nib.load(pmapGMpath)
        pmapGM_data = pmapGM.get_data()
        pmapCSF = nib.load(pmapCSFpath)
        pmapCSF_data = pmapCSF.get_data()
        
        affine = pmapWM.get_affine() 
        (x,y,z) = orx.aff2axcodes(affine)
        ornt = orx.axcodes2ornt((x,y,z))  
        refOrnt = orx.axcodes2ornt(('R','A','S'))
        newOrnt = orx.ornt_transform(ornt,refOrnt)    

        pmapWM_data = orx.apply_orientation(pmapWM_data,newOrnt)
        pmapGM_data = orx.apply_orientation(pmapGM_data,newOrnt)
        pmapCSF_data = orx.apply_orientation(pmapCSF_data,newOrnt)
        
        pmapWM_data = np.fliplr(np.rot90(pmapWM_data,1))
        pmapGM_data = np.fliplr(np.rot90(pmapGM_data,1))
        pmapCSF_data = np.fliplr(np.rot90(pmapCSF_data,1))
        
        pmapWMslice = pmapWM_data[:,:,self.z]
        pmapGMslice = pmapGM_data[:,:,self.z]
        pmapCSFslice = pmapCSF_data[:,:,self.z]
        
#        plt.imshow(self.img2)
#        plt.pause(1)
#        plt.imshow(pmapWMslice)
        
#        img1 = gaussian_filter(self.img1,[1,1], mode = 'mirror')
#        img2 = gaussian_filter(self.img2,[1,1], mode = 'mirror')
        [nTissuePrior, abTissuePrior,maskWM,maskGM,maskCSF] = probEstROI.AtlasBasedSegmentation(self.img1,self.img2,self.mask,pmapWMslice, pmapGMslice,pmapCSFslice,self.useT1CB, self.useT2CB)
        
 
        
        if not(self.thVal is None):
            (indX1,indY1) = np.where (abTissuePrior>=self.thVal)
        else:
            (indX1,indY1) = np.where (abTissuePrior>=0.3)
        (indX2,indY2) = np.where (abTissuePrior==1)
        (indX3,indY3) = np.where (nTissuePrior>0.9)
        abTissuePrior[indX1,indY1] = 1

        if self.segCount == 0:
            gI = segmentation.gborders(abTissuePrior, self.mask, alpha=100, sigma=1)
    #        gI[indX2,indY2] = 1
            gI[indX3,indY3] = 1
        
            mgac = segmentation.MorphGAC(gI, smoothing=2, threshold=0.5, balloon=-1)
            mgac.levelset = self.circle_levelset(self.img1.shape, (self.x, self.y), 40)
          
            ## This is for saving segmentation results 
            if self.stopEvolving == 0:
                self.evolve_visual(mgac, num_iters=50, background=self.img1)
                for i in range(50):
                    mgac.step()

                
            self.segCount+=1
            finalImg = np.zeros((self.shape))
            finalImg[:,:,self.z] = mgac.levelset
            finalImg = np.rot90(np.fliplr(finalImg),3)
    
            refOrnt = orx.axcodes2ornt((self.Orx,self.Ory,self.Orz))  
            ornt = orx.axcodes2ornt(('R','A','S')) 
            newOrnt = orx.ornt_transform(ornt,refOrnt)  
            finalImg = orx.apply_orientation(finalImg,newOrnt) 
    
            new_image = nib.Nifti1Image(finalImg, self.affine2)        
            os.chdir(self.filePath2)
            if self.fileName2.endswith('.gz'):
                nib.save(new_image, 'Seg2D_' + self.fileName2[:len(self.fileName2)-7]+ '_' + str(self.z) + '.nii.gz')
            else:
                nib.save(new_image, 'Seg2D_' + self.fileName2[:len(self.fileName2)-4] + '_' + str(self.z) + '.nii.gz')
        
#            from matplotlib.pylab import pause
#            from skimage import measure
#            contours = measure.find_contours(mgac.levelset, 0.8)
#            self.allxpoints=np.ndarray.tolist(contours[0][:,1])
#            self.allypoints=np.ndarray.tolist(contours[0][:,0])
            
            if self.stopEvolving == 1:
                self.stopEvolving = 0
            else:
                self.saveROIFunc()
            
        else:
            plt.subplot(1,3,1)
            plt.imshow(maskWM,cmap='gray')
            plt.subplot(1,3,2)
            plt.imshow(maskGM,cmap='gray')
            plt.subplot(1,3,3)
            plt.imshow(maskCSF,cmap='gray')
            plt.show()   
            
            refOrnt = orx.axcodes2ornt((self.Orx,self.Ory,self.Orz))  
            ornt = orx.axcodes2ornt(('R','A','S')) 
            newOrnt = orx.ornt_transform(ornt,refOrnt)  
            
            finalImg = np.zeros((self.shape))
            finalImg[:,:,self.z] = maskWM
            finalImg = np.rot90(np.fliplr(finalImg),3)
            finalImg = orx.apply_orientation(finalImg,newOrnt) 
            
            new_image = nib.Nifti1Image(finalImg, self.affine2)        
            os.chdir(self.filePath2)
            nib.save(new_image, 'maskWM.nii.gz')
            
            finalImg = np.zeros((self.shape))
            finalImg[:,:,self.z] = maskGM
            finalImg = np.rot90(np.fliplr(finalImg),3)
            finalImg = orx.apply_orientation(finalImg,newOrnt) 
    
            new_image = nib.Nifti1Image(finalImg, self.affine2)        
            os.chdir(self.filePath2)
            nib.save(new_image, 'maskGM.nii.gz')
    
            finalImg = np.zeros((self.shape))
            finalImg[:,:,self.z] = maskCSF
            finalImg = np.rot90(np.fliplr(finalImg),3)
            finalImg = orx.apply_orientation(finalImg,newOrnt) 
    
            new_image = nib.Nifti1Image(finalImg, self.affine2)        
            os.chdir(self.filePath2)
            nib.save(new_image, 'maskCSF.nii.gz')
            self.ui.label_4.setText("Probability maps saved! Press T1&T2 buttons: Load new images!")  


    def segmentationFunc2(self):
        self.segCount = 0
        self.ui.label_4.setText("Running... Please Wait!") 
        self.ui.label_4.show()

        self.segmentationFunc()
#        self.segmentationFunc()
                    

    def segmentationFunc3(self):
        self.segFlag == '3D'
        self.orgPSz = self.PSz
        self.orgZ = self.z
        self.preProcessing3DFunc()

        minX1 = round(min(self.allxpoints))
        minY1 = round(min(self.allypoints))  
        maxX1 = round(max(self.allxpoints))
        maxY1 = round(max(self.allypoints))
        
        minX3 = round(min(self.allxpoints3))
        minY3 = round(min(self.allypoints3))
        maxX3 = round(max(self.allxpoints3))
        maxY3 = round(max(self.allypoints3))
        
        minX4 = round(min(self.allxpoints4))
        minY4 = round(min(self.allypoints4))   
        maxX4 = round(max(self.allxpoints4))
        maxY4 = round(max(self.allypoints4))

        
#        minX = min(minX1,minX4)
#        maxX = max(maxX1,maxX4)
#        minY = min(minY1,minX3)
#        maxY = max(maxY1,maxX3)
        minX = minX4
        maxX = maxX4
        minY = minY1
        maxY = maxY1
        minZ = round(self.shape[2] - max(maxY3,maxY4)*self.orgPSz-1)
        maxZ = round(self.shape[2] - min(minY3,minY4)*self.orgPSz-1)
        self.z = round(self.orgZ*self.orgPSz-1)

        rect3D = [[minX,minY,minZ],[maxX,maxY,maxZ]]
#        centerP = (center4[0],center3[0], centerZ)
#        mask3D3 = np.zeros(self.shape)
        mask3D = np.zeros(self.shape)
        mask3D[minY:maxY,minX:maxX,minZ:maxZ] = 1        
#        mask3D3[minY+20:maxY-20,minX+20:maxX-20,minZ+2:maxZ-2] = 1 
#        mask3D2 = np.fliplr(np.rot90(mask3D,3))
        
        self.mask = self.getMask(self.img1)
        
#        new_image = nib.Nifti1Image(mask3D2, self.affine2)        
#        os.chdir(self.filePath2)
#        nib.save(new_image, 'testMasck3D')     
#        mask3D = self.shape

        os.chdir(self.filePath2)
        
        if self.fileName2.endswith('.nii'):  
            pmapWMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[1:len(self.fileName2)-4] +'/Ideformed_pbmap_WM.nii.gz'        
            pmapGMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[1:len(self.fileName2)-4] + '/Ideformed_pbmap_GM.nii.gz'
            pmapCSFpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[1:len(self.fileName2)-4] + '/Ideformed_pbmap_CSF.nii.gz'
        elif self.fileName2.endswith('.gz'):
            pmapWMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[1:len(self.fileName2)-7] +'/Ideformed_pbmap_WM.nii'        
            pmapGMpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[1:len(self.fileName2)-7] + '/Ideformed_pbmap_GM.nii'
            pmapCSFpath = self.filePath2 + 'atlasTransformations_' + self.fileName2[1:len(self.fileName2)-7] + '/Ideformed_pbmap_CSF.nii'

        pmapWM = nib.load(pmapWMpath)
        pmapWM_data = pmapWM.get_data()
        pmapGM = nib.load(pmapGMpath)
        pmapGM_data = pmapGM.get_data()
        pmapCSF = nib.load(pmapCSFpath)
        pmapCSF_data = pmapCSF.get_data()
        
        affine = pmapWM.get_affine() 
        (x,y,z) = orx.aff2axcodes(affine)
        ornt = orx.axcodes2ornt((x,y,z))  
        refOrnt = orx.axcodes2ornt(('R','A','S'))
        newOrnt = orx.ornt_transform(ornt,refOrnt)    

        pmapWM_data = orx.apply_orientation(pmapWM_data,newOrnt)
        pmapGM_data = orx.apply_orientation(pmapGM_data,newOrnt)
        pmapCSF_data = orx.apply_orientation(pmapCSF_data,newOrnt)
        
        pmapWM_data = np.fliplr(np.rot90(pmapWM_data,1))
        pmapGM_data = np.fliplr(np.rot90(pmapGM_data,1))
        pmapCSF_data = np.fliplr(np.rot90(pmapCSF_data,1))
        
        pmapWMslice = pmapWM_data[:,:,self.z]
        pmapGMslice = pmapGM_data[:,:,self.z]
        pmapCSFslice = pmapCSF_data[:,:,self.z]
        
        nTissuePrior, abTissuePrior = probEstROI3D.AtlasBasedSegmentation(self.img_data1,self.img_data2,self.z, self.mask, mask3D, pmapWMslice, pmapGMslice,pmapCSFslice,rect3D)
        
        (numrows,numcols,dep) =self.img_data1.shape 
        
#        averageImg = (normImg1+normImg2)/2        
#        (th,centerX,centerY) = resampleROIVector.ROIstats(normImg1,normImg2,averageImg,self.mask, self.allxpoints, self.allypoints)        


        (indX1,indY1,indZ1) = np.where (abTissuePrior>=0.3)
        (indX2,indY2,indZ2) = np.where (abTissuePrior<0.3)
        (indX3,indY3,indZ3) = np.where (abTissuePrior==1) 
#        (indX4,indY4,indZ4) = np.where (nTissuePrior>0.5)
        abTissuePrior[indX1,indY1,indZ1] = 1
        abTissuePrior[indX2,indY2,indZ2] = 0

        gI = segmentation.gborders3D(abTissuePrior, mask3D, alpha=100, sigma=[2,2,1])
        gI[indX3,indY3,indZ3] = 1
              
        
        gI1 = np.fliplr(np.rot90(gI,3))
        
        
#        mgac = segmentation.MorphACWE(gI, smoothing=1, lambda1=1, lambda2=1)        
        mgac = segmentation.MorphGAC(gI, smoothing=1, threshold=0.5, balloon=-1)
        mgac.levelset = mask3D
        mgac.run(40)
#        for i in range(80):
#            mgac.step()
#            plt.imshow(mgac.levelset[:,:,15])
#            plt.show()
        
#        self.finalROI = mgac.levelset
#        finalROI = np.fliplr(np.rot90(mgac.levelset,3))
        
        labelData = label(mgac.levelset)
        test = np.multiply(labelData[0][:,:,self.z],self.mask)
        (indX,indY) = np.where(test > 0)
        labels = mode(test[indX,indY])      
        tumLabel = labels[0][0]
        self.refZ = deepcopy(self.z)       
        
        (indX1,indY1,indZ1) = np.where(labelData[0] == tumLabel)
        self.original3DSeg = np.zeros(self.shape)
        self.original3DSeg[indX1,indY1,indZ1]=1

        self.ui.T1Contrast.addItem(self.filePath1 + self.fileName1[1:])   
        index = self.ui.T1Contrast.findText(self.filePath1 + self.fileName1[1:])
        self.ui.T1Contrast.setCurrentIndex(index)
        self.ui.T2Image.addItem(self.filePath2 + self.fileName2[1:])   
        index = self.ui.T2Image.findText(self.filePath2 + self.fileName2[1:])
        self.ui.T2Image.setCurrentIndex(index)
        self.loadDataFunc()  

        self.original3DSeg = interp3D.zoom(self.original3DSeg,[1,1,1/self.PSz])
        self.original3DSeg = np.ones(self.original3DSeg.shape)*(self.original3DSeg>0.1)

#        slices = np.multiply(range(self.shape[2]),self.PSz)
#        newSegImg = np.zeros(self.shape)
#        for i in range(self.shape[2]):
#            newSegImg[:,:,i] = self.original3DSeg[:,:,round(slices[i])]
#            
#        self.load3DSegFunc()
        
            
        finalROI = np.rot90(np.fliplr(self.original3DSeg),3)
        
        refOrnt = orx.axcodes2ornt((self.Orx,self.Ory,self.Orz))  
        ornt = orx.axcodes2ornt(('R','A','S')) 
        newOrnt = orx.ornt_transform(ornt,refOrnt)  
        finalROI = orx.apply_orientation(finalROI,newOrnt)
        
        
        self.save3DPath = self.filePath2
        
        new_image = nib.Nifti1Image(finalROI, self.affine2)       
        os.chdir(self.filePath2)
        nib.save(new_image, 'current_seg3D.nii')
        
        
        self.segImg = deepcopy(self.original3DSeg)
        self.ui.overlaySeg.setChecked(True)
        
    def preProcessing3DFunc(self):
        file1 = self.filePath1+self.fileName1
        file2 = self.filePath2+self.fileName2
        preProcessing3D.interpolateData(self.filePath1,self.filePath2,file1,file2,self.fileName1,self.fileName2)        
        self.ui.T1Contrast.addItem(self.filePath1 + 'I' + self.fileName1)   
        index = self.ui.T1Contrast.findText(self.filePath1 + 'I' + self.fileName1)
        self.ui.T1Contrast.setCurrentIndex(index)
        self.ui.T2Image.addItem(self.filePath2 + 'I' + self.fileName2)   
        index = self.ui.T2Image.findText(self.filePath2 + 'I' + self.fileName2)
        self.ui.T2Image.setCurrentIndex(index)
        self.loadDataFunc()  

    def load2DSegFunc(self):
#        path = self.filePath2 + 'automated3DSegmentations/'+ self.fileName2[:len(self.fileName2)-4] + '_seg3D.nii'
        if self.fileName2.endswith('.gz'):
            segFileName = 'Seg2D_' + self.fileName2[:len(self.fileName2)-7]+ '_' + str(self.z) + '.nii.gz'
        else:
            segFileName = 'Seg2D_' + self.fileName2[:len(self.fileName2)-4] + '_' + str(self.z) + '.nii.gz'
        path = self.filePath2 +  segFileName
        segImgObj = nib.load(path)
        segImgData = segImgObj.get_data()
        
        ornt = orx.axcodes2ornt((self.Orx,self.Ory,self.Orz))  
        refOrnt = orx.axcodes2ornt(('R','A','S'))
        newOrnt = orx.ornt_transform(ornt,refOrnt)
        segImgData = orx.apply_orientation(segImgData,newOrnt)      
        segImgData = np.fliplr(np.rot90(segImgData,1))
        self.segImg = deepcopy(segImgData)
        self.ui.overlaySeg.setChecked(True)
        
    def load3DSegFunc(self):
#        path = self.filePath2 + 'automated3DSegmentations/'+ self.fileName2[:len(self.fileName2)-4] + '_seg3D.nii'
        path = self.filePath2 +  'current_seg3D.nii'
        segImgObj = nib.load(path)
        segImgData = segImgObj.get_data()
        
        ornt = orx.axcodes2ornt((self.Orx,self.Ory,self.Orz))  
        refOrnt = orx.axcodes2ornt(('R','A','S'))
        newOrnt = orx.ornt_transform(ornt,refOrnt)
        segImgData = orx.apply_orientation(segImgData,newOrnt)      
        segImgData = np.fliplr(np.rot90(segImgData,1))
        self.segImg = deepcopy(segImgData)
        self.ui.overlaySeg.setChecked(True)


        
    def circle_levelset(self, shape, center, sqradius, scalerow=1.0):
        """Build a binary function with a circle as the 0.5-levelset."""
#        grid = np.mgrid[map(slice, shape)].T - center
#        phi = sqradius - np.sqrt(np.sum((grid.T)**2, 0))
#        u = np.float_(phi > 0)
        u = self.getMask(self.img1)
        return u        
        
    
    def evolve_visual(self, msnake, levelset=None, num_iters=20, background=None):
#        self.ui.lineEdit.setText("zeynettin")  
        """
        Visual evolution of a morphological snake.
        
        Parameters
        ----------
        msnake : MorphGAC or MorphACWE instance
            The morphological snake solver.
        levelset : array-like, optional
            If given, the levelset of the solver is initialized to this. If not
            given, the evolution will use the levelset already set in msnake.
        num_iters : int, optional
            The number of iterations.
        background : array-like, optional
            If given, background will be shown behind the contours instead of
            msnake.data.
        """
#        from matplotlib import pyplot as ppl
        
        if levelset is not None:
            msnake.levelset = levelset
   
        # Prepare the visual environment.
        self.ui.figure1.canvas.ax.clear()
        self.ui.figure2.canvas.ax.clear()

        self.ui.figure1.canvas.ax.imshow(self.img1, cmap=plt.cm.gray)
        self.ui.figure2.canvas.ax.imshow(self.img2, cmap=plt.cm.gray)

        self.ui.figure1.canvas.ax.contour(msnake.levelset, [0.5], colors='r')
        self.ui.figure2.canvas.ax.contour(msnake.levelset, [0.5], colors='r')
        self.ui.figure1.canvas.draw()
        self.ui.figure2.canvas.draw()

        plt.pause(0.001)
        # Iterate.
        for i in xrange(num_iters):
            # Evolve.
            msnake.step()
            
            # Update figure.
            del self.ui.figure1.canvas.ax.collections[0]
            del self.ui.figure2.canvas.ax.collections[0]
            self.ui.figure1.canvas.ax.imshow(self.img1, cmap=plt.cm.gray)
            self.ui.figure2.canvas.ax.imshow(self.img2, cmap=plt.cm.gray)
#            self.ui.figure1.canvas.fig.hold(True)
#            self.ui.figure2.canvas.fig.hold(True)
            self.ui.figure1.canvas.ax.contour(msnake.levelset, [0.5], colors='r')
            self.ui.figure2.canvas.ax.contour(msnake.levelset, [0.5], colors='r')
#            ax_u.set_data(msnake.levelset)
            self.ui.figure1.canvas.draw()
            self.ui.figure2.canvas.draw()
            QtGui.QApplication.processEvents()
#            QtGui.Application.processEvents()
#            plt.pause(1)
        
        # Return the last levelset.
        return msnake.levelset  
        
    def imshowFunc(self):
        overlayFlag = self.ui.overlaySeg.isChecked()      
              
        self.ui.figure1.canvas.ax.clear()
        self.ui.figure1.canvas.ax.imshow(self.img1,cmap=plt.cm.gray)
#        self.ui.figure1.canvas.ax.set_aspect('auto')
        self.ui.figure1.canvas.ax.get_xaxis().set_visible(False)
        self.ui.figure1.canvas.ax.get_yaxis().set_visible(False)
#        self.ui.figure1.canvas.ax.set_aspect('auto')
        self.ui.figure1.canvas.ax.set_title('T1 Contrast',color = 'white')
        self.ui.figure1.canvas.draw()
        
        
        self.ui.figure2.canvas.ax.clear()
        self.ui.figure2.canvas.ax.imshow(self.img2,cmap=plt.cm.gray)
#        self.ui.figure2.canvas.ax.set_aspect('auto')
        self.ui.figure2.canvas.ax.get_xaxis().set_visible(False)
        self.ui.figure2.canvas.ax.get_yaxis().set_visible(False)
#        self.ui.figure2.canvas.ax.set_aspect('auto')
        self.ui.figure2.canvas.ax.set_title('T2 Weighted', color = 'white')
        self.ui.figure2.canvas.draw()
        if overlayFlag == True: 
            self.colormap1 = mpl.colors.LinearSegmentedColormap.from_list('mycmap',[(0,0,0,0),(1,0,0,self.ui.alphaSet.value()/10.0)])
            self.ui.figure2.canvas.ax.hold(True)
            self.ui.figure2.canvas.ax.imshow(self.segImg[:,:,self.z],cmap = self.colormap1)           
            self.ui.figure2.canvas.draw()

        
    def onclickWidget1(self, event):
        self.ui.figure1.canvas.ax.set_title(str(int(event.xdata))+','+str(int(event.ydata))+','+str(int(self.img1[np.round(event.ydata),np.round(event.xdata)])), color='green')
        self.ui.figure1.canvas.draw()
    
    def onclickWidget2(self, event):
        self.ui.figure2.canvas.ax.set_title(str(int(event.xdata))+','+str(int(event.ydata))+','+str(int(self.img2[np.round(event.ydata),np.round(event.xdata)])), color='green')
         
        if self.ui.volBrushCB.isChecked() == True:
            self.ui.figure2.canvas.ax.hold(True)
            sizeV = int(self.ui.brushSize.value())
            sizeZ = 1#int(sizeV/2)
            row = int(event.ydata)
            col = int(event.xdata) 
            dep = self.shape[2]-self.z
            
#            if self.ui.isoBrushCB.isChecked() == False:
#                self.overlayImgAX[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 1
#                self.overlayImgSAG[dep-sizeZ:dep+sizeZ,row-sizeV:row+sizeV] = 1
#                self.overlayImgCOR[dep-sizeZ:dep+sizeZ,col-sizeV:col+sizeV] = 1
#            else:
#                self.overlayImgAX[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 0
#                self.overlayImgSAG[dep-sizeZ:dep+sizeZ,row-sizeV:row+sizeV] = 0
#                self.overlayImgCOR[dep-sizeZ:dep+sizeZ,col-sizeV:col+sizeV] = 0
#            self.refreshSAGCORViews()
        else:
            self.coordXPoint = event.xdata
            self.coordYPoint = event.ydata
            self.ui.figure3.canvas.ax.clear()
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(event.xdata),:]),1),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[round(event.ydata),:,:]),1),cmap=plt.cm.gray)
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
            self.ui.figure4.canvas.draw()
            
            self.refreshSAGCORViews()
#            self.ui.figure2.canvas.ax.hold(True)            
#            self.ui.figure2.canvas.ax.imshow(self.overlayImgAX,cmap = self.colormap)    
#            self.ui.figure2.canvas.draw()
#            self.ui.figure3.canvas.ax.hold(True)
#            self.ui.figure3.canvas.ax.imshow(self.overlayImgSAG,cmap = self.colormap)
#            self.ui.figure3.canvas.ax.set_aspect('auto')       
#            self.ui.figure3.canvas.draw()
#            self.ui.figure4.canvas.ax.hold(True)
#            self.ui.figure4.canvas.ax.imshow(self.overlayImgCOR,cmap = self.colormap) 
#            self.ui.figure4.canvas.ax.set_aspect('auto')
#            self.ui.figure4.canvas.draw()
            

        #self.img1[np.round(event.xdata),np.round(event.ydata)]
        self.ui.figure2.canvas.draw()
        
    def onMotion2(self,event):
        if self.ui.volBrushCB.isChecked() == True and event.button == 1:
            self.ui.figure2.canvas.ax.hold(True)
            sizeV = int(self.ui.brushSize.value())
            sizeZ = 1#int(sizeV/2)
            row = int(event.ydata)
            col = int(event.xdata) 
            dep = self.shape[2]-self.z
            
            if self.ui.isoBrushCB.isChecked() == True:
                self.overlayImgAX[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 0
#                self.overlayImgSAG[dep-sizeZ:dep+sizeZ,row-sizeV:row+sizeV] = 0
#                self.overlayImgCOR[dep-sizeZ:dep+sizeZ,col-sizeV:col+sizeV] = 0
#                self.ui.figure2.canvas.ax.imshow(self.img_data2[:,:,self.z],cmap = 'gray')
#                self.ui.figure2.canvas.ax.hold(True) 
                self.imshowFunc()
                self.ui.figure2.canvas.ax.imshow(self.overlayImgAX,cmap = self.colormap)
                self.ui.figure2.canvas.draw()                  
            else:
                self.overlayImgAX[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 1
#                self.overlayImgSAG[dep-sizeZ:dep+sizeZ,row-sizeV:row+sizeV] = 1
#                self.overlayImgCOR[dep-sizeZ:dep+sizeZ,col-sizeV:col+sizeV] = 1
                self.ui.figure2.canvas.ax.imshow(self.overlayImgAX,cmap = self.colormap)
                self.ui.figure2.canvas.draw()     
#            self.ui.figure2.canvas.ax.hold(True)  

    def refreshSAGCORViews(self):
            self.ui.figure3.canvas.ax.clear()
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(self.coordXPoint),:]),1),cmap=plt.cm.gray)
#            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
#            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[round(self.coordYPoint),:,:]),1),cmap=plt.cm.gray)
#            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
#            self.ui.figure4.canvas.draw()
            
            self.ui.figure3.canvas.ax.hold(True)
            self.ui.figure3.canvas.ax.imshow(np.rot90(self.segImg[:,round(self.coordXPoint),:]),cmap = self.colormap1)
            self.ui.figure3.canvas.ax.set_aspect('auto')       
            self.ui.figure3.canvas.draw()
            self.ui.figure4.canvas.ax.hold(True)
            self.ui.figure4.canvas.ax.imshow(np.rot90(self.segImg[round(self.coordYPoint),:,:]),cmap = self.colormap1) 
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.draw()   

    def onRelease2(self,event):
        if self.ui.isoBrushCB.isChecked() == True:

            self.ui.figure3.canvas.ax.clear()
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(self.coordXPoint),:]),1),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[round(self.coordYPoint),:,:]),1),cmap=plt.cm.gray)
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
            self.ui.figure4.canvas.draw()
            
            self.ui.figure3.canvas.ax.imshow(self.overlayImgSAG,cmap = self.colormap)
            self.ui.figure3.canvas.ax.set_aspect('auto')       
            self.ui.figure3.canvas.draw()
#            self.ui.figure4.canvas.ax.hold(True)
            self.ui.figure4.canvas.ax.imshow(self.overlayImgCOR,cmap = self.colormap) 
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.draw()       
        else:
            t=1
#            self.ui.figure3.canvas.ax.hold(True)
#            self.ui.figure3.canvas.ax.imshow(self.overlayImgSAG,cmap = self.colormap)
#            self.ui.figure3.canvas.ax.set_aspect('auto')       
#            self.ui.figure3.canvas.draw()
##            self.ui.figure4.canvas.ax.hold(True)
#            self.ui.figure4.canvas.ax.imshow(self.overlayImgCOR,cmap = self.colormap) 
#            self.ui.figure4.canvas.ax.set_aspect('auto')
#            self.ui.figure4.canvas.draw()
#        time.sleep(2)
#        self.overlayImgAX =np.zeros((self.shape[0],self.shape[1]))
#        if self.ui.volBrushCB.isChecked() == True:
#            self.ui.figure2.canvas.draw()    
#            self.ui.figure3.canvas.draw()
#            self.ui.figure4.canvas.draw()            

            
            
    def onclickWidget3(self, event):
        self.ui.figure3.canvas.ax.set_title(str(int(event.xdata))+','+str(int(self.shape[2]-event.ydata+1)), color='green')            
        self.ui.figure3.canvas.ax.set_aspect('auto')
        self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
        self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
#        self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')        
        self.ui.figure3.canvas.draw()
        
#        if self.ui.volBrushCB.isChecked():
#            self.ui.figure3.canvas.ax.hold(True)
#            sizeV = int(self.ui.brushSize.value())
#            sizeZ = 1#int(sizeV/2)
#            row = int(event.ydata)
#            col = int(event.xdata) 
#            dep = self.shape[2]-self.z+1
#            self.overlayImgSAG[row-sizeZ:row+sizeZ,col-sizeV:col+sizeV] = 1
#            self.ui.figure3.canvas.ax.imshow(self.overlayImgSAG,cmap = self.colormap)
#            self.ui.figure3.canvas.ax.set_aspect('auto')       
#            self.ui.figure3.canvas.draw()
#
#            self.overlayImgAX[col-sizeV:col+sizeV,self.coordXPoint-sizeV:self.coordXPoint+sizeV] = 1
#            self.overlayImgCOR[dep-sizeZ:dep+sizeZ,self.coordYPoint-sizeV:self.coordYPoint+sizeV,] = 1
#            self.ui.figure2.canvas.ax.hold(True)
#            self.ui.figure2.canvas.ax.imshow(self.overlayImgAX,cmap = self.colormap)
##            self.ui.figure2.canvas.ax.set_aspect('auto')       
#            self.ui.figure2.canvas.draw()
#            self.ui.figure4.canvas.ax.hold(True)
#            self.ui.figure4.canvas.ax.imshow(self.overlayImgCOR,cmap = self.colormap) 
#            self.ui.figure4.canvas.ax.set_aspect('auto')
#            self.ui.figure4.canvas.draw()
            
    def onMotion3(self,event):
        if self.ui.volBrushCB.isChecked() == True and event.button == 1:
            self.ui.figure3.canvas.ax.hold(True)
            sizeV = int(self.ui.brushSize.value())
            sizeZ = 1#int(sizeV/2)
            row = int(event.ydata)
            col = int(event.xdata) 
            dep = self.shape[2]-self.z
            
            if self.ui.isoBrushCB.isChecked() == True:
                self.overlayImgSAG[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 0
                self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(self.coordXPoint),:]),1),cmap=plt.cm.gray)
                self.ui.figure3.canvas.ax.imshow(self.overlayImgSAG,cmap = self.colormap)
                self.ui.figure3.canvas.ax.set_aspect('auto')
                self.ui.figure3.canvas.draw()                  
            else:
                self.overlayImgSAG[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 1
                self.ui.figure3.canvas.ax.imshow(self.overlayImgSAG,cmap = self.colormap)
                self.ui.figure3.canvas.ax.set_aspect('auto')
                self.ui.figure3.canvas.draw()    
                

            
    def onRelease3(self,event):
        t=1
        
            
    def onclickWidget4(self, event):
        self.ui.figure4.canvas.ax.set_title(str(int(event.xdata))+','+str(int(self.shape[2]-event.ydata+1)), color='green')
        self.ui.figure4.canvas.ax.set_aspect('auto')
        self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
        self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
#        self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')        
        self.ui.figure4.canvas.draw()
  
                     
    def onMotion4(self,event):
        if self.ui.volBrushCB.isChecked() == True and event.button == 1:
            self.ui.figure4.canvas.ax.hold(True)
            sizeV = int(self.ui.brushSize.value())
            sizeZ = 1#int(sizeV/2)
            row = int(event.ydata)
            col = int(event.xdata) 
            dep = self.shape[2]-self.z
            
            if self.ui.isoBrushCB.isChecked() == True:
                self.overlayImgCOR[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 0
                self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[:,round(self.coordXPoint),:]),1),cmap=plt.cm.gray)
                self.ui.figure4.canvas.ax.imshow(self.overlayImgCOR,cmap = self.colormap)
                self.ui.figure4.canvas.ax.set_aspect('auto')
                self.ui.figure4.canvas.draw()                  
            else:
                self.overlayImgCOR[row-sizeV:row+sizeV,col-sizeV:col+sizeV] = 1
                self.ui.figure4.canvas.ax.imshow(self.overlayImgCOR,cmap = self.colormap)
                self.ui.figure4.canvas.ax.set_aspect('auto')
                self.ui.figure4.canvas.draw()   
            
    def onRelease4(self,event):
        t=1
        
    def imhistFunc(self):
        self.ui.plotHist.canvas.ax.set_title('Histogram',color = 'w', fontsize = '10')
#        temp = self.img1
        self.ui.plotHist.canvas.ax.hist(self.img1.flatten(), 256, range=(0.0,100), fc='gray', ec='r') 
        self.ui.plotHist.canvas.draw()
#        self.ui.lineEdit.setText("zeynettin")

    def saveROIFunc(self):
        os.chdir(self.filePath2)
        f = open(self.fileName2[:len(self.fileName2)-4] + '_ROI_J1.txt', 'w')
        if self.segFlag == '2D':
            data = (self.segFlag,self.allxpoints,self.allypoints,self.z)
        else:    
            data = (self.segFlag,self.allxpoints,self.allypoints,self.z,self.allxpoints3,self.allypoints3,self.allxpoints4,self.allypoints4, self.coordXPoint,self.coordYPoint)
        
        jsondata = json.dumps(data, indent=4, skipkeys=True, sort_keys=True)
        f.write(jsondata)

        f.close()
    
    def deleteROI(self):
        self.imshowFunc()
        self.ui.polygon.setChecked(False)
        self.ui.polygon.setChecked(True)
        
    def loadROIFunc(self):
        os.chdir(self.filePath2)
        filename = self.fileName2[:len(self.fileName2)-4] + '_ROI_J1.txt'
        f = open(filename, 'r')
        text = f.read()
        f.close()
        jsonROIdata = json.loads(text)
        if self.segFlag == '2D':
            self.allxpoints = jsonROIdata[1]
            self.allypoints = jsonROIdata[2]
            self.ui.imageSlider.setValue(jsonROIdata[3])
        else:
            self.allxpoints = jsonROIdata[1]
            self.allypoints = jsonROIdata[2]
            self.ui.imageSlider.setValue(jsonROIdata[3])
        
            self.allxpoints3 = jsonROIdata[4]
            self.allypoints3 = jsonROIdata[5]
            self.allxpoints4 = jsonROIdata[6]
            self.allypoints4 = jsonROIdata[7]
#        
            self.coordXPoint = jsonROIdata[8]
            self.coordYPoint = jsonROIdata[9]
        self.displayROI()

    def roipolyFunc(self):
        if (self.ui.polygon.isChecked()):
            
            self.ui.figure1.canvas.mpl_disconnect(self.clickFlag1)
            self.ui.figure2.canvas.mpl_disconnect(self.clickFlag2)
            self.ui.figure1.canvas.mpl_disconnect(self.scrolFlag1)
            self.ui.figure2.canvas.mpl_disconnect(self.scrolFlag2)
            
            self.previous_point = []
            self.allxpoints = []
            self.allypoints = []
            self.start_point = []
            self.end_point = []
            self.line = None
            self.roicolor = 'r'

            self.previous_point = []
            self.allxpoints = []
            self.allypoints = []
            self.start_point = []
            self.end_point = []
            self.line = None
            self.roicolor = 'r'

            self.previous_point3 = []
            self.allxpoints3 = []
            self.allypoints3 = []
            self.start_point3 = []
            self.end_point3 = []
            self.line3 = None
            self.roicolor3 = 'g'

            self.previous_point4 = []
            self.allxpoints4 = []
            self.allypoints4 = []
            self.start_point4 = []
            self.end_point4 = []
            self.line4 = None
            self.roicolor4 = 'b'
    #        self.fig = self.ui.figure1
    #        self.ax = self.ui.figure1.canvas.ax
            #self.fig.canvas.draw()
            
            self.__ID1 = self.ui.figure2.canvas.mpl_connect(
                'motion_notify_event', self.__motion_notify_callback)
            self.__ID2 = self.ui.figure2.canvas.mpl_connect(
                'button_press_event', self.__button_press_callback)
            self.__ID3 = self.ui.figure1.canvas.mpl_connect(
                'motion_notify_event', self.__motion_notify_callback)
            self.__ID4 = self.ui.figure1.canvas.mpl_connect(
                'button_press_event', self.__button_press_callback)
            self.__ID5 = self.ui.figure3.canvas.mpl_connect(
                'motion_notify_event', self.__motion_notify_callback)
            self.__ID6 = self.ui.figure3.canvas.mpl_connect(
                'button_press_event', self.__button_press_callback)
            self.__ID7 = self.ui.figure4.canvas.mpl_connect(
                'motion_notify_event', self.__motion_notify_callback)
            self.__ID8 = self.ui.figure4.canvas.mpl_connect(
                'button_press_event', self.__button_press_callback)
        else:
            self.scrolFlag1 = self.ui.figure1.canvas.mpl_connect('scroll_event', self.scrollT1CImage)
            self.scrolFlag2 = self.ui.figure2.canvas.mpl_connect('scroll_event', self.scrollT2WImage)
            self.clickFlag1 = self.ui.figure1.canvas.mpl_connect('button_press_event', self.onclickWidget1)
            self.clickFlag2 = self.ui.figure2.canvas.mpl_connect('button_press_event', self.onclickWidget2)
            
            self.clickFlag5 = self.ui.figure2.canvas.mpl_connect('motion_notify_event', self.onMotion2)
            self.clickFlag6 = self.ui.figure2.canvas.mpl_connect('button_release_event', self.onRelease2)
            
#            self.clickFlag5 = self.ui.figure2.canvas.mpl_connect('button_press_event', self.__scribble_button_press_callback)
#            self.clickFlag6 = self.ui.figure2.canvas.mpl_connect('motion_notify_event', self.__scribble_motion_notify_callback)
#            self.clickFlag7 = self.ui.figure2.canvas.mpl_connect('button_release_event', self.__scribble_button_release_callback)
        
#            self.ui.figure2.canvas.mpl_connect('motion_notify_event', self.on_move)
#            self.clickFlag2 = self.ui.figure2.canvas.mpl_connect('button_press_event', self.__scribble_button_press_callback)
#            self.ui.figure2.canvas.mpl_connect('motion_notify_event', self.__scribble_motion_notify_callback)
#            self.ui.figure2.canvas.mpl_connect('button_press_event', self.__scribble_button_release_callback)

            self.ui.figure2.canvas.mpl_disconnect(self.__ID1)
            self.ui.figure2.canvas.mpl_disconnect(self.__ID2)
            self.ui.figure1.canvas.mpl_disconnect(self.__ID3)
            self.ui.figure1.canvas.mpl_disconnect(self.__ID4)
            self.ui.figure3.canvas.mpl_disconnect(self.__ID5)
            self.ui.figure3.canvas.mpl_disconnect(self.__ID6)
            self.ui.figure4.canvas.mpl_disconnect(self.__ID7)
            self.ui.figure4.canvas.mpl_disconnect(self.__ID8)            

                   
    def getMask(self, currentImage):
        nx, ny = np.shape(currentImage)
        poly_verts = [(self.allxpoints[0], self.allypoints[0])]
        for i in range(len(self.allxpoints)-1, -1, -1):
            poly_verts.append((self.allxpoints[i], self.allypoints[i]))

        # Create vertex coordinates for each grid cell...
        # (<0,0> is at the top left of the grid in this system)
        x, y = np.meshgrid(np.arange(nx), np.arange(ny))
        x, y = x.flatten(), y.flatten()
        points = np.vstack((x,y)).T

        ROIpath = mplPath.Path(poly_verts)
        grid = ROIpath.contains_points(points).reshape((nx,ny))
        
        img = Image.new('L', (ny, nx), 0)
        ImageDraw.Draw(img).polygon(poly_verts, outline=1, fill=1)
        mask = np.array(img) > 0
        return mask

    def getMask3D(self, center, sqradius):
        grid = np.mgrid[map(slice,self.shape)].T - center
        grid = np.multiply(grid,[self.PSx,self.PSy,self.PSz])
        phi = sqradius - np.sqrt(np.sum(grid.T**2, 0))
        mask3D = np.float_(phi > 0)
        return mask3D
      
    def displayROI(self):
        if self.segFlag =='2D':
            l = plt.Line2D(self.allxpoints +
                         [self.allxpoints[0]],
                         self.allypoints +
                         [self.allypoints[0]],
                         color='r')
            self.imageSliderFunc()
            self.ui.figure2.canvas.ax.add_line(l)
            self.ui.figure2.canvas.draw()
        
        else:
            
            l = plt.Line2D(self.allxpoints +
                         [self.allxpoints[0]],
                         self.allypoints +
                         [self.allypoints[0]],
                         color='r')
            self.imageSliderFunc()
            self.ui.figure2.canvas.ax.add_line(l)
            self.ui.figure2.canvas.draw()
            
            self.ui.figure3.canvas.ax.clear()
            self.ui.figure3.canvas.ax.imshow(np.rot90((self.img_data2[:,round(self.coordXPoint),:]),1),cmap=plt.cm.gray)
            self.ui.figure3.canvas.ax.set_aspect('auto')
            self.ui.figure3.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure3.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure3.canvas.ax.set_title('Sagittal View', color = 'white')
    
            self.ui.figure3.canvas.draw()
            
            self.ui.figure4.canvas.ax.clear()
            self.ui.figure4.canvas.ax.imshow(np.rot90((self.img_data2[round(self.coordYPoint),:,:]),1),cmap=plt.cm.gray)
            self.ui.figure4.canvas.ax.set_aspect('auto')
            self.ui.figure4.canvas.ax.get_xaxis().set_visible(False)
            self.ui.figure4.canvas.ax.get_yaxis().set_visible(False)
            self.ui.figure4.canvas.ax.set_title('Coronal View', color = 'white')
            self.ui.figure4.canvas.draw()
            
            l = plt.Line2D(self.allxpoints3 +
                         [self.allxpoints3[0]],
                         self.allypoints3 +
                         [self.allypoints3[0]],
                         color='g')
            self.ui.figure3.canvas.ax.add_line(l)
            self.ui.figure3.canvas.draw()
    
            l = plt.Line2D(self.allxpoints4 +
                         [self.allxpoints4[0]],
                         self.allypoints4 +
                         [self.allypoints4[0]],
                         color='b')
            self.ui.figure4.canvas.ax.add_line(l)
            self.ui.figure4.canvas.draw()

    def displayMean(self,currentImage, **textkwargs):
        mask = self.getMask(currentImage)
        meanval = np.mean(np.extract(mask, currentImage))
        stdval = np.std(np.extract(mask, currentImage))
        string = "%.3f +- %.3f" % (meanval, stdval)
        plt.text(self.allxpoints[0], self.allypoints[0],
                 string, color=self.roicolor,
                 bbox=dict(facecolor='w', alpha=0.6), **textkwargs)

    def on_move(self,event):
        self.ui.figure2.canvas.ax.set_title(str(int(event.xdata))+','+str(int(event.ydata))+','+str(int(self.img2[np.round(event.ydata),np.round(event.xdata)])), color='green')
        self.ui.figure2.canvas.draw()


    def __motion_notify_callback(self, event):
        if event.inaxes:
            ax = event.inaxes
            figure = str(event.canvas)[1:8]
            x, y = event.xdata, event.ydata
            if figure == 'figure2':
                if (event.button == None or event.button == 1) and self.line != None: # Move line around
                    self.line.set_data([self.previous_point[0], x],
                                       [self.previous_point[1], y])
                    self.ui.figure1.canvas.draw()
                    self.ui.figure2.canvas.draw()
            elif figure == 'figure3':
                if (event.button == None or event.button == 1) and self.line3 != None: # Move line around
                    self.line3.set_data([self.previous_point3[0], x],
                                       [self.previous_point3[1], y])
                    self.ui.figure3.canvas.draw()
            elif figure == 'figure4':
                if (event.button == None or event.button == 1) and self.line4 != None: # Move line around
                    self.line4.set_data([self.previous_point4[0], x],
                                       [self.previous_point4[1], y])
                    self.ui.figure4.canvas.draw()

    def __button_press_callback(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes
            figure = str(event.canvas)[1:8]
            if figure == 'figure2':
                if event.button == 1 and event.dblclick == False:  # If you press the left button, single click
                    if self.line == None: # if there is no line, create a line
                        self.line = plt.Line2D([x, x],
                                               [y, y],
                                               marker='o',
                                               color=self.roicolor)
                        self.start_point = [x,y]
                        self.previous_point =  self.start_point
                        self.allxpoints=[x]
                        self.allypoints=[y]
                                                    
                        ax.add_line(self.line)
                        self.ui.figure1.canvas.draw()
                        self.ui.figure2.canvas.draw()
                        # add a segment
                    else: # if there is a line, create a segment
                        self.line = plt.Line2D([self.previous_point[0], x],
                                               [self.previous_point[1], y],
                                               marker = 'o',color=self.roicolor)
                        self.previous_point = [x,y]
                        self.allxpoints.append(x)
                        self.allypoints.append(y)
                                                                                    
                        event.inaxes.add_line(self.line)
                        self.ui.figure1.canvas.draw()
                elif ((event.button == 1 and event.dblclick==True) or
                      (event.button == 3 and event.dblclick==False)) and self.line != None: # close the loop and disconnect
                    self.ui.figure1.canvas.mpl_disconnect(self.__ID1) #joerg
                    self.ui.figure1.canvas.mpl_disconnect(self.__ID2) #joerg
                    self.ui.figure2.canvas.mpl_disconnect(self.__ID1) #joerg
                    self.ui.figure2.canvas.mpl_disconnect(self.__ID2) #joerg
                            
                    self.line.set_data([self.previous_point[0],
                                        self.start_point[0]],
                                       [self.previous_point[1],
                                        self.start_point[1]])
                    ax.add_line(self.line)
                    self.ui.figure2.canvas.draw()
                    self.ui.figure1.canvas.draw()
                    self.line = None
            elif figure == 'figure3':
                if event.button == 1 and event.dblclick == False:  # If you press the left button, single click
                    if self.line3 == None: # if there is no line, create a line
                        self.line3 = plt.Line2D([x, x],
                                               [y, y],
                                               marker='o',
                                               color=self.roicolor3)
                        self.start_point3 = [x,y]
                        self.previous_point3 =  self.start_point3
                        self.allxpoints3=[x]
                        self.allypoints3=[y]
                                                    
                        ax.add_line(self.line3)
                        self.ui.figure3.canvas.draw()
                        # add a segment
                    else: # if there is a line, create a segment
                        self.line3 = plt.Line2D([self.previous_point3[0], x],
                                               [self.previous_point3[1], y],
                                               marker = 'o',color=self.roicolor3)
                        self.previous_point3 = [x,y]
                        self.allxpoints3.append(x)
                        self.allypoints3.append(y)
                                                                                    
                        event.inaxes.add_line(self.line3)
                        self.ui.figure3.canvas.draw()
                elif ((event.button == 1 and event.dblclick==True) or
                      (event.button == 3 and event.dblclick==False)) and self.line3 != None: # close the loop and disconnect
                    self.ui.figure3.canvas.mpl_disconnect(self.__ID5) #joerg
                    self.ui.figure3.canvas.mpl_disconnect(self.__ID6) #joerg

                            
                    self.line3.set_data([self.previous_point3[0],
                                        self.start_point3[0]],
                                       [self.previous_point3[1],
                                        self.start_point3[1]])
                    ax.add_line(self.line3)
                    self.ui.figure3.canvas.draw()
                    self.line3 = None  
#                    self.allypoints3 = self.shape[2] - self.allypoints3

            elif figure == 'figure4':
                if event.button == 1 and event.dblclick == False:  # If you press the left button, single click
                    if self.line4 == None: # if there is no line, create a line
                        self.line4 = plt.Line2D([x, x],
                                               [y, y],
                                               marker='o',
                                               color=self.roicolor4)
                        self.start_point4 = [x,y]
                        self.previous_point4 =  self.start_point4
                        self.allxpoints4=[x]
                        self.allypoints4=[y]
                                                    
                        ax.add_line(self.line4)
                        self.ui.figure4.canvas.draw()
                        # add a segment
                    else: # if there is a line, create a segment
                        self.line4 = plt.Line2D([self.previous_point4[0], x],
                                               [self.previous_point4[1], y],
                                               marker = 'o',color=self.roicolor4)
                        self.previous_point4 = [x,y]
                        self.allxpoints4.append(x)
                        self.allypoints4.append(y)
                                                                                    
                        event.inaxes.add_line(self.line4)
                        self.ui.figure4.canvas.draw()
                elif ((event.button == 1 and event.dblclick==True) or
                      (event.button == 3 and event.dblclick==False)) and self.line4 != None: # close the loop and disconnect
                    self.ui.figure4.canvas.mpl_disconnect(self.__ID5) #joerg
                    self.ui.figure4.canvas.mpl_disconnect(self.__ID6) #joerg

                            
                    self.line4.set_data([self.previous_point4[0],
                                        self.start_point4[0]],
                                       [self.previous_point4[1],
                                        self.start_point4[1]])
                    ax.add_line(self.line4)
                    self.ui.figure4.canvas.draw()
                    self.line4 = None  
#                    self.allypoints4 = self.shape[2] - self.allypoints4
#                if sys.flags.interactive:
#                    pass
#                else:
#                    #figure has to be closed so that code can continue
#                    plt.close(self.fig) 
        
            
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
    
    
#app = QApplication(sys.argv)
#MainWindow = QtGui.QMainWindow()
#ui = Ui_MainWindow()
#ui.setupUi(MainWindow)
#
#MainWindow.show()
#sys.exit(app.exec_())
    
    