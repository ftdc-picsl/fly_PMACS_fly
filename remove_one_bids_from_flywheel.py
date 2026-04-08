import sys
import flywheel

fw = flywheel.Client('')

# Usage: python remove_bids_from_flywheel.py <subject> <session> <group> <project> 
subject = sys.argv[1]
session = sys.argv[2]
group = sys.argv[3]
project = sys.argv[4]
bids_to_rm = sys.argv[5]

# Flywheel location:
# get session 
try:
    sess = fw.lookup(f"{group}/{project}/{subject}/{session}")
except:
    print("no session found for group: " + group + ", project: " + project + ", subject: " + subject + ", session: " + session + " exiting..." )
    exit()


def fw_remove_one_bids(sess):
    for acq in sess.acquisitions.iter_find(): 
        for f in acq.files:
            f_origin = f.origin.type
            f_type = f.type
            f_name = f.name 
            if f_type == "dicom":
                print("keeping dicom " + f_name )
            elif f_origin == "user" and (f_type == "nifti" or f_type == "source code"  or f_type == "bvec" or f_type == "bval") :
                file_id = f.file_id
                # print (f.info.get('BIDS', {}).get(bids_to_rm))
                bids_folder = f.info.get('BIDS', {}).get('Folder',{})
                if bids_folder == bids_to_rm:
                    print("removing " + bids_folder + ' ' + f_name + ' ' + f_type)
                    fw.delete_file(file_id)
                else:
                    print("keeping " + bids_folder + ' ' + f_name + ' ' + f_type)

fw_remove_one_bids(sess)