import os, json, random
import cv2

#Check json values
for annotation_file in os.listdir(os.path.join('prepared_coco_data', 'annotations')):
    subset = annotation_file.split('.')[0]

    with open(os.path.join('prepared_coco_data', 'annotations', annotation_file)) as file:
        coco_data = json.load(file)

    # Check image ids
    for i, image in enumerate(coco_data['images']):
        if image['id'] != i: print(image)

    # Check annotation image_ids
    for annotation in coco_data['annotations']:
        try:
            image = next(image for image in coco_data['images'] if str(image['id']) == str(annotation['image_id']))
        except:
            print("Didnt find image for ", annotation)

