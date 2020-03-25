def xywh2xcycwh_norm(bbox, im_w, im_h):
    x_center_norm = (bbox[0] + bbox[2]/2)/im_w
    y_center_norm = (bbox[1] + bbox[3]/2)/im_h
    w_norm = bbox[2]/im_w
    h_norm = bbox[3]/im_h

    return f"{x_center_norm} {y_center_norm} {w_norm} {h_norm}"

if __name__ == '__main__':
    import argparse
    import os
    import json
    from tqdm import tqdm

    parser = argparse.ArgumentParser(description='Converts annotations from COCO format to Darknet format')
    parser.add_argument('--input_path', help="Path to input folder")
    parser.add_argument('--output_path', default='darknet_annotations', help="Path to output folder")
    args = parser.parse_args()

    # Parse arguments
    input_path, output_path = args.input_path, args.output_path

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for annotation_file in os.listdir(os.path.join(input_path, 'annotations')):
        subset = annotation_file.split('.')[0]
        if not os.path.exists(os.path.join(output_path, subset)):
            os.mkdir(os.path.join(output_path, subset))

        with open(os.path.join(input_path, 'annotations', annotation_file)) as file:
            coco_data = json.load(file)

        print(f"Converting {subset} to Darknet")
        for annotation in tqdm(coco_data['annotations']):
            image = next(image for image in coco_data['images'] if image['id'] == annotation['image_id'])
            im_w = image['width']
            im_h = image['height']
            annotation_name = image['file_name'].split('.')[0] + '.txt'
            with open(os.path.join(output_path, subset, annotation_name), 'a') as file:
                file.write(f"{annotation['category_id']} {xywh2xcycwh_norm(annotation['bbox'], im_w, im_h)}\n")
            
