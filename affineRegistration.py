# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 10:37:05 2015

@author: m131199
"""

import os
import numpy as np
import nibabel as nib
from nipype.interfaces.ants import Registration


def affineRegFunc(path,fileName,input_fixed,input_moving):
    os.chdir(path)
    reg = Registration()
    # ants-registration parameters:
    reg.inputs.fixed_image = input_fixed  # fixed image
    reg.inputs.moving_image = input_moving  # moving image
    reg.inputs.output_transform_prefix = path  # file path
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
    reg.inputs.collapse_output_transforms = True
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