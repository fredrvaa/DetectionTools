import os
import cv2

input_path = '../videos/Lade2_val'
output_path = 'vid_ims'

if not os.path.exists(output_path):
    os.makedirs(output_path)

for video in os.listdir(input_path):
    vid_dir = os.path.join(output_path,video.split('.')[0])
    os.makedirs(vid_dir)
    print(f"Converting {video}")
    cap = cv2.VideoCapture(os.path.join(input_path,video))
    success,image = cap.read()
    i = 0
    while success:
        cv2.imwrite(f"{vid_dir}/{video.split('.')[0]}_{i}.jpg", image)     # save frame as JPEG file      
        success,image = cap.read()
        i += 1
