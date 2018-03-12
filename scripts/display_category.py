#!/usr/bin/env python

"""
Visualization of a category. Example of use:
python diplay_category.py Voc2007 1
"""

import os
import argparse
import cv2

# Extensions
E_IMG = '.jpg'


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='\
      The directory with the dataset (should have Images/ and Annotations/).')
    parser.add_argument('category', type=int, help='\
      The category index to display.')
    
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

    # Get the categories
    categories = ["" for _ in range(0,256)]
    if 'categories' in paths:
        categories = [line.rstrip('\n') for line in open(paths['categories'])]
    
    # Get list of images
    relevant_boxes = []
    for annot_name in os.listdir(paths['annotations']):
        annot_path = os.path.join(paths['annotations'], annot_name)
        annotation = {
            # 'vocFormat': boxesVocFormat(annotation_path, paths['categories']),
            # 'tfRecords': boxesTfRecordsFormat(annotation_path),
        }[format]
        image_name = os.path.splitext(annot_name)[0]
        for box in annotation:
            box = [int(b) for b in box]
            if box[0] == category:
                relevant_boxes.append([image_name] + box[1:5])
    
    # For each image
    current_img = 0
    while True:
        box = relevant_boxes[current_img]
        image_path = os.path.join(paths['images'], box[0] + E_IMG)
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
