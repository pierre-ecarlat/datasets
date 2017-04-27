#!/usr/bin/env python

"""
Visualization of a dataset. Example of use:
python diplay_dataset.py Foodinc
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import cv2

# Extensions
E_IMG = '.png'
E_ANN = '.txt'


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
    

if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Get the colors of the classes
    colors = [(0,255,0) for _ in range(0,256)]
    colors_path = None
    if os.path.isfile(os.path.join(args.dataset, "infos", "colors.txt")):
        colors_path = os.path.join(args.dataset, "infos", "colors.txt")
    if args.colors:
        colors_path = args.colors
    if colors_path:
        colors_ = [line.rstrip('\n').split() for line in open(colors_path)]
        for i in range(0,len(colors_)):
            colors_[i] = [float(c) for c in colors_[i]]
            colors[i] = (colors_[i][0], colors_[i][1], colors_[i][2])
    
    # Get the categories
    categories = ["" for _ in range(0,256)]
    categories_path = None
    if os.path.isfile(os.path.join(args.dataset, "infos", "categories.txt")):
        categories_path = os.path.join(args.dataset, "infos", "categories.txt")
    if args.categories:
        categories_path = args.categories
    if categories_path:
        categories = [line.rstrip('\n') for line in open(categories_path)]
    
    # For each image 
    imgs_list = os.listdir(os.path.join(args.dataset, "Images"))
    current_img = 0
    
    while (1):
        image_name = os.path.splitext(imgs_list[current_img])[0]
        image_path = os.path.join(args.dataset, "Images", imgs_list[current_img])
        annotation_path = os.path.join(args.dataset, "Annotations", image_name + E_ANN)
        if not (os.path.isfile(image_path) and os.path.isfile(annotation_path)):
          continue
        
        cv2.namedWindow('input')
        cv2.moveWindow('input', 0, 0)
        image = cv2.imread(image_path)
        annotation = [line.rstrip('\n').split() for line in open(annotation_path)]
        for box in annotation:
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
    
