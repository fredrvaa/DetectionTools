import json,os
import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

ann_type = 'bbox'
prefix = 'instances'
dataType='val2014'
ann_file = 'datasets/C10/annotations/train.json'

with open(ann_file) as gt_file:
    gts = json.load(gt_file)
    gt_images = gts['images']

    for k,z in enumerate(gts['annotations']):
        z['id'] = k
        z['iscrowd'] = 0
        z['area'] = int(z['bbox'][2]) * int(z['bbox'][3])
        z['category_id'] = 1
    print(len(gt_images))
    gts['categories'][0]['id'] = 1

    for k,z in enumerate(gts['annotations']):
        if gts['annotations'].count(z) > 1: print(z)
        

gt_test = 'gt_test.json'
with open(gt_test,'w') as out_test:
    json.dump(gts,out_test)

cocoGt = COCO(gt_test)

with open('manual/annotations/train.json') as file:
    coco = json.load(file)
    images = coco['images']
    annotations = coco['annotations']
    l = 0
    for k,a in enumerate(annotations):
        file_name = [x for x in images if int(x['id']) == int(a['image_id'])][0]['file_name']
        if file_name not in os.listdir('datasets/C10/train'): print('file not in train')
        new_image = [y for y in gt_images if y['file_name'] == file_name]
        #print(new_image)
        if len(new_image) == 0: 
            annotations.pop(k)
            continue
        l += 1
        new_image_id = new_image[0]['id']
        a['image_id'] = new_image_id
        a['score'] = 1
        a['category_id'] = 1

    print(len(annotations), l)

res_file = 'results_file.json'
with open(res_file,'w') as rf:
    json.dump(annotations,rf)

cocoDt = cocoGt.loadRes(res_file)

print('Loaded')

dts = json.load(open(res_file,'r'))
imgIds = [imid['image_id'] for imid in dts]
imgIds = sorted(list(set(imgIds)))
del dts

print('ImgIds initialized')

cocoEval = COCOeval(cocoGt,cocoDt,ann_type)
print('Eval initialized')
cocoEval.params.imgIds = imgIds
print('Params initialized')
cocoEval.evaluate()
cocoEval.accumulate()
cocoEval.summarize()