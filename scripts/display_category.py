#!/usr/bin/env python

"""
Visualization of a category. Example of use:
python diplay_category.py Foodinc 1
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import cv2

# Extensions
E_IMG = '.jpg'
E_ANN = '.txt'


def getArguments():
  """Defines and parses command-line arguments to this script."""
  parser = argparse.ArgumentParser()

  # Required arguments
  parser.add_argument('dataset', help='\
    The directory with the dataset (should have Images/ and Annotations/).')
  parser.add_argument('category', type=int, help='\
    The category to display.')
  
  return parser.parse_args()


def displayFincCategory(dataset_path, category):
  # Get the categories
  categories = ["" for _ in range(0,256)]
  categories_path = None
  if os.path.isfile(os.path.join(dataset_path, "infos", "categories.txt")):
    categories_path = os.path.join(dataset_path, "infos", "categories.txt")
  if categories_path:
    categories = [line.rstrip('\n') for line in open(categories_path)]
  
  # Get list of images
  relevant_boxes = []
  for annotation_name in os.listdir(os.path.join(dataset_path, "Annotations")):
    annotation_path = os.path.join(dataset_path, "Annotations", annotation_name)
    annotation = [line.rstrip('\n').split() for line in open(annotation_path)]
    image_name = os.path.splitext(annotation_name)[0]
    for box in annotation:
      box = [int(b) for b in box]
      if box[0] == category:
        relevant_boxes.append( [image_name, box[1], box[2], box[3], box[4]] )
  
  current_img = 0
  while (1):
    box = relevant_boxes[current_img]
    image_path = os.path.join(dataset_path, "Images", box[0] + E_IMG)
    image = cv2.imread(image_path)
    cropped_image = image[box[2]:box[4], box[1]:box[3]]
    
    while (1):
      visu = cv2.imshow(box[0], cropped_image)
      k = cv2.waitKey(0)
      if k != 27 and k != 83 and k != 81: # Esc & right & left
        continue
      
      if k == 83 and current_img < len(relevant_boxes) - 1:
        current_img += 1
      elif k == 81 and current_img > 0:
        current_img -= 1
      
      cv2.destroyAllWindows()
      break
    
    if k == 27:
      break
  

if __name__ == "__main__":
  # Get the arguments
  args = getArguments()
  
  # Check the format
  format = [l.rstrip('\n') for l in open(os.path.join(args.dataset, ".format"))][0]

  if format == "fincFormat":
    displayFincCategory(args.dataset, args.category)
  elif format == "vocFormat":
    print "Format not implemented."
  elif format == "tfRecords":
    print "Format not implemented."
  else:
    print "Unknown format."
    
  raise SystemExit
  
