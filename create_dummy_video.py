import cv2
import numpy as np
import os

def create_dummy_video(path, duration=2, fps=10, size=(320, 240)):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    total_frames = int(duration * fps)
    for i in range(total_frames):
        # Simple moving color gradient
        img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        color = (i * 5 % 256, i * 3 % 256, i * 7 % 256)
        img[:] = color
        out.write(img)
    out.release()
    print(f"Dummy video created at {path}")

if __name__ == '__main__':
    os.makedirs(os.path.dirname(path := 'd:/NEUROFRAME X/dummy.mp4'), exist_ok=True)
    create_dummy_video(path)
