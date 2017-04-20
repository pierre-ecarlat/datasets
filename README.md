This directory groups all the scripts I use for downloading / convert the datasets used in my projects. Also permit to generate some files (train / test for CNN, colors for a given number of classes, etc.).

# Getting started

## Requirements

```
apt install xml-twig-tools
```

## Instructions

To download a dataset, simply do:
```
bash scripts/get_.sh DATASET_NAME
```


# Datasets

## Format

After using get_.sh, the dataset will be in the main directory, respecting the following architecture:
```
|-- _Images
    |-- image_n.png
|-- _Annotations
    |-- annotation_n.txt
|-- _ImageSets
    |-- trainval.txt / test.txt / all.txt
|-- _infos
    |-- categories.txt
    |-- colors.txt
```
The original dataset will be in "orig_datasets", except if you use the "--clean" argument to save place (not implemented yet).

The images are all in the png format. The annotations are all in the txt format, with the following informations: "class xmin ymin xmax ymax" (multilines if multiple boxes). The class number starts from 1 to NB_OF_CATEGORIES (included). 0 may be used for the background class (not included in NB_OF_CATEGORIES).

# Available datasets

* [VOC2007](http://host.robots.ox.ac.uk/pascal/VOC/voc2007/)
* [UECFOOD100](http://foodcam.mobi/dataset100.html)
* [UECFOOD256](http://foodcam.mobi/dataset256.html)
* [Foodinc](https://finc.com/) - Private dataset (you won't be able to download the images)

