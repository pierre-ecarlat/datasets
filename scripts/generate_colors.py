#!/usr/bin/env python

"""
Generate a list of distributed colors for a dataset. Example of use:
python generate_colors.py Food 67
"""

# Auto-generated python class for protobuf formats
import argparse
import colorsys
import io
import os


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='\
    The directory with the dataset.')
    parser.add_argument('nb_classes', type=int, help='\
    The number of classes of the dataset.')
    
    return parser.parse_args()
    

if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Compute the colors
    HSV_tuples = [(x*1.0/args.nb_classes, 0.5, 0.5) for x in range(args.nb_classes)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    for i in range(len(RGB_tuples)):
        RGB_tuples[i] = [int((x*255-63)*4) for x in RGB_tuples[i]]
    
    if not os.path.exists(os.path.join(args.dataset, "infos")):
        os.makedirs(os.path.join(args.dataset, "infos"))
    with io.FileIO(os.path.join(args.dataset, "infos", "colors.txt"), "a") as file:
        for tup in RGB_tuples:
            file.write(str(tup[0]) + " " + str(tup[1]) + " " + str(tup[2]) + "\n")
    
