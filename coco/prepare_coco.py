import os, glob, shutil, datetime
import numpy as np
from tqdm import tqdm
from PIL import Image

# cfg file must be specified to run script
# each line in cfg specifies 1) a path to dataset containing .json file and images 2) wether the image that are annotated should be aggregated

def to_bool(s):
    return True if s.lower() in ['true', 't', 'yes', 'y'] else False

def parse_cfg(cfg):
    with open(cfg) as file:
        datasets = [x.split(' ') for x in [line.rstrip() for line in file]]
    return datasets

def initialize_dict():
    return {'info':{"date_created":str(datetime.datetime.now())}, 'images':[], 'annotations':[], 'categories': [{'supercategory': "corrosion","id": 1,"name": "corrosion"}]}

def splits_to_subsets(splits):
    subsets = ['train', 'val', 'test']
    splits = list(map(float, list(splits.split('/'))))
    subsets = subsets[:len(splits)]

    return [{'subset':s,'prob':p} for (s,p) in zip(subsets, splits)], splits

def split_dataset(coco_dict, subsets, splits, remove, src_folder, dst_folder, detectron2):
    for image in tqdm(coco_dict['images']):
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

        # Check if image has been anotated
        annotations = []
        for d in coco_dict['annotations']:
            if (d['image_id'] == str(image['id'])):
                d['image_id'] = int(d['image_id'])
                if detectron2:
                    from detectron2.structures import BoxMode
                    d['category_id'] = 1
                    d['segmentation'] = [d['segmentation']]
                    #d['bbox_mode'] = BoxMode.XYXY_ABS
                    #bbox = d['bbox']
                    #d['bbox'][2] = bbox[0]+bbox[2]
                    #['bbox'][3] = bbox[1]+bbox[3]
                annotations.append(d)

        if remove:
            if len(annotations) is 0:
                continue

        # Append data to correct subset
        subset = np.random.choice(subsets, 1, p=splits)[0]
        subset['coco_data']['images'].append(image)
        subset['coco_data']['annotations'].extend(annotations)

        # Saving images instead of copying to remove metadata which can cause conflict when loading images with PIL
        img.convert('RGB').save(f"{dst_folder}/{subset['subset']}/{image['file_name']}")   

    return subsets

if __name__ == '__main__':
    import json
    import argparse

    parser = argparse.ArgumentParser(description='Merges coco.json files and splits dataset')
    parser.add_argument('--cfg', help="Path to cfg file for jsons. Each line in the cfg specifies path to dataset and specifies if images without annotations should be skipped. Format:'/path/to/dataset True/False'")
    parser.add_argument('--output_path', default='prepared_coco_data', help="Path to output folder")
    parser.add_argument('--splits', default='0.85/0.15', help="Subset splits (train/val/test) as percentages (must equal 1) of whole dataset. Format:'x' for only train; or 'x/y' for train and val; or 'x/y/z' for train, val, and test")
    parser.add_argument('--detectron2', action='store_true', help="Add coco data that is needed for detectron2")
    args = parser.parse_args()

    # Parse arguments
    datasets = parse_cfg(args.cfg)
    output_path, splits, detectron2 = args.output_path, args.splits, args.detectron2

    # Initialize subset dicts
    subsets, splits = splits_to_subsets(splits)
    for subset in subsets:
        subset['coco_data'] = initialize_dict()

    # Prepare folders
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        os.mkdir(os.path.join(output_path, 'annotations'))
        for subset in subsets:
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
        print(f"Started splitting {path}. Remove images without annotations: {str(remove)}")

        # Read annotated coco data
        json_file = [x for x in os.listdir(path) if x.endswith(".json")][0]
 
        with open(os.path.join(path, json_file), 'r') as file:
            coco_dict = json.load(file)

        subsets = split_dataset(coco_dict, subsets, splits, remove, path, output_path, detectron2)

        print(f"Finished splitting {path}")
            
    for subset in subsets:
        with open(f"{output_path}/annotations/{subset['subset']}.json", 'w') as file:
            json.dump(subset['coco_data'], file)

    print("Created coco dataset with following attributes:")
    for subset in subsets:
        print(f"{subset['subset']} \t | #images = {len(subset['coco_data']['images'])} \t | #annotations = {len(subset['coco_data']['annotations'])}")
        

    
        


