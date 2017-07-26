#!/bin/bash
# Expected format 
# ./builders/UECFOOD100/download.sh UECFOOD100

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
wget http://foodcam.mobi/dataset100.zip

echo "Extract archives..."
unzip dataset100.zip

echo "Move the dataset to the output directory"
mv UECFOOD100/* $OUTPUT

echo "Sign the dataset"
echo "uecFormat" > UECFOOD100/.format

cd -
rm -r $TMP_DIR


