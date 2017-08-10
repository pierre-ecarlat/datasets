#!/usr/bin/env python

"""
Display the current balance of a dataset, based on a 
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import io
import cv2
import numpy as np

# Extensions
E_IMG = '.jpg'
E_ANN = '.txt'
E_LIST = '.txt'

# General (TODO: shouldn't exist)
NB_CATEG = 67


def getArguments():
  """Defines and parses command-line arguments to this script."""
  parser = argparse.ArgumentParser()

  # Required arguments
  parser.add_argument('dataset', help='\
    The name of the dataset.')
  
  return parser.parse_args()


def getImagesList(dataset_path):
  images_dir = os.path.join(dataset_path, 'Images')
  annotations_dir = os.path.join(dataset_path, 'Annotations')
  all_txt_annotations = [os.path.splitext(f)[0] for f in os.listdir(annotations_dir) if f.endswith('.txt')]

  filtered_list = []
  for txt_annotation in all_txt_annotations:
    if os.path.isfile(os.path.join(images_dir, txt_annotation + E_IMG)):
      filtered_list.append(txt_annotation)

  return filtered_list


def sumUpBoxesPerImage(dataset_path, img_list):
  boxesPerImages = []
  for name in img_list:
    annotation_path = os.path.join(dataset_path, "Annotations", name + E_ANN)
    image_boxes = [name]
    annotation = [line.rstrip('\n').split() for line in open(annotation_path)]
    for box in annotation:
      image_boxes.append([int(float(b)) for b in box[:5]])
    boxesPerImages.append(image_boxes)

  return boxesPerImages


def categsPerImages(boxesPerImages):
  categsPerImages = []
  for img in boxesPerImages:
    image = [img[0]]
    for box in img[1:]:
      image.append(box[0])
    categsPerImages.append(image)
  return categsPerImages


def categsPerImagesDict(categsPerImages):
  categsPerImages_dict = {}
  for img in categsPerImages:
    categsPerImages_dict[img[0]] = img[1:]
  return categsPerImages_dict


def imagesPerCategs(categsPerImages):
  imagesPerCategs = []
  for i in range(NB_CATEG): imagesPerCategs.append([])
  for img in categsPerImages:
    for categ in img[1:]:
      imagesPerCategs[categ-1].append(img[0])
  return imagesPerCategs


def nbBoxesPerCateg(boxesPerImages):
  nbBoxesPerCateg = [0]*(NB_CATEG)
  for box in boxesPerImages:
    for element in box[1:]:
      nbBoxesPerCateg[int(element[0]) - 1] += 1
  return nbBoxesPerCateg

def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


if __name__ == "__main__":
  # Get the arguments
  args = getArguments()
  
  # Get the name of all the valid (annotated) images
  imgList = getImagesList(args.dataset)
  
  # Get the number of boxes for each category
  boxesPerImages = sumUpBoxesPerImage(args.dataset, imgList)
  
  # Get the categories found for each category
  categsPerImages = categsPerImages(boxesPerImages)
  categsPerImages_dict = categsPerImagesDict(categsPerImages)
  
  # Get the images for each category
  imagesPerCategs = imagesPerCategs(categsPerImages)
  
  # Get the number of boxes per category
  nbBoxesPerCateg = nbBoxesPerCateg(boxesPerImages)
  
  # Get the rank of each category
  sortedIndexes = argsort(nbBoxesPerCateg)

  # Minimal number of boxes over all the categories
  minNbBox = nbBoxesPerCateg[sortedIndexes[0]]



  # Create the balanced dataset
  balanced_nbBoxesPerCateg = [0]*(NB_CATEG)
  balanced_imagesList = []
  # Add all the images with the weakest category
  for ix, img in enumerate(imagesPerCategs[sortedIndexes[0]]):
    for ix2, categ in enumerate(categsPerImages_dict[img]):
      balanced_nbBoxesPerCateg[categ] += 1
      categsPerImages_dict[img].pop(ix2)
    balanced_imagesList.append(img)
    imagesPerCategs[sortedIndexes[0]].pop(ix)

  while True in [nbBoxes < minNbBox for nbBoxes in balanced_nbBoxesPerCateg]:
    change = False
    for categ_idx in range(1, NB_CATEG):
      categ_to_balance = sortedIndexes[categ_idx]
      
      for ix, img in enumerate(imagesPerCategs[categ_to_balance]):
        if balanced_nbBoxesPerCateg[categ_to_balance] >= minNbBox:
          break
        
        for ix2, categ in enumerate(categsPerImages_dict[img]):
          categ -= 1
          balanced_nbBoxesPerCateg[categ] += 1
          categsPerImages_dict[img].pop(ix2)
        balanced_imagesList.append(img)
        imagesPerCategs[categ_to_balance].pop(ix)
        change = True

    if not change:
      break

  # Get list of categories if exists
  categories = {}
  categs_file = os.path.join(args.dataset, 'infos', 'categories.txt')
  if os.path.isfile(categs_file):
    categs = [l.rstrip('\n') for l in open(categs_file)]
  else:
    categs = [str(x) for x in range(NB_CATEG)]
  for ix, categ in enumerate(categs):
    categories[ix] = categ

  
  # Display
  print 'Current balance:'
  print 'Minimum nb of boxes over the classes:', str(min(balanced_nbBoxesPerCateg))
  print 'Maximum nb of boxes over the classes:', str(max(balanced_nbBoxesPerCateg))
  print 'Standard deviation:', str(np.std(balanced_nbBoxesPerCateg))
  print
  print 'Weakest to strongest categories (top and low 3):'
  for i in range(3):
    print '-', categories[sortedIndexes[i]], '->', str(nbBoxesPerCateg[sortedIndexes[i]]), 'boxes'
  print ' ', '...'
  for i in range(NB_CATEG-3, NB_CATEG):
    print '-', categories[sortedIndexes[i]], '->', str(nbBoxesPerCateg[sortedIndexes[i]]), 'boxes'
  print

  # Save the list of images
  approval = raw_input('Keep this one? [y/N] > ') in ['Y', 'y', 'Yes', 'yes', 'YES']
  if approval:
    with open('output.txt', 'w') as f:
      f.write('\n'.join(balanced_imagesList))
    print 'Saved here, in the output.txt file'
  
  
  raise SystemExit
  
