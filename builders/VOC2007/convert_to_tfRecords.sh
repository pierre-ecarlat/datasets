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
# TODO: relative path vvvv
BUILDERS=$DATASET_DIR/../builders

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
if [ ! -f $BUILDERS/VOC2007/label_map.pbtxt ]; then
    echo "The conversion require a file $BUILDERS/VOC2007/label_map.pbtxt."
    exit 1
fi
INSTALLATION_URL="https://github.com/tensorflow/models/blob/master/object_detection/g3doc/installation.md"
echo "This conversion method require the object detection model utils " \
     "from the tensorflow models. Current PYTHONPATH:"
echo "> "$PYTHONPATH
if [[ $PYTHONPATH == *"models"* ]]; then
  echo "Found something that should be that. If it doesn't work, please check " \
       "the installation procedure here: $INSTALLATION_URL"
else
  echo "You apparently don't have the object_detection utils in your PYTHONPATH. " \
       "Please check the installation procedure here: $INSTALLATION_URL."
  echo "My guess would be the following command:"
  LOC=`(locate -e models/object_detection/ | head -n 1)`
  PYPATH=${LOC%"models"*}"models"
  echo "export PYTHONPATH=\$PYTHONPATH:"$PYPATH""
  read -p "Try that? [Y/n] " -r
  if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 1
  fi

  export_me_that() {
    export PYTHONPATH=$PYTHONPATH:$PYPATH
  }
  export_me_that
fi



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
                  --label_map_path $BUILDERS/VOC2007/label_map.pbtxt
done


##############################################
# Transfer the lists
cp $BUILDERS/VOC2007/label_map.pbtxt $DATASET_OUTPUT_DIR/infos/


##############################################
# Clean up
chmod -R 755 $DATASET_OUTPUT_DIR
if [ "$DUPLICATE" = false ]; then rm $DATASET_DIR; fi

