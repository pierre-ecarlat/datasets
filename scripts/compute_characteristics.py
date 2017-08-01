#!/usr/bin/env python

"""
Computes the caracteristics of the dataset. Example of use:
python compute_caracteristics.py Foodinc --list test
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import io
import cv2

# Extensions
E_IMG = '.jpg'
E_ANN = '.txt'
E_LIST = '.txt'


def getArguments():
  """Defines and parses command-line arguments to this script."""
  parser = argparse.ArgumentParser()

  # Required arguments
  parser.add_argument('dataset', help='\
    The name of the dataset.')
  
  # Optional arguments
  parser.add_argument('--list', default="all", help='\
    The list of images (ImageSets/{all ; trainval ; test ; ... }.txt).')
  
  return parser.parse_args()


def createFincCaracts(dataset_path, list_name):
  # Check conditions
  list_path = os.path.join(dataset_path, "ImageSets", list_name + E_LIST)
  if not os.path.isfile(list_path):
    print "Can't find the file ImageSets/" + list_name + E_LIST
    return -1
  
  # Output directory
  output_dir = os.path.join(dataset_path, "ImageSets", "characteristics_" + list_name)
  if os.path.exists(output_dir):
    print "Caracteristics already computed in " + output_dir
    return 1
  os.makedirs(output_dir)
  
  # Global variables
  nb_images = sum(1 for line in open(list_path))
  nb_boxes = 0
  min_categ = 10000
  max_categ = -10000
  
  # Get list of images
  boxes = []
  names = [line.rstrip('\n') for line in open(list_path)]
  for name in names:
    image_path = os.path.join(dataset_path, "Images", name + E_IMG)
    annotation_path = os.path.join(dataset_path, "Annotations", name + E_ANN)
    
    image_boxes = []
    image_boxes.append(name)
    annotation = [line.rstrip('\n').split() for line in open(annotation_path)]
    for box in annotation:
      image_boxes.append([int(b) for b in box])
      if int(box[0]) > max_categ: max_categ = int(box[0])
      if int(box[0]) < min_categ: min_categ = int(box[0]) 
      nb_boxes += 1
    boxes.append(image_boxes)
  
  # Create categories_idx_per_image.txt file
  with open(os.path.join(output_dir, "categories_idx_per_image.txt"), "a") as f:
    for box in boxes:
      f.write(" ".join([row if isinstance(row, str) else str(row[0]) for row in box]) + "\n")
  
  # Create nb_images_per_category.txt file
  categs = [0]*(max_categ + 1 - min_categ)
  for box in boxes:
    for element in box:
      if isinstance(element, str): continue 
      categs[int(element[0]) - min_categ] += 1
  for categ in categs:
    with io.FileIO(os.path.join(output_dir, "nb_images_per_category.txt"), "a") as file:
      file.write(str(categ) + "\n")
  
  # Create nb_images_with_x_boxes.txt
  nb_images_with_x_boxes = [0]*(100)
  for box in boxes:
    nb_images_with_x_boxes[len(box) - 1] += 1
  while nb_images_with_x_boxes[-1] == 0: nb_images_with_x_boxes.pop()
  for x_boxes in nb_images_with_x_boxes:
    with io.FileIO(os.path.join(output_dir, "nb_images_with_x_boxes.txt"), "a") as file:
      file.write(str(x_boxes) + "\n")
  
  return 1
  

if __name__ == "__main__":
  # Get the arguments
  args = getArguments()
  
  # Check the format
  format = [l.rstrip('\n') for l in open(os.path.join(args.dataset, ".format"))][0]

  if format == "fincFormat":
    createFincCaracts(args.dataset, args.list)
  elif format == "vocFormat":
    print "Format not implemented."
  elif format == "tfRecords":
    print "Format not implemented."
  else:
    print "Unknown format."

  raise SystemExit
  
