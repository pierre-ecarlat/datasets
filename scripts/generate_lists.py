#!/usr/bin/env python

"""
Generate trainval.txt test.txt, train.txt and val.txt using given proportions. Example of use:
python generate_lists.py Foodinc 0.8
"""

# Auto-generated python class for protobuf formats
import argparse
import io
import numpy as np
import random
import os


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='\
    The directory with the dataset.')
    parser.add_argument('proportion', type=float, help='\
    The proportion for the dataset, between 0 and 1. 0.8 would create a trainval.txt \
    with 80% of the images, and the train.txt with 80% of the train_val images.')
    
    return parser.parse_args()
    

if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Get main directory
    dir_lists = os.path.join(args.dataset, "ImageSets") + "/"
    
    # Get the list of images
    if not os.path.exists(dir_lists + "all.txt"):
        print ("ImageSets/all.txt is missing.. Please compute it.")
    
    images = open(dir_lists + "all.txt").readlines()
    random.shuffle(images)
    
    # Split it
    nb_images   = len(images)
    nb_trainval = int(nb_images   * args.proportion)
    nb_train    = int(nb_trainval * args.proportion)
    i_trainval = images[:nb_trainval]
    i_test     = images[nb_trainval:]
    i_train    = i_trainval[:nb_train]
    i_val      = i_trainval[nb_train:]
    
    # Write lists
    open(dir_lists + "trainval.txt", 'w').writelines(np.sort(i_trainval))
    open(dir_lists + "test.txt"    , 'w').writelines(np.sort(i_test))
    open(dir_lists + "train.txt"   , 'w').writelines(np.sort(i_train))
    open(dir_lists + "val.txt"     , 'w').writelines(np.sort(i_val))
    
