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
#import scikits.learn.mixture as gmm
import sklearn.mixture as gmm
from scipy.ndimage import gaussian_filter

def AtlasBasedSegmentation(img1data, img2data, sliceZ, mask, mask3D, pmapWMSlice, pmapGMSlice, pmapCSFSlice, rect3D):

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
    
    img1Slice = img1data[:,:,sliceZ]
    img2Slice = img2data[:,:,sliceZ]
    
    minV1 = np.min(img1Slice)
    maxV1 = np.max(img1Slice)
#    minV1 = np.min(img1data)
#    maxV1 = np.max(img1data)
    normImg1 = (img1Slice-minV1)*(1/np.float(maxV1-minV1))  
    minV2 = np.min(img2Slice)
    maxV2 = np.max(img2Slice)
#    minV2 = np.min(img2data)
#    maxV2 = np.max(img2data)
    normImg2 = (img2Slice-minV2)*(1/np.float(maxV2-minV2))    
    
    img1data = np.multiply(img1data,mask3D)
    img2data = np.multiply(img2data,mask3D)

    img1data = (img1data-minV1)*(1/np.float(maxV1-minV1))  
#    minV = np.min(img2data)
#    maxV = np.max(img2data)
    img2data = (img2data-minV2)*(1/np.float(maxV2-minV2))  
    
    (row,col,dep) = img1data.shape

    invMask = np.invert(mask)

    img1WM = np.multiply(np.multiply(normImg1,pmapWMSlice), invMask)
    img2WM = np.multiply(np.multiply(normImg2,pmapWMSlice), invMask)    
    
    img1GM = np.multiply(np.multiply(normImg1,pmapGMSlice), invMask)
    img2GM = np.multiply(np.multiply(normImg2,pmapGMSlice), invMask)

    img1CSF = np.multiply(np.multiply(normImg1,pmapCSFSlice), invMask)
    img2CSF = np.multiply(np.multiply(normImg2,pmapCSFSlice), invMask)

 
 
    (indX1,indY1) = np.where(np.multiply(invMask,pmapWMSlice)>0.5)
    (indX2,indY2) = np.where(np.multiply(invMask,pmapGMSlice)>0.5)
    (indXcsf,indYcsf) = np.where(np.multiply(invMask,pmapCSFSlice)>0.5)
    
    
    (indX3,indY3) = np.where(mask>0)
    maskedDataImg1 = normImg1[indX3,indY3]
    maskedDataImg2 = normImg2[indX3,indY3]
    
    maskedData = np.vstack((maskedDataImg1,maskedDataImg2))
    
    
    minX = rect3D[0][0]
    maxX = rect3D[1][0]
    minY = rect3D[0][1]
    maxY = rect3D[1][1]
    minZ = rect3D[0][2]
    maxZ = rect3D[1][2]
    
    dx = maxX-minX
    dy = maxY-minY
    dz = maxZ-minZ
    
    #3D mask data
    maskedDataImg1_3D = img1data[minY:maxY,minX:maxX,minZ:maxZ].reshape(1,dx*dy*dz)    
    maskedDataImg2_3D = img2data[minY:maxY,minX:maxX,minZ:maxZ].reshape(1,dx*dy*dz) 
    maskedData3D = np.vstack((maskedDataImg1_3D,maskedDataImg2_3D))
    
    
    mImg1WM = np.mean(img1WM[indX1,indY1])
    mImg2WM = np.mean(img2WM[indX1,indY1])
    mImg1GM = np.mean(img1GM[indX2,indY2])
    mImg2GM = np.mean(img2GM[indX2,indY2])
    mImg1CSF = np.mean(img1CSF[indXcsf,indYcsf])
    mImg2CSF = np.mean(img2CSF[indXcsf,indYcsf]) + 0.2
    mMaskData1 = np.mean(maskedDataImg1)
    mMaskData2 = np.mean(maskedDataImg2)
    WMdata = np.vstack((img1WM[indX1,indY1],img2WM[indX1,indY1]))
    
    dataWM = np.vstack((img1WM[indX1,indY1],img2WM[indX1,indY1]))    
    dataGM = np.vstack((img1GM[indX1,indY1],img2GM[indX1,indY1])) 
    dataCSF = np.vstack((img1CSF[indXcsf,indYcsf],img2CSF[indXcsf,indYcsf]))
    
    covWM = np.cov(dataWM)
    covGM = np.cov(dataGM)
    covCSF = np.cov(dataCSF)
    covMaskData = np.cov(maskedData)
    
#    plt.imshow(np.multiply(img2WM,pmapWMSlice), cmap = 'gray')
#    plt.show()

#+======================================
# This EM removes the unsupressed CSF in WM
    f = gmm.GMM(n_components=2, covariance_type = 'full', n_iter = 10, thresh = 0.01)
    f.means = np.array([[mImg1WM,mImg2WM],[mImg1CSF,mImg2CSF]])
    f.covars = np.array([covWM,covCSF])
    f.weights = np.array([1/2.0,1/2.0])
    f.fit(WMdata.T)
    probMaskWM = f.predict_proba(WMdata.T)
    
    maskWM1 = np.zeros((row,col))
    maskWM2 = np.zeros((row,col))
    maskWM1[indX1,indY1] = probMaskWM[:,0]
    maskWM2[indX1,indY1] = probMaskWM[:,1]

    (ixCSF1,iyCSF1) = np.where(maskWM1 > 0.8)
    (ixCSF2,iyCSF2) = np.where(maskWM2 > 0.8)

    
#    maskWM = np.zeros((row,col))
    
    if np.mean(normImg2[ixCSF1,iyCSF1])<np.mean(normImg2[ixCSF2,iyCSF2]):
        mImg1WM = np.mean(img1WM[ixCSF1,iyCSF1])
        mImg2WM = np.mean(img2WM[ixCSF1,iyCSF1])
        dataWM = np.vstack((img1WM[ixCSF1,iyCSF1],img2WM[ixCSF1,iyCSF1]))
        covWM = np.cov(dataWM)
#        plt.imshow(np.multiply(maskWM1,img2WM), cmap = 'gray')
#        plt.show()
    else:
        mImg1WM = np.mean(img1WM[ixCSF2,iyCSF2])
        mImg2WM = np.mean(img2WM[ixCSF2,iyCSF2])
        dataWM = np.vstack((img1WM[ixCSF2,iyCSF2],img2WM[ixCSF2,iyCSF2]))
        covWM = np.cov(dataWM)
#        plt.imshow(np.multiply(maskWM2,img2WM), cmap = 'gray')
#        plt.show()
##    
#========================================
    

#    g = gmm.GMM(n_states=3, cvtype = 'full')
#    g.means = np.array([[mImg1WM,mImg2WM],[mImg1GM,mImg2GM],[mMaskData1,mMaskData2]])
#    g.covars = np.array([covWM,covGM,covMaskData])
#    g.weights = np.array([1/4.0,1/4.0,1/2.0])
#    g.fit(maskedData.T, n_iter = 10, thresh = 0.01)
#    probMask = g.predict_proba(maskedData.T)

    g = gmm.GMM(n_components=2, n_iter = 1, covariance_type = 'full', thresh = 0.01)
    g.means = np.array([[mImg1WM,mImg2WM],[mMaskData1,mMaskData2]])
    g.covars = np.array([covWM,covMaskData])
    g.weights = np.array([1/3.0,2/3.0])
    g.fit(maskedData.T)
    probMask = g.predict_proba(maskedData3D.T)
    
    probMask1 = probMask[:,0].reshape(dy,dx,dz)
    mask1Img = np.zeros((row,col,dep))
    mask1Img[minY:maxY,minX:maxX,minZ:maxZ] = probMask1
    
    probMask2 = probMask[:,1].reshape(dy,dx,dz)
    mask2Img = np.zeros((row,col,dep))
    mask2Img[minY:maxY,minX:maxX,minZ:maxZ] = probMask2
    
    mProb1data = np.multiply(mask[minY:maxY,minX:maxX],np.multiply(probMask1[:,:,sliceZ-minZ],img2data[minY:maxY,minX:maxX,sliceZ]))
    mProb2data = np.multiply(mask[minY:maxY,minX:maxX],np.multiply(probMask2[:,:,sliceZ-minZ],img2data[minY:maxY,minX:maxX,sliceZ]))
    
    [indX1,indY1] = np.where(mask[minY:maxY,minX:maxX]>0)    
    
    mPb1 = np.mean(mProb1data[indX1,indY1])    
    mPb2 = np.mean(mProb2data[indX1,indY1])
    
    nTMask = np.zeros((row,col,dep))
    abTMask = np.zeros((row,col,dep))
    
    if mPb2>mPb1:
        nTMask = mask1Img
        abTMask = mask2Img
        
    else:
        nTMask = mask2Img
        abTMask = mask1Img
    
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

    
  
