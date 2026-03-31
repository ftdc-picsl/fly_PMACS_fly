# -*- coding: utf-8 -*-
'''
Created on September 5, 2023
@author Hamsi
Add intended for field to diffusion fieldmaps in BIDS format, if dcm2bids did not do it.
'''

import json
import os
import sys
import glob

sub = str(sys.argv[1])
ses = str(sys.argv[2]) 
bids_base = str(sys.argv[3])

dwi_dir = "{}/sub-{}/ses-{}/dwi/".format(bids_base,sub,ses)
print("dwi_dir: ", dwi_dir)
dwi_file = os.path.basename(glob.glob(dwi_dir+"*.nii.gz")[0])
fmap_dir = "{}/sub-{}/ses-{}/fmap/".format(bids_base,sub,ses)
json_file = glob.glob(fmap_dir+"/*epi.json")[0]
print("json_file: ", json_file)
with open(json_file,'r') as f:
    data=json.load(f)
    data["IntendedFor"] = "ses-{}/dwi/{}".format(ses,dwi_file)
with open(json_file,'w') as f:
    json.dump(data,f,indent=4,sort_keys=True)

