#!/bin/bash
# Expected format 
# ./builders/UECFOOD100/convert_to_fincFormat.sh false

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
for i in `seq 1 $NB_CATEGORIES`; do
  echo -ne "Process category $i / $NB_CATEGORIES\\r"

  SUB_DIR=$DATASET_DIR/$i
  for image in $SUB_DIR/*.jpg; do
    if [ "$IMAGE_EXTENSION" = "png" ]; then 
      mogrify -format png $image
      mv "${image%.*}."$IMAGE_EXTENSION $DATASET_OUTPUT_DIR/Images/
    else 
      cp $image $DATASET_OUTPUT_DIR/Images/
    fi
    if [ "$DUPLICATE" = false ]; then rm $image; fi
  done
  
  while read p; do
    BB=()
    
    IFS=' ' read -ra VAL <<< "$p"
    for v in "${VAL[@]}"; do
      if [ "$v" == "img" ]; then break; fi
      BB+=($v)
    done
    
    if [ ${#BB[@]} -eq 0 ]; then continue; fi
    
    COORDS="${BB[1]} ${BB[2]} ${BB[3]} ${BB[4]}"
    echo "$i $COORDS" >> $DATASET_OUTPUT_DIR/Annotations/${BB[0]}.txt
    
  done <$SUB_DIR/bb_info.txt
  if [ "$DUPLICATE" = false ]; then rm -r $SUB_DIR; fi
done
echo


##############################################
# Transfer the lists
cp $BUILDERS/UECFOOD100/categories.txt $DATASET_OUTPUT_DIR/infos/
if [ -f $BUILDERS/UECFOOD100/colors.txt ]; then
  cp $BUILDERS/UECFOOD100/colors.txt $DATASET_OUTPUT_DIR/infos/
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
if [ "$DUPLICATE" = false ]; then rm -r $DATASET_DIR; fi



