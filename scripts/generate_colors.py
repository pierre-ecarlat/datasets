#!/usr/bin/env python

"""
Generate a list of distributed colors for a dataset (a good location 
for the color file is into the `infos` directory). Example of use:
python scripts/generate_colors.py 20 VOC2007/colors.txt
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
    parser.add_argument('nb_classes', type=int, help='\
        The number of classes of the dataset.')
    parser.add_argument('output', help='\
        Where to save the colors.')
    
    return parser.parse_args()
  

if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Compute the colors
    HSV_tuples = [(x*1.0/args.nb_classes, 0.5, 0.5)
                  for x in range(args.nb_classes)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    for i in range(len(RGB_tuples)):
        RGB_tuples[i] = [int((x*255-63)*4) for x in RGB_tuples[i]]
    
    with open(args.output, 'w') as f:
        for tup in RGB_tuples:
            f.write(' '.join([str(tup[0]), str(tup[1]), str(tup[2])]) + "\n")
