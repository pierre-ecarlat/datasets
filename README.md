This project contains all the scripts I use for downloading / converting / manipulating / analyzing datasets. Most of them have been written to be generic, but are still quite high level, so any uncommon use may work, but there is no guarantee. These datasets are used in my projects, see the other repositories for some example of use.  
[Quite important notice]: there is no rollback on the scripts, so it's always better to use the duplicate option / do a backup.


## Requirements
```shell
$ apt install xml-twig-tools 
```
Note1: the conversion into tfRecords require -obviously- Tensorflow.  
Note2: may not be all.


## Possible use
```shell
# Download VOC2007
./scripts/download_.sh VOC2007
# Convert the dataset into tfRecords
./scripts/convert_.sh VOC2007 tfRecords
# Reduced it to a 4-categories dataset following the transition map in 
# builders/VOC2007/reduction_to_4/transition.txt
./scripts/reduce_.sh VOC2007 4
```
Note: The reduced dataset won't be conversible into any new format because it will require some builders in `builders/VOC2007_4C` (which doesn't exist). Fell free to create it if needed, or to rename the dataset to VOC2007 and, then, change the NB_CATEGORIES in the conversions scripts. This will be fixed soon, but the way to deal with different VOC (given the years, given the number of categories, etc) still has to be defined (and it starts to be too much for shell, should have switch to python a while ago).


## Repo architecture
```
|-- _builders
    |-- _DATASET_1
        |-- [scripts specific to DATASET_1]
    |-- _DATASET_2
    |-- _DATASET_n
|-- _scripts
    |-- [generic scripts (supposed to work for any dataset)]
```
Add your new dataset by adding its builders, the generic should still be usable.


## Current formats
### vocFormat
Used for the [ILSVRC](http://www.image-net.org/challenges/LSVRC/) challenge.
```
|-- _VOC[year]
    |-- _JPEGImages
        |-- image_n.jpg
    |-- _Annotations
        |-- annotation_n.xml
    |-- _ImageSets
        |-- _Main
            |-- trainval.txt / test.txt / all.txt
    |-- _infos
        |-- categories.txt
        |-- colors.txt
```
Image sets are list of the image names (no extension).
Annotations are written in the following format:
```xml
<annotation>
	<folder>VOC[year]</folder>
	<filename>[name].jpg</filename>
	<size>
		<width>600</width>
		<height>800</height>
		<depth>3</depth>
	</size>
	<object>
		<name>pikachu</name>
		<bndbox>
			<xmin>50</xmin>
			<ymin>30</ymin>
			<xmax>360</xmax>
			<ymax>280</ymax>
		</bndbox>
	</object>
</annotation>
```


### tfRecords
Common format for [tensorlow](tensorflow.org).
```
|-- DATASET_NAME_train.tfrecord
|-- DATASET_NAME_val.tfrecord
|-- DATASET_NAME_trainval.tfrecord
|-- DATASET_NAME_test.tfrecord
|-- _infos
    |-- label_map.pbtxt
```
Usually stores the image size, filename, bounding boxes, classes under the following labels:
```
image/height
image/width
image/filename
image/object/bbox/xmin
image/object/bbox/xmax
image/object/bbox/ymin
image/object/bbox/ymax
image/object/class/text
image/object/class/label
image/object/other_details_to_save
```
But check the scripts to be sure, the details to save changed depending on the datasets.


### fincFormat
Used by [FiNC](https://finc.com/).
```
|-- _Images
    |-- image_n.jpg
|-- _Annotations
    |-- annotation_n.txt
|-- _ImageSets
    |-- trainval.txt / test.txt / all.txt
|-- _infos
    |-- categories.txt
    |-- colors.txt
```
Image sets are list of the image names (no extension).
Annotations are written in the following format:
```
CLS X1 X2 Y1 Y2
```
With one bounding box per line, and the classes going from 1 to NB_CLASS (0 is let free for the background).


## Current datasets
* [VOC2007](http://host.robots.ox.ac.uk/pascal/VOC/voc2007/)
* [UECFOOD100](http://foodcam.mobi/dataset100.html)
* [UECFOOD256](http://foodcam.mobi/dataset256.html)
* [Foodinc](https://finc.com/) - Private dataset (you won't be able to download the images)

