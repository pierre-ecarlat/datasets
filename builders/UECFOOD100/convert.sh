#!/bin/bash
# Expected format bash convert.sh path/to/dataset path/to/converted_dataset

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
ROOT="$EUID"
DATASET_DIR=$1
DATASET_OUTPUT_DIR=$2
BUILDERS=$DATASET_OUTPUT_DIR/../builders
NB_CATEGORIES=100


##############################################
# Invalid conditions
if [ ! -d $DATASET_DIR ]; then
  echo "Unable to find $DATASET_DIR."
  exit
fi


##############################################
# Main
if [ -d $DATASET_OUTPUT_DIR ]; then
  rm -r $DATASET_OUTPUT_DIR
fi

mkdir -m 755 $DATASET_OUTPUT_DIR
mkdir $DATASET_OUTPUT_DIR/Annotations
mkdir $DATASET_OUTPUT_DIR/Images
mkdir $DATASET_OUTPUT_DIR/ImageSets

for i in `seq 1 $NB_CATEGORIES`; do
  echo "Process category $i / $NB_CATEGORIES"
  
  SUB_DIR=$DATASET_DIR/$i
  mogrify -format png $SUB_DIR/*.jpg
  # if --clean; then rm $SUB_DIR/*.jpg; fi
  
  for image in $SUB_DIR/*.png; do
    mv $image $DATASET_OUTPUT_DIR/Images/
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
  # if --clean; then rm -r $SUB_DIR; fi
done

chmod -R 755 $DATASET_OUTPUT_DIR
# if --clean; then rm -r $DATASET_DIR; fi



