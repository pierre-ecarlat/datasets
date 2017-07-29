#!/bin/bash
# Expected format 
# ./builders/VOC2007/download.sh OpenImages food

##############################################
# Arguments
NB_ARGUMENTS_MIN=1
NB_ARGUMENTS_MAX=2
if [ $# -lt $NB_ARGUMENTS_MIN ]; then
  echo 1>&2 "$0: Not enough arguments."
  exit 2
elif [ $# -gt $NB_ARGUMENTS_MAX ]; then
  echo 1>&2 "$0: Too many arguments."
  exit 2
fi


##############################################
# General variables
OUTPUT=$1
CATEG=$2
# TODO: relative paths vvvv
ROOT=${OUTPUT%/*}
BUILDERS=$ROOT/builders
SCRIPTS=$ROOT/scripts


##############################################
# PART 1: Get the helpers

TMP_DIR=`date +%d%H%M%S`
mkdir $TMP_DIR
cd $TMP_DIR

BUILDERS_HELPER=$BUILDERS/OpenImages/helper
if [ ! -d $BUILDERS_HELPER ]; then
  mkdir $BUILDERS_HELPER
fi

declare -A images
declare -A bb_hum_annotations
declare -A hum_annotations
declare -A mach_annotations
declare -A classes
images=( \
  ["text"]="Image URLs and metadata (990 MB)" \
  ["archive"]="images_2017_07.tar.gz" \
  ["control_file"]="train/images.csv" \
)
bb_hum_annotations=( \
  ["text"]="Bounding box annotations (train, validation, and test sets) (37 MB)" \
  ["archive"]="annotations_human_bbox_2017_07.tar.gz" \
  ["control_file"]="train/annotations-human-bbox.csv" \
)
hum_annotations=( \
  ["text"]="Image-level annotations (train, validation, and test sets) (66 MB)" \
  ["archive"]="annotations_human_2017_07.tar.gz" \
  ["control_file"]="train/annotations-human.csv" \
)
mach_annotations=( \
  ["text"]="Machine-populated image-level annotations (train, validation, and test sets) (447 MB)" \
  ["archive"]="annotations_machine_2017_07.tar.gz" \
  ["control_file"]="train/annotations-machine.csv" \
)
classes=( \
  ["text"]="Classes and class descriptions (293 KB)" \
  ["archive"]="classes_2017_07.tar.gz" \
  ["control_file"]="classes.txt" \
)

download_and_store() {
  local -n infos
  infos=$1

  HOST="https://storage.googleapis.com/openimages/2017_07/"
  
  if [ ! -f $BUILDERS_HELPER/${infos[control_file]} ]; then
    echo "-----------------------------------------------------"
    echo "${infos[text]}"
    wget $HOST"${infos[archive]}"
    tar xvf "${infos[archive]}"
    rm "${infos[archive]}"
    echo
  fi
}


echo "Download and extract archives..."
download_and_store images
download_and_store bb_hum_annotations
download_and_store hum_annotations
download_and_store mach_annotations
download_and_store classes


if [ -d 2017_07 ]; then
  echo "Move the dataset to the output directory"
  mv 2017_07/* $BUILDERS_HELPER
else
  echo "Already downloaded the helpers, no need to download them again."
fi


cd -
rm -r $TMP_DIR


#############################################
# PART 2: Get the dataset

#if [ ! -d $OUTPUT ]; then
#  mkdir -p $OUTPUT;
#fi
python $BUILDERS/OpenImages/download_dataset.py \
              $OUTPUT \
              $BUILDERS_HELPER \
              "$CATEG"
#if [ $(ls -p OpenImages/ | grep -v / | wc -l) -eq 0 ]; then
#  echo "Failed to download the dataset..."
#fi









