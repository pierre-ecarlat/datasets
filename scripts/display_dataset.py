#!/usr/bin/env python

"""
Visualization of a dataset. Example of use:
python diplay_dataset.py Foodinc
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import cv2

import xml.etree.ElementTree as ET

# Extensions
E_IMG = '.jpg'
E_ANN = ''


def getArguments():
  """Defines and parses command-line arguments to this script."""
  parser = argparse.ArgumentParser()

  # Required arguments
  parser.add_argument('dataset', help='\
    The directory with the dataset (should have Images/ and Annotations/).')
  
  # Optional arguments
  parser.add_argument('--colors', help='\
    The text file listing the colors of each class.')
  parser.add_argument('--categories', help='\
    The text file listing the categories.')
  
  return parser.parse_args()


def getFincInfos(paths_to_, dataset_path):
  infos_path = os.path.join(dataset_path, "infos")
  if os.path.isfile(os.path.join(infos_path, "colors.txt")):
    paths_to_['colors'] = os.path.join(infos_path, "colors.txt")
  if os.path.isfile(os.path.join(infos_path, "categories.txt")):
    paths_to_['categories'] = os.path.join(infos_path, "categories.txt")
  
  paths_to_['images'] = os.path.join(dataset_path, "Images")
  paths_to_['annotations'] = os.path.join(dataset_path, "Annotations")

  global E_ANN
  E_ANN = '.txt'

  return paths_to_


def getVocInfos(paths_to_, dataset_path):
  infos_path = os.path.join(dataset_path, "VOC2007", "infos")
  if os.path.isfile(os.path.join(infos_path, "colors.txt")):
    paths_to_['colors'] = os.path.join(infos_path, "colors.txt")
  if os.path.isfile(os.path.join(infos_path, "categories.txt")):
    paths_to_['categories'] = os.path.join(infos_path, "categories.txt")
  
  paths_to_['images'] = os.path.join(dataset_path, "VOC2007", "JPEGImages")
  paths_to_['annotations'] = os.path.join(dataset_path, "VOC2007", "Annotations")

  global E_ANN
  E_ANN = '.xml'
  
  return paths_to_


def boxesFincFormat(path):
  return [line.rstrip('\n').split() for line in open(path)]


def boxesVocFormat(path, categories_path):
  categs_dict = {}
  categs_lines = [l.rstrip('\n') for l in open(categories_path)]
  for ix, line in enumerate(categs_lines):
    categs_dict[line] = ix+1

  annotation = []
  root = ET.parse(path).getroot()
  for obj in root.findall('object'):
    bb = obj.find('bndbox')
    annotation.append([str(categs_dict[obj.find('name').text]), 
                       bb.find('xmin').text, bb.find('ymin').text, 
                        bb.find('xmax').text, bb.find('ymax').text])
  return annotation
  

if __name__ == "__main__":
  # Get the arguments
  args = getArguments()
  
  # Check the format
  format = [l.rstrip('\n') for l in open(os.path.join(args.dataset, ".format"))][0]

  paths_to_ = {
    'colors': '',
    'categories': '',
    'images': '',
    'annotations': '',
  }

  if format == "fincFormat":
    paths_to_ = getFincInfos(paths_to_, args.dataset)
  elif format == "vocFormat":
    paths_to_ = getVocInfos(paths_to_, args.dataset)
  elif format == "tfRecords":
    print "Format not implemented."
  else:
    print "Unknown format."
  
  # Get the colors of the classes
  colors = [(0,255,0) for _ in range(0,256)]
  colors_path = None
  if args.colors:
    paths_to_['colors'] = args.colors
  if paths_to_['colors'] and os.path.isfile(paths_to_['colors']):
    colors_ = [line.rstrip('\n').split() for line in open(colors_path)]
    for i in range(0, len(colors_)):
      colors_[i] = [float(c) for c in colors_[i]]
      colors[i] = (colors_[i][0], colors_[i][1], colors_[i][2])
  
  # Get the categories
  categories = ["" for _ in range(0,256)]
  categories_path = None
  if args.categories:
    paths_to_['categories'] = args.categories
  if paths_to_['categories'] and os.path.isfile(paths_to_['categories']):
    categories = [line.rstrip('\n') for line in open(paths_to_['categories'])]

  # Requirements
  if format == "fincFormat":
    pass
  elif format == "vocFormat":
    if not os.path.isfile(paths_to_['categories']):
      print "Invalid categories file (" + paths_to_['categories'] + ")"
      raise SystemExit
  elif format == "tfRecords":
    pass
  
  # For each image 
  imgs_list = os.listdir(paths_to_['images'])
  current_img = 0
  
  while (1):
    image_name = os.path.splitext(imgs_list[current_img])[0]
    image_path = os.path.join(paths_to_['images'], imgs_list[current_img])
    annotation_path = os.path.join(paths_to_['annotations'], image_name + E_ANN)
    if not (os.path.isfile(image_path) and os.path.isfile(annotation_path)):
      continue
    
    cv2.namedWindow('input')
    cv2.moveWindow('input', 0, 0)
    image = cv2.imread(image_path)

    annotation = ""
    if format == "fincFormat":
      annotation = boxesFincFormat(annotation_path)
    elif format == "vocFormat":
      annotation = boxesVocFormat(annotation_path, paths_to_['categories'])
    elif format == "tfRecords":
      print "Format not implemented."
    else:
      print "Unknown format."

    for box in annotation:
      if float(box[1]) < 1 and float(box[3]) <= 1:
        box[1] = float(box[1]) * image.shape[1]
        box[2] = float(box[2]) * image.shape[0]
        box[3] = float(box[3]) * image.shape[1]
        box[4] = float(box[4]) * image.shape[0]
      box = [int(b) for b in box]
      cv2.rectangle(image, (box[1],box[2]), (box[3],box[4]), colors[box[0]-1], 2)
      cv2.putText(image, categories[box[0]-1], (box[1],box[2]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[box[0]-1], 1)
    
    while (1):
      visu = cv2.imshow('input', image)
      k = cv2.waitKey(0)
      if k != 27 and k != 83 and k != 81: # Esc & right & left
        continue
      
      if k == 83 and current_img < len(imgs_list) - 1:
        current_img += 1
      elif k == 81 and current_img > 0:
        current_img -= 1
      
      cv2.destroyAllWindows()
      break
    
    if k == 27:
      break
    
  raise SystemExit
  
