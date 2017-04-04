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
NB_CATEGORIES=20


##############################################
# Invalid conditions
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
NB_IMAGES=$(find $DATASET_DIR/VOC2007/JPEGImages -type f | wc -l)
CATEGORIES=(`cat $BUILDERS/VOC2007/categories.txt`)
for image in $DATASET_DIR/VOC2007/JPEGImages/*.jpg; do
  echo "Process image $count / $NB_IMAGES"
  
  image_base=$(basename ${image})
  
  mogrify -format png $image
  mv "${image%.*}.png" $DATASET_OUTPUT_DIR/Images/
  # if --clean; then rm $image; fi
  
  objects=$(xml_grep 'object' $DATASET_DIR/VOC2007/Annotations/"${image_base%.*}.xml")
  names=($(echo $objects | xml_grep 'name' --text_only))
  xmins=($(echo $objects | xml_grep 'xmin' --text_only))
  ymins=($(echo $objects | xml_grep 'ymin' --text_only))
  xmaxs=($(echo $objects | xml_grep 'xmax' --text_only))
  ymaxs=($(echo $objects | xml_grep 'ymax' --text_only))
  for i in `seq 0 $((${#names[@]}-1))`; do
    class=0
    for i in ${!CATEGORIES[@]}; do
      if [[ "${CATEGORIES[$i]}" == "${names[$i]}" ]]; then class=$(($i+1)); fi
    done
    
    annotation="$class ${xmins[$i]} ${ymins[$i]} ${xmaxs[$i]} ${ymaxs[$i]}"
    echo $annotation >> $DATASET_OUTPUT_DIR/Annotations/"${image_base%.*}.txt"
  done
  # if --clean; then rm "${image_base%.*}.xml"; fi
  
  count=$((count+1))
done

chmod -R 755 $DATASET_OUTPUT_DIR
# if --clean; then rm -r $DATASET_DIR; fi



