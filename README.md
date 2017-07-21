This project contains all the scripts I use for downloading / converting / manipulating / analyzing datasets. Most of them have been written to be generic, but are still quite high level, so any uncommon use may work, but there is no guarantee. These datasets are used in my projects, see the other repositories for some example of use.

## Requirements
```shell
$ apt install xml-twig-tools 
```
Note1: the conversion into tfRecords require -obviously- Tensorflow.
Note2: may not be all.

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

## Current datasets
* [VOC2007](http://host.robots.ox.ac.uk/pascal/VOC/voc2007/)
* [UECFOOD100](http://foodcam.mobi/dataset100.html)
* [UECFOOD256](http://foodcam.mobi/dataset256.html)
* [Foodinc](https://finc.com/) - Private dataset (you won't be able to download the images)

