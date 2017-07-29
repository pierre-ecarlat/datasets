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
import json
from PIL import Image


SNP_EXT = ".csv"
IMG_EXT = ".jpg"
ANN_EXT = ".txt"

MAX_W = 640
MAX_H = 480

start = time.time()


def getArguments():
    """Defines and parses command-line arguments to this script."""
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument('output', help='\
    The directory where to save the dataset.')
    parser.add_argument('helpers', help='\
    The directory with the labels (expects subdirectories train & validation with their labels.csv.')
    # TODO: replace underscores by spaces
    parser.add_argument('categ', help='\
    The category (human-readable way, (underscores will be replaced by spaces) to download.')
    
    # Optional arguments
    parser.add_argument('--snapshot', default="tmpSnapshot", help='\
    The snapshot to restore, time saver.')
    parser.add_argument('--threshold', default=0.7, help='\
    The minimum confidence required for machine-based annotations.')
    parser.add_argument('--test', default=False, action='store_true', help='\
    Debug mode, deals with smaller files, faster.')
    parser.add_argument('--clean', default=False, action='store_true', help='\
    Cleans the snapshots.')
    parser.add_argument('--skip_until_uri', help='\
    Should be removed: skip the downloads until the given uri (debug command).')
    
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
    if path == '': return False
    r = requests.head(path)
    return r.status_code == requests.codes.ok



def readSnapshot(snapshot_path):
    """
    Reads and return the snapshot as a dict.
    Dictionary format:
        { 1: [ { id: <id1>, set: <set>, uri: <uri>, thumb: <thumb>, categs: [ { id: <id>, confidence: <confidence>, xmin: <xmin>, ymin: <ymin>, xmax: <xmax>, ymax: <ymax> }, {..} ] }, 
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
        displayProgress (count, nbImages, 5000)
        
        uri = "" if row['ImageURI'] != row['ImageURI'] else row['ImageURI']
        thumbnail = "" if row['Thumbnail300KURL'] != row['Thumbnail300KURL'] else row['Thumbnail300KURL']
        values = { 'fc':         str(row['FoodincCategory']),
                   'img_id':     row['ImageID'],
                   'img_set':    row['ImageSet'],
                   'img_uri':    uri,
                   'img_thumb':  thumbnail,
                   'categ_id':   row['CategId'],
                   'categ_conf': row['Confidence'],
                   'xmin':       row['XMin'],
                   'ymin':       row['YMin'],
                   'xmax':       row['XMax'],
                   'ymax':       row['YMax'] }
        
        AddValuesToInfos (values, infos, imgs_idxs)
    pong ()
    
    return infos


def writeSnapshot(infos, snapshot_path):
    """
    Writes the snapshot.
    Snapshot format:
        <FoodincCategory>,<ImageID>,<ImageSet>,<ImageURI>,<Thumbnail300KURL>,<CategId>,<Confidence>,<XMin>,<YMin>,<XMax>,<YMax>
    """
    with open(snapshot_path, 'w') as f:
        f.write("FoodincCategory,ImageID,ImageSet,ImageURI,Thumbnail300KURL,CategId,Confidence,XMin,YMin,XMax,YMax\n")
        for k_fc, v_fc in infos.iteritems():
            for img in v_fc:
                for categ in img['categs']:
                    f.write(','.join(['"' + str(k_fc) + '"', 
                                      '"' + img['id'] + '"', 
                                      '"' + img['set'] + '"', 
                                      '"' + img['uri'] + '"', 
                                      '"' + str(img['thumb']) + '"', 
                                      '"' + categ['id'] + '"', 
                                      '"' + str(categ['confidence']) + '"', 
                                      '"' + str(categ['xmin']) + '"', 
                                      '"' + str(categ['ymin']) + '"', 
                                      '"' + str(categ['xmax']) + '"', 
                                      '"' + str(categ['ymax']) + '"']) + '\n')
    
    print "Snapshot written into " + snapshot_path + ".\n"


def findJSONObject(j, name, acc):
    if j['name'] == name:
        acc.append(j)
    if 'children' in j:
        for c in j['children']:
            findJSONObject(c, name, acc)

def getAllNames(j, acc):
    acc.append(j['name'])
    if 'children' in j:
        for c in j['children']:
            getAllNames(c, acc)


# TODO: conflict if category given exists, but is not bounding box trainable
# Note: I don't care for now, so won't be changed asap
def computeTransitionsFor(transitions_path, helpers_dir, categ):
    # Read the categories list
    classes_file = os.path.join(helpers_dir, 'class-descriptions.csv')
    all_categs = pd.read_csv(classes_file, delimiter=',', header=None) \
                    .as_matrix()

    if categ == '':
        print "Will put all the categories in the transitions file."
        with open(transitions_path, 'w') as f:
            for count, categ in enumerate(all_categs[:,0]):
                f.write(','.join(['"' + categ + '"', 
                                  '"' + str(count+1) + '"']) + '\n')
        return True

    if not categ in all_categs[:,1]:
        print "Unable to find the categ '" + categ + "' in OpenImages."
        print "Can't compute the transition map."
        return False

    print "Will compute the transitions for the " + categ + " category."
    # TODO: relative path vvvv
    with open(os.path.join(helpers_dir, '..', 'bbox_hierarchy.json'), 'r') as f:
        json_str = f.readlines()[0]
    jdata = json.loads(json_str)
    all_objs_of_categ = []
    findJSONObject(jdata, categ, all_objs_of_categ)
    if len(all_objs_of_categ) == 0:
        print "Invalid category (probably an existing non box-trainable category)."
        return False

    all_names = []
    getAllNames(all_objs_of_categ[0], all_names)

    all_ids = []
    for name in all_names:
        subcategs = all_categs[np.where(all_categs[:,1] == name)]
        if len(subcategs) > 1:
            print "[Warning]: the category " + name + " has multiple IDs, add them all."
        for subcateg in subcategs:
            all_ids.append(subcateg[0])

    with open(transitions_path, 'w') as f:
        for count, categ in enumerate(all_ids):
            f.write(','.join(['"' + categ + '"', 
                              '"' + str(count+1) + '"']) + '\n')


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
                             'thumb': values['img_thumb'], 
                             'categs': [] } )
        imgs_idxs[fc].insert (0, values['img_id'])
        idx = len(infos[fc]) - 1
    
    infos[fc][idx]['categs'].append ( { 'id': values['categ_id'], 
                                        'xmin': values['xmin'], 
                                        'ymin': values['ymin'], 
                                        'xmax': values['xmax'], 
                                        'ymax': values['ymax'], 
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
    # TODO: Only bounding boxes, because I am only interested in them, but
    # this is the part of the code that should be modified if you are also
    # interested in classification tasks
    # ['annotations-human', 'annotations-machine', 'annotations-human-bbox']
    for set_path in labels_paths:
        set_path = set_path['annotations-human-bbox']
        print "-----------------------------------------------"
        print set_path
        print "-----------------------------------------------"
        
        training_set = os.path.basename(os.path.dirname(set_path))
        
        task1 = ['Reading', set_path]
        task2 = ['Extracting labels with confidence higher than', thresh]
        task3 = ['Extracting food_related labels']
        task4 = ['Organize the labels']
        
        ping (task1)
        labels = pd.read_csv(set_path, delimiter=',', dtype='unicode')
        labels['Confidence'] = labels['Confidence'].astype(float)
        labels['XMin'] = labels['XMin'].astype(float)
        labels['XMax'] = labels['XMax'].astype(float)
        labels['YMin'] = labels['YMin'].astype(float)
        labels['YMax'] = labels['YMax'].astype(float)
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
            displayProgress (count, nbLabels, 5000)
            
            categ_trans_idx = np.argwhere(transitions[:,0] == row['LabelName'])[0,0]
            values = { 'img_id':     row['ImageID'],
                       'img_set':    training_set,
                       'img_uri':    "",
                       'img_thumb':  "",
                       'categ_id':   row['LabelName'],
                       'categ_conf': row['Confidence'],
                       'fc':         transitions[categ_trans_idx][1],
                       'xmin':       row['XMin'],
                       'ymin':       row['YMin'],
                       'xmax':       row['XMax'],
                       'ymax':       row['YMax'],
                     }
            
            AddValuesToInfos (values, infos, imgs_idxs)
        pong ()
        
        print
    
    return infos


def GetImages (images_paths, infos):
    images = {}
    
    # Get the list of relevant images
    relevant_images = []
    ping (["Get the list of the relevant images"])
    nbRelImages = len(infos)
    for count, fc in enumerate(infos.values()):
        displayProgress (count, nbRelImages, 1)
        for img in fc:
            if not img['id'] in relevant_images:
                relevant_images.insert(0, img['id'])
    pong ()
    print
    
    # For each set
    for set_path in images_paths:
        print "-----------------------------------------------"
        print set_path
        print "-----------------------------------------------"
        
        training_set = os.path.basename(os.path.dirname(set_path))
        
        task1 = ["Unpacking images for set", training_set]
        task2 = ["Extract only the relevant images for set", training_set]
        
        ping (task1)
        tmp_images = pd.read_csv(set_path, delimiter=',', dtype='unicode', 
                                 usecols=['ImageID', 'OriginalURL', 'Thumbnail300KURL'])
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
            if not img['id'] in relev_images:
                images_set = images[img['set']]
                img_infos = images_set.loc[images_set['ImageID'] == img['id']]
                relev_images[img['id']] = { 
                    'uri': img_infos['OriginalURL'].iloc[0],
                    'thumb': img_infos['Thumbnail300KURL'].iloc[0],
                }
            img['uri'] = relev_images[img['id']]['uri']
            img['thumb'] = relev_images[img['id']]['thumb']
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
                   'validation': os.path.join(p_sets, "validation.txt"),
                   'test':       os.path.join(p_sets, "test.txt") }
    
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
            uri_to_use = img['thumb']
            resize = False
            if not imageOnlineExists (img['thumb']):
                if not imageOnlineExists (img['uri']):
                    with open(p_errors, 'a') as f:
                        f.write(img['id'] + " " + img['uri'] + " " + img['set'] + "\n")
                    continue
                else:
                    uri_to_use = img['uri']
                    resize = True
            
            # Download image
            if not os.path.exists(img_path):
                urllib.urlretrieve(uri_to_use, img_path)
                try:
                    pymg = Image.open (img_path)
                    if resize:
                        ratio = min(MAX_H / float(pymg.size[0]), MAX_W / float(pymg.size[1]))
                        if ratio < 1:
                            newSize = (int(pymg.size[0] * ratio), int(pymg.size[1] * ratio))
                            pymg = pymg.resize(newSize, Image.ANTIALIAS)
                    pymg.save (img_path, optimize=True, quality=95)
                except IOError: 
                    os.remove(img_path)
            
            # Create the annotation
            with open(ann_path, 'a') as f:
                for box in img['categs']:
                    f.write(' '.join([str(k_fc), str(box['xmin']), str(box['ymin']), str(box['xmax']), str(box['ymax']) + "\n"]))
            
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
    snapshot_base_path = os.path.join(args.helpers, args.snapshot)
    infos = readSnapshot(snapshot_base_path + test + SNP_EXT)
    
    # Analize the restoration
    restored_status = -1
    if not infos:                           restored_status = 0
    elif infos.values()[0][0]['uri'] == "": restored_status = 1
    else:                                   restored_status = 2
    
    # Paths to the main files
    transitions_path  = os.path.join(args.helpers, "transitions_" + args.categ + SNP_EXT)
    if not os.path.isfile(transitions_path):
        if not computeTransitionsFor(transitions_path, args.helpers, args.categ):
            raise SystemExit

    paths = {}
    for _set in ['train', 'validation', 'test']:
        paths[_set] = {
            'images': os.path.join(args.helpers, _set, "images.csv"),
            'annotations': {}
        }
        for _file in ['annotations-human', 'annotations-machine', 'annotations-human-bbox']:
            paths[_set]['annotations'][_file] = os.path.join(args.helpers, _set, _file + ".csv")

    # Check conditions
    checkDirs ([args.helpers])
    if restored_status < 1:
        checkFiles ([transitions_path] +
                    [paths['train']['annotations'][f] for f in paths['train']['annotations']] + 
                    [paths['validation']['annotations'][f] for f in paths['validation']['annotations']] + 
                    [paths['test']['annotations'][f] for f in paths['test']['annotations']])
    if restored_status < 2:
        checkFiles ([paths['train']['images'], 
                     paths['validation']['images'],
                     paths['test']['images']])
    
    # Compute the infos if not restored
    if restored_status < 1:
        infos = GetInfos (transitions_path, 
                          [paths[_set]['annotations'] for _set in ['train', 'validation', 'test']],
                          args.threshold)
        
        # Write the first snapshot
        writeSnapshot (infos, snapshot_base_path + test + SNP_EXT)
    
    # Get all the images
    if restored_status < 2:
        images = GetImages ([paths[_set]['images'] for _set in ['train', 'validation', 'test']], 
                            infos)
        
        # Update infos
        addURIsToInfos (infos, images)
        
        # Write the new snapshot and replace the previous snapshot by the new one
        writeSnapshot (infos, snapshot_base_path + "URI" + test + SNP_EXT)
        os.rename (snapshot_base_path + test + SNP_EXT, snapshot_base_path + test + SNP_EXT + ".toDelete")
        os.rename (snapshot_base_path + "URI" + test + SNP_EXT, snapshot_base_path + test + SNP_EXT)
        os.remove (snapshot_base_path + test + SNP_EXT + ".toDelete")
    
    # Check if the images directory exists
    if restored_status < 3:
        # Warning if dataset already exists
        if not os.path.exists(args.output):
            os.makedirs (args.output)
        else:
            answer = raw_input("The directory " + args.output + " already exists. " +
                               "Do you want to pursue (may affects the existing content)? [y/n] ")
            if not answer.lower() in ("y", "yes"):
                raise SystemExit
        
        # Download the images and annotations
        downloadImages(infos, args.output)

    # Add infos
    # TODO: Not tested
    transitions = pd.read_csv(transitions_path, delimiter=',', header=None) \
                    .as_matrix()[:,0]
    with open(os.path.join(args.output, "infos", "categories.txt"), 'w') as f:
        for categ in transition:
            f.write(elem)
    with open(os.path.join(args.output, ".format"), 'w') as f:
        f.write("fincFormat")
    
    # Remove the snapshots if arg clean is set
    if args.clean:
        os.remove(snapshot_base_path + test + SNP_EXT)
    
    raise SystemExit
    
    
    
    
