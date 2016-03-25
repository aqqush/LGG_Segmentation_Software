# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 12:49:44 2015

@author: m131199
"""

import nibabel as nib
import numpy as np
import os
import matplotlib.pylab as plt
#from scikits.learn.mixture import GMM
import scikits.learn.mixture as gmm
from scipy.ndimage import gaussian_filter

def AtlasBasedSegmentation(img1Slice, img2Slice, mask, pmapWMSlice, pmapGMSlice):

#    os.chdir('/Users/m131199/Documents/testData/testAtlasReg/')
#    #
#    path = '/Users/m131199/Documents/testData/testAtlasReg/'
#    image1 = '/Users/m131199/Documents/testData/testAtlasReg/LGG_144_T2.nii'
#    image2 = '/Users/m131199/Documents/testData/testAtlasReg/registeredT1C_144.nii'
#    
#    pmapWMpath = '/Users/m131199/Documents/testData/testAtlasReg/SyN/deformed_pbmap_WM.nii'
#    pmapWM = nib.load(pmapWMpath)
#    pmapWM_data = pmapWM.get_data()
#    
#    pmapGMpath = '/Users/m131199/Documents/testData/testAtlasReg/SyN/deformed_pbmap_GM.nii'
#    pmapGM = nib.load(pmapGMpath)
#    pmapGM_data = pmapGM.get_data()
#    
#    img1 = nib.load(image1)
#    img2 = nib.load(image2)
#    
#    img1_data = img1.get_data()
#    img2_data = img2.get_data()
    
#    z = 25
    
    minV = np.min(img1Slice)
    maxV = np.max(img1Slice)
    normImg1 = (img1Slice-minV)*(1/np.float(maxV-minV))  
    minV = np.min(img2Slice)
    maxV = np.max(img2Slice)
    normImg2 = (img2Slice-minV)*(1/np.float(maxV-minV))    
    
    (row,col) = img1Slice.shape

    invMask = np.invert(mask)
    
    
    (indX1,indY1) = np.where(np.multiply(invMask,pmapWMSlice)>0.5)
    (indX2,indY2) = np.where(np.multiply(invMask,pmapGMSlice)>0.5)
    
    img1WM = np.multiply(np.multiply(normImg1,pmapWMSlice), invMask)
    img2WM = np.multiply(np.multiply(normImg2,pmapWMSlice), invMask)
    
    img1GM = np.multiply(np.multiply(normImg1,pmapGMSlice), invMask)
    img2GM = np.multiply(np.multiply(normImg2,pmapGMSlice), invMask)
 
    
    (indX3,indY3) = np.where(mask>0)
    maskedDataImg1 = normImg1[indX3,indY3]
    maskedDataImg2 = normImg2[indX3,indY3]
    maskedData = np.vstack((maskedDataImg1,maskedDataImg2))
    
    mImg1WM = np.mean(img1WM[indX1,indY1])
    mImg2WM = np.mean(img2WM[indX1,indY1])
    mImg1GM = np.mean(img1GM[indX2,indY2])
    mImg2GM = np.mean(img2GM[indX2,indY2])
    mMaskData1 = np.mean(maskedDataImg1)
    mMaskData2 = np.mean(maskedDataImg2)
    
    
    dataWM = np.vstack((img1WM[indX1,indY1],img2WM[indX1,indY1]))    
    dataGM = np.vstack((img1GM[indX1,indY1],img2GM[indX1,indY1])) 
    covWM = np.cov(dataWM)
    covGM = np.cov(dataGM)
    covMaskData = np.cov(maskedData)
    
#    g = gmm.GMM(n_states=3, cvtype = 'full')
#    g.means = np.array([[mImg1WM,mImg2WM],[mImg1GM,mImg2GM],[mMaskData1,mMaskData2]])
#    g.covars = np.array([covWM,covGM,covMaskData])
#    g.weights = np.array([1/4.0,1/4.0,1/2.0])
#    g.fit(maskedData.T, n_iter = 10, thresh = 0.01)
#    probMask = g.predict_proba(maskedData.T)

    g = gmm.GMM(n_states=2, cvtype = 'full')
    g.means = np.array([[mImg1WM,mImg2WM],[mMaskData1,mMaskData2]])
    g.covars = np.array([covWM,covMaskData])
    g.weights = np.array([1/3.0,2/3.0])
    g.fit(maskedData.T, n_iter = 10, thresh = 0.01)
    probMask = g.predict_proba(maskedData.T)
    
    mask1 = np.zeros((row,col))
    mask1[indX3,indY3] = probMask[:,0]
    mask2 = np.zeros((row,col))
    mask2[indX3,indY3] = probMask[:,1]   
    mask3 = np.zeros((row,col))
#    mask3[indX3,indY3] = probMask[:,2]
    
    probImage = np.zeros((row,col,3))  
    probImage[:,:,0] = mask1
    probImage[:,:,1] = mask2
    probImage[:,:,2] = mask3
    
 #    rgbImg = Image.fromarray(probImage)
    plt.imshow(probImage)
    plt.show()    
    
    
    (indX4,indY4) = np.where(mask1 > 0.8)
    (indX5,indY5) = np.where(mask2 > 0.8)
    class1 = probMask[:,0]
    class2 = probMask[:,1]
    cidx1 = np.where(class1>0.9)
    cidx2 = np.where(class1<0.9)
    cidx3 = np.where(class2>0.9)
    cidx4 = np.where(class2<0.9)
    
    nTMask = np.zeros((row,col))
    abTMask = np.zeros((row,col))
    
    if np.mean(normImg2[indX4,indY4])<np.mean(normImg2[indX5,indY5]):
        class1[cidx1] = 1
        class1[cidx2] = 0
        nTMask[indX3,indY3] = class1
        abTMask[indX3,indY3] = probMask[:,1]
        
    else:
        class2[cidx3] = 1
        class2[cidx4] = 0
        nTMask[indX3,indY3] = class2 
        abTMask[indX3,indY3] = probMask[:,0]
    
#    plt.imshow(nTMask, cmap = 'gray')
#    plt.show()        
    
#    nTMask = gaussian_filter(nTMask,3,0)
    
    
        
    

       
#    fig, ax = plt.subplots()    
#    ax.imshow(mask1, cmap = 'gray')
#    numrows, numcols = mask1.shape  
#     
#    def format_coord(x, y):
#        col = int(x+0.5)
#        row = int(y+0.5)
#        if col>=0 and col<numcols and row>=0 and row<numrows:
#            z = mask1[row,col]
#            return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
#        else:
#            return 'x=%1.4f, y=%1.4f'%(x, y)
#    ax.format_coord = format_coord
#    plt.show()
#     
#    fig, ax = plt.subplots()       
#    ax.imshow(mask2, cmap = 'gray')
#    def format_coord(x, y):
#        col = int(x+0.5)
#        row = int(y+0.5)
#        if col>=0 and col<numcols and row>=0 and row<numrows:
#            z = mask2[row,col]
#            return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
#        else:
#            return 'x=%1.4f, y=%1.4f'%(x, y)
#    ax.format_coord = format_coord    
#    plt.show()
     
    return nTMask,abTMask
#==============================================================================
#      fig, ax = plt.subplots()    
#      ax.imshow(mask3, cmap = 'gray')
#      def format_coord(x, y):
#          col = int(x+0.5)
#          row = int(y+0.5)
#          if col>=0 and col<numcols and row>=0 and row<numrows:
#              z = mask3[row,col]
#              return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
#          else:
#              return 'x=%1.4f, y=%1.4f'%(x, y)
#      ax.format_coord = format_coord
#      plt.show()
#      
#      fig1 = plt.figure()
#      ax = fig1.add_subplot(1, 1, 1)
#      color = np.array([[1,0,0],[0,0,1]])
#      plt.scatter(img1WM[indX1,indY1],img2WM[indX1,indY1], c = color, alpha=0.5)
#      ax.set_xlabel('T1C_WM')
#      ax.set_ylabel('T2_WM')
#      ax.legend()
#      ax.draw
#      plt.show()
#      
#      fig2 = plt.figure()
#      plt.imshow(img1WM, cmap = 'gray')
#      plt.show()
#      
#      fig3 = plt.figure()
#      ax = fig3.add_subplot(1, 1, 1)
#      color = np.array([[1,0,0],[0,0,1]])
#      plt.scatter(img1GM[indX2,indY2],img2GM[indX2,indY2], c = color, alpha=0.5)
#      ax.set_xlabel('T1C_GM')
#==============================================================================
#==============================================================================
#      ax.set_ylabel('T2_GM')
#      ax.legend()
#==============================================================================
    
    
#==============================================================================
#      ax.draw
#      plt.show()
#      
#      fig4 = plt.figure()
#      plt.imshow(img1GM, cmap = 'gray')
#      plt.show()
#==============================================================================

    
  
