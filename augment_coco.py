import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage


seq = iaa.Sequential(
    [
        iaa.Fliplr(0.5), # horizontally flip 50% of all images
        iaa.Flipud(0.5), # vertically flip 50% of all images
        iaa.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)}, # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)} # translate by -20 to +20 percent (per axis)
        ),
        iaa.GaussianBlur(sigma=(0, 2))
    ]
)

if __name__=='__main__':
    import os, argparse, json
    import cv2
    from tqdm import tqdm

    parser = argparse.ArgumentParser(description='Augment folder of images')
    parser.add_argument('--input', type=str, help='path to input folder')
    parser.add_argument('--output', type=str, help='path to ouput folder')
    parser.add_argument('--n', type=int, help='number of augmentations')
    args = parser.parse_args()
    if not os.path.exists(args.output):
        os.mkdir(args.output)

    json_files = [x for x in os.listdir(args.input) if x.endswith('.json')]
    assert len(json_files) == 1, print('Not exactly 1 json file in inpout folder')

    with open(os.path.join(args.input, json_files[0])) as file:
        coco_data = json.load(file)

    new_coco_data = {
                    'info': coco_data['info'],
                    'images': [],
                    'annotations': [],
                    'categories': coco_data['categories']
                    }

    image_id = 0
    annotations_id = 0
    for image_data in tqdm(coco_data['images']):
        annotations = [a for a in coco_data['annotations'] if a['image_id'] == image_data['id']]
        bbs = [a['bbox'] for a in annotations]


        image = cv2.imread(os.path.join(args.input, image_data['file_name']))
        bboxes = BoundingBoxesOnImage([BoundingBox(x1=b[0],y1=b[1],x2=b[0]+b[2],y2=b[1]+b[3]) for b in bbs], shape=image.shape)
        
        # Perform augmentations
        for n in range(args.n):
            image_aug, bboxes_aug = seq(image=image, bounding_boxes=bboxes)

            # Create COCO data
            image_data = {
                        'id': image_id,
                        'width': image_aug.shape[1],
                        'height': image_aug.shape[0],
                        'file_name': f"{image_id}.jpg"
                        }
            bboxes_aug = bboxes_aug.remove_out_of_image().clip_out_of_image()
            annotations_data = []
            for b in bboxes_aug:
                annotation_data = {
                                'id': annotations_id,
                                'image_id': image_id,
                                'bbox': [int(b.x1), int(b.y1), int(b.x2 - b.x1), int(b.y2 - b.y1)],
                                'category_id': 0
                                }
                annotations_data.append(annotation_data)
                annotations_id += 1

            new_coco_data['images'].append(image_data)
            new_coco_data['annotations'].extend(annotations_data)

            cv2.imwrite(os.path.join(args.output, f"{image_id}.jpg"), image_aug)

            image_id += 1
            

    with open(os.path.join(args.output, f"annotations.json"), 'w') as file:
        json.dump(new_coco_data, file)

        
        


