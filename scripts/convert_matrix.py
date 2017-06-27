#!/usr/bin/env python

"""
?? Undefined yet
"""

# Auto-generated python class for protobuf formats
import argparse
import os
import numpy as np
try:
  import cPickle as pickle
except ImportError:
  import pickle


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('matrix', help='\
    The path to the matrix.txt.')

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


def ReadMatrix(path):
    matrix = np.asarray([line.rstrip('\n').split() for line in open(path)])
    assert matrix.shape[0] == matrix.shape[1]
    return matrix

def WriteMatrix(matrix, path):
    with open(path, 'wb') as fid:
      pickle.dump(matrix, fid, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    # Get the arguments
    args = getArguments()

    matrix = ReadMatrix(args.matrix)
    WriteMatrix(matrix, args.matrix[:-4] + '.pkl')
    
    raise SystemExit
    
