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

echo "Find the dataset txt file"
max_dts_txt=0
DATASET_TXTS=($(ls -1 $BUILDER/dataset_* | xargs -n1 basename | cut -d'_' -f2 | cut -d'.' -f1))
for txt in ${DATASET_TXTS[@]}; do
  if [[ $max_dts_txt -lt $txt ]]; then max_dts_txt=$txt; fi
done
if [ ! -f $BUILDER/dataset_$max_dts_txt.txt ]; then
  echo "No dataset textfile, aborted."
  exit
fi

echo "Download images and create annotations"
mkdir $TMP_DIR
python $BUILDER/create_dataset.py $BUILDER/dataset_$max_dts_txt.txt $TMP_DIR/Foodinc
if [ $(ls -p $TMP_DIR/Foodinc/Images/ | grep -v / | wc -l) -eq 0 ]; then
  echo "Failed to download the dataset..."
  rm -r $TMP_DIR
  exit
fi

echo "Move the dataset to the output directory"
if [ ! -d $OUTPUT ]; then
  mkdir -p $OUTPUT;
fi
mv $TMP_DIR/Foodinc/* $OUTPUT

rm -r $TMP_DIR

