#!/bin/bash
# Expected format 
# ./builders/Foodinc/download.sh Foodinc

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
# TODO: relative paths vvvv
ROOT=$OUTPUT/..
BUILDERS=$ROOT/builders
SCRIPTS=$ROOT/scripts


##############################################
# Main
if [ ! -d $OUTPUT ]; then
  mkdir -p $OUTPUT;
fi

TMP_DIR=`date +%d%H%M%S`
mkdir $TMP_DIR
cd $TMP_DIR

echo "Find the dataset txt file to use (dataset_[number_images].txt)"
MAX_VERSION=0
DATASET_TXTS=($(ls -1 $BUILDERS/Foodinc/dataset_*.txt | # for all eligible files
                xargs -n1 basename |                    # extract the name only
                cut -d'_' -f2 |                         # extract the number only
                cut -d'.' -f1))                         # remove extension
for txt in ${DATASET_TXTS[@]}; do
  if [[ $MAX_VERSION -lt $txt ]]; then MAX_VERSION=$txt; fi
done
if [ ! -f $BUILDERS/Foodinc/dataset_$MAX_VERSION.txt ]; then
  echo "No dataset textfile, aborted."
  exit
fi

echo "Download images and create annotations"
export_me_that() {
  export PYTHONPATH=$PYTHONPATH:$SCRIPTS
}
export_me_that
python $BUILDERS/Foodinc/download_dataset.py \
              $BUILDERS/Foodinc/dataset_$MAX_VERSION.txt \
              Foodinc
if [ $(ls -p Foodinc/Images/ | grep -v / | wc -l) -eq 0 ]; then
  echo "Failed to download the dataset..."
  cd -
  rm -r $TMP_DIR
  exit
fi

cp $BUILDERS/Foodinc/categories.txt Foodinc/infos/
if [ -f $BUILDERS/Foodinc/colors.txt ]; then
  cp $BUILDERS/Foodinc/colors.txt Foodinc/infos/
else
  echo "No colors.txt found in the builders. Not mandatory, but may improve " \
       "the visualization scripts (note: if you have the list of categories, you " \
       "can generate the colors using scripts/generate_colors.py)."
fi

echo "Move the dataset to the output directory"
if [ ! -d $Foodinc ]; then
  mkdir -p $OUTPUT;
fi
mv Foodinc/* $OUTPUT

cd -
rm -r $TMP_DIR

