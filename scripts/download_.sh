#!/bin/bash
# Expected format: 
# ./scripts/download_.sh DATASET_NAME


##############################################
# Arguments
NB_ARGUMENTS_MIN=1
NB_ARGUMENTS_MAX=1
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
BUILDERS="$MAIN/builders"

DATASET_DIR=$MAIN/$DATASET_NAME


##############################################
# Requirements
if [ -d $DATASET_DIR ]; then
    echo "The dataset $DATASET_NAME already exists. No need to download it."
    echo "> If you want to re-download it, simply remove $DATASET_NAME."
    exit 1
fi
if [ ! -f $BUILDERS/$DATASET_NAME/download.sh ]; then
    echo -e "The dataset $DATASET_NAME doesn't have downloading instructions. "
    "Please add the $(basename $BUILDERS)/$DATASET_NAME/download.sh script."
    exit 1
fi


##############################################
# Preparation
echo "-------------------------------------------"
echo "Create the $DATASET_DIR directory."
mkdir $DATASET_DIR


##############################################
# Download the raw dataset
echo "Download ..."
bash $BUILDERS/$DATASET_NAME/download.sh $DATASET_DIR

