import os, json, random
import cv2

dataset = 'datasets/C10'

#Check json values
for annotation_file in os.listdir(os.path.join(dataset, 'annotations')):
    subset = annotation_file.split('.')[0]

    with open(os.path.join(dataset, 'annotations', annotation_file)) as file:
        coco_data = json.load(file)

    # Check image ids
    for i, image in enumerate(coco_data['images']):
        if image['id'] != i: print(image)

    # Check annotation image_ids and out of bounds
    for annotation in coco_data['annotations']:
        try:
            image = next(image for image in coco_data['images'] if str(image['id']) == str(annotation['image_id']))
            bbox = annotation['bbox']
            
        except:
            print("Didnt find image for ", annotation)

        assert 0 <= bbox[0] <= image['width'], f"x1 out of bounds for {annotation}"
        assert 0 <= bbox[1] <= image['height'], f"y1 out of bounds for {annotation}"
        assert 0 <= bbox[2] <= image['width'] - bbox[0], f"w out of bounds for {annotation}"
        assert 0 <= bbox[3] <= image['height'] - bbox[1], f"h out of bounds for {annotation}"
    print(annotation_file, ' pass')

        
            

