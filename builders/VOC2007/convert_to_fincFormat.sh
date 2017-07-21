#!/bin/bash
# Expected format
# ./builders/VOC2007/convert_to_fincFormat.sh VOC2007 false

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
FORMAT_NAME="fincFormat"

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
if [ ! -f $BUILDERS/VOC2007/categories.txt ]; then
    echo "The conversion require a file $BUILDERS/VOC2007/categories.txt."
    exit 1
fi


##############################################
# Preparation
echo "-------------------------------------------"
echo "Create the $DATASET_OUTPUT_DIR directory."
mkdir -m 755 $DATASET_OUTPUT_DIR
mkdir $DATASET_OUTPUT_DIR/Annotations
mkdir $DATASET_OUTPUT_DIR/Images
mkdir $DATASET_OUTPUT_DIR/ImageSets


##############################################
# Convert images one by one
count=1
NB_IMAGES=$(find $DATASET_DIR/VOC2007/JPEGImages -type f | wc -l)
CATEGORIES=(`cat $BUILDERS/VOC2007/categories.txt`)
for image in $DATASET_DIR/VOC2007/JPEGImages/*.jpg; do
  echo "Process image $count / $NB_IMAGES"
  
  image_base=$(basename ${image})
  
  if [ "$IMAGE_EXTENSION" = "png" ]; then mogrify -format png $image; fi
  mv "${image%.*}."$IMAGE_EXTENSION $DATASET_OUTPUT_DIR/Images/
  if [ "$DUPLICATE" = false ]; then rm $image; fi
  
  objects=$(xml_grep 'object' $DATASET_DIR/VOC2007/Annotations/"${image_base%.*}.xml")
  names=($(echo $objects | xml_grep 'name' --text_only))
  xmins=($(echo $objects | xml_grep 'xmin' --text_only))
  ymins=($(echo $objects | xml_grep 'ymin' --text_only))
  xmaxs=($(echo $objects | xml_grep 'xmax' --text_only))
  ymaxs=($(echo $objects | xml_grep 'ymax' --text_only))
  for i in `seq 0 $((${#names[@]}-1))`; do
    class=0
    for i in ${!CATEGORIES[@]}; do
      if [[ "${CATEGORIES[$i]}" == "${names[$i]}" ]]; then class=$(($i+1)); fi
    done
    
    annotation="$class ${xmins[$i]} ${ymins[$i]} ${xmaxs[$i]} ${ymaxs[$i]}"
    echo $annotation >> $DATASET_OUTPUT_DIR/Annotations/"${image_base%.*}.txt"
  done
  if [ "$DUPLICATE" = false ]; then rm "${image_base%.*}.xml"; fi
  
  count=$((count+1))
done


##############################################
# TODO: transfer the lists


##############################################
# Clean up
chmod -R 755 $DATASET_OUTPUT_DIR
if [ "$DUPLICATE" = false ]; then rm $DATASET_DIR; fi

