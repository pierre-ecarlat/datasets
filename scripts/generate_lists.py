#!/usr/bin/env python

"""
Generate trainval.txt test.txt, train.txt and val.txt using given 
proportions. Example of use:
python scripts/generate_lists.py Foodinc \
                --in all                 \
                --out1 trainval          \
                --out2 test              \
                --proportion 0.8
TODO: WARNING: old code, I haven't cehck all the possible situations, 
may create some irrelevant lists, double check
"""

# Auto-generated python class for protobuf formats
import argparse
import io
import numpy as np
import random
import os
#import compute_characteristics as cc


def getArguments():
  """Defines and parses command-line arguments to this script."""
  parser = argparse.ArgumentParser()

  # Required arguments
  parser.add_argument('dataset', help='\
    The directory with the dataset.')
  parser.add_argument('--inp', default='all', help='\
    The input set to use (default: all).')
  parser.add_argument('--out1', default='trainval', help='\
    The name of the first output set (default: trainval).')
  parser.add_argument('--out2', default='test', help='\
    The name of the first output set (default: test).')
  parser.add_argument('--proportion', default=0.8, type=float, help='\
    The proportion for the dataset, between 0 and 1 (defaut: 0.8).')
  
  return parser.parse_args()


def getFincInfos(paths_to_, dataset_path):
  paths_to_['image_sets'] = os.path.join(dataset_path, "ImageSets")
  paths_to_['characts'] = os.path.join(dataset_path, "ImageSets", "characteristics_")
  return paths_to_


def getVocInfos(paths_to_, dataset_path):
  paths_to_['image_sets'] = os.path.join(dataset_path, "VOC2007", "ImageSets", "Main")
  paths_to_['characts'] = os.path.join(dataset_path, "VOC2007", "ImageSets", "Main", "characteristics_")
  return paths_to_
  

if __name__ == "__main__":
  # Get the arguments
  args = getArguments()
  
  # Check the format
  format = [l.rstrip('\n') for l in open(os.path.join(args.dataset, ".format"))][0]

  paths_to_ = {
    'image_sets': '',
    'characts': '',
  }

  if format == "fincFormat":
    paths_to_ = getFincInfos(paths_to_, args.dataset)
  elif format == "vocFormat":
    paths_to_ = getVocInfos(paths_to_, args.dataset)
  elif format == "tfRecords":
    print "Format not implemented."
  else:
    print "Unknown format."
  
  # Get the list of images
  if not os.path.exists(os.path.join(paths_to_['image_sets'], args.inp + ".txt")):
    print (args.inp + ".txt is missing.. Please compute it.")
    raise SystemExit
  
  # Create the caracteristics if not created
  if not os.path.exists(paths_to_['characts'] + args.inp):
    compute_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                'compute_characteristics.py')
    os.system(' '.join(['python', compute_path, args.dataset, 
                        '--list', args.inp]))
  if not os.path.exists(paths_to_['characts'] + args.inp):
    print "Failed to compute the characteristics."
    raise SystemExit
  
  # Get caracteristics directory
  dir_characts = paths_to_['characts'] + args.inp
  
  # Create the output_categ_distrib_idxes.txt
  nipc = [line.rstrip('\n') for line in open(os.path.join(dir_characts, "nb_images_per_category.txt"))]
  nipc_sorted_idx = sorted(range(len(nipc)), key=lambda k: int(nipc[k]))

  # Create the output_categ_idxes.txt
  cipi = [line.rstrip('\n') for line in open(os.path.join(dir_characts, "categories_idx_per_image.txt"))]
  cipi_used = [False] * len(cipi)
  
  # Creates the sets
  out1 = ""
  out2 = ""
  # For each line in output_categ_distrib_idxes.txt
  for curr_categ in nipc_sorted_idx:
    list_img = []
    for j in range(len(cipi)):
      if not cipi_used[j]:
        curr_cipi = cipi[j].split()
        if str(int(curr_categ)+1) in curr_cipi[1:]: 
          list_img.append(curr_cipi[0])
          cipi_used[j] = True
    
    fp = int(len(list_img) * args.proportion)
    for j in range(0, fp):
      out1 += list_img[j] + "\n"
    for j in range(fp, len(list_img)):
      out2 += list_img[j] + "\n"

  # Write results
  out1 = out1[:-1]
  out2 = out2[:-1]
  open(os.path.join(paths_to_['image_sets'], args.out1 + ".txt"), 'w').writelines(out1)
  open(os.path.join(paths_to_['image_sets'], args.out2 + ".txt"), 'w').writelines(out2)
  
