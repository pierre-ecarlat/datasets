#!/usr/bin/env python

"""
Generate trainval.txt test.txt, train.txt and val.txt using given 
proportions. Example of use:
python scripts/generate_lists.py Voc2007 \
                --in all                 \
                --out1 trainval          \
                --out2 test              \
                --proportion 0.8
TODO: WARNING: old code, I haven't cehck all the possible situations, 
may create some irrelevant lists, double check
"""

import os
import io
import argparse
import random

import numpy as np


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('dataset', help='\
        The directory with the dataset.')
    parser.add_argument('--inp', default='all', help='\
        The input set to use (default: all).')
    parser.add_argument('--out1', default='trainval', help='\
        The name of the first output set (default: trainval).')
    parser.add_argument('--out2', default='test', help='\
        The name of the first output set (default: test).')
    parser.add_argument('--proportion', default=0.8, type=float, help='\
        The proportion for the dataset, between 0 and 1 (defaut: 0.8).')
    
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

    # Requirements
    paths['characts'] = os.path.join(paths['image_sets'],
                                     paths['characteristics_'] + args.inp)
    list_file = os.path.join(paths['image_sets'], args.inp + ".txt")
    assert os.path.isfile(list_file), \
        args.inp + '.txt is missing.. Please compute it.'

    # Create the caracteristics if not created
    if not os.path.exists(paths['characts']):
        this_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                'compute_characteristics.py')
        os.system(' '.join(['python', this_dir, args.dataset, 
                            '--list', args.inp]))
    assert os.path.exists(paths['characts']), \
        'Failed to compute the characteristics.'

    # Create the output_categ_distrib_idxes.txt
    paths['nbimg_per_categs'] = os.path.join(paths['characts'],
                                             "nb_images_per_category.txt")
    nipc = [line.rstrip('\n') for line in open(paths['nbimg_per_categs'])]
    nipc_sorted_idx = sorted(range(len(nipc)), key=lambda k: int(nipc[k]))

    # Create the output_categ_idxes.txt
    paths['categ_per_images'] = os.path.join(paths['characts'],
                                             "categories_idx_per_image.txt")
    cipi = [line.rstrip('\n') for line in open(paths['categ_per_images'])]
    cipi_used = [False] * len(cipi)

    # Creates the sets
    out1 = ""
    out2 = ""

    # For each line in output_categ_distrib_idxes.txt
    for curr_categ in nipc_sorted_idx:
        list_img = []
        for j in range(len(cipi)):
            if not cipi_used[j]:
                curr_cipi = cipi[j].split()
                if str(int(curr_categ)+1) in curr_cipi[1:]: 
                    list_img.append(curr_cipi[0])
                    cipi_used[j] = True

        fp = int(len(list_img) * args.proportion)
        for j in range(0, fp):
            out1 += list_img[j] + "\n"
        for j in range(fp, len(list_img)):
            out2 += list_img[j] + "\n"

    # Write results
    open(os.path.join(paths['image_sets'], args.out1 + ".txt"), 'w')\
        .writelines(out1[:-1])
    open(os.path.join(paths['image_sets'], args.out2 + ".txt"), 'w')\
        .writelines(out2[:-1])
