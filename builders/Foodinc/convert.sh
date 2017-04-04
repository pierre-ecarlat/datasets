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
NB_ANNOTATIONS=$(ls -1q $DATASET_DIR/Annotations/* | wc -l)
NB_CATEGORIES=67


##############################################
# Invalid conditions
if [ ! -d $DATASET_DIR ]; then
  echo "Unable to find $DATASET_DIR."
  exit
fi


##############################################
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


count=1
for annotation in $DATASET_DIR/Annotations/*.txt; do
  echo "Process image $count / $NB_ANNOTATIONS"
  
  FILENAME=$(basename $annotation)
  
  while read p; do
    BB=()
    
    IFS=' ' read -ra VAL <<< "$p"
    for v in "${VAL[@]}"; do
      BB+=($v)
    done
    
    if [ ${#BB[@]} -eq 0 ]; then continue; fi
    
    COORDS="$((${BB[0]}+1)) ${BB[2]} ${BB[3]} ${BB[4]} ${BB[5]}"
    echo "$COORDS" >> $DATASET_OUTPUT_DIR/Annotations/$FILENAME
    
  done <$annotation
  # if --clean; then rm -r $annotation; fi
  
  cp $DATASET_DIR/Images/${FILENAME%.*}.png $DATASET_OUTPUT_DIR/Images/
  # if --clean; then rm -r $DATASET_DIR/Images/${FILENAME%.*}.png; fi
  
  count=$((count+1))
done

chmod -R 755 $DATASET_OUTPUT_DIR
# if --clean; then rm -r $DATASET_DIR; fi


