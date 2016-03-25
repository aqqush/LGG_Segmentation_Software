# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 12:19:54 2015

@author: m131199
"""

import os
import numpy as np
import nibabel as nib
from nipype.interfaces.ants import Registration
from nipype.interfaces.ants import ApplyTransforms


def rigidRegFunc(path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'rigid_'+fileName[:len(fileName)-7] 
    else:
        folderName = 'rigid_'+fileName[:len(fileName)-4]
    
    os.mkdir(folderName)    
    newPath = path + folderName + '/'
    os.chdir(newPath)
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Rigid']  # list of transformations
    reg.inputs.transform_parameters = [(.5,)]
    reg.inputs.number_of_iterations = [[40, 20, 10]]
#    reg.inputs.number_of_iterations = [[1, 1, 1]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
    reg.inputs.metric = ['MI']  # mutual information
    reg.inputs.metric_weight = [1]
    reg.inputs.radius_or_number_of_bins = [64]
    reg.inputs.sampling_strategy = ['Regular']
    reg.inputs.sampling_percentage = [0.5]
    reg.inputs.terminal_output = 'allatonce'
    reg.inputs.convergence_threshold = [1.e-6]
    reg.inputs.convergence_window_size = [10]
    reg.inputs.smoothing_sigmas = [[3, 1, 0]]
    reg.inputs.sigma_units = ['vox']
    reg.inputs.shrink_factors = [[ 2, 1, 0]]
    reg.inputs.use_estimate_learning_rate_once = [True]
    reg.inputs.use_histogram_matching = [True]
    reg.terminal_output = 'none'
    reg.inputs.num_threads = 4  # ?
    reg.inputs.winsorize_lower_quantile = 0.025
    reg.inputs.winsorize_upper_quantile = 0.95
    reg.inputs.output_warped_image = True
#    reg.ignore_exception = True
    #reg.inputs.collapse_linear_transforms_to_fixed_image_header = False
    reg.inputs.output_warped_image = path + 'rigid_reg_'+ fileName
    reg.cmdline
    reg.run()

    
def affineRegFunc(path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'affine_'+fileName[:len(fileName)-7] 
    else:
        folderName = 'affine_'+fileName[:len(fileName)-4]
    
    os.mkdir(folderName)
    newPath = path + folderName + '/'
    os.chdir(newPath)
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Affine']  # list of transformations
    reg.inputs.transform_parameters = [(.3,)]
    reg.inputs.number_of_iterations = [[40, 20, 10]]
#    reg.inputs.number_of_iterations = [[1, 1, 1]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
    reg.inputs.metric = ['MI']  # mutual information
    reg.inputs.metric_weight = [1]
    reg.inputs.radius_or_number_of_bins = [64]
    reg.inputs.sampling_strategy = ['Regular']
    reg.inputs.sampling_percentage = [0.5]
    reg.inputs.terminal_output = 'allatonce'
    reg.inputs.convergence_threshold = [1.e-6]
    reg.inputs.convergence_window_size = [10]
    reg.inputs.smoothing_sigmas = [[3, 1, 0]]
    reg.inputs.sigma_units = ['vox']
    reg.inputs.shrink_factors = [[ 2, 1, 0]]
    reg.inputs.use_estimate_learning_rate_once = [True]
    reg.inputs.use_histogram_matching = [True]
    reg.terminal_output = 'none'
    reg.inputs.num_threads = 4  # ?
    reg.inputs.winsorize_lower_quantile = 0.025
    reg.inputs.winsorize_upper_quantile = 0.95
    reg.inputs.output_warped_image = True
    #reg.inputs.collapse_linear_transforms_to_fixed_image_header = False
    reg.inputs.output_warped_image = path + 'affine_reg_'+ fileName
    reg.cmdline
    reg.run()
    return
    
def nonrigidRegFunc(path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'nonrigid'+fileName[:len(fileName)-7] 
    else:
        folderName = 'nonrigid'+fileName[:len(fileName)-4]    
    os.mkdir(folderName)    
    newPath = path + folderName + '/'
    os.chdir(newPath)
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['SyN']  # list of transformations
    reg.inputs.transform_parameters = [(.1,3,.0)]
    reg.inputs.number_of_iterations = ([[40, 20, 10]])
    reg.inputs.dimension = 3
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
    reg.inputs.metric = ['Mattes']  # mutual information
    reg.inputs.metric_weight = [1]
    reg.inputs.radius_or_number_of_bins = [64]
    reg.inputs.sampling_strategy = ['Regular']
    reg.inputs.sampling_percentage = [0.5]
    reg.inputs.terminal_output = 'allatonce'
    reg.inputs.convergence_threshold = [1.e-6]
    reg.inputs.convergence_window_size = [10]
    reg.inputs.smoothing_sigmas = [[3, 1, 0]]
    reg.inputs.sigma_units = ['vox']
    reg.inputs.shrink_factors = [[ 2, 1, 0]]
    reg.inputs.use_estimate_learning_rate_once = [True]
    reg.inputs.use_histogram_matching = [True]
    reg.terminal_output = 'none'
    reg.inputs.num_threads = 4  # ?
    reg.inputs.winsorize_lower_quantile = 0.025
    reg.inputs.winsorize_upper_quantile = 0.95
    reg.inputs.output_warped_image = True
    #reg.inputs.collapse_linear_transforms_to_fixed_image_header = False
    reg.inputs.output_warped_image = path + 'nonrigid_reg_'+ fileName
    reg.cmdline
    reg.run()
    return
    
def rigid_nonrigidRegFunc(path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'rigid_nonrigid'+fileName[:len(fileName)-7] 
    else:
        folderName = 'rigid_nonrigid'+fileName[:len(fileName)-4]
    os.mkdir(folderName)    
    newPath = path + folderName + '/'
    os.chdir(newPath)
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Rigid','SyN']  # list of transformations
    reg.inputs.transform_parameters = [(.5,),(0.1,3.0,0.0)]
    reg.inputs.number_of_iterations = [[40, 20, 10],[40, 20, 10]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
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
    reg.inputs.output_warped_image = path + 'rigid_nonrigid_reg_'+ fileName
    reg.cmdline
    reg.run()
    return
    
def affine_nonrigidRegFunc(path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'affine_nonrigid'+fileName[:len(fileName)-7] 
    else:
        folderName = 'affine_nonrigid'+fileName[:len(fileName)-4]
    os.mkdir(folderName)    
    newPath = path + folderName + '/'
    os.chdir(newPath)
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Affine','SyN']  # list of transformations
    reg.inputs.transform_parameters = [(.3,),(0.1,3.0,0.0)]
    reg.inputs.number_of_iterations = [[40, 20, 10],[40, 20, 10]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
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
    reg.inputs.output_warped_image = path + 'affine_nonrigid_reg_'+ fileName
    reg.cmdline
    reg.run()
    return

def atlasRegFunc(homedir,path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'atlasTransformations_'+fileName[:len(fileName)-7] 
    else:
        folderName = 'atlasTransformations_'+fileName[:len(fileName)-4]
    os.mkdir(folderName)    
    newPath = path + folderName + '/'
    os.chdir(newPath)
#    atlasPath = '/Users/m131199/Documents/LGG_GUI/LGG/'
    atlasPath = homedir + '/'
    input_moving = atlasPath + 'atlas_unstripped.nii'
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Rigid','SyN']  # list of transformations
    reg.inputs.transform_parameters = [(.5,),(0.1,3.0,0.0)]
    reg.inputs.number_of_iterations = [[40, 20, 10],[40, 20, 10]]
#    reg.inputs.number_of_iterations = [[1, 1, 1],[1, 1, 1]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
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
    reg.inputs.output_warped_image = path + 'registeredAtlas_' + fileName
    reg.cmdline
    reg.run()
    
#    reg.inputs.fixed_image = input_fixed  # fixed image
#    reg.inputs.moving_image = input_moving  # moving image
#    reg.inputs.output_transform_prefix = newPath  # file path
#    reg.inputs.transforms = ['SyN']  # list of transformations
#    reg.inputs.transform_parameters = [(0.1,3.0,0.0)]
#    reg.inputs.number_of_iterations = [[40, 20, 10]]
##    reg.inputs.number_of_iterations = [[1, 1, 1],[1, 1, 1]]
#    reg.inputs.dimension = 3
#    reg.inputs.initial_moving_transform_com = True
#    #reg.inputs.invert_initial_moving_transform = True
#    reg.inputs.output_warped_image = True
#    reg.inputs.output_inverse_warped_image = True
#    reg.inputs.write_composite_transform = True
#    reg.inputs.collapse_output_transforms = False
#    reg.inputs.metric = ['Mattes']  # mutual information
#    reg.inputs.metric_weight = [1]
#    reg.inputs.radius_or_number_of_bins = [64]
#    reg.inputs.sampling_strategy = ['Regular']
#    reg.inputs.sampling_percentage = [0.5]
#    reg.inputs.terminal_output = 'allatonce'
#    reg.inputs.convergence_threshold = [1.e-6]
#    reg.inputs.convergence_window_size = [10]
#    reg.inputs.smoothing_sigmas = [[3, 1, 0]]
#    reg.inputs.sigma_units = ['vox']
#    reg.inputs.shrink_factors = [[ 2, 1, 0]]
#    reg.inputs.use_estimate_learning_rate_once = [True]
#    reg.inputs.use_histogram_matching = [True]
#    reg.terminal_output = 'none'
#    reg.inputs.num_threads = 4  # ?
#    reg.inputs.winsorize_lower_quantile = 0.025
#    reg.inputs.winsorize_upper_quantile = 0.95
#    reg.inputs.output_warped_image = True
#    #reg.inputs.collapse_linear_transforms_to_fixed_image_header = False
#    reg.inputs.output_warped_image = path + 'registeredAtlas_' + fileName
#    reg.cmdline
#    reg.run()
     
    at = ApplyTransforms()
#    os.chdir(newPath)
    fileNames = ['pbmap_GM.nii','pbmap_WM.nii','pbmap_CSF.nii','tissues.nii']    
    for i in range(4):    
        at.inputs.dimension = 3
        at.inputs.input_image = atlasPath+fileNames[i]
        at.inputs.reference_image = input_fixed
        at.inputs.output_image = 'deformed_'+fileNames[i]
        at.inputs.interpolation = 'BSpline'
#        at.inputs.default_value = 0
        at.inputs.transforms = ['2Warp.nii.gz','1Rigid.mat','0DerivedInitialMovingTranslation.mat']
#        at.inputs.invert_transform_flags = [False, False, False]
        at.cmdline
        at.run()
        
    return
    
def atlasRegFunc2(homedir,path,fileName,input_fixed,input_moving):
    os.chdir(path)
    if fileName.endswith('.gz'):
        folderName = 'atlasTransformations_'+fileName[:len(fileName)-7] 
    else:
        folderName = 'atlasTransformations_'+fileName[:len(fileName)-4]
    os.mkdir(folderName)    
    newPath = path + folderName + '/'
    os.chdir(newPath)
#    atlasPath = '/Users/m131199/Documents/LGG_GUI/LGG/'
    atlasPath = homedir + '/'
    input_moving = atlasPath + 'atlas_stripped.nii'
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = newPath  # file path
    reg.inputs.transforms = ['Rigid','SyN']  # list of transformations
    reg.inputs.transform_parameters = [(.5,),(0.1,3.0,0.0)]
    reg.inputs.number_of_iterations = [[40, 20, 10],[40, 20, 10]]
#    reg.inputs.number_of_iterations = [[1, 1, 1],[1, 1, 1]]
    reg.inputs.dimension = 3
    reg.inputs.initial_moving_transform_com = True
    #reg.inputs.invert_initial_moving_transform = True
    reg.inputs.output_warped_image = True
    reg.inputs.output_inverse_warped_image = True
    reg.inputs.write_composite_transform = True
    reg.inputs.collapse_output_transforms = False
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
    reg.inputs.output_warped_image = path + 'registeredAtlas_' + fileName
    reg.cmdline
    reg.run()
     
    at = ApplyTransforms()
#    os.chdir(newPath)
    fileNames = ['pbmap_GM.nii','pbmap_WM.nii','pbmap_CSF.nii','tissues.nii']    
    for i in range(4):    
        at.inputs.dimension = 3
        at.inputs.input_image = atlasPath+fileNames[i]
        at.inputs.reference_image = input_fixed
        at.inputs.output_image = 'deformed_'+fileNames[i]
        at.inputs.interpolation = 'BSpline'
#        at.inputs.default_value = 0
        at.inputs.transforms = ['2Warp.nii.gz','1Rigid.mat','0DerivedInitialMovingTranslation.mat']
#        at.inputs.invert_transform_flags = [False, False, False]
        at.cmdline
        at.run()
        
    return