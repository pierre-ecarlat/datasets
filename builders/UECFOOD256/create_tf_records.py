# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

r"""Convert raw PASCAL dataset to TFRecord for object_detection.
Example usage:
    ./create_pascal_tf_record --data_dir=/home/user/VOCdevkit \
        --year=VOC2012 \
        --output_path=/home/user/pascal.record
"""

# Slightly modified from the original version

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import hashlib
import io
import logging
import os
import re
import numpy as np

from lxml import etree
import PIL.Image
import tensorflow as tf

from utils import dataset_util


flags = tf.app.flags
flags.DEFINE_string('data_dir', '', 'Root directory to raw UECFOOD256 dataset.')
flags.DEFINE_string('set', 'train', 'Convert training set, validation set or '
                    'merged set.')
flags.DEFINE_string('images_dir', 'Images',
                    '(Relative) path to images directory.')
flags.DEFINE_string('annotations_dir', 'Annotations',
                    '(Relative) path to annotations directory.')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
flags.DEFINE_string('categories_path', 'data/categories.txt',
                    'Path to the list of categories')
flags.DEFINE_boolean('ignore_difficult_instances', False, 'Whether to ignore '
                     'difficult instances')
FLAGS = flags.FLAGS

SETS = ['train', 'val', 'trainval', 'test']


def dict_to_tf_example(data,
                       dataset_directory,
                       categories,
                       ignore_difficult_instances=False,
                       image_subdirectory='Images'):
  """Convert XML derived dict to tf.Example proto.
  Notice that this function normalizes the bounding box coordinates provided
  by the raw data.
  Args:
    data: dict holding PASCAL XML fields for a single image (obtained by
      running dataset_util.recursive_parse_xml_to_dict)
    dataset_directory: Path to root directory holding PASCAL dataset
    label_map_dict: A map from string label names to integers ids.
    ignore_difficult_instances: Whether to skip difficult instances in the
      dataset  (default: False).
    image_subdirectory: String specifying subdirectory within the
      PASCAL dataset directory holding the actual image data.
  Returns:
    example: The converted tf.Example.
  Raises:
    ValueError: if the image pointed to by data['filename'] is not a valid JPEG
  """
  img_path = os.path.join(data['data_dir'], data['filename'])
  full_path = os.path.join(dataset_directory, img_path)
  with tf.gfile.GFile(full_path, 'rb') as fid:
    encoded_jpg = fid.read()
  encoded_jpg_io = io.BytesIO(encoded_jpg)
  image = PIL.Image.open(encoded_jpg_io)
  if image.format != 'JPEG':
    raise ValueError('Image format not JPEG')
  key = hashlib.sha256(encoded_jpg).hexdigest()

  # Image characteristics
  width, height = PIL.Image.open(img_path).size

  xmin = []
  ymin = []
  xmax = []
  ymax = []
  classes = []
  classes_text = []
  for ix, obj in enumerate(data['boxes']):
    xmin.append(np.clip(float(obj[0]) / width, 0, 1))
    ymin.append(np.clip(float(obj[1]) / height, 0, 1))
    xmax.append(np.clip(float(obj[2]) / width, 0, 1))
    ymax.append(np.clip(float(obj[3]) / height, 0, 1))
    classes_text.append(categories[int(data['labels'][ix])-1])
    classes.append(int(data['labels'][ix]))

  example = tf.train.Example(features=tf.train.Features(feature={
      'image/height': dataset_util.int64_feature(height),
      'image/width': dataset_util.int64_feature(width),
      'image/filename': dataset_util.bytes_feature(
          data['filename'].encode('utf8')),
      'image/source_id': dataset_util.bytes_feature(
          data['filename'].encode('utf8')),
      'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
      'image/encoded': dataset_util.bytes_feature(encoded_jpg),
      'image/format': dataset_util.bytes_feature('jpeg'.encode('utf8')),
      'image/object/bbox/xmin': dataset_util.float_list_feature(xmin),
      'image/object/bbox/xmax': dataset_util.float_list_feature(xmax),
      'image/object/bbox/ymin': dataset_util.float_list_feature(ymin),
      'image/object/bbox/ymax': dataset_util.float_list_feature(ymax),
      'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
      'image/object/class/label': dataset_util.int64_list_feature(classes),
  }))
  return example


def main(_):
  if FLAGS.set not in SETS:
    raise ValueError('set must be in : {}'.format(SETS))
  
  data_dir = FLAGS.data_dir

  writer = tf.python_io.TFRecordWriter(FLAGS.output_path)

  categories = [line.rstrip('\n') for line in open(FLAGS.categories_path)]

  logging.info('Reading from UECFOOD256 dataset.')
  list_set_path = os.path.join(data_dir, 'ImageSets', FLAGS.set + '.txt')
  images_dir = os.path.join(data_dir, FLAGS.images_dir)
  annotations_dir = os.path.join(data_dir, FLAGS.annotations_dir)
  list_set = dataset_util.read_examples_list(list_set_path)
  for idx, example in enumerate(list_set):
    if idx % 100 == 0:
      logging.info('On image %d of %d', idx, len(list_set))

    # Annotation characteristics
    ann_path = os.path.join(annotations_dir, example + '.txt')

    # Read annots
    data = [line.rstrip('\n').split() for line in open(ann_path)]
    bboxes = []
    labels = []
    for obj in data:
      labels.append(float(obj[0]))
      bboxes.append([float(obj[1]), float(obj[2]), 
                     float(obj[3]), float(obj[4])])

    data = {
      'data_dir': images_dir, 
      'filename': example + '.jpg', 
      'boxes': bboxes, 
      'labels': labels, 
    }

    tf_example = dict_to_tf_example(data, FLAGS.data_dir, categories,
                                    FLAGS.ignore_difficult_instances)
    writer.write(tf_example.SerializeToString())

  writer.close()


if __name__ == '__main__':
  tf.app.run()

