#!/bin/bash
# Expected format bash get_.sh DATASET_NAME

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
DATASET_NAME=$1

ROOT="$EUID"
PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

MAIN=$(readlink -m $PWD/..)
SCRIPTS="$MAIN/scripts"
BUILDERS="$MAIN/builders"
ORIG="$MAIN/datasets_orig"

DATASET_ORIG_DIR=$ORIG/$DATASET_NAME
DATASET_CONV_DIR=$MAIN/$DATASET_NAME

LINK_TO=("/home/pierre/projects/food_detection/py-faster-rcnn/data/")


##############################################
# Preparation
if [ ! -d $ORIG ]; then
    echo "Create the datasets_orig directory."
    mkdir $ORIG
fi


##############################################
# Download the dataset
echo "-------------------------------------------"
if [ -d $DATASET_ORIG_DIR ]; then
    echo "The dataset $DATASET_NAME already exists in $(basename $ORIG). No need to download it again."
    echo "> If you want to re-download it, simply remove $(basename $ORIG)/$DATASET_NAME."
else
    echo "Will download $DATASET_NAME."
    bash $BUILDERS/$DATASET_NAME/download.sh $DATASET_ORIG_DIR
    if [ ! -d $DATASET_ORIG_DIR ]; then
        echo "Fail to download the dataset, aborted."
        exit
    fi
fi


##############################################
# Convert it
echo "-------------------------------------------"
if [ -d $DATASET_CONV_DIR ]; then
    echo "The dataset $DATASET_NAME already exists in $(basename $MAIN). No need to convert it again."
    echo "> If you want to convert it again, simply remove $(basename $MAIN)/$DATASET_NAME."
else
    echo "Will convert $DATASET_NAME."
    bash $BUILDERS/$DATASET_NAME/convert.sh $DATASET_ORIG_DIR $DATASET_CONV_DIR
fi


##############################################
# Complete the infos
echo "-------------------------------------------"
if [ -f $DATASET_CONV_DIR/infos/colors.txt ]; then
    echo -e "The dataset $DATASET_NAME already have colors, no need to create them."
else
    categories="$BUILDERS/$DATASET_NAME/categories.txt"
    if [ -f $categories ]; then
        echo "-------------------------------------------"
        echo "Will create the colors for $DATASET_NAME."
        python $SCRIPTS/generate_colors.py $DATASET_CONV_DIR $(cat $categories | wc -l)
        echo "Copy the categories for $DATASET_NAME."
        cp $categories $DATASET_CONV_DIR/infos/
    else
        echo "The file $DATASET_NAME/infos/categories.txt is missing in the builders.. You will have to add them manually to the dataset."
    fi
fi


##############################################
# Link it to concerning directories
for link in ${LINK_TO[@]}; do
    if [ -d $link ]; then
        if [ ! -f $link/$DATASET_NAME ]; then
            echo "Create a symbolic link to $DATASET_NAME in ${link}"
            ln -s $DATASET_CONV_DIR $link
        else
            echo "Symbolic link already exists, no need to create it again."
        fi
    fi
done


