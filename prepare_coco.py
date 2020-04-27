import os, glob, shutil, datetime, copy
import json
import numpy as np
from tqdm import tqdm
from PIL import Image

# cfg file must be specified to run script. Example /path/to/dataset True

# Each line in cfg specifies:
# 1) a path to dataset containing .json file and images 
# 2) wether images without annotation should be removed

def to_bool(s):
    return True if s.lower() in ['true', 't', 'yes', 'y'] else False

def parse_cfg(cfg):
    with open(cfg) as file:
        datasets = [x.split(' ') for x in [line.rstrip() for line in file]]
    return datasets

def initalize_data(output_path, subset):
    subset_path = os.path.join(output_path, 'annotations', f"{subset}.json")
    {'info':{"date_created":str(datetime.datetime.now())}, 'images':[], 'annotations':[], 'categories': [{'supercategory': "corrosion", "id": 0,"name": "corrosion"}]}
    if os.path.exists(subset_path):
        with open(subset_path) as file:
            return json.load(file)
    return {'info':{"date_created":str(datetime.datetime.now())}, 'images':[], 'annotations':[], 'categories': [{'supercategory': "corrosion","id": 0,"name": "corrosion"}]}

def splits_to_subsets(splits):
    subsets = ['train', 'val', 'test']
    splits = list(map(float, list(splits.split('/'))))
    subsets = subsets[:len(splits)]

    return [{'subset':s,'prob':p} for (s,p) in zip(subsets, splits)], splits

def split_dataset(coco_data, subsets, splits, remove, src_folder, dst_folder):
    ids = [len(s['coco_data']['images']) for s in subsets]
    anno_ids = [len(s['coco_data']['annotations']) for s in subsets]
    for image in tqdm(coco_data['images']):
        subset = np.random.choice(subsets, 1, p=splits)[0]
        
        # Check if image is present
        file_name = image['file_name']
        if os.path.exists(f'dataset/train/{file_name}'):
            print(f"Skipped {file_name} because it was not found in {src_folder}")
            continue

        try:
            img = Image.open(os.path.join(src_folder, file_name))
        except:
            print(f"Skipped {file_name} because it could not be loaded")
            continue

        # Check if image has been annotated
        annotations = [annotation for annotation in coco_data['annotations'] if str(annotation['image_id']) == str(image['id'])]
        if remove and len(annotations) is 0: continue

        for annotation in annotations:
            new_annotation = {}
            new_annotation['id'] = anno_ids[subsets.index(subset)]
            new_annotation['image_id'] = ids[subsets.index(subset)]
            
            bbox = copy.deepcopy(annotation['bbox'])
            # Check if out of bounds in wrong direction
            if bbox[0] > image['width'] or bbox[1] > image['height'] or bbox[2] <= 0 or bbox[3] <= 0:
                print(f"Out of bounds bbox: {bbox} | Width: {image['width']}, Height: {image['height']}")
                continue

            # Check if x,y slightly out of bounds
            if bbox[0] < 0:
                bbox[2] += bbox[0]
                bbox[0] = 0

            if bbox[1] < 0: 
                bbox[3] += bbox[1]
                bbox[1] = 0

            # Check if w,h slightly out of bounds
            if bbox[0] + bbox[2] > image['width']: bbox[2] = image['width'] - bbox[0]
            if bbox[1] + bbox[3] > image['height']: bbox[3] = image['height'] - bbox[1]
            
            new_annotation['bbox'] = bbox
            new_annotation['category_id'] = 1
            new_annotation['iscrowd'] = 0
            new_annotation['area'] = bbox[2] * bbox[3]
            subset['coco_data']['annotations'].append(new_annotation)

            anno_ids[subsets.index(subset)] += 1
        
        image['id'] = ids[subsets.index(subset)]
        subset['coco_data']['images'].append(image)

        ids[subsets.index(subset)] += 1

        img.convert('RGB').save(f"{dst_folder}/{subset['subset']}/{image['file_name']}")   

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Merges coco.json files and splits dataset')
    parser.add_argument('--cfg', help="Path to cfg file for jsons. Each line in the cfg specifies path to dataset and specifies if images without annotations should be skipped. Format:'/path/to/dataset True/False'")
    parser.add_argument('--output_path', default='prepared_coco_data', help="Path to output folder")
    parser.add_argument('--splits', default='0.70/0.15/0.15', help="Subset splits (train/val/test) as percentages (must equal 1) of whole dataset. Format:'x' for only train; or 'x/y' for train and val; or 'x/y/z' for train, val, and test")
    args = parser.parse_args()

    # Parse arguments
    datasets = parse_cfg(args.cfg)
    output_path, splits = args.output_path, args.splits

    # Initialize subset dicts
    subsets, splits = splits_to_subsets(splits)
    prev_subset_data = {}
    for subset in subsets:
        subset['coco_data'] = initalize_data(output_path, subset['subset'])
        prev_subset_data[subset['subset']] = {'num_images':0, 'annotations':0}
        prev_subset_data[subset['subset']]['num_images'] = len(subset['coco_data']['images'])
        prev_subset_data[subset['subset']]['num_annotations'] = len(subset['coco_data']['annotations'])

    # Prepare folders
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    if not os.path.exists(os.path.join(output_path, 'annotations')):
        os.mkdir(os.path.join(output_path, 'annotations'))
    for subset in subsets:
        if not os.path.exists(os.path.join(output_path, subset['subset'])):
            os.mkdir(os.path.join(output_path, subset['subset']))

    # Make sure exactly one .json file in each dataset directory
    for dataset in datasets:
        path = dataset[0]
        json_file = [x for x in os.listdir(path) if x.endswith(".json")]
        assert len(json_file) == 1

    # Merge coco datasets and split into subsets
    for dataset in datasets:
        path = dataset[0]
        remove = to_bool(dataset[1])
        print(f"Adding {path}. Remove images without annotations: {str(remove)}")

        # Read annotated coco data
        json_file = [x for x in os.listdir(path) if x.endswith(".json")][0]
 
        with open(os.path.join(path, json_file), 'r') as file:
            coco_data = json.load(file)
        
        split_dataset(coco_data, subsets, splits, remove, path, output_path)

            
    for subset in subsets:
        with open(f"{output_path}/annotations/{subset['subset']}.json", 'w') as file:
            json.dump(subset['coco_data'], file)

    print("Created coco dataset with following attributes:")
    for subset in subsets:
        image_num = len(subset['coco_data']['images'])
        new_image_num = len(subset['coco_data']['images']) - prev_subset_data[subset['subset']]['num_images']
        annotations_num = len(subset['coco_data']['annotations'])
        new_annotations_num = len(subset['coco_data']['annotations']) - prev_subset_data[subset['subset']]['num_annotations']
        print(f'''{subset['subset']} \t | #images = {image_num} ({new_image_num} new)\t | #annotations = {annotations_num} ({new_annotations_num} new)''')
        

    
        


