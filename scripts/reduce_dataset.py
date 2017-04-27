#!/usr/bin/env python

"""
Reduces the dataset to one with a lower number of categories. Example of use:
python reduce_dataset.py Foodinc Foodinc_reduced transition.txt
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import io
import cv2
import shutil

# Extensions
E_IMG = '.png'
E_ANN = '.txt'


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset_orig', help='\
    The directory with the dataset to reduce.')
    parser.add_argument('dataset_dest', help='\
    The directory where to save the reduced dataset.')
    parser.add_argument('path_to_reduce_files', help='\
    The path to the directory with the transition files for the conversion (transition.txt format: <old_categ> <new_categ>\\n).')
    
    return parser.parse_args()
    

if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Check conditions
    if not os.path.exists(args.dataset_orig):
        print "No dataset found (" + args.dataset_orig + ")."
        raise SystemExit
    if os.path.exists(args.dataset_dest):
        print "The destination dataset already exists (" + args.dataset_dest + ")."
        raise SystemExit
    if not os.path.exists(args.path_to_reduce_files):
        print "Can't find the directory with reducing files (" + args.path_to_reduce_files + "."
        raise SystemExit
    
    # Main files needed
    transition_path = os.path.join(args.path_to_reduce_files, "transition.txt")
    categories_path = os.path.join(args.path_to_reduce_files, "categories.txt")
    if not os.path.isfile(transition_path):
        print "Can't find " + transition_path + "."
        raise SystemExit
    
    # Output dataset
    os.makedirs(args.dataset_dest)
    imgs_orig = os.path.abspath(os.path.join(args.dataset_orig, "Images"))
    imgs_dest = os.path.abspath(os.path.join(args.dataset_dest, "Images"))
    sets_orig = os.path.abspath(os.path.join(args.dataset_orig, "ImageSets"))
    sets_dest = os.path.abspath(os.path.join(args.dataset_dest, "ImageSets"))
    os.symlink(imgs_orig, imgs_dest)
    os.makedirs(os.path.join(args.dataset_dest, "Annotations"))
    os.symlink(sets_orig, sets_dest)
    os.makedirs(os.path.join(args.dataset_dest, "infos"))
    
    # Transition matrix
    new_categs = [-1] * 256
    new_categs_lines = [line.rstrip('\n').split() for line in open(transition_path)]
    for transition in new_categs_lines:
        new_categs[int(transition[0])] = int(transition[1])
    while new_categs[-1] == -1: new_categs.pop()
    while new_categs[0]  == -1: new_categs.pop(0)
    
    # For each annotations 
    anns_list = os.listdir(os.path.join(args.dataset_orig, "Annotations"))
    for anns in anns_list:
        anns_orig_path = os.path.join(args.dataset_orig, "Annotations", anns)
        anns_dest_path = os.path.join(args.dataset_dest, "Annotations", anns)
        annotation = [line.rstrip('\n').split() for line in open(anns_orig_path)]
        for box in annotation:
            box[0] = new_categs[int(box[0]) - 1]
        
        annotation_unsplit = [' '.join(str(e) for e in a) for a in annotation]
        with io.FileIO(anns_dest_path, "a") as file:
            file.write('\n'.join(annotation_unsplit))
    
    if os.path.isfile(categories_path):
        shutil.copy2(transition_path, os.path.join(args.dataset_dest, "infos"))
        
    raise SystemExit
    
