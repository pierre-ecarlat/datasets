# Scripts

## Overview
```python
python scripts/compute_characteristics.py DATASET_NAME --list LIST_NAME
```
Generate a folder in the list's directory including some characteristics of a set (all, trainval, test, ..), such as:
- the 'categories_idx_per_image.txt' (line x: xth image) "image_name bb1_categ bb2_categ .."
- the 'nb_images_per_category' (line x = xth category): "nb_images"
- the 'nb_images_with_x_boxes' (line x = x nb of box): "nb_images"
`fincFormat` is the only supported format so far, this probably won't change.


```python
python scripts/display_category.py DATASET_NAME CATEG
```
Visualize all the boxes belonging to a category in a dataset (this crop the image for visualization).  


```python
python scripts/display_dataset.py DATASET_NAME
```
Visualize a dataset with its bounding boxes.  
Supports `fincFormat` and `vocFormat`.


```python
python scripts/generate_colors.sh NB_CATEGS OUTPUT_FILE
```
Generate a list of `nb_categs` colors (equally distributed over the color spectrum). The colors are RGB, following the "R G B" format, one color per line. Dataset independant.


```python
python scripts/generate_lists.sh DATASET_NAME \-\-inp all \-\-out1 trainval \-\-out2 test
```
Generate sublists from an initial set (example: generates `trainval` and `test` from the `all` set (default)). The set is splitted into two separate sets, supposed to have, as much as possible, the same class repartition (in case of imbalanced datasets). Greedy algorithm, be tolerant.  
If may also computes a characteristics folder in the lists' directory.


