# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 00:47:24 2015

@author: m131199
"""

import sys
import os
import numpy as np
import nibabel as nib
import scipy
import scipy.ndimage.interpolation as interp3D
from nibabel.affines import apply_affine



def interpolateData(path1,path2,file1,file2,filename1,filename2):
    filePath1 = path1
    filePath2 = path2
    T2Wfname = file2
    T1Cfname = file1

    if filename2.endswith('.nii'):
        atlasPath = filePath2+'atlasTransformations_'+filename2[:len(filename2)-4]
    elif filename2.endswith('.gz'):
        atlasPath = filePath2+'atlasTransformations_'+filename2[:len(filename2)-7]
        
    os.chdir(filePath2)  
        
    img1Obj = nib.load(T1Cfname)
    img2Obj = nib.load(T2Wfname)
    
    PSz = img2Obj.get_header()['pixdim'][3]
    
    img1_data = img1Obj.get_data()
    img2_data = img2Obj.get_data()
        
    affine1 = img1Obj.get_affine()
    scaling_affine1 = np.array([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1/PSz, 0],[0, 0, 0, 1]])
    affine1 = affine1.dot(scaling_affine1)
    
    affine2 = img2Obj.get_affine()
    scaling_affine2 = np.array([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1/PSz, 0],[0, 0, 0, 1]])
    affine2 = affine2.dot(scaling_affine2)
    
    pmapWMpath = atlasPath + '/deformed_pbmap_WM.nii'
    pmapWM = nib.load(pmapWMpath)
    pmapWM_data = pmapWM.get_data()
            
    pmapGMpath = atlasPath + '/deformed_pbmap_GM.nii'
    pmapGM = nib.load(pmapGMpath)
    pmapGM_data = pmapGM.get_data()
    
    pmapCSFpath = atlasPath + '/deformed_pbmap_CSF.nii'
    pmapCSF = nib.load(pmapCSFpath)
    pmapCSF_data = pmapCSF.get_data()
        
    if len(img1Obj.shape)>3:
        Iimg1_data = interp3D.zoom(img1_data[:,:,:,1],[1,1,PSz])
    else:
        Iimg1_data = interp3D.zoom(img1_data,[1,1,PSz])
        
    if len(img2Obj.shape)>3:
        Iimg2_data = interp3D.zoom(img2_data[:,:,:,1],[1,1,PSz])
    else:
        Iimg2_data = interp3D.zoom(img2_data,[1,1,PSz])
     
#    (x1,y1,z1) = orx.aff2axcodes(self.affine1)
#    self.Orx = x1
#    self.Ory = y1
#    self.Orz = z1
#    ornt = orx.axcodes2ornt((x1,y1,z1))  
#    refOrnt = orx.axcodes2ornt(('R','A','S'))
#    newOrnt1 = orx.ornt_transform(ornt,refOrnt)
#    
#    (x2,y2,z2) = orx.aff2axcodes(self.affine2)
#    self.Orx = x2
#    self.Ory = y2
#    self.Orz = z2
#    ornt = orx.axcodes2ornt((x2,y2,z2))  
#    refOrnt = orx.axcodes2ornt(('R','A','S'))
#    newOrnt2 = orx.ornt_transform(ornt,refOrnt)
#
#    self.img_data1 = orx.apply_orientation(self.img_data1,newOrnt1)
#    self.img_data2 = orx.apply_orientation(self.img_data2,newOrnt2)
    
    os.chdir(filePath1) 
    new_image1 = nib.Nifti1Image(Iimg1_data, affine1)    
    nib.save(new_image1, 'I'+filename1)
    
    os.chdir(filePath2) 
    new_image2 = nib.Nifti1Image(Iimg2_data, affine2)    
    nib.save(new_image2, 'I'+filename2)   
    
    IpmapWM_data = interp3D.zoom(pmapWM_data,[1,1,PSz])
    IpmapGM_data = interp3D.zoom(pmapGM_data,[1,1,PSz])    
    IpmapCSF_data = interp3D.zoom(pmapCSF_data,[1,1,PSz])    
    
    
#    os.mkdir('atlasTransformations_LGG_' +str(num[i])+ '_T2')
    os.chdir(atlasPath) 
    new_image3 = nib.Nifti1Image(IpmapWM_data, affine2)    
    nib.save(new_image3, 'Ideformed_pbmap_WM.nii')       
    
    new_image4 = nib.Nifti1Image(IpmapGM_data, affine2)    
    nib.save(new_image4, 'Ideformed_pbmap_GM.nii')   
    
    new_image5 = nib.Nifti1Image(IpmapCSF_data, affine2)    
    nib.save(new_image5, 'Ideformed_pbmap_CSF.nii')   