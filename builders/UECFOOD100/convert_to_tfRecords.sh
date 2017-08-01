#!/bin/bash
# Expected format
# NOTE: require to have been converted into the fincFormat first (will be changed)
# ./builders/UECFOOD100/convert_to_tfRecords.sh UECFOOD100 false

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

IMAGES_DIR=$DATASET_DIR"/Images"
ANNOTATIONS_DIR=$DATASET_DIR"/Annotations"
IMAGESETS_DIR=$DATASET_DIR"/ImageSets"
NB_CATEGORIES=100

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
if [ ! -f $BUILDERS/UECFOOD100/categories.txt ]; then
    echo "The conversion require the file $BUILDERS/UECFOOD100/categories.txt."
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
  python $BUILDERS/UECFOOD100/create_tf_records.py \
                  --data_dir $DATASET_DIR \
                  --set ${SETS[$i]} \
                  --output_path $DATASET_OUTPUT_DIR/UECFOOD100_${SETS[$i]}.tfrecord \
                  --categories_path $BUILDERS/UECFOOD100/categories.txt
done


##############################################
# Transfer the lists
cp $BUILDERS/UECFOOD100/categories.txt $DATASET_OUTPUT_DIR/infos/


##############################################
# Sign
echo "tfRecords" > $DATASET_OUTPUT_DIR/.format


##############################################
# Clean up
chmod -R 755 $DATASET_OUTPUT_DIR
if [ "$DUPLICATE" = false ]; then rm -r $DATASET_DIR; fi

