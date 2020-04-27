import os,json

for d in os.listdir('datasets'):
    if not d.startswith('D') or d == 'D0': continue
    with open(('datasets/'+d+'/annotations.json')) as file:
        coco = json.load(file)

    p = ' fail'
    images = coco['images']
    annotations = coco['annotations']
    for e,a in enumerate(annotations):
        image_id = a['image_id']
        image = [x for x in images if x['id']==image_id][0]
        
        if annotations.count(a) != 1: print(a)

        for f in os.listdir(f'datasets/{d}'):
            if f.endswith('.json'): continue
            if image['file_name'] == f:
                p = ' pass'

        a['id'] = e
        a['category_id'] = 1

    for x,i in enumerate(images):
        if images.count(i) != 1:
            del images[x]
            print(i)

    with open(('datasets/'+d+'/annotations.json'),'w') as dump:
        json.dump(coco,dump)

    print(f'Dataset {d}\t {p}\t {len(images)}')

    
    # if d == 'D7':
    #     for i in sorted(file_names, key=lambda s:(ord(s[0]),ord(s[1]),ord(s[2]),
    #                                     int(s.split('_')[0][len(s.split('_')[0].rstrip('0123456789')):]),
    #                                     int(s.split('_')[1].split('.')[0]))):
