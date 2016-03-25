# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 12:23:24 2015

@author: m131199
"""

import os
import numpy as np
import nibabel as nib
from nipype.interfaces.ants import Registration
from nipype.interfaces.ants import ApplyTransforms

#filenames = ['brats_tcia_pat101_1','brats_tcia_pat141_1','brats_tcia_pat177_1',
#'brats_tcia_pat202_1','brats_tcia_pat248_1','brats_tcia_pat249_1','brats_tcia_pat254_1',
#'brats_tcia_pat255_1','brats_tcia_pat266_1','brats_tcia_pat276_2','brats_tcia_pat298_1',
#'brats_tcia_pat299_1','brats_tcia_pat310_1','brats_tcia_pat312_2','brats_tcia_pat325_1',
#'brats_tcia_pat351_1','brats_tcia_pat402_1','brats_tcia_pat413_1','brats_tcia_pat428_1',
#'brats_tcia_pat442_1','brats_tcia_pat449_1','brats_tcia_pat466_1','brats_tcia_pat483_1',
#'brats_tcia_pat490_1','brats_tcia_pat493_1']

folderNames = ['brats_tcia_pat493_1']

homedir = '/Users/m131199/Documents/LGG_GUI/LGG/'
path = '/Users/m131199/Documents/segData/Brats2014/'
fileName = 'T2.nii'


for i in range(len(folderNames)):
    folder = path+folderNames[i] + '/'
    input_fixed = folder + fileName
    os.chdir(folder)
    folderName = 'atlasTransformations_'+fileName[:len(fileName)-4]
    os.mkdir(folderName)    
    newPath = folder + folderName + '/'
    os.chdir(newPath)
#    atlasPath = '/Users/m131199/Documents/LGG_GUI/LGG/'
    atlasPath = homedir 
    input_moving = atlasPath + 'atlas_stripped.nii'
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Affine','SyN']  # list of transformations
    reg.inputs.transform_parameters = [(.3,),(0.1,3.0,0.0)]
    reg.inputs.number_of_iterations = [[40, 20, 10],[40, 20, 10]]
#    reg.inputs.number_of_iterations = [[1, 1, 1],[1, 1, 1]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = True
    reg.inputs.metric = ['MI','Mattes']  # mutual information
    reg.inputs.metric_weight = [1]*2
    reg.inputs.radius_or_number_of_bins = [64]*2
    reg.inputs.sampling_strategy = ['Regular']*2
    reg.inputs.sampling_percentage = [0.5]*2
    reg.inputs.terminal_output = 'allatonce'
    reg.inputs.convergence_threshold = [1.e-6]*2
    reg.inputs.convergence_window_size = [10]*2
    reg.inputs.smoothing_sigmas = [[3, 1, 0]]*2
    reg.inputs.sigma_units = ['vox']*2
    reg.inputs.shrink_factors = [[ 2, 1, 0]]*2
    reg.inputs.use_estimate_learning_rate_once = [True]*2
    reg.inputs.use_histogram_matching = [True]*2
    reg.terminal_output = 'none'
    reg.inputs.num_threads = 4  # ?
    reg.inputs.winsorize_lower_quantile = 0.025
    reg.inputs.winsorize_upper_quantile = 0.95
    reg.inputs.output_warped_image = True
    #reg.inputs.collapse_linear_transforms_to_fixed_image_header = False
    reg.inputs.output_warped_image = folder + 'registeredAtlas_' + fileName
    reg.cmdline
    reg.run()
     
    at = ApplyTransforms()
#    os.chdir(newPath)
    fileNames = ['pbmap_GM.nii','pbmap_WM.nii','pbmap_CSF.nii','tissues.nii']    
    for j in range(4):    
        at.inputs.dimension = 3
        at.inputs.input_image = atlasPath+fileNames[j]
        at.inputs.reference_image = input_fixed
        at.inputs.output_image = 'deformed_'+fileNames[j]
        at.inputs.interpolation = 'BSpline'
        at.inputs.default_value = 0
        at.inputs.transforms = ['0GenericAffine.mat','1Warp.nii.gz']
        at.inputs.invert_transform_flags = [False, False]
        at.cmdline
        at.run()
