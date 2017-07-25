#!/bin/bash
# Expected format: 
# ./scripts/reduce_.sh DATASET_NAME NB_CATEGS


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
DATASET_NAME=$1
NEW_NB_CATEGS=$2

ROOT="$EUID"
PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN=$(readlink -m $PWD/..)
BUILDERS="$MAIN/builders"

DATASET_DIR=$MAIN/$DATASET_NAME
OUTPUT_DIR=$MAIN/$DATASET_NAME"_"$NEW_NB_CATEGS"C"
REDUCTION_FILES_PATH=$BUILDERS"/"$DATASET_NAME"/reduction_to_"$NEW_NB_CATEGS
NEW_CATEGS_FILE=$REDUCTION_FILES_PATH"/categories.txt"
TRANSITION_FILE=$REDUCTION_FILES_PATH"/transition.txt"


##############################################
# Requirements
if [ ! -d $DATASET_DIR ]; then
    echo "The dataset $DATASET_NAME doesn't exist. Please download it first."
    exit 1
fi
if [ -d $OUTPUT_DIR ]; then
    echo "The reduced dataset $OUTPUT_DIR already exist."
    echo "> If you want to re-reduce it, simply remove $OUTPUT_DIR."
    exit 1
fi
if [ ! -d $REDUCTION_FILES_PATH ] || \
   [ ! -f $NEW_CATEGS_FILE      ] || \
   [ ! -f $TRANSITION_FILE      ]; then
    echo "Problem with the reduction files (no $REDUCTION_FILES_PATH directory? "
         "No categories.txt? No transition.txt?"
    exit 1
fi

##############################################
# Preparation
echo "-------------------------------------------"
echo "Create the $OUTPUT_DIR directory."
mkdir $OUTPUT_DIR
mkdir $OUTPUT_DIR/Annotations
mkdir $OUTPUT_DIR/infos

declare -A transitions_dict
while read p; do
  IFS=' ' read -ra VAL <<< "$p"
  if [ ${#VAL[@]} -eq 0 ]; then continue; fi
  transitions_dict+=( [${VAL[0]}]=${VAL[1]} )
done <$TRANSITION_FILE


##############################################
# Copy the images / sets and convert the annotations
echo "Conversion ..."
ln -s $DATASET_DIR/Images/ $OUTPUT_DIR/Images
ln -s $DATASET_DIR/ImageSets/ $OUTPUT_DIR/ImageSets

# Convert annotations one by one
for annotation in $DATASET_DIR/Annotations/*.txt; do
  while read p; do
    BB=()
    
    IFS=' ' read -ra VAL <<< "$p"
    for v in "${VAL[@]}"; do
      BB+=($v)
    done
    
    if [ ${#BB[@]} -eq 0 ]; then continue; fi
    
    CATEG=${transitions_dict[${BB[0]}]}
    COORDS="${BB[1]} ${BB[2]} ${BB[3]} ${BB[4]}"
    ANN_NAME=`basename $annotation`
    echo "$CATEG $COORDS" >> $OUTPUT_DIR/Annotations/$ANN_NAME    
  done <$annotation
done

cp $DATASET_DIR/infos/* $OUTPUT_DIR/infos/
cp $NEW_CATEGS_FILE $OUTPUT_DIR/infos/


