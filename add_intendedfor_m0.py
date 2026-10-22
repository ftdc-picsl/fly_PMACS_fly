# -*- coding: utf-8 -*-
'''
Created on September 5, 2023
And also sort of March 31, 2026
@author Hamsi
@author Chris 
Modified version of dwi one to add intended for field to M0 jsons in asl acquisitions in BIDS format, as dcm2bids does not do it.
'''

import json
import os
import sys
import glob

sub = str(sys.argv[1])
ses = str(sys.argv[2]) 
bids_base = str(sys.argv[3])

perf_dir = "{}/sub-{}/ses-{}/perf/".format(bids_base,sub,ses)
print("perf_dir: ", perf_dir)
asl_file = os.path.basename(glob.glob(perf_dir+"*asl.nii.gz")[0])
m0json_file = glob.glob(perf_dir+"/*m0scan.json")[0]
print("json_file: ", m0json_file)
with open(m0json_file,'r') as f:
    data=json.load(f)
    data["IntendedFor"] = "ses-{}/perf/{}".format(ses,asl_file)
with open(m0json_file,'w') as f:
    json.dump(data,f,indent=4,sort_keys=True)

