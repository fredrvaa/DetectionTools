import json, cv2, random, os

path = '../DeepLabeler/data/Lade'
path2 = 'datasets/C'

# for i in range(10,11):
#     if not os.path.exists(f'{path2}{i}'):continue
#     with open(f'{path2}{i}/annotations/train.json') as af:
#         gts = json.load(af)
#         for image in gts['images']:
#             file_name = image['file_name']
#             print(file_name)
#             annotations = [y for y in gts['annotations'] if y['image_id'] == image['id']]
#             bboxes = [a['bbox'] for a in annotations]

#             img = cv2.imread(f'{path2}{i}/train/{file_name}')

#             for b in bboxes:
#                 cv2.rectangle(img,(int(b[0]),int(b[1])),(int(b[0])+int(b[2]),int(b[1])+int(b[3])),(255,0,0),2)
#             ims = cv2.resize(img,(960, 540))
#             cv2.imshow('img',ims)
#             cv2.waitKey(-1)    

with open(f'datasets/V/annotations/val.json') as af:
    gts = json.load(af)
    for image in gts['images']:
        file_name = image['file_name']
        print(file_name)
        annotations = [y for y in gts['annotations'] if y['image_id'] == image['id']]
        bboxes = [a['bbox'] for a in annotations]

        img = cv2.imread(f'datasets/V/val/{file_name}')

        for b in bboxes:
            cv2.rectangle(img,(int(b[0]),int(b[1])),(int(b[0])+int(b[2]),int(b[1])+int(b[3])),(255,0,0),2)
        ims = cv2.resize(img,(960, 540))
        cv2.imshow('img',ims)
        cv2.waitKey(-1) 