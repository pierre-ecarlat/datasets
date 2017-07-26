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
# TODO: relative paths vvvv
ROOT=$DATASET_DIR/..
BUILDERS=$ROOT/builders

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
  echo "The categories.txt file is needed in the builders."
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
mkdir $DATASET_OUTPUT_DIR/infos


##############################################
# Convert images one by one
count=1
NB_IMAGES=$(find $IMAGES_DIR -type f | wc -l)
CATEGORIES=(`cat $BUILDERS/VOC2007/categories.txt`)
for image in $IMAGES_DIR/*.jpg; do
  echo -ne "Process image $count / $NB_IMAGES\\r"
  
  image_base=$(basename ${image})
  
  if [ "$IMAGE_EXTENSION" = "png" ]; then 
    mogrify -format png $image
    mv "${image%.*}.png" $DATASET_OUTPUT_DIR/Images/
  else
    cp $image $DATASET_OUTPUT_DIR/Images/
  fi
  if [ "$DUPLICATE" = "false" ]; then rm $image; fi
  
  objects=$(xml_grep 'object' $ANNOTATIONS_DIR/"${image_base%.*}.xml")
  names=($(echo $objects | xml_grep 'name' --text_only))
  xmins=($(echo $objects | xml_grep 'xmin' --text_only))
  ymins=($(echo $objects | xml_grep 'ymin' --text_only))
  xmaxs=($(echo $objects | xml_grep 'xmax' --text_only))
  ymaxs=($(echo $objects | xml_grep 'ymax' --text_only))
  for i in `seq 0 $((${#names[@]}-1))`; do
    class=0
    for j in ${!CATEGORIES[@]}; do
      if [[ "${CATEGORIES[$j]}" == "${names[$i]}" ]]; then class=$(($j+1)); fi
    done
    
    annotation="$class ${xmins[$i]} ${ymins[$i]} ${xmaxs[$i]} ${ymaxs[$i]}"
    echo $annotation >> $DATASET_OUTPUT_DIR/Annotations/"${image_base%.*}.txt"
  done
  if [ "$DUPLICATE" = "false" ]; then rm $ANNOTATIONS_DIR/"${image_base%.*}.xml"; fi
  
  count=$((count+1))
done
echo


##############################################
# Transfer the lists
SETS=("train" "val" "trainval" "test")
for i in "${!SETS[@]}"; do
  if [ -f $IMAGESETS_DIR/${SETS[$i]}.txt ]; then
    cp $IMAGESETS_DIR/${SETS[$i]}.txt $DATASET_OUTPUT_DIR/ImageSets/
  else
    echo "No "${SETS[$i]}" found, skipped.. please make sure you won't need " \
         "it later. Note: you can generate them using scripts/generate_lists.py."
  fi
done
cp $BUILDERS/VOC2007/categories.txt $DATASET_OUTPUT_DIR/infos/
if [ -f $BUILDERS/VOC2007/colors.txt ]; then
  cp $BUILDERS/VOC2007/colors.txt $DATASET_OUTPUT_DIR/infos/
else
  echo "No colors.txt found in the builders. Not mandatory, but may improve " \
       "the visualization scripts (note: if you have the list of categories, you " \
       "can generate the colors using scripts/generate_colors.py)."
fi

##############################################
# Sign
echo "fincFormat" > $DATASET_OUTPUT_DIR/.format


##############################################
# Clean up
chmod -R 755 $DATASET_OUTPUT_DIR
if [ "$DUPLICATE" = "false" ]; then rm -r $DATASET_DIR; fi

