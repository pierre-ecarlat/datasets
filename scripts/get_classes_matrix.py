#!/usr/bin/env python

"""
?? Undefined yet
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import sys
import io
import cv2
import time
import numpy as np
import pandas as pd
import urllib
import requests
from PIL import Image


start = time.time()


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('labels', help='\
    The path to the labels.csv.')
    parser.add_argument('dict', help='\
    The directory with the labels (expects subdirectories train & validation with their labels.csv.')
    parser.add_argument('--output', default="matrix.txt", help='\
    The path where to save results.')

    return parser.parse_args()


def checkFiles (files):
    for f in files:
        if not os.path.isfile(f):
            print "Can't find " + f + "."
            raise SystemExit
def checkDirs (dirs):
    for d in dirs:
        if not os.path.exists(d):
            print "Can't find " + d + "."
            raise SystemExit

def ping (txts):
    txt = ' '.join([str(t) for t in txts])
    print "[Info    ]>>> " + txt + "..."
    global start
    start = time.time()
def pong ():
    t_spent = int(time.time() - start)
    print "[Timer   ]>>> Done in", t_spent, "secondes."
def displayProgress (index, nbMax, tempo):
    if index % tempo != 0 and index < nbMax-1: return
    sys.stdout.write("\r[Process ]>>> " + str(int(index / float(nbMax) * 100)) + " % done.")
    sys.stdout.flush()
    if index >= nbMax-1: print


def WriteMatrix(matrix, path):
    assert matrix.shape[0] == matrix.shape[1]

    ping(['Write matrix'])
    nbLines = matrix.shape[0]
    with open(path, 'w') as f:
        for count, x in enumerate(matrix):
            displayProgress (count, nbLines, 1)
            f.write(' '.join([str(el) for el in x]) + '\n')
    pong ()
    
    print "Matrix written into " + path + ".\n"


def ReadDict (dict_path):
    # Dictionary to complete
    return [line.rstrip('\n').split(',')[0][1:-1] for line in open(dict_path)]


def computeCategs(categs, matrix):
    for ix, cat in enumerate(categs):
        for ix2, cat2 in enumerate(categs):
            if ix <= ix2:
                continue
            matrix[cat[0]][cat2[0]] += cat[1] * cat2[1]
    return matrix


def ComputeMatrix (labels_path, dict):
    nb_categs = len(dict)

    # Matrix to complete
    matrix = np.zeros((nb_categs, nb_categs), dtype=np.float)
    
    # Tasks
    task1 = ['Reading the labels']
    task2 = ['Organize the labels']
    
    ping (task1)
    labels = pd.read_csv(labels_path, delimiter=',', dtype='unicode')
    labels['Confidence'] = labels['Confidence'].astype(float)
    pong ()

    ping (task2)
    nbLabels = labels.shape[0] 

    curr_image_id = ""
    all_categs = []
    for count, (index, row) in enumerate(labels.iterrows()):
        if curr_image_id != row['ImageID']:
            matrix = computeCategs(all_categs, matrix)
            curr_image_id = row['ImageID']
            all_categs = []

        categ_idx = dict.index(row['LabelName'])
        all_categs.append([categ_idx, row['Confidence']])

        displayProgress (count, nbLabels, 10000)

    if len(all_categs) > 0:
        matrix = computeCategs(all_categs, matrix)
    pong ()
    
    print
    
    return matrix


if __name__ == "__main__":
    # Get the arguments
    args = getArguments()

    # Check conditions
    checkFiles ([args.labels, args.dict])

    # Read the dicts
    dict = ReadDict (args.dict)

    # Compute the infos if not restored
    matrix = ComputeMatrix (args.labels, dict)

    # Write the first snapshot
    WriteMatrix (matrix, args.output)
    
    raise SystemExit
    
