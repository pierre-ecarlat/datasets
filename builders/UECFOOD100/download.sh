#!/bin/bash
# Expected format bash download.sh path/where/to/store

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
PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OUTPUT=$(readlink -f $1)
MAIN=$(readlink -m $OUTPUT/../..)
BUILDER=$MAIN/builders/${OUTPUT##*/}
TMP_DIR=$PWD/$(date +%d%H%M%S)


##############################################
# Main

if [ ! -d $OUTPUT ]; then
  mkdir -p $OUTPUT;
fi

mkdir $TMP_DIR && cd $TMP_DIR

echo "Download archives..."
wget http://foodcam.mobi/dataset100.zip

echo "Extract archives..."
unzip dataset100.zip -d $TMP_DIR/Food100

echo "Move the dataset to the output directory"
mv $TMP_DIR/Food100/UECFOOD100/* $OUTPUT

cd $PWD
rm -r $TMP_DIR


