#!/bin/bash
# Expected format 
# ./builders/VOC2007/download.sh VOC2007

##############################################
# Arguments
NB_ARGUMENTS=1
if [ $# -lt $NB_ARGUMENTS ]; then
  echo 1>&2 "$0: Not enough arguments (should be $NB_ARGUMENTS)."
  exit 2
elif [ $# -gt $NB_ARGUMENTS ]; then
  echo 1>&2 "$0: Too many arguments (should be $NB_ARGUMENTS)."
  exit 2
fi


##############################################
# General variables
OUTPUT=$1


##############################################
# Main
if [ ! -d $OUTPUT ]; then
  mkdir -p $OUTPUT;
fi

TMP_DIR=`date +%d%H%M%S`
mkdir $TMP_DIR
cd $TMP_DIR

echo "Download archives..."
wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar
wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtest_06-Nov-2007.tar
wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar

echo "Extract archives..."
tar xvf VOCtrainval_06-Nov-2007.tar
tar xvf VOCtest_06-Nov-2007.tar
tar xvf VOCdevkit_08-Jun-2007.tar

echo "Move the dataset to the output directory"
mv VOCdevkit/* $OUTPUT

cd -
rm -r $TMP_DIR

