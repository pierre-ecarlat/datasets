import sys
import argparse
import io
import cv2
import urllib
import numpy as np
import os

parser = argparse.ArgumentParser(description='Process the path to the file.')
parser.add_argument('txt_dataset', type=str, help='Path to dataset.txt')
parser.add_argument('output_dir', type=str, help='Path to the directory where to download images (will create it if doesnt exists')
args = parser.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)
if not os.path.exists(args.output_dir + "/Images"):
    os.makedirs(args.output_dir + "/Images")
if not os.path.exists(args.output_dir + "/Images/skipped"):
    os.makedirs(args.output_dir + "/Images/skipped")
if not os.path.exists(args.output_dir + "/Annotations"):
    os.makedirs(args.output_dir + "/Annotations")

with open(args.txt_dataset) as f:
    l = f.readlines()

    for idx, line in enumerate(l):
        line = line.split('; ')

        image_id = line[0]
        image_rId = line[1]
        image_skipped = line[2]
        image_annotations = line[3]
        image_url = line[4]

        details = str(idx+1) + " " + str(image_id) + " " + str(image_rId) + "\n"
        with io.FileIO(str(args.output_dir) + "/ids.txt", "a") as file:
            file.write(details)

        image_url_response = urllib.urlopen(image_url)
        image_array = np.array(bytearray(image_url_response.read()), dtype=np.uint8)
        image = cv2.imdecode(image_array, -1)
        if image is None:
            print ("This dataset has already been used, please use an other one.")
            sys.exit()

        if (image_skipped == "false"):
            cv2.imwrite(str(args.output_dir) + "/Images/" + str(idx) + ".png", image)
            annotations = image_annotations.replace(":", "\n")
            with io.FileIO(str(args.output_dir) + "/Annotations/" + str(idx) + ".txt", "w") as file:
                file.write(annotations[1:-1])
            with io.FileIO(str(args.output_dir) + "/list.txt", "a") as file:
                file.write("Images/" + str(idx) + ".png Annotations/" + str(idx) + ".txt\n")
        else:
            cv2.imwrite(str(args.output_dir) + "/Images/skipped/" + str(idx) + ".png", image)
            with io.FileIO(str(args.output_dir) + "/skipped_list.txt", "a") as file:
                file.write("Images/skipped/" + str(idx) + ".png\n")

        print (str(idx) + " / " + str(len(l)) + " done")
