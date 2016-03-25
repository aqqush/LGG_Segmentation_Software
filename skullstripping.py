# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 15:27:16 2015

@author: m131199
"""

#root = '/Users/m131199/Documents/testData/'
#image1 = '/Users/m131199/Documents/testData/PN-10_T1C.nii'
import sys
import os
import nipype.interfaces.fsl as fsl
#os.chdir(root)


def stripSkull(path1,path2,image1,image2,filename1, filename2):
    
    mybet = fsl.BET()
    mybet.inputs.in_file = image1
    mybet.inputs.out_file = path1 + 'SS_' + filename1
    mybet.run()

    mybet.inputs.in_file = image2
    mybet.inputs.out_file = path2 + 'SS_' + filename2
    mybet.run()


