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


SNP_EXT = ".csv"
IMG_EXT = ".jpg"
ANN_EXT = ".txt"

MAX_W = 700
MAX_H = 700

start = time.time()


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('directory', help='\
    The directory with the labels (expects subdirectories train & validation with their labels.csv.')
    parser.add_argument('--snapshot', default="tmpSnapshot", help='\
    The snapshot to restore.')
    parser.add_argument('--threshold', default=0.7, help='\
    The minimum confidence required.')
    parser.add_argument('--test', default=False, action='store_true', help='\
    Debug mode, deals with smaller files, faster.')
    parser.add_argument('--clean', default=False, action='store_true', help='\
    Cleans the snapshots.')
    parser.add_argument('--skip_until_uri', help='\
    Should be removed: skip the downloads until the given uri.')
    
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

def imageOnlineExists (path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok



def readSnapshot(snapshot_path):
    """
    Reads and return the snapshot as a dict.
    Dictionary format:
        { 1: [ { id: <id1>, set: <set>, uri: <uri>, categs: [ { id: <id>, confidence: <confidence> }, {..} ] }, 
               { id: <id2>, ... }, 
               {..} ],
          2: [..],
          ...
          67: [..]
        }
    """
    # No snapshot
    if not os.path.isfile(snapshot_path):
        return {}
    
    ping (["Will restore snapshot"])
    snapshot = pd.read_csv(snapshot_path, delimiter=",")
    
    infos = {}
    imgs_idxs = {}
    nbImages = snapshot.shape[0]  
    for count, (index, row) in enumerate(snapshot.iterrows()):
        displayProgress (count, nbImages, 10000)
        
        uri = "" if row['ImageURI'] != row['ImageURI'] else row['ImageURI']
        values = { 'fc':         str(row['FoodincCategory']),
                   'img_id':     row['ImageID'],
                   'img_set':    row['ImageSet'],
                   'img_uri':    uri,
                   'categ_id':   row['CategId'],
                   'categ_conf': row['Confidence'] }
        
        AddValuesToInfos (values, infos, imgs_idxs)
    pong ()
    
    return infos


def writeSnapshot(infos, snapshot_path):
    """
    Writes the snapshot.
    Snapshot format:
        <FoodincCategory>,<ImageID>,<ImageSet>,<ImageURI>,<CategId>,<Confidence>
    """
    with open(snapshot_path, 'w') as f:
        f.write("FoodincCategory,ImageID,ImageSet,ImageURI,CategId,Confidence\n")
        for k_fc, v_fc in infos.iteritems():
            for img in v_fc:
                for categ in img['categs']:
                    f.write(','.join(['"' + str(k_fc) + '"', 
                                      '"' + img['id'] + '"', 
                                      '"' + img['set'] + '"', 
                                      '"' + img['uri'] + '"', 
                                      '"' + categ['id'] + '"', 
                                      '"' + str(categ['confidence']) + '"']) + '\n')
    
    print "Snapshot written into " + snapshot_path + ".\n"
    

def AddValuesToInfos (values, infos, imgs_idxs):
    fc = values['fc']
    if not fc in infos:
        infos[fc] = []
        imgs_idxs[fc] = []
    
    all_ids = imgs_idxs[fc]
    try:
        idx = all_ids.index(values['img_id'])
    except ValueError:
        infos[fc].append ( { 'id': values['img_id'], 
                             'set': values['img_set'], 
                             'uri': values['img_uri'], 
                             'categs': [] } )
        imgs_idxs[fc].insert (0, values['img_id'])
        idx = len(infos[fc]) - 1
    
    infos[fc][idx]['categs'].append ( { 'id': values['categ_id'], 
                                        'confidence': values['categ_conf'] } )



def GetInfos (transitions_path, labels_paths, thresh):
    # Dictionary to complete
    infos = {}
    imgs_idxs = {}
    
    # Read the transitions
    transitions = pd.read_csv(transitions_path, delimiter=',', header=None) \
                    .as_matrix()
    
    # Handler for all the new categories
    #for nc in np.unique(transitions[:,1]):
    #    infos[nc] = []
    
    # Read labels
    for set_path in labels_paths:
        print "-----------------------------------------------"
        print set_path, "set"
        print "-----------------------------------------------"
        
        training_set = os.path.basename(os.path.dirname(set_path))
        
        task1 = ['Reading', set_path]
        task2 = ['Extracting labels with confidence higher than', thresh]
        task3 = ['Extracting food_related labels']
        task4 = ['Organize the labels']
        
        ping (task1)
        labels = pd.read_csv(set_path, delimiter=',', dtype='unicode')
        labels['Confidence'] = labels['Confidence'].astype(float)
        pong ()
        
        ping (task2)
        labels = labels.loc[labels['Confidence'] > thresh]
        pong ()
        
        ping (task3)
        labels = labels.loc[labels['LabelName'].isin(transitions[:,0])]
        pong ()
        
        ping (task4)
        nbLabels = labels.shape[0] 
        for count, (index, row) in enumerate(labels.iterrows()):
            displayProgress (count, nbLabels, 10000)
            
            categ_trans_idx = np.argwhere(transitions[:,0] == row['LabelName'])[0,0]
            values = { 'img_id':     row['ImageID'],
                       'img_set':    training_set,
                       'img_uri':    "",
                       'categ_id':   row['LabelName'],
                       'categ_conf': row['Confidence'],
                       'fc':         transitions[categ_trans_idx][1] }
            
            AddValuesToInfos (values, infos, imgs_idxs)
        pong ()
        
        print
    
    return infos


def GetImages (images_paths, infos):
    images = {}
    
    # Get the list of relevant images
    relevant_images = []
    ping (["Get the list of the relevant images"])
    nbCategs = len(infos)
    for count, fc in enumerate(infos.values()):
        displayProgress (count, nbCategs, 1)
        for img in fc:
            if not img['id'] in relevant_images:
                relevant_images.insert(0, img['id'])
    pong ()
    print
    
    # For each set
    for set_path in images_paths:
        print "-----------------------------------------------"
        print set_path, "set"
        print "-----------------------------------------------"
        
        training_set = os.path.basename(os.path.dirname(set_path))
        
        task1 = ["Unpacking images for set", set_path]
        task2 = ["Extract only the relevant images for set", set_path]
        
        ping (task1)
        tmp_images = pd.read_csv(set_path, delimiter=',', dtype='unicode', 
                                 usecols=['ImageID', 'OriginalURL'])
        pong ()
        
        ping (task2)
        tmp_images = tmp_images.loc[tmp_images['ImageID'].isin(relevant_images)]
        pong ()
        
        images[training_set] = tmp_images
        print
    
    return images


def addURIsToInfos (infos, images):
    relev_images = {}
    
    ping (["Update infos with the URIs"])
    nbInfos = len(infos)
    for count, fc in enumerate(infos.values()):
        displayProgress (count, nbInfos, 1)
        
        for img in fc:
            if img['id'] in relev_images:
                img['uri'] = relev_images[img['id']]
            else:
                images_set = images[img['set']]
                img_infos = images_set.loc[images_set['ImageID'] == img['id']]
                img['uri'] = img_infos['OriginalURL'].iloc[0]
                relev_images[img['id']] = img['uri']
    pong ()


def downloadImages(infos, p_data):
    # Error file
    p_errors = "download_errors.txt";
    
    skip = bool(args.skip_until_uri)
    
    # Create the dataset architecture
    p_images = os.path.join(p_data, "Images");
    p_annots = os.path.join(p_data, "Annotations");
    p_sets   = os.path.join(p_data, "ImageSets");
    p_infos  = os.path.join(p_data, "infos");
    for path in [p_images, p_annots, p_sets, p_infos]:
        if not os.path.exists(path):
            os.makedirs (path)
    
    sets_paths = { 'all':        os.path.join(p_sets, "all.txt"),
                   'train':      os.path.join(p_sets, "train.txt"),
                   'validation': os.path.join(p_sets, "validation.txt") }
    
    ping (["Download the images"])
    nbInfos = len(infos)
    for count, (k_fc, v_fc) in enumerate(infos.iteritems()):
        displayProgress (count, nbInfos, 1)
        
        for img in v_fc:
            if skip and img['uri'] != args.skip_until_uri:
                continue
            skip = False
            img_path = os.path.join(p_images, img['id'] + IMG_EXT)
            ann_path = os.path.join(p_annots, img['id'] + ANN_EXT)
            
            # Makes sure the image exists
            if not imageOnlineExists (img['uri']):
                with open(p_errors, 'a') as f:
                    f.write(img['id'] + " " + img['uri'] + " " + img['set'] + "\n")
                continue
            
            # Download image
            if not os.path.exists(img_path):
                urllib.urlretrieve(img['uri'], img_path)
                try:
                    pymg = Image.open (img_path)
                    ratio = min(MAX_H / float(pymg.size[0]), MAX_W / float(pymg.size[1]))
                    if ratio < 1:
                        newSize = (int(pymg.size[0] * ratio), int(pymg.size[1] * ratio))
                        pymg = pymg.resize(newSize, Image.ANTIALIAS)
                        pymg.save (img_path, optimize=True, quality=95)
                except IOError: 
                    os.remove(img_path)
            
            # Create the annotation
            with open(ann_path, 'a') as f:
                f.write(k_fc + "\n")
            
            # Update the lists
            with open(sets_paths['all'], 'a') as f:
                f.write(img['id'] + "\n")
            with open(sets_paths[img['set']], 'a') as f:
                f.write(img['id'] + "\n")
    pong ()


if __name__ == "__main__":
    # Get the arguments
    args = getArguments()
    
    # Debug mode
    test = "_small" if args.test else ""
    
    # Restores the snapshot
    infos = readSnapshot(args.snapshot + test + SNP_EXT)
    
    # Analize the restoration
    restored_status = -1
    if not infos:                           restored_status = 0
    elif infos.values()[0][0]['uri'] == "": restored_status = 1
    else:                                   restored_status = 2
    
    # Paths to the main files
    transitions_path  = os.path.join(args.directory, "transition" + SNP_EXT)
    train_labels_path = os.path.join(args.directory, "train", "labels" + test + SNP_EXT)
    train_images_path = os.path.join(args.directory, "train", "images" + SNP_EXT)
    val_labels_path   = os.path.join(args.directory, "validation", "labels" + test + SNP_EXT)
    val_images_path   = os.path.join(args.directory, "validation", "images" + SNP_EXT)
    data_path         = os.path.join(args.directory, "data")
    
    # Check conditions
    checkDirs ([args.directory])
    if restored_status < 1:
        checkFiles ([transitions_path, train_labels_path, val_labels_path])
    if restored_status < 2:
        checkFiles ([train_images_path, val_images_path])
    
    # Compute the infos if not restored
    if restored_status < 1:
        infos = GetInfos (transitions_path, 
                          [train_labels_path, val_labels_path],
                          args.threshold)
        
        # Write the first snapshot
        writeSnapshot (infos, args.snapshot + test + SNP_EXT)
    
    # Get all the images
    if restored_status < 2:
        images = GetImages ([train_images_path, val_images_path], infos)
        
        # Update infos
        addURIsToInfos (infos, images)
        
        # Write the new snapshot and replace the previous snapshot by the new one
        writeSnapshot (infos, args.snapshot + "URI" + test + SNP_EXT)
        os.rename (args.snapshot + test + SNP_EXT, args.snapshot + test + SNP_EXT + ".toDelete")
        os.rename (args.snapshot + "URI" + test + SNP_EXT, args.snapshot + test + SNP_EXT)
        sys.remove (args.snapshot + test + SNP_EXT + ".toDelete")
    
    # Check if the images directory exists
    if restored_status < 3:
        # Warning if dataset already exists
        if not os.path.exists(data_path):
            os.makedirs (data_path)
        else:
            answer = raw_input("The directory " + data_path + " already exists. " +
                               "Do you want to pursue (may affects the existing content)? [y/n] ")
            if not answer.lower() in ("y", "yes"):
                raise SystemExit
        
        # Download the images and annotations
        downloadImages(infos, data_path)
    
    # Remove the snapshots if arg clean is set
    if args.clean:
        os.remove(args.snapshot + test + SNP_EXT)
    
    raise SystemExit
    
    
    
    
