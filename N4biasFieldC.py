# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 09:45:22 2015

@author: m131199
"""


import sys
import nipype.interfaces.ants as ants
from nipype.interfaces.ants import N4BiasFieldCorrection
import nibabel as nib
import os


def biasFieldCorrection(path1, path2, image1, image2, filename1, filename2):

    os.chdir(path1)
    n4  = N4BiasFieldCorrection()
    n4.inputs.dimension = 3
    n4.inputs.input_image = image1
    n4.inputs.bspline_fitting_distance = 300
    n4.inputs.shrink_factor = 3
    n4.inputs.n_iterations = [50,50,30,20]
    n4.inputs.convergence_threshold = 1e-6
#    n4.inputs.save_bias = True
#    n4.inputs.output_image = 'BFC_' + filename1
#    n4.cmdline
    n4.run()
    
    os.chdir(path2)
    n4.inputs.input_image = image2
#    n4.inputs.output_image = path2 + 'BFC_' + filename2
    n4.run()