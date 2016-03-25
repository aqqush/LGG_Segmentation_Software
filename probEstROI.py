# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 13:47:52 2015

@author: m131199
"""

from sklearn.cluster import KMeans
import nibabel as nib
import numpy as np
import os
import matplotlib.pylab as plt
#from scikits.learn.mixture import GMM
#import scikits.learn.mixture as gmm
import sklearn.mixture as gmm
from scipy.ndimage import gaussian_filter

def AtlasBasedSegmentation(img1Slice, img2Slice, mask, pmapWMSlice, pmapGMSlice, pmapCSFSlice, useT1, useT2):

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

    img1WM = np.multiply(np.multiply(normImg1,pmapWMSlice), invMask)
    img2WM = np.multiply(np.multiply(normImg2,pmapWMSlice), invMask)    
    
    img1GM = np.multiply(np.multiply(normImg1,pmapGMSlice), invMask)
    img2GM = np.multiply(np.multiply(normImg2,pmapGMSlice), invMask)

    img1CSF = np.multiply(np.multiply(normImg1,pmapCSFSlice), invMask)
    img2CSF = np.multiply(np.multiply(normImg2,pmapCSFSlice), invMask)


#    plt.imshow(img2WM, cmap = 'gray')
#    plt.show()
#    plt.imshow(img2GM, cmap = 'gray')
#    plt.show()    
#====================================================
#    (indX11,indY11) = np.where(img2WM>0.5)
#    pmapWMSlice[indX11,indY11] = 0  
#    
#    (indX22,indY22) = np.where(img2GM>0.5)
#    pmapGMSlice[indX22,indY22] = 0       
#
#    img1WM = np.multiply(np.multiply(normImg1,pmapWMSlice), invMask)
#    img2WM = np.multiply(np.multiply(normImg2,pmapWMSlice), invMask)    
#    
#    img1GM = np.multiply(np.multiply(normImg1,pmapGMSlice), invMask)
#    img2GM = np.multiply(np.multiply(normImg2,pmapGMSlice), invMask)    
#====================================================
 
    (indX1,indY1) = np.where(np.multiply(invMask,pmapWMSlice)>0.5)
    (indX2,indY2) = np.where(np.multiply(invMask,pmapGMSlice)>0.5)
    (indXcsf,indYcsf) = np.where(np.multiply(invMask,pmapCSFSlice)>0.5)
    
    
    (indX3,indY3) = np.where(mask>0)
    maskedDataImg1 = normImg1[indX3,indY3]
    maskedDataImg2 = normImg2[indX3,indY3]
    
    maskedData = np.vstack((maskedDataImg1,maskedDataImg2))
    
    mImg1WM = np.mean(img1WM[indX1,indY1])
    mImg2WM = np.mean(img2WM[indX1,indY1])
    mImg1GM = np.mean(img1GM[indX2,indY2])
    mImg2GM = np.mean(img2GM[indX2,indY2])
    mImg1CSF = np.mean(img1CSF[indXcsf,indYcsf])
    mImg2CSF = np.mean(img2CSF[indXcsf,indYcsf]) + 0.2
    mMaskData1 = np.mean(maskedDataImg1)
    mMaskData2 = np.mean(maskedDataImg2)
    
#    mImg2WM = (mImg2WM + mImg2GM)/2
#    mImg1WM = (mImg1WM + mImg1GM)/2    
    
#    WMdata = np.vstack((img1WM[indX1,indY1],img2WM[indX1,indY1]))
    
    if (useT1 and useT2):
#        WMdata = np.vstack((img1WM[indX1,indY1],img2WM[indX1,indY1]))
        dataWM = np.vstack((img1WM[indX1,indY1],img2WM[indX1,indY1]))    
        dataGM = np.vstack((img1GM[indX2,indY2],img2GM[indX2,indY2])) 
        dataCSF = np.vstack((img1CSF[indXcsf,indYcsf],img2CSF[indXcsf,indYcsf]))
        
        covWM = np.cov(dataWM)
        covGM = np.cov(dataGM)
        covCSF = np.cov(dataCSF)
        covMaskData = np.cov(maskedData)
        #combine GM and WM        
#        dataWMGM = np.hstack((dataWM,dataGM))
#        covWM = np.cov(dataWMGM)
    else:
#        WMdata = np.vstack(img2WM[indX1,indY1])
        dataWM = np.vstack(img2WM[indX1,indY1])    
        dataGM = np.vstack(img2GM[indX2,indY2]) 
        dataCSF = np.vstack(img2CSF[indXcsf,indYcsf])
        
        covWM = np.cov(dataWM.T)
        covGM = np.cov(dataGM.T)

        #combine GM and WM
#        dataWMGM = np.hstack((dataWM,dataGM))
#        covWM = np.cov(dataWMGM)
        
        covCSF = np.cov(dataCSF.T)
        maskedData = np.vstack(maskedDataImg2)
        covMaskData = np.cov(maskedData.T)
    
#    plt.imshow(np.multiply(img2WM,pmapWMSlice), cmap = 'gray')
#    plt.show()
#    plt.imshow(np.multiply(img2GM,pmapGMSlice), cmap = 'gray')
#    plt.show()

#+======================================
# This EM removes the unsupressed CSF in WM
    if (useT1 and useT2):
        f = gmm.GMM(n_components=2, n_iter = 10, covariance_type = 'full')
        f.means = np.array([[mImg1WM,mImg2WM],[mImg1CSF,mImg2CSF]])
        f.covars = np.array([covWM,covCSF])
        f.weights = np.array([1/2.0,1/2.0])
        f.fit(dataWM.T)
        probMaskWM = f.predict_proba(dataWM.T)      
        
        maskWM1 = np.zeros((row,col))
        maskWM2 = np.zeros((row,col))
        maskWM = np.zeros((row,col))
        maskWM1[indX1,indY1] = probMaskWM[:,0]
        maskWM2[indX1,indY1] = probMaskWM[:,1]
    
        (ixCSF1,iyCSF1) = np.where(maskWM1 > 0.8)
        (ixCSF2,iyCSF2) = np.where(maskWM2 > 0.8)

        maskCSF1 = np.zeros((row,col))
        maskCSF2 = np.zeros((row,col))
        
        if np.mean(normImg2[ixCSF1,iyCSF1])<np.mean(normImg2[ixCSF2,iyCSF2]):
            mImg1WM = np.mean(img1WM[ixCSF1,iyCSF1])
            mImg2WM = np.mean(img2WM[ixCSF1,iyCSF1])
            dataWM = np.vstack((img1WM[ixCSF1,iyCSF1],img2WM[ixCSF1,iyCSF1]))
            covWM = np.cov(dataWM)
            maskCSF = maskWM2
            maskWM = maskWM1
#            plt.imshow(np.multiply(maskWM1,img2WM), cmap = 'gray')
#            plt.show()
        else:
            mImg1WM = np.mean(img1WM[ixCSF2,iyCSF2])
            mImg2WM = np.mean(img2WM[ixCSF2,iyCSF2])
            dataWM = np.vstack((img1WM[ixCSF2,iyCSF2],img2WM[ixCSF2,iyCSF2]))
            covWM = np.cov(dataWM)
            maskCSF = maskWM1
            maskWM=maskWM2
#            plt.imshow(np.multiply(maskWM2,img2WM), cmap = 'gray')
#            plt.show()            
            
        # for CSF mask
        f.fit(dataCSF.T)
        probMaskCSF = f.predict_proba(dataCSF.T)  

        maskCSF1[indXcsf,indYcsf] = probMaskCSF[:,0]
        maskCSF2[indXcsf,indYcsf] = probMaskCSF[:,1]
 
        (ixCSF1,iyCSF1) = np.where(maskCSF1 > 0.8)
        (ixCSF2,iyCSF2) = np.where(maskCSF2 > 0.8)
        
        if np.mean(normImg2[ixCSF1,iyCSF1])<np.mean(normImg2[ixCSF2,iyCSF2]):
            dataCSF = np.vstack((img1CSF[ixCSF2,iyCSF2],img2CSF[ixCSF2,iyCSF2]))
            maskCSF=maskCSF2+maskCSF
#            plt.imshow(np.multiply(maskCSF,normImg2), cmap = 'gray')
#            plt.show()
        else:
            dataCSF = np.vstack((img1CSF[ixCSF1,iyCSF1],img2CSF[ixCSF1,iyCSF1]))
            maskCSF=maskCSF1+maskCSF
#            plt.imshow(np.multiply(maskCSF,normImg2), cmap = 'gray')
#            plt.show()

        # This is for GM to remove CSF
        f2 = gmm.GMM(n_components=2, n_iter = 10, covariance_type = 'full')
        f2.means = np.array([[mImg1GM,mImg2GM],[mImg1CSF,mImg2CSF]])
        f2.covars = np.array([covGM,covCSF])
        f2.weights = np.array([1/2.0,1/2.0])
        f2.fit(dataGM.T)
        probMaskGM = f2.predict_proba(dataGM.T)
        
        maskGM1 = np.zeros((row,col))
        maskGM2 = np.zeros((row,col))
        maskGM = np.zeros((row,col))
        maskGM1[indX2,indY2] = probMaskGM[:,0]
        maskGM2[indX2,indY2] = probMaskGM[:,1]
    
        (ixCSF3,iyCSF3) = np.where(maskGM1 > 0.8)
        (ixCSF4,iyCSF4) = np.where(maskGM2 > 0.8)
        
#        maskGM3 = np.zeros((row,col))
#        maskGM3[ixCSF4,iyCSF4] = 1
#        plt.imshow(np.multiply(img2GM,maskGM3), cmap = 'gray') 
#        plt.show()
        
        if np.mean(normImg2[ixCSF3,iyCSF3])<np.mean(normImg2[ixCSF4,iyCSF4]):
            mImg1GM = np.mean(img1GM[ixCSF3,iyCSF3])
            mImg2GM = np.mean(img2GM[ixCSF3,iyCSF3])
            dataGM = np.vstack((img1GM[ixCSF3,iyCSF3],img2GM[ixCSF3,iyCSF3]))
            covGM = np.cov(dataGM)
            maskGM = maskGM1
#            plt.imshow(np.multiply(maskGM1,img2GM), cmap = 'gray')
#            plt.show()
        else:
            mImg1GM = np.mean(img1GM[ixCSF4,iyCSF4])
            mImg2GM = np.mean(img2GM[ixCSF4,iyCSF4])
            dataGM = np.vstack((img1GM[ixCSF4,iyCSF4],img2GM[ixCSF4,iyCSF4]))
            covGM = np.cov(dataGM)
            maskGM=maskGM2
#            plt.imshow(np.multiply(maskGM2,img2GM), cmap = 'gray')
#            plt.show()
        

    else:
        f = gmm.GMM(n_components=2, n_iter = 10, covariance_type = 'diag')
        f.means = np.array([[mImg2WM],[mImg2CSF]])
        f.covars = np.array([[covWM],[covCSF]])
        f.weights = np.array([1/2.0,1/2.0])
        f.fit(dataWM)
        probMaskWM = f.predict_proba(dataWM)       
    
        maskWM1 = np.zeros((row,col))
        maskWM2 = np.zeros((row,col))
        maskWMF = np.zeros((row,col))
        maskWM1[indX1,indY1] = probMaskWM[:,0]
        maskWM2[indX1,indY1] = probMaskWM[:,1]
    
        (ixCSF1,iyCSF1) = np.where(maskWM1 > 0.8)
        (ixCSF2,iyCSF2) = np.where(maskWM2 > 0.8)

    
    #    maskWM = np.zeros((row,col))
        
        if np.mean(normImg2[ixCSF1,iyCSF1])<np.mean(normImg2[ixCSF2,iyCSF2]):
            mImg1WM = np.mean(img1WM[ixCSF1,iyCSF1])
            mImg2WM = np.mean(img2WM[ixCSF1,iyCSF1])
            dataWM = np.vstack(img2WM[ixCSF1,iyCSF1])
            covWM = np.cov(dataWM.T)
            maskWMF=maskWM1
#            plt.imshow(np.multiply(maskWM1,img2WM), cmap = 'gray')
#            plt.show()
        else:
            mImg1WM = np.mean(img1WM[ixCSF2,iyCSF2])
            mImg2WM = np.mean(img2WM[ixCSF2,iyCSF2])
            dataWM = np.vstack(img2WM[ixCSF2,iyCSF2])
            covWM = np.cov(dataWM.T)
            maskWMF=maskWM2
#            plt.imshow(np.multiply(maskWM2,img2WM), cmap = 'gray')
#            plt.show()
##    
#========================================
    if (useT1 and useT2):
        mImg1WMGM = (mImg1WM + mImg1GM)/2
        mImg2WMGM = (mImg2WM + mImg2GM)/2
        covVMGM = np.cov(np.hstack((dataWM,dataGM)))
    else:
        mImg1WMGM = (mImg1WM + mImg1GM)/2
        mImg2WMGM = (mImg2WM + mImg2GM)/2
        covVMGM = np.cov(np.vstack((dataWM,dataGM)))
#    g = gmm.GMM(n_states=3, covariance_type = 'full')
#    g.means = np.array([[mImg1WM,mImg2WM],[mImg1GM,mImg2GM],[mMaskData1,mMaskData2]])
#    g.covars = np.array([covWM,covGM,covMaskData])
#    g.weights = np.array([1/4.0,1/4.0,1/2.0])
#    g.fit(maskedData.T, n_iter = 10, thresh = 0.01)
#    probMask = g.predict_proba(maskedData.T)
    if (useT1 and useT2):
        g = gmm.GMM(n_components=2, n_iter = 0, covariance_type = 'full')
        g.means = np.array([[mImg1WM,mImg2WM],[mMaskData1,mMaskData2]])
        g.covars = np.array([covWM,covMaskData])
        g.weights = np.array([1/3.0,2/3.0])
        g.fit(maskedData.T)
        probMask = g.predict_proba(maskedData.T)
### K-means clustering       
#        t = KMeans(n_clusters = 2)
#        t.fit(maskedData.T)
#        labels = t.labels_
    else:
        g = gmm.GMM(n_components=2, n_iter = 0, covariance_type = 'diag')
        g.means = np.array([[mImg2WM],[mMaskData2]])
        g.covars = np.array([[covWM],[covMaskData]])
        g.weights = np.array([1/3.0,2/3.0])
        g.fit(maskedData)
        probMask = g.predict_proba(maskedData)
    
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
#    plt.imshow(probImage)
#    plt.show()    
#    
    
    (indX4,indY4) = np.where(mask1 > 0.8)
    (indX5,indY5) = np.where(mask2 > 0.8)
#    class1 = probMask[:,0]
#    class2 = probMask[:,1]
#    cidx1 = np.where(class1>0.9)
#    cidx2 = np.where(class1<0.9)
#    cidx3 = np.where(class2>0.9)
#    cidx4 = np.where(class2<0.9)
    
    nTMask = np.zeros((row,col))
    abTMask = np.zeros((row,col))
    
    if np.mean(normImg2[indX4,indY4])<np.mean(normImg2[indX5,indY5]):
#        class1[cidx1] = 1
#        class1[cidx2] = 0
#        nTMask[indX3,indY3] = class1
#        abTMask[indX3,indY3] = probMask[:,1]
        nTMask[indX3,indY3] = probMask[:,0]
        abTMask[indX3,indY3] = probMask[:,1]
        
    else:
#        class2[cidx3] = 1
#        class2[cidx4] = 0
#        nTMask[indX3,indY3] = class2 
#        abTMask[indX3,indY3] = probMask[:,0]
        nTMask[indX3,indY3] = probMask[:,1]
        abTMask[indX3,indY3] = probMask[:,0]



#    abTMask[indX3,indY3] = labels
#        
#    plt.imshow(abTMask, cmap = 'gray')
#    plt.show()        
    
#    nTMask = gaussian_filter(nTMask,3,0)
    
    
        
    

#       
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
#     
    return nTMask,abTMask,maskWM,maskGM,maskCSF
#    return abTMask,nTMask
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

    
  
