# Scripts

## Overview

```
bash scripts/get_.sh DATASET_NAME
```
Get the dataset DATASET_NAME; List of action:
- Download the dataset and store it in MAIN_DIR/datasets_orig/DATASET_NAME/
    > Uses MAIN/builders/DATASET_NAME/download.sh
- Convert it into a basic format (see the 'datasets' section) and store it in MAIN_DIR/DATASET_NAME/
    > Uses MAIN/builders/DATASET_NAME/convert.sh
- Generate the colors for the categories in MAIN_DIR/DATASET_NAME/infos/colors.txt
    > Uses MAIN/builders/DATASET_NAME/categories.txt
- Generate the list of all the images, store it in MAIN_DIR/DATASET_NAME/ImageSets/all.txt
- Generate the set lists (trainval, test), store it in MAIN_DIR/DATASET_NAME/ImageSets/
- Create a symbolic link between the dataset directory to all the paths stored in $LINK_TO

```
python scripts/generate_lists.py DATASET_NAME PROPORTION
```
Generate the lists for the tranval and the test sets. Will create a 'caracteristics' directory into ImageSets/, and will use it to make sure that both sets have the same proportion (included between 0 and 1) of each class.

```
python scripts/reduce_dataset.py DATASET_NAME DATASET_REDUCED_NAME path/to/reducing/files
```
Reduce a dataset with high level category (white rice, crustacean, ...) into an lower one (with categories such as rice, fish, ...). Requires a transition file and a categories file in <path/to/reducing/files>. The transition file should list the categories to change (<old_categ_nb> <new_categ_nb>). See Foodinc/reduced_to_18/ directory for an example.

```
python scripts/compute_caracteristics.py DATASET_NAME --list LIST_NAME
```
Generate a folder into ImagSets including caracteristics of a set (all, trainval, test, ..):
- the 'categories_idx_per_image.txt' (line x: xth image) <image_name> <bb1_categ> <bb2_categ> <..>
- the 'nb_images_per_category' (line x = xth category): <nb_images>
- the 'nb_images_with_x_boxes' (line x = x nb of box): <nb_images>

```
bash scripts/generate_colors.sh DATASET_NAME NB_CATEG
```
Generate a color for each category (equally distributed over the color spectrum)

```
bash scripts/display_dataset.sh DATASET_NAME
```
Visualize a dataset with its bounding boxes.

```
bash scripts/display_category.sh DATASET_NAME
```
Visualize the images for a category in a dataset with its bounding boxes.


