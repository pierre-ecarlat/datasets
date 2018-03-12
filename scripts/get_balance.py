#!/usr/bin/env python

"""
Display the current balance of a dataset, based on a 
"""

# Auto-generated python class for protobuf formats
import os
import io
import argparse

import cv2
import numpy as np

# Extensions
E_IMG = '.jpg'
E_ANN = '.txt'
E_LIST = '.txt'

# General (TODO: shouldn't exist)
NB_CATEG = 21


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='The name of the dataset.')

    return parser.parse_args()


def getImagesList(paths):
    """Get the list of usable images"""
    filtered_list = []
    for f in os.listdir(paths['annotations']):
        annot = os.path.splitext(f)
        if annot[1] != E_ANN: continue
        if os.path.isfile(os.path.join(paths['images'], annot[0] + E_IMG)):
            filtered_list.append(os.path.splitext(f)[0])

    return filtered_list


def sumUpBoxesPerImage(paths, img_list):
    """Get the boxes of a list of images"""
    boxesPerImages = []
    for name in img_list:
        annot_path = os.path.join(paths['annotations'], name + E_ANN)
        image_boxes = [name]
        annotation = {
            # 'vocFormat': boxesVocFormat(annotation_path, paths['categories']),
            # 'tfRecords': boxesTfRecordsFormat(annotation_path),
        }[format]
        for box in annotation:
            image_boxes.append([int(float(b)) for b in box[:5]])
        boxesPerImages.append(image_boxes)

    return boxesPerImages


def categsPerImages(boxesPerImages):
    """Get the annotations from a list of boxes"""
    categsPerImages = []
    for img in boxesPerImages:
        image = [img[0]]
        for box in img[1:]:
            image.append(box[0])
        categsPerImages.append(image)
    return categsPerImages


def categsPerImagesDict(categsPerImages):
    """Converts to a dictionary categs / images"""
    categsPerImages_dict = {}
    for img in categsPerImages:
        categsPerImages_dict[img[0]] = img[1:]
    return categsPerImages_dict


def imagesPerCategs(categsPerImages):
    """Converts to a dictionary images / categs"""
    imagesPerCategs = []
    for i in range(NB_CATEG): imagesPerCategs.append([])
    for img in categsPerImages:
        for categ in img[1:]:
            imagesPerCategs[categ-1].append(img[0])
    return imagesPerCategs


def nbBoxesPerCateg(boxesPerImages):
    """Converts to a dictionary nb_boxes / categs"""
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
    
    # Check the format
    paths = { 'dataset': args.dataset }
    paths['format'] = os.path.join(paths['dataset'], ".format")
    format = [l.rstrip('\n') for l in open(paths['format'])][0]

    paths = {
        # 'vocFormat': voc_format.getPaths(paths),
        # 'tfRecords': tf_format.getPaths(paths),
    }[format]

    # Get the name of all the valid (annotated) images
    imgList = getImagesList(paths)

    # Get the number of boxes for each category
    boxesPerImages = sumUpBoxesPerImage(paths, imgList)

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
    for img in imagesPerCategs[sortedIndexes[0]]:
        for categ in categsPerImages_dict[img]:
            categ -= 1
            balanced_nbBoxesPerCateg[categ] += 1
        balanced_imagesList.append(img)
        categsPerImages_dict[img] = []
    imagesPerCategs[sortedIndexes[0]] = []

    while True in [nbBoxes < minNbBox for nbBoxes in balanced_nbBoxesPerCateg]:
        change = False
        for categ_idx in range(1, NB_CATEG):
            categ_to_balance = sortedIndexes[categ_idx]

            used_imgs = []
            for img in imagesPerCategs[categ_to_balance]:
                if balanced_nbBoxesPerCateg[categ_to_balance] >= minNbBox:
                    break
                if img in used_imgs:
                    continue

                used_imgs.append(img)
                for categ in categsPerImages_dict[img]:
                    categ -= 1
                    balanced_nbBoxesPerCateg[categ] += 1
                balanced_imagesList.append(img)
                categsPerImages_dict[img] = []
                change = True

            imagesPerCategs[categ_to_balance] = [img
                for img in imagesPerCategs[categ_to_balance]
                if not img in used_imgs]

        if not change:
            break

    # Get list of categories if exists
    categories = {}
    categs_file = os.path.join(paths['infos'], 'categories.txt')
    if os.path.isfile(categs_file):
        categs = [l.rstrip('\n') for l in open(categs_file)]
    else:
        categs = [str(x) for x in range(NB_CATEG)]
    for ix, categ in enumerate(categs):
        categories[ix] = categ


    # Display
    print 'Total number of annotated images:', len(categsPerImages)
    print 'Total number of bounding boxes over them:', sum(nbBoxesPerCateg)
    print 
    print 'Current balanced set:'
    print len(balanced_imagesList), 'images, with',
          sum(balanced_nbBoxesPerCateg), 'boxes'
    print 'Nb of boxes between', str(min(balanced_nbBoxesPerCateg)), 'and',
          str(max(balanced_nbBoxesPerCateg))
    print 'Standard deviation:', str(np.std(balanced_nbBoxesPerCateg))
    print 'Complete list:'
    print balanced_nbBoxesPerCateg
    print
    print 'Weakest to strongest categories (top and low 3):'
    for i in range(3):
        print '-', categories[sortedIndexes[i]], '->',
              str(balanced_nbBoxesPerCateg[sortedIndexes[i]]), 'boxes'
    print ' ', '...'
    for i in range(NB_CATEG-3, NB_CATEG):
        print '-', categories[sortedIndexes[i]], '->',
              str(balanced_nbBoxesPerCateg[sortedIndexes[i]]), 'boxes'
    print

    # Save the list of images
    yeses = ['Y', 'y', 'Yes', 'yes', 'YES']
    approval = raw_input('Keep this one? [y/N] > ') in yeses
    if approval:
        with open('output.txt', 'w') as f:
            f.write('\n'.join(balanced_imagesList))
        print 'Saved here, in the output.txt file'

    raise SystemExit
