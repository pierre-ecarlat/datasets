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

import xml.etree.ElementTree as ET


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
  for path in [transition_path, categories_path, args.prev_categs]:
    if not os.path.isfile(path):
      print "Can't find " + path + "."
      raise SystemExit

  # Output dataset
  orig_dataset = os.path.abspath(args.dataset_orig)
  dest_dataset = os.path.abspath(args.dataset_dest)
  os.makedirs(dest_dataset)
  os.makedirs(os.path.join(dest_dataset, "VOC2007"))
  imgs_orig = os.path.join(orig_dataset, "VOC2007", "JPEGImages")
  imgs_dest = os.path.join(dest_dataset, "VOC2007", "JPEGImages")
  sets_orig = os.path.join(orig_dataset, "VOC2007", "ImageSets")
  sets_dest = os.path.join(dest_dataset, "VOC2007", "ImageSets")
  os.symlink(imgs_orig, imgs_dest)
  os.makedirs(os.path.join(dest_dataset, "VOC2007", "Annotations"))
  os.symlink(sets_orig, sets_dest)

  # Categories
  old_categories = [l.rstrip('\n') for l in open(args.prev_categs)]
  new_categories = [l.rstrip('\n') for l in open(categories_path)]

  # Transition matrix
  transition_lines = [l.rstrip('\n').split() for l in open(transition_path)]
  transition_dict = {}
  for line in transition_lines:
    transition_dict[old_categories[int(line[0])-1]] = new_categories[int(line[1])-1]
  
  # For each annotations 
  anns_list = os.listdir(os.path.join(orig_dataset, "VOC2007", "Annotations"))
  for anns in anns_list:
    anns_orig_path = os.path.join(orig_dataset, "VOC2007", "Annotations", anns)
    anns_dest_path = os.path.join(dest_dataset, "VOC2007", "Annotations", anns)

    tree = ET.parse(anns_orig_path)
    root = tree.getroot()

    for obj in root.findall('object'):
      name = obj.find('name')
      prev_name = name.text
      name.text = transition_dict[prev_name]

    tree.write(anns_dest_path)

  raise SystemExit
    
