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
import compute_caracteristics as cc


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='\
    The directory with the dataset.')
    parser.add_argument('proportion', default=0.8, type=float, help='\
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
    
    # Create the caracteristics
    if cc.createCaracts(args.dataset, "all") == -1:
        raise SystemExit
    
    # Get caracteristics directory
    dir_caracts = os.path.join(dir_lists, "caracteristics_all") + "/"
    
    # Create the output_categ_distrib_idxes.txt
    nipc = open(dir_caracts + "nb_images_per_category.txt").readlines()
    nipc_sorted_idx = sorted(range(len(nipc)), key=lambda k: int(nipc[k][:-1]), reverse=True)
    # Create the output_categ_idxes.txt
    cipi = open(dir_caracts + "categories_idx_per_image.txt").readlines()
    cipi_used = [False] * len(cipi)
    
    trainval = ""
    test = ""
    # for line in output_categ_distrib_idxes.txt
    for categ_idx in range(len(nipc)):
        curr_categ = nipc_sorted_idx[categ_idx] + 1
        list_img = []
        for j in range(len(cipi)):
            if not cipi_used[j]:
                curr_cipi = cipi[j].split()
                if str(curr_categ) in curr_cipi[1:]: 
                    list_img.append(curr_cipi[0])
                    cipi_used[j] = True
        
        eighty = int(len(list_img) * 0.8)
        for j in range(0, eighty):
            trainval += list_img[j] + "\n"
        for j in range(eighty, len(list_img)):
            test += list_img[j] + "\n"
    
    trainval = trainval[:-1]
    test = test[:-1]
    open(dir_lists + "trainval.txt", 'w').writelines(trainval)
    open(dir_lists + "test.txt"    , 'w').writelines(test)
    
    
    
