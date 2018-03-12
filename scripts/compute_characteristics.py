#!/usr/bin/env python

"""
Computes the caracteristics of the dataset. Example of use:
python compute_caracteristics.py Voc2007 --list test
"""

import os
import io
import argparse
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
        The directory with the dataset (should have Images/, Annotations/).')
  
    # Optional arguments
    parser.add_argument('--list', default="all", help='\
        The list of images (ImageSets/{all ; trainval ; test ; ... }.txt).')
    
    return parser.parse_args()
  

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

    # Check conditions
    paths['list'] = os.path.join(paths['image_sets'], args.list + E_LIST)
    assert os.path.isfile(paths['list']), \
        'Cant find the file ImageSets/' + paths['list']

    # Output directory
    output_dirname = "characteristics_" + args.list
    paths['outputs'] = os.path.join(paths['image_sets'], output_dirname)
    assert not os.path.exists(paths['outputs']), \
        'Caracteristics already computed in ' + output_dirname
    os.makedirs(paths['outputs'])

    # Global variables
    nb_images = len(open(paths['list']))
    nb_boxes = 0
    min_categ = 10000
    max_categ = -10000
    
    # Get list of images
    boxes = []
    names = [line.rstrip('\n') for line in open(list_path)]
    for name in names:
        image_path = os.path.join(paths['images'], name + E_IMG)
        annotation_path = os.path.join(paths['annotations'], name + E_ANN)
        
        image_boxes = []
        image_boxes.append(name)
        annotation = {
            # 'vocFormat': boxesVocFormat(annotation_path, paths['categories']),
            # 'tfRecords': boxesTfRecordsFormat(annotation_path),
        }[format]
        for box in annotation:
            image_boxes.append([int(float(b)) for b in box])
            if int(float(box[0])) > max_categ: max_categ = int(float(box[0]))
            if int(float(box[0])) < min_categ: min_categ = int(float(box[0])) 
            nb_boxes += 1
        boxes.append(image_boxes)
    
    # Create categories_idx_per_image.txt file
    paths['categ_per_images'] = os.path.join(paths['outputs'],
                                             "categories_idx_per_image.txt")
    with open(paths['categ_per_images'], "a") as f:
        f.write('\n'.join([' '.join([row if isinstance(r, str) else str(r[0])
                                     for r in box])
                                     for box in boxes]))

    # Create nb_images_per_category.txt file
    paths['nbimg_per_categs'] = os.path.join(paths['outputs'],
                                             "nb_images_per_category.txt")
    categs = [0]*(max_categ + 1 - min_categ)
    for box in boxes:
        for element in box:
            if isinstance(element, str): continue 
            categs[int(element[0]) - min_categ] += 1
    for categ in categs:
        with io.FileIO(paths['nbimg_per_categs'], "a") as file:
            file.write(str(categ) + "\n")
    
    # Create nb_images_with_x_boxes.txt
    paths['nbimg_with'] = os.path.join(paths['outputs'],
                                       "nb_images_with_x_boxes.txt")
    nb_images_with_x_boxes = [0]*(100)
    for box in boxes:
        nb_images_with_x_boxes[len(box) - 1] += 1
    while nb_images_with_x_boxes[-1] == 0: nb_images_with_x_boxes.pop()
    for x_boxes in nb_images_with_x_boxes:
        with io.FileIO(paths['nbimg_with'], "a") as file:
            file.write(str(x_boxes) + "\n")
