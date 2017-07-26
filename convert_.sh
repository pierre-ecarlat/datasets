#!/bin/bash
# Expected format: 
# ./scripts/convert_.sh -d DATASET_NAME FORMAT_NAME

##############################################
# Arguments
DUPLICATE=false
while getopts :hd opt; do
    case $opt in 
        h) exit ;;
        d) DUPLICATE=true ;;
        :) echo "Missing argument for option -$OPTARG"; exit 1;;
       \?) echo "Unknown option -$OPTARG"; exit 1;;
    esac
done
shift $(( OPTIND - 1 ))

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
DATASET_NAME=`(basename $1)`
FORMAT_NAME=$2

PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN=$(readlink -m $PWD)
BUILDERS="$MAIN/builders"

DATASET_DIR=$MAIN/$DATASET_NAME


##############################################
# Requirements
if [ ! -d $DATASET_DIR ]; then
    echo "The dataset $DATASET_NAME doesn't exist. Please download it first."
    exit 1
fi
if [ ! -f $BUILDERS/$DATASET_NAME/convert_to_$FORMAT_NAME.sh ]; then
    echo -e "The dataset $DATASET_NAME doesn't have conversion instructions " \
    "for the format $FORMAT_NAME."
    "Please add a convert_to_$FORMAT_NAME.sh script in the builders."
    exit 1
fi


##############################################
# Download the raw dataset
echo "Convert the dataset $DATASET_NAME to the $FORMAT_NAME format " \
"(Duplicate? $DUPLICATE) ..."
if [ "$DUPLICATE" = "false" ]; then
  echo "This operation will erase the current dataset to replace it by the " \
          "converted new one (may lose some data depending on the conversion). " \
          "(If you have enough place on your computer, consider the -d option)."
  read -p "Pursue anyway? [y/N] " -r
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Let's convert!"
  else
    exit 1
  fi
fi

bash $BUILDERS/$DATASET_NAME/convert_to_$FORMAT_NAME.sh $DATASET_DIR $DUPLICATE
