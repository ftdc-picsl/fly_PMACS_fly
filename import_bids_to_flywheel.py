import os
import re
import json
import sys
import flywheel

fw = flywheel.Client('')

# Usage: python import_bids_to_flywheel.py <subject> <session> <group> <project> <bids_folder_on_disk>
subject = sys.argv[1]
session = sys.argv[2]
group = sys.argv[3]
project = sys.argv[4]
bids_folder = sys.argv[5] 

# Flywheel location:
# get session 
try:
    sess = fw.lookup(f"{group}/{project}/{subject}/{session}")
except:
    print("no session found for group: " + group + ", project: " + project + ", subject: " + subject + ", session: " + session + " exiting..." )
    exit()

# Disk location:
bids_path = f"{bids_folder}/sub-{subject}/ses-{session}/"

def fw_upload_file(acquisition, file_path, json_data, classification):
    """Uploads a file to the specified flywheel acquisition and updates its metadata."""
    uploaded_files = fw.upload_file_to_acquisition(acquisition.id, file_path)
    uploaded_file = uploaded_files[0]
    # print(acquisition)
    uploaded_file.replace_info(json_data)
    print(classification)
    acquisition.replace_file_classification(os.path.basename(file_path), classification, modality='MR')
    # print(uploaded_file)


for mod in ["anat", "func", "dwi", "perf", "fmap", "swi"]: #all modalities available for our data
    mod_path = os.path.join(bids_path, mod)
    # print(mod_path)
    if os.path.exists(mod_path):
        for file in os.listdir(mod_path):
            if file.endswith('.json'): # look for metadata
                json_path = os.path.join(mod_path, file)
                with open(json_path, 'r') as f:
                    json_data = json.load(f)

                # Extract filename components
                filename = os.path.basename(json_path)
                folder = mod
                path = os.path.relpath(mod_path, bids_path)
                base_filename = os.path.splitext(filename)[0]
                modality = base_filename.split("_")[-1]

                # Create the BIDS dictionary to be compatible with the BIDS tab on flywheel
                bids = {
                    "Acq": re.search(r'acq-([^_]+)', filename).group(1) if "acq-" in filename else "",
                    "Ce": re.search(r'ce-([^_]+)', filename).group(1) if "ce-" in filename else "",
                    "Dir": re.search(r'dir-([^_]+)', filename).group(1) if "dir-" in filename else "",
                    "Echo": re.search(r'echo-([^_]+)', filename).group(1) if "echo-" in filename else "",
                    "error_message": "",
                    "Filename": base_filename,
                    "Folder": folder,
                    "ignore": "",
                    "IntendedFor": "",
                    "Mod": re.search(r'mod-([^_]+)', filename).group(1) if "mod-" in filename else "",
                    "Modality": modality,
                    "Path": path,
                    "Rec": re.search(r'rec-([^_]+)', filename).group(1) if "rec-" in filename else "",
                    "Run": re.search(r'run-([^_]+)', filename).group(1) if "run-" in filename else "",
                    "Task": re.search(r'task-([^_]+)', filename).group(1) if "task-" in filename else "",
                    "template": "",
                    "valid": True
                }

                # Append the BIDS dictionary to json_data
                json_data["BIDS"] = bids

                # Save the updated JSON data back to the file -- just for posterity's sake
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=4)

                series_instance_uid = json_data.get("SeriesInstanceUID", None) #to idenify the acquisition to upload to
                series_description = json_data.get("SeriesDescription", None) #because the RMS files don't work the same way
                print(series_instance_uid)
                if series_instance_uid:
                    for acq in sess.acquisitions.iter_find(): 
                        dicoms = [f for f in acq.files if f.type == "dicom"]
                        if not dicoms:
                            continue
                        for dicom in dicoms: # loop through the flywheel acquisitions to find the one that matches the SeriesInstanceUID
                            dicom_name = dicom.name
                            if series_instance_uid == acq.uid: #upload json, nifti, bvec, and bval files to the acquisition
                                # print(dicom)
                                # json_data["Classification"] = dicom.classification
                                with open(json_path, 'w') as f:
                                    json.dump(json_data, f, indent=4)
                                fw_upload_file(acq, json_path, json_data, dicom.classification)
                                nifti_path = os.path.splitext(json_path)[0] + ".nii.gz"
                                if os.path.exists(nifti_path):
                                    fw_upload_file(acq, nifti_path, json_data, dicom.classification)
                                bvec_path = os.path.splitext(json_path)[0] + ".bvec"
                                if os.path.exists(bvec_path):
                                    fw_upload_file(acq, bvec_path, json_data, dicom.classification)
                                bval_path = os.path.splitext(json_path)[0] + ".bval"
                                if os.path.exists(bval_path):
                                    fw_upload_file(acq, bval_path, json_data, dicom.classification)
                                break # stop searching for dicoms once we find the one that matches the SeriesInstanceUID
