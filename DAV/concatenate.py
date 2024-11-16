import os
import subprocess
import cv2

video_dir = 'concatenation'
num_chunks = 10
frame_rate = 20

# Extract frames from each video sequentially
frames_dir = os.path.join(video_dir, 'frames')
os.makedirs(frames_dir, exist_ok=True)

for i in range(1, num_chunks + 1):
    video_path = os.path.join(video_dir, f'depthvideos/video{i}.mp4')
    output_dir = os.path.join(frames_dir, f'video{i}')
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', video_path,
        os.path.join(output_dir, 'frame%04d.png')
    ]
    subprocess.run(ffmpeg_cmd, check=True)

# Reassemble frames in linear concatenation order
reordered_frames_dir = os.path.join(video_dir, 'reordered_frames')
os.makedirs(reordered_frames_dir, exist_ok=True)

target_size = (752, 480)
frame_index = 1

# Process each video's frames in order
for i in range(1, num_chunks + 1):
    video_frames_dir = os.path.join(frames_dir, f'video{i}')
    frame_files = sorted(os.listdir(video_frames_dir))  # Ensure frames are in order
    
    for frame_file in frame_files:
        src_path = os.path.join(video_frames_dir, frame_file)
        image = cv2.imread(src_path)
        if image is not None:
            resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
            dst_path = os.path.join(reordered_frames_dir, f'frame{frame_index:04d}.png')
            cv2.imwrite(dst_path, resized_image)
            frame_index += 1

# Assemble the reordered frames into the final video with linear concatenation
final_video_path = os.path.join(video_dir, 'final_video.mp4')
ffmpeg_cmd = [
    'ffmpeg',
    '-framerate', str(frame_rate),
    '-pattern_type', 'glob',
    '-i', os.path.join(reordered_frames_dir, '*.png'),
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    final_video_path
]
subprocess.run(ffmpeg_cmd, check=True)
