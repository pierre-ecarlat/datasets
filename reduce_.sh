#!/bin/bash
# Expected format: 
# ./scripts/reduce_.sh DATASET_NAME NB_CATEGS ORIG_CATEGS


##############################################
# Arguments
NB_ARGUMENTS_MIN=2
NB_ARGUMENTS_MAX=3
if [ $# -lt $NB_ARGUMENTS_MIN ]; then
  echo 1>&2 "$0: Not enough arguments."
  exit 2
elif [ $# -gt $NB_ARGUMENTS_MAX ]; then
  echo 1>&2 "$0: Too many arguments."
  exit 2
fi


##############################################
# General variables
DATASET_NAME=$1
NEW_NB_CATEGS=$2
if [ -z "$3" ]
then ORIG_CATEG_PATH=""
else ORIG_CATEG_PATH=$3
fi

PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN=$(readlink -m $PWD)
BUILDERS="$MAIN/builders"
SCRIPTS="$MAIN/scripts"

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
if [ ! -f $DATASET_DIR/.format ]; then
    echo "Unknown format."
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


FORMAT=`cat $DATASET_DIR/.format`
python $SCRIPTS/formats/reduce_$FORMAT.py \
                $DATASET_DIR \
                $OUTPUT_DIR \
                $REDUCTION_FILES_PATH \
                --prev_categs "$ORIG_CATEG_PATH"
cp $DATASET_DIR/.format $OUTPUT_DIR/

