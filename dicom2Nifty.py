# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 18:20:32 2015

@author: m131199
"""
import os
os.chdir('/Users/m131199/Downloads/LGG-229/MRI_Hd/axial_T1/')

from nipype.interfaces.dcmstack import DcmStack

stacker = DcmStack()
stacker.inputs.dicom_files = '/Users/m131199/Downloads/LGG-229/MRI_Hd/axial_T1/'
stacker.run() 
#result.outputs.out_file


import dcmstack
from glob import glob
src_dcms = glob('/Users/m131199/Downloads/LGG-229/MRI_Hd/axial_T1/*.dcm')
stacks = dcmstack.parse_and_stack(src_dcms)
stack = stacks.values[0]
nii = stack.to_nifti()
nii.to_filename('output.nii.gz')

#import os
#os.chdir('/Users/m131199/Downloads/LGG-229/MRI_Hd/AX_T2_OBL/')
#from nipype.interfaces.freesurfer import DICOMConvert
#cvt = DICOMConvert()
#cvt.inputs.dicom_dir = '/Users/m131199/Downloads/LGG-229/MRI_Hd/AX_T2_OBL/'
#cvt.inputs.file_mapping = [('nifti', '*.nii'), ('info', 'dicom*.txt'), ('dti', '*dti.bv*')]
#
#from nipype.interfaces.dcm2nii import Dcm2nii
#converter = Dcm2nii()
#converter.inputs.source_names = ['/Users/m131199/Downloads/LGG-229/MRI_Hd/AX_T2_OBL/9999.193444720349620986809184775663710556976.dcm']
#converter.inputs.gzip_output = True
#converter.inputs.output_dir = '/Users/m131199/Downloads/LGG-229/MRI_Hd/AX_T2_OBL/'
#converter.cmdline 
#converter.run() 
#
import dcmstack,dicom
from glob import glob
src_paths = glob('/Users/m131199/Downloads/LGG-229/MRI_Hd/axial_T1/*.dcm')
i=0
my_stack = dcmstack.DicomStack()
for src_path in src_paths:
    src_dcm = dicom.read_file(src_path)
    my_stack.add_dcm(src_dcm)
    i=i+1
nii_wrp = my_stack.to_nifti_wrapper()
nii_wrp.get_meta('InversionTime')
stack_data = my_stack.get_data()
stack_affine = my_stack.get_affine()
nii = my_stack.to_nifti()
nii.to_filename('output.nii.gz')