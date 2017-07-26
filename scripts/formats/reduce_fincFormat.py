#!/usr/bin/env python

"""
Reduces the dataset to one with a lower number of categories. Example of use:
python reduce_dataset.py Foodinc Foodinc_reduced directory/where/is/transition.txt
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import io
import cv2
import shutil

# Extensions
E_IMG = '.jpg'
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
  parser.add_argument('--prev_categs', default="", help='\
    The path to the the original non-reduced categories.')
  
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
  orig_dataset = os.path.abspath(args.dataset_orig)
  dest_dataset = os.path.abspath(args.dataset_dest)
  
  # Output dataset
  os.makedirs(dest_dataset)
  imgs_orig = os.path.join(orig_dataset, "Images")
  imgs_dest = os.path.join(dest_dataset, "Images")
  sets_orig = os.path.join(orig_dataset, "ImageSets")
  sets_dest = os.path.join(dest_dataset, "ImageSets")
  os.symlink(imgs_orig, imgs_dest)
  os.makedirs(os.path.join(dest_dataset, "Annotations"))
  os.symlink(sets_orig, sets_dest)
  os.makedirs(os.path.join(dest_dataset, "infos"))
  
  # Transition matrix
  transition_lines = [l.rstrip('\n').split() for l in open(transition_path)]
  transition_dict = {}
  for line in transition_lines:
    transition_dict[line[0]] = line[1]

  # For each annotations 
  anns_list = os.listdir(os.path.join(args.dataset_orig, "Annotations"))
  for anns in anns_list:
    anns_orig_path = os.path.join(args.dataset_orig, "Annotations", anns)
    anns_dest_path = os.path.join(args.dataset_dest, "Annotations", anns)
    annotation = [line.rstrip('\n').split() for line in open(anns_orig_path)]
    for box in annotation:
      box[0] = transition_dict[box[0]]
    
    annotation_unsplit = [' '.join(str(e) for e in a) for a in annotation]
    with io.FileIO(anns_dest_path, "a") as file:
      file.write('\n'.join(annotation_unsplit))
  
  if os.path.isfile(categories_path):
    shutil.copy2(categories_path, os.path.join(args.dataset_dest, "infos"))
    
  raise SystemExit
  
