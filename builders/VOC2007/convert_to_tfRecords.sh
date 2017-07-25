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
# TODO: relative paths vvvv
ROOT=$DATASET_DIR/..
BUILDERS=$ROOT/builders
SCRIPTS=$ROOT/scripts

IMAGES_DIR=$DATASET_DIR"/VOC2007/JPEGImages"
ANNOTATIONS_DIR=$DATASET_DIR"/VOC2007/Annotations"
IMAGESETS_DIR=$DATASET_DIR"/VOC2007/ImageSets/Main"
NB_CATEGORIES=20

DATASET_OUTPUT_DIR=$DATASET_DIR"_"$FORMAT_NAME
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
if [ ! -f $BUILDERS/VOC2007/categories.txt ]; then
    echo "The conversion require the file $BUILDERS/VOC2007/categories.txt."
    exit 1
fi

export_me_that() {
  export PYTHONPATH=$PYTHONPATH:$SCRIPTS
}
export_me_that


##############################################
# Preparation
echo "-------------------------------------------"
echo "Create the $DATASET_OUTPUT_DIR directory."
mkdir -m 755 $DATASET_OUTPUT_DIR
mkdir $DATASET_OUTPUT_DIR/infos


##############################################
# Conversion
SETS=("train" "val" "trainval" "test")

for i in "${!SETS[@]}"; do
  python $BUILDERS/VOC2007/create_tf_records.py \
                  --data_dir $DATASET_DIR \
                  --set ${SETS[$i]} \
                  --output_path $DATASET_OUTPUT_DIR/VOC2007_${SETS[$i]}.tfrecord \
                  --categories_path $BUILDERS/VOC2007/categories.txt
done


##############################################
# Transfer the lists
cp $BUILDERS/VOC2007/label_map.pbtxt $DATASET_OUTPUT_DIR/infos/


##############################################
# Clean up
chmod -R 755 $DATASET_OUTPUT_DIR
if [ "$DUPLICATE" = false ]; then rm $DATASET_DIR; fi

