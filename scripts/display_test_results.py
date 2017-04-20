#!/usr/bin/env python

"""
Visualization of the test results. Example of use:
python display_test_results.py Foodinc path/to/test_results/ 
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import cv2
import numpy as np

# Extensions
E_IMG = '.png'
E_ANN = '.txt'


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='\
    The directory with the dataset (should have Images/ and Annotations/).')
    parser.add_argument('test_results_dir', help='\
    The directory with the results.')
    parser.add_argument('threshold', default=0.3, help='\
    The threshold for vcisualization, between 0 and 1, 0.3 is the default value.')
    
    return parser.parse_args()
    

if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Get the colors of the classes
    colors = [(0,255,0) for _ in range(0,256)]
    colors_path = None
    if os.path.isfile(os.path.join(args.dataset, "infos", "colors.txt")):
        colors_path = os.path.join(args.dataset, "infos", "colors.txt")
        colors_ = [line.rstrip('\n').split() for line in open(colors_path)]
        for i in range(0,len(colors_)):
            colors_[i] = [float(c) for c in colors_[i]]
            colors[i] = (colors_[i][0], colors_[i][1], colors_[i][2])
    
    # Get the categories
    categories = ["" for _ in range(0,256)]
    categories_path = None
    if os.path.isfile(os.path.join(args.dataset, "infos", "categories.txt")):
        categories_path = os.path.join(args.dataset, "infos", "categories.txt")
        categories = [line.rstrip('\n') for line in open(categories_path)]
    
    # For each image 
    imgs_list = os.listdir(os.path.join(args.dataset, "Images"))
    current_img = 0
    
    # For each result file
    all_annotations = []
    list_results = os.listdir(args.test_results_dir)
    for res in list_results:
        categ = int(res.split('_det_test_')[1].split('.')[0])
        results_detail = [line.rstrip('\n').split() for line in open(os.path.join(args.test_results_dir, res))]
        for box in results_detail:
            box = [float(b) for b in box]
            all_annotations.append([int(box[0]), categ, box[1], box[2], box[3], box[4], box[5]])
    
    np_anns = np.array(all_annotations)
    np_anns = np_anns[np.argsort(np_anns[:,0])]
    
    all_images = []
    for ann in np_anns:
        if not all_images or all_images[-1][0] != ann[0]:
            all_images.append([ann[0], []])
        all_images[-1][1].append([int(ann[1]), ann[2], int(ann[3]), int(ann[4]), int(ann[5]), int(ann[6])])
    
    # Display all images
    current_img = 0
    while (1):
        image_name = str(int(all_images[current_img][0]))
        image_path = os.path.join(args.dataset, "Images", image_name + E_IMG)
        if not os.path.isfile(image_path):
            current_img += 1
            continue
        
        cv2.namedWindow('input')
        cv2.moveWindow('input', 0, 0)
        image = cv2.imread(image_path)
        for box in all_images[current_img][1]:
            if box[1] > float(args.threshold):
                cv2.rectangle(image, (box[2],box[3]), (box[4],box[5]), colors[box[0]-1], 2)
                label = categories[box[0]-1] + ": " + str(box[1])
                point = (box[2], box[3]+15)
                size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                cv2.rectangle(image, (box[2], box[3]), (point[0]+size[0], point[1]+size[1]), (255,255,255), -1)
                cv2.putText(image, label, point, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)
                
        
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
    
