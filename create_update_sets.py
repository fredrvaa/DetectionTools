def init_coco_data():
    coco_data = {
                'info':{'date':str(datetime.now())},
                'images':[],
                'annotations':[],
                "categories": [{"supercategory": "damage_type", "id": 1, "name": "corrosion"}]
                }
    return coco_data

if __name__=='__main__':
    import os, copy
    import shutil
    import json
    from datetime import datetime
    
    SIZE = 200
    INPUT_PATH = '../data/labeled'
    OUTPUT_PATH = 'datasets'

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH, exist_ok=True)

    current_dir = None
    dataset_count = 0
    counter = 0
    objects_counter = 0
    current_coco_data = init_coco_data()
    
    image_id = 0
    annotation_id = 0
    with open(os.path.join(OUTPUT_PATH,'log.txt'), 'a') as log_file:
        log_file.write('----New Session----\n')

    with open('../MTTK-Thesis/data/dataset_sizes.csv') as reader:
        for i,line in enumerate(reader):
            if i == 0: continue
            name = line.split(',')[2]

            with open(os.path.join(INPUT_PATH,name,'annotations.json')) as annotations_file:
                annotations = json.load(annotations_file)

            for file_name in sorted([f for f in os.listdir(os.path.join(INPUT_PATH,name)) if f.endswith('.jpg')],
                                key=lambda d:(int(d.rstrip('.jpg').split('_')[1]))):
                # Init dir
                if current_dir == None:
                    dataset_count += 1
                    current_dir = f"D{dataset_count}"
                    os.makedirs(os.path.join(OUTPUT_PATH,current_dir),exist_ok=True)
                    print('Created dataset',current_dir)

                added = False
                # Copy images and annotations
                for image in annotations['images']:
                    if image['file_name'] == file_name:
                        # Copy image and make sure shutil copies it
                        shutil.copy(os.path.join(INPUT_PATH,name,file_name), os.path.join(OUTPUT_PATH,current_dir,file_name))
                        l = len(os.listdir(os.path.join(OUTPUT_PATH,current_dir))) - 1
                        if l != counter: continue

                        # Extend with annotations
                        annos = [a for a in copy.deepcopy(annotations['annotations']) if a['image_id'] == image['id']]
                        # if len(annos) > 2: 
                        #     print(file_name)
                        #     print(image)
                        #     print(annos)
                        for an in annos:
                            an['id'] = annotation_id
                            an['image_id'] = image_id
                            annotation_id += 1
                        current_coco_data['annotations'].extend(annos)

                         # Append image
                        image['id'] = image_id
                        current_coco_data['images'].append(image)
                        image_id += 1
                        
                        added = True
                        counter += 1
                        break

                if added == False: print(file_name, "not added")
                if counter >= SIZE:
                    #Save data
                    with open(os.path.join(OUTPUT_PATH,current_dir,'annotations.json'), 'w') as file:
                        json.dump(current_coco_data, file)
                    with open(os.path.join(OUTPUT_PATH,'log.txt'), 'a') as log_file:
                        log_file.write(f"{current_dir}: {objects_counter}\n")
                    
                    # Reset vars
                    counter = 0
                    image_id = 0
                    annotation_id = 0
                    
                    dataset_count += 1
                    objects_counter = len(current_coco_data['annotations'])

                    # New dir
                    current_dir = f"D{dataset_count}"
                    os.makedirs(os.path.join(OUTPUT_PATH,current_dir),exist_ok=True)

                    # New annotations
                    current_coco_data = init_coco_data()
                    print('Created dataset',current_dir)

                    #if current_dir == 'D2': break
            #if current_dir == 'D2': break

        

                