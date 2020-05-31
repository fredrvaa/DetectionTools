import json, cv2, random, os

dataset = '../datasets/T'


with open(f'{dataset}/annotations/test.json') as af:
    gts = json.load(af)

os.makedirs(f'style/T', exist_ok=True)

for i in range(100,200,5):
    image=gts['images'][i]  
    file_name = image['file_name']
    print(file_name)
    annotations = [y for y in gts['annotations'] if y['image_id'] == image['id']]
    bboxes = [a['bbox'] for a in annotations]

    img = cv2.imread(f'{dataset}/test/{file_name}')
    width = img.shape[1]

    for b in bboxes:
        cv2.rectangle(img,(int(b[0]),int(b[1])),(int(b[0])+int(b[2]),int(b[1])+int(b[3])),(255,0,0),int(width/250))
    
    cv2.imwrite(f'style/T/{i}.jpg', img)