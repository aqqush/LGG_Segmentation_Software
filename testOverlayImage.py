# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 01:31:18 2015

@author: m131199
"""

import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


path = '/Users/m131199/Documents/segData/T2/LGG_49_T2.nii'
segPath = '/Users/m131199/Documents/segData/automatedSegmentations/LGG_49_T2_ASeg_Z1.nii'

imgObj = nib.load(path)
imgData = imgObj.get_data()
img = imgData[:,:,41]

imgObj2 = nib.load(segPath)
imgData2 = imgObj2.get_data()
segImg = imgData2[:,:,41]

plt.imshow(img,cmap = 'gray')
plt.show()

testmap = mpl.colors.LinearSegmentedColormap.from_list('mycmap',[(0,0,0,0),(1,0,0,0.6)])

ax = plt.subplot(111)
ax.imshow(img,cmap = 'gray')
ax.hold(True)
ax.imshow(segImg,cmap = testmap)
plt.show()


