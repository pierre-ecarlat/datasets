#!/usr/bin/env python

"""
Download the FiNC dataset using a valid 'dataset_xxxx.txt' (single use). This 
dataset is private, so all the provided 'dataset_xxxx.txt' won't work, they are
just here as examples. Please conatct directly the author if you want to know more
about it. Example of use:
python download_dataset.py dataset_xxxx.txt Foodinc
"""
import sys
import argparse
import io
import cv2
import urllib
import numpy as np
import os
import time
from socket import error as SocketError
import errno

from utils import timer_util

# Extensions
E_IMG = 'jpg'


def getArguments():
  """Defines and parses command-line arguments to this script."""
  parser = argparse.ArgumentParser()

  # Required arguments
  parser.add_argument('txt_dataset', type=str, help='\
    Path to dataset.txt')
  parser.add_argument('output_dir', type=str, help='\
    Path to the directory where to download images (will create it if doesnt exists')
  
  return parser.parse_args()
    

if __name__ == "__main__":
  # Get the arguments
  args = getArguments()

  # Requirements
  DATASET_PATH = os.path.join(args.output_dir) 
  IMAGES_PATH = os.path.join(DATASET_PATH, "Images")
  SKIPPED_PATH = os.path.join(DATASET_PATH, "Images", "skipped")
  ANNOTATIONS_PATH = os.path.join(DATASET_PATH, "Annotations")
  IMAGESETS_PATH = os.path.join(DATASET_PATH, "ImageSets")
  INFOS_PATH = os.path.join(DATASET_PATH, "infos")
  for path in [DATASET_PATH, IMAGES_PATH, SKIPPED_PATH, 
                             ANNOTATIONS_PATH,
                             IMAGESETS_PATH,
                             INFOS_PATH]:
    if not os.path.exists(path):
      os.makedirs(path)

  # Open the dataset text file
  timer_util.ping(['Start reading the dataset', args.txt_dataset])
  with open(args.txt_dataset) as f:
    l = f.readlines()

    # For each line, respecting the following format:
    # IMG_NAME; IMG_ID; ?SKIPPED; [BB1:BB2:BB3]; IMG_URI
    nbImages = len(l)
    for idx, line in enumerate(l):
      new_image_name = str(idx)

      timer_util.displayProgress (idx, nbImages, 1)
      name, rID, skipped, boxes, uri = line.split('; ')
      skipped = (skipped == "true")

      # Write the joint table ID -> new name (to have sequential names without losses)
      details = ' '.join([new_image_name, name, rID])
      with io.FileIO(os.path.join(INFOS_PATH, "ids.txt"), "a") as file:
        file.write(details + "\n")

      # Load the image
      success = False
      waiting_times = [1,1,1,5,5,5,30,60,120]
      while not success:
        try:
          image_url_response = urllib.urlopen(uri)
          success = True
        except SocketError | IOError as e:
          if len(waiting_times) > 0:
            print "\nError , will try again in", waiting_times[0]
            time.sleep(waiting_times[0])
            waiting_times = waiting_times[1:]
          else:
            print "\nTime out. exit"
            raise SystemExit

      image_array = np.array(bytearray(image_url_response.read()), dtype=np.uint8)
      image = cv2.imdecode(image_array, -1)
      if image is None:
        print ("This dataset file has already been used, please use another one.")
        sys.exit()

      # Save it and its annotations
      image_path = os.path.join(SKIPPED_PATH if skipped else IMAGES_PATH, 
                                '.'.join([new_image_name, E_IMG]))
      related_list = os.path.join(IMAGESETS_PATH, 
                                  "skipped.txt" if skipped else "all.txt")
      cv2.imwrite(image_path, image)
      with io.FileIO(related_list, 'a') as file:
        file.write(new_image_name + "\n")

      if not skipped:
        annotations = boxes.replace(":", "\n")[1:-1].split('\n')
        with io.FileIO(os.path.join(ANNOTATIONS_PATH, new_image_name + ".txt"), "w") as file:
          for annotation in annotations:
            a = annotation.split()
            if a:
              # Add 1 to the category (so they are all included in [1; NB_CATEG])
              file.write(' '.join([str(int(a[0])+1), a[2], a[3], a[4], a[5]]) + '\n')

  timer_util.pong()



