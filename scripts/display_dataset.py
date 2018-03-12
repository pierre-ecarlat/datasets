#!/usr/bin/env python

"""
Visualization of a dataset. Example of use:
python diplay_dataset.py Foodinc
"""

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
        The directory with the dataset (should have Images/, Annotations/).')

    # Optional arguments
    parser.add_argument('--colors', help='\
        The text file listing the colors of each class.')
    parser.add_argument('--categories', help='\
        The text file listing the categories.')

    return parser.parse_args()


def getVocInfos(paths):
    """
    Get the paths to the main directories / files, here based on a VOC
    architecture format.
    """
    paths['voc'] = os.path.join(paths['dataset'], "VOC2007")

    paths['images'] = osp.join(paths['voc'], "JPEGImages")
    paths['annotations'] = osp.join(paths['voc'], "Annotations")

    paths['infos'] = osp.join(paths['voc'], "infos")
    if osp.isfile(osp.join(paths['infos'], "colors.txt")):
        paths['colors'] = osp.join(paths['infos'], "colors.txt")
    if osp.isfile(osp.join(paths['infos'], "categories.txt")):
        paths['categories'] = osp.join(paths['infos'], "categories.txt")

    global E_ANN
    E_ANN = '.xml'

    return paths


def boxesVocFormat(file, categories_path):
    """
    Read the annotations of one image, for VOC, its an XML
    """
    categs_dict = {}
    categs_lines = [l.rstrip('\n') for l in open(categories_path)]
    for ix, line in enumerate(categs_lines):
        categs_dict[line] = ix+1

    annotation = []
    root = ET.parse(file).getroot()
    for obj in root.findall('object'):
        bb = obj.find('bndbox')
        annotation.append([str(categs_dict[obj.find('name').text]), 
                           bb.find('xmin').text, bb.find('ymin').text, 
                           bb.find('xmax').text, bb.find('ymax').text])
    return annotation


def assertVocRequirements(paths):
    """Requirements for VOC dataset."""
    assert os.path.isfile(paths['categories']),
        'Invalid categories file (' + paths_to_['categories'] + ')'


if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Check the format
    paths = { 'dataset': args.dataset }
    paths['format'] = os.path.join(paths['dataset'], ".format")
    format = [l.rstrip('\n') for l in open(paths['format'])][0]
    paths = {
        "vocFormat": getVocInfos(paths),
        # "tfRecords": getTfRecordsInfos(paths),
    }[format]

    # Get the colors of the classes
    colors = [(0,255,0) for _ in range(0,256)]
    if args.colors:
        paths['colors'] = args.colors
    if 'colors' in paths:
        colors_ = [line.rstrip('\n').split() for line in open(paths['colors'])]
        for i in range(0, len(colors_)):
            colors_[i] = [float(c) for c in colors_[i]]
            colors[i] = (colors_[i][0], colors_[i][1], colors_[i][2])

    # Get the categories
    categories = ["" for _ in range(0,256)]
    categories_path = None
    if args.categories:
        paths['categories'] = args.categories
    if 'categories' in paths:
        categories = [line.rstrip('\n') for line in open(paths['categories'])]

    # Requirements
    { 'vocFormat': assertVocRequirements(paths),
      # 'tfRecords': assertTfRecordsRequirements(paths),
    }[format]

    # For each image
    imgs_list = os.listdir(paths['images'])
    current_img = 0
    while True:
        # Get paths to this image / annotations
        image_name = osp.splitext(imgs_list[current_img])[0]
        image_path = osp.join(paths['images'], imgs_list[current_img])
        annotation_path = osp.join(paths['annotations'], image_name + E_ANN)
        if not (osp.isfile(image_path) and osp.isfile(annotation_path)):
            current_img += 1
            continue

        # Read the image and annotations
        cv2.namedWindow('input')
        cv2.moveWindow('input', 0, 0)
        image = cv2.imread(image_path)
        annotation = {
            'vocFormat': boxesVocFormat(annotation_path, paths['categories']),
            # 'tfRecords': boxesTfRecordsFormat(annotation_path),
        }[format]

        # Draw the boxes
        for box in annotation:
            if float(box[1]) < 1 and float(box[3]) <= 1:
                box[1] = float(box[1]) * image.shape[1]
                box[2] = float(box[2]) * image.shape[0]
                box[3] = float(box[3]) * image.shape[1]
                box[4] = float(box[4]) * image.shape[0]
            box = [int(b) for b in box]
            cv2.rectangle(image, (box[1], box[2]), (box[3], box[4]),
                          colors[box[0]-1], 2)
            cv2.putText(image, categories[box[0]-1], (box[1],box[2]+15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[box[0]-1], 1)

        # Key listener
        while True:
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
