#!/bin/bash
# Expected format
# ./builders/VOC2007/convert_to_tfRecords.sh VOC2007 false

##############################################
# Arguments
NB_ARGUMENTS=2
if [ $# -lt $NB_ARGUMENTS ]; then
  echo 1>&2 "$0: Not enough arguments (should be $NB_ARGUMENTS)."
  exit 2
elif [ $# -gt $NB_ARGUMENTS ]; then
  echo 1>&2 "$0: Too many arguments (should be $NB_ARGUMENTS)."
  exit 2
fi


##############################################
# General variables
DATASET_DIR=$1
DUPLICATE=$2
FORMAT_NAME="tfRecords"

DATASET_OUTPUT_DIR=$DATASET_DIR"_"$FORMAT_NAME
# TODO: relative path vvvv
BUILDERS=$DATASET_DIR/../builders
NB_CATEGORIES=20
IMAGE_EXTENSION="jpg" # jpg / png supported


##############################################
# Invalid conditions
if [ ! -d $DATASET_DIR ]; then
  echo "Unable to find $DATASET_DIR."
  exit
fi


##############################################
# Requirements
if [ -d $DATASET_OUTPUT_DIR ]; then
    echo "The converted dataset $DATASET_OUTPUT_DIR already exists. No need " \
    "to convert it again."
    echo "> If you want to re-download it, simply remove $DATASET_OUTPUT_DIR."
    exit 1
fi
if [ ! -f $BUILDERS/VOC2007/label_map.pbtxt ]; then
    echo "The conversion require a file $BUILDERS/VOC2007/label_map.pbtxt."
    exit 1
fi


##############################################
# Preparation
echo "-------------------------------------------"
echo "Create the $DATASET_OUTPUT_DIR directory."
mkdir -m 755 $DATASET_OUTPUT_DIR


##############################################
# Conversion
declare -a SETS=("train", "val", "trainval", "test")

for i in "${SETS[@]}"; do
  python $BUILDERS/VOC2007/create_tf_records.py \
                  --data_dir $DATASET_DIR \
                  --set ${arr[i]} \
                  --output_path $DATASET_OUTPUT_DIR \
                  --label_map_path $BUILDERS/VOC2007/label_map.pbtxt
done


##############################################
# Clean up
chmod -R 755 $DATASET_OUTPUT_DIR
if [ "$DUPLICATE" = false ]; then rm $DATASET_DIR; fi

