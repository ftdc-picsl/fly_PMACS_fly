#!/bin/bash


if [[ $# -lt 7 ]] ; then
    echo "USAGE: ./dcm2bids.sh <subID> <sesID> <scripts_dir> <vnav_parse_scripts_dir> <dcm2bids_conda_path> <dicom_base> <bids_base> "
    echo " converts dicoms to bids, including some helpful organization"
    echo "      subID: FlywheelSubjectLabel"
    echo "      sesID: FlywheelSessionLabel"
    echo "      scripts_dir: directory with a bunch of helper scripts like add_intendedfor_dwi.py and calculate_add_motion.sh "
    echo "      vnav_parse_scripts_dir: directory with the vnav parser script for calculate_add_motion.sh"  
    echo "      dcm2bids_conda_path: path to conda environment with dcm2bids set up"
    echo "      dicom_base: directory containing all subID/sesID directories with dicoms inside"
    echo "      bids_base: directory with sub-subj/ses-sess bids directories "
    echo "   "
    echo " some detail"  
    echo "  1. downloads dicoms from flywheel, or un-tars dicoms if already exported"
    echo "  2. applies harmonized heuristic to convert to bids format" 
    echo "  3. adds IntendedFor: dwi to the fmap json"
    echo "  4. calculates max and rms motion from vnav setters (if available) and appends to matching jsons"
    echo ""
    exit 1
fi

subj=$1
sess=$2
scripts_dir=$3
dcm2bids_conda_path=$4
dicom_base=$5
bids_base=$6
heuristic=$7
calculate_add_motion=$8

dicom_dir=${dicom_base}/${subj}/${sess}
uncompressed_dicom_dir=${dicom_base}/${subj}/${sess}/uncompressed/

module unload miniconda 
module load miniconda/3-25
eval "$(conda shell.bash hook)"

conda activate $dcm2bids_conda_path

echo "Running dcm2niix for subject: $subj and session: $sess"

nifti_dir=${bids_base}/tmp_dcm2bids/sub-${subj}_ses-${sess}

rm -rf ${nifti_dir} #avoiding conflicts with previous runs
mkdir -p ${nifti_dir}
#  
if [ -e "${dicom_dir}/dicoms.tar" ] ; then
    echo "Unzipping dicoms.tar"
    tar -xvf ${dicom_dir}/dicoms.tar -C ${dicom_dir}
else
    if [[ ! -d ${uncompressed_dicom_dir} ]] ; then
        mkdir -p ${uncompressed_dicom_dir}
    fi
    mv ${dicom_dir}/* ${uncompressed_dicom_dir}
fi


for file in ${uncompressed_dicom_dir}/*.zip; do
    zipname=$(echo $file | rev | cut -d '/' -f1 | rev | sed 's/.zip/_unzipped/')
    unzip -o ${file} -d ${uncompressed_dicom_dir}/${zipname}/
done


# Run dcm2niix:
dcm2niix -b y -ba n -z y -f %3s_%f_%p_%t -o ${nifti_dir} ${uncompressed_dicom_dir}

# echo "finished dcm2niix exiting"
# exit 1
echo "BIDSifying subject: $subj, session: $sess"

rm -rf ${bids_base}/sub-${subj}/ses-${sess} # just delete if exists


# Run dcm2bids:
dcm2bids -d ${uncompressed_dicom_dir} -c ${heuristic} -o ${bids_base} -p ${subj} -s ${sess} --auto_extract_entities --skip_dcm2niix

# Add IntendedFor field to DWI JSON files
python ${scripts_dir}add_intendedfor_dwi.py ${subj} ${sess} ${bids_base}

# Add IntendedFor field to m0scan JSON files
python ${scripts_dir}add_intendedfor_m0.py ${subj} ${sess} ${bids_base}


if [[ $calculate_add_motion == "" || $calculate_add_motion == True ]] ; then 
    echo "Calculating and adding vnav motion to jsons, if vnavs are present"
    calculate_add_motion=1
    cam_cmd="bash ${scripts_dir}/calculate_add_motion.sh ${subj} ${sess} ${scripts_dir} ${dicom_base} ${bids_base}"
    echo $cam_cmd
    $cam_cmd
elif [[ $calculate_add_motion == False ]] ; then 
    echo "Skipping calculation and addition of vnav motion to jsons"
    calculate_add_motion=0
else 
    echo "calculate_add_motion must be 0 or 1...exiting"
    exit 1
fi

rm -rf ${nifti_dir}

if [ ! -e ${dicom_dir}/dicoms.tar ]; then
    tar -cvf ${dicom_dir}/dicoms.tar -C ${dicom_dir} .
fi
if [ -e ${dicom_dir}/dicoms.tar ]; then
    rm -rf ${uncompressed_dicom_dir}
fi

