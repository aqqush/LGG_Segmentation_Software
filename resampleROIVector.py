# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 09:55:27 2015

@author: m131199
"""

from scipy import interpolate
import matplotlib.pylab as plt
import numpy as np
import os
import nibabel as nib
import GUI_Starter
from scipy.ndimage import gaussian_gradient_magnitude
        
def ROIstats(img1, img2, img, mask, polyXpoints, polyYpoints):        
#    os.chdir('/Users/m131199/Documents/testData/testLGGdata/')
#    imgVol = nib.load('registered113.nii')
#    imgVol_data = imgVol.get_data()
#    img = imgVol_data[:,:,11]
#    (r,c) = img.shape     
#    img  = ndimage.rotate(img, -90, reshape=False)
    (r,c) = img.shape
    
    x = np.arange(0,r)
    y = np.arange(0,c)
    xx, yy = np.meshgrid(x, y)
    f1 = interpolate.interp2d(x, y, img, kind='cubic')
    f2 = interpolate.interp2d(x, y, mask.astype(int), kind='linear')
    f3 = interpolate.interp2d(x, y, img1, kind='cubic')
    f4 = interpolate.interp2d(x, y, img2, kind='cubic')
    minX = min(polyXpoints)
    maxX = max(polyXpoints)
    minY = min(polyYpoints)
    maxY = max(polyYpoints)
    
    centerX = round((minX+maxX)/2)
    centerY = round((minY+maxY)/2)

#    centerX = 95
#    centerY = 110
    d = np.round(np.sqrt((maxX-minX)**2 + (maxY-minY)**2)/2) 
#    d = 50 
    theta = 36
    xray = np.arange(centerX, centerX+d)
#    yray = centerY+(xray-centerX)*np.float(np.tan(np.pi/3))
    
#    (indX,indY) = np.where(mask==True)
#    maskImg1Val = img1[indX,indY]
#    maskImg2Val = img2[indX,indY]
#    fig = plt.gcf()
#    fig.clf()
#    ax1 = fig.add_subplot(1,1,1)
#    plt.scatter(maskImg1Val,maskImg2Val,alpha = 0.5)
#    ax1.set_ylabel('T2 Image')
#    ax1.set_xlabel('T1C Image')
#    ax1.set_title('Joint Instensity Histogram for Tumor ROI')
#    plt.show()
#    
#    fig = plt.gcf()
#    fig.clf()
#    ax1 = fig.add_subplot(1,1,1)
#    plt.scatter(img1,img2,alpha = 0.5)
#    ax1.set_ylabel('T2 Image')
#    ax1.set_xlabel('T1C Image')
#    ax1.set_title('Joint Instensity Histogram (T1C and T2)')
#    plt.show()
        
#    plt.imshow(img,cmap = 'gray')
#    plt.figure()

#    fig = plt.gcf()
#    fig.clf()
#    ax1 = fig.add_subplot(1,1,1)
#    ax1.imshow(mask,cmap = 'gray')
#    fig.canvas.draw()
    
    fig = plt.gcf()
    fig.clf()
    ax1 = fig.add_subplot(1,1,1)
    ax1.imshow(img,cmap = 'gray')
    ax1.hold(True)
    
    
    
    alpha=100
    sigma = 3
    marginX = 3
    gradMat = []
#    plt.imshow(img,cmap = 'gray')
#    plt.hold(True)    
    for phi in range(0,360,theta):
        if phi<90:
            endX = abs(np.round(d*np.cos(np.deg2rad(phi))))
            xray = (np.arange(centerX,centerX+endX))
            yray = (centerY-(xray-centerX)*np.float(np.tan(np.deg2rad(phi))))
            resImgMatrix = np.rot90(f1(xray,yray),3)
            vecImageValues = np.diag(resImgMatrix)
            
            resMaskMatrix = np.rot90(f2(xray,yray),3)
            vecMaskValues = list(np.diag(resMaskMatrix))                        
            ind = vecMaskValues.index(0)
            gradVec = gaussian_gradient_magnitude(vecImageValues[0:ind], sigma, mode='mirror')
            gradVec = 1.0/np.sqrt(1.0 + alpha*gradVec)
            gradMat.append(list(gradVec))
#            ax1.hold(True)
            ax1.plot(xray[0:ind],yray[0:ind],'b-')
            fig.canvas.draw()
            
        
#            plt.show()

#            resImgMatrix1 = np.rot90(f3(xray,yray),3)
#            resImgMatrix2 = np.rot90(f4(xray,yray),3)
#            vecImageValues1 = np.diag(resImgMatrix1)
#            vecImageValues2 = np.diag(resImgMatrix2)
#            fig = plt.gcf()
#            fig.clf()
#            ax1 = fig.add_subplot(1,1,1)
#            plt.plot(vecImageValues1[0:ind],'b')
#            plt.plot(vecImageValues2[0:ind],'r')
#            ax1.set_ylabel('T2 Image')
#            ax1.set_xlabel('T1C Image')
#            ax1.set_title('Intensity profile of a ray')
#            plt.show()
#            

#            fig = plt.gcf()
#            fig.clf()
#            ax1 = fig.add_subplot(1,1,1)
#            plt.scatter(vecImageValues1[0:ind],vecImageValues2[0:ind], alpha=0.5)
#            ax1.set_ylabel('T2 Image')
#            ax1.set_xlabel('T1C Image')
#            ax1.set_title('Joint Intensity histogram for a ray')
#            plt.show()
#            
        elif phi>90 and phi<=180:
            endX = abs(np.round(d*np.cos(np.deg2rad(phi))))+marginX
            xray = (np.arange(centerX,centerX-endX,-1))
            yray = (centerY-(xray-centerX)*np.float(np.tan(np.deg2rad(phi))))
            resImgMatrix = f1(xray,yray)
            vecImageValues = np.diag(resImgMatrix)
            vecImageValues = vecImageValues[np.arange(len(vecImageValues)-1,0,-1)]
            
            resMaskMatrix = f2(xray,yray)
            vecMaskValues = list(np.diag(resMaskMatrix))                        
            ind = endX-vecMaskValues.index(1)
            gradVec = gaussian_gradient_magnitude(vecImageValues[0:ind], sigma, mode='mirror')
            gradVec = 1.0/np.sqrt(1.0 + alpha*gradVec)
            gradMat.append(list(gradVec))
#            ax1.hold(True)
            ax1.plot(xray[0:ind],yray[0:ind],'b-')
            fig.canvas.draw()
            
            
#            resImgMatrix1 = np.rot90(f3(xray,yray))
#            resImgMatrix2 = np.rot90(f4(xray,yray))
#            vecImageValues1 = np.diag(resImgMatrix1)
#            vecImageValues1 = vecImageValues1[np.arange(len(vecImageValues1)-1,0,-1)]
#            vecImageValues2 = np.diag(resImgMatrix2)
#            vecImageValues2 = vecImageValues2[np.arange(len(vecImageValues2)-1,0,-1)]
#            plt.plot(np.arange(0,ind), vecImageValues1[0:ind],'b')
#            plt.plot(np.arange(0,ind), vecImageValues2[0:ind],'r')
#            plt.show()
#            
#
#            plt.scatter(vecImageValues1[0:ind],vecImageValues2[0:ind], alpha=0.5)
#            plt.show()
#            
        elif phi>180 and phi<=270:
            endX = abs(np.round(d*np.cos(np.deg2rad(phi))))+marginX
            xray = (np.arange(centerX,centerX-endX,-1))
            yray = (centerY-(xray-centerX)*np.float(np.tan(np.deg2rad(phi))))
            resImgMatrix = np.rot90(f1(xray,yray),1)
            vecImageValues = np.diag(resImgMatrix)
            gradMat.append(list(gradVec))
            
            resMaskMatrix = np.rot90(f2(xray,yray))
            vecMaskValues = list(np.diag(resMaskMatrix))                        
            ind = vecMaskValues.index(0)
            gradVec = gaussian_gradient_magnitude(vecImageValues[0:ind], sigma, mode='mirror')
            gradVec = 1.0/np.sqrt(1.0 + alpha*gradVec)
#            ax1.hold(True)
            ax1.plot(xray[0:ind],yray[0:ind],'b-')
            fig.canvas.draw()
            
#            resImgMatrix1 = np.rot90(f3(xray,yray),1)
#            resImgMatrix2 = np.rot90(f4(xray,yray),1)
#            vecImageValues1 = np.diag(resImgMatrix1)
#            vecImageValues2 = np.diag(resImgMatrix2)
#            plt.plot(vecImageValues1[0:ind],'b')
#            plt.plot(vecImageValues2[0:ind],'r')
#            plt.show()
#            
#
#            plt.scatter(vecImageValues1[0:ind],vecImageValues2[0:ind], alpha=0.5)
#            plt.show()
    
            
        elif phi>270 and phi<360:
            endX = abs(np.round(d*np.cos(np.deg2rad(phi))))+marginX
            xray = (np.arange(centerX,centerX+endX))
            yray = (centerY-(xray-centerX)*np.float(np.tan(np.deg2rad(phi))))
            resImgMatrix = f1(xray,yray)
            vecImageValues = np.diag(resImgMatrix)
            
            resMaskMatrix = f2(xray,yray)
            vecMaskValues = list(np.diag(resMaskMatrix))                        
            ind = vecMaskValues.index(0)
            gradVec = gaussian_gradient_magnitude(vecImageValues[0:ind], sigma, mode='mirror')
            gradVec = 1.0/np.sqrt(1.0 + alpha*gradVec)
            gradMat.append(list(gradVec))
#            ax1.hold(True)
            ax1.plot(xray[0:ind],yray[0:ind],'b-')
            fig.canvas.draw()
            
#            resImgMatrix1 = f3(xray,yray)
#            resImgMatrix2 = f4(xray,yray)
#            vecImageValues1 = np.diag(resImgMatrix1)
#            vecImageValues2 = np.diag(resImgMatrix2)
#            plt.plot(vecImageValues1[0:ind],'b')
#            plt.plot(vecImageValues2[0:ind],'r')
#            plt.show()
#            
#
#            plt.scatter(vecImageValues1[0:ind],vecImageValues2[0:ind], alpha=0.5)
#            plt.show()
#            GUI_Starter.Main.ui.figure1.canvas.ax.plot(xray[0:d],yray[0:d],'b-')
#            GUI_Starter.Main.ui.figure1.canvas.ax.draw()
#            GUI_Starter.Ui_MainWindow.figure1.canvas.ax.plot(xray[0:d],yray[0:d],'b-')
#            GUI_Starter.Ui_MainWindow.figure1.canvas.ax.draw()
#    normGrad = []
    minGradVec = []
#    minNormGrad = []
#    minG = []
    
    for i in range(len(gradMat)):
        minGradVec.append(min(gradMat[i]))
#    minG = min(minGradVec) 
    
#    for i in range(len(gradMat)):
##        normGrad.append(np.divide(gradMat[i],minG))
#        minNormGrad.append(min(normGrad[i]))
        
    th = np.mean(minGradVec)+4*np.std(minGradVec)
#    th = np.percentile(minGradVec,100)
#    plt.show()
    return th,centerX,centerY
    
    