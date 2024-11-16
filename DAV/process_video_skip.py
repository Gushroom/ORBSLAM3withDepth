import os
import subprocess
from tqdm import tqdm
import shutil

euroc_image_path = '../autodl-tmp/MH_01_easy/cam0/data'
frame_rate = 20
first_timestamp = "1403636579813555456"
timestamp_increment = 500000  # 0.5 milliseconds
target_resolution = (752, 480)

# Create the rgb and depth directories if they don't exist
rgb_dir = os.path.join(euroc_image_path, 'rgb')
depth_dir = os.path.join(euroc_image_path, 'depth')
video_dir = os.path.join(euroc_image_path, 'video')
os.makedirs(rgb_dir, exist_ok=True)
os.makedirs(depth_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

# List of image extensions to consider
image_extensions = ('.png')

# Get the list of image files
image_files = sorted([f for f in os.listdir(euroc_image_path) if f.lower().endswith(image_extensions)])

# Number of chunks
num_chunks = 9

# Create directories for each chunk
for i in range(num_chunks):
    chunk_dir = os.path.join(rgb_dir, f'chunk{i+1}')
    os.makedirs(chunk_dir, exist_ok=True)

# Copy images to respective chunk directories with frame skipping
for i, image in enumerate(tqdm(image_files, desc="Copying images to chunk directories...")):
    chunk_index = i % num_chunks
    chunk_dir = os.path.join(rgb_dir, f'chunk{chunk_index+1}')
    src_path = os.path.join(euroc_image_path, image)
    dst_path = os.path.join(chunk_dir, image)
    shutil.copy(src_path, dst_path)

# Assemble images into videos for each chunk
for i in range(num_chunks):
    chunk_dir = os.path.join(rgb_dir, f'chunk{i+1}')
    video_path = os.path.join(video_dir, f'video{i+1}.mp4')
    ffmpeg_cmd = [
        'ffmpeg',
        '-framerate', str(frame_rate),
        '-pattern_type', 'glob',
        '-i', os.path.join(chunk_dir, '*.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        video_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)

# # Create directories for each chunk
# for i in range(num_chunks):
#     chunk_dir = os.path.join(rgb_dir, f'chunk{i+1}')
#     os.makedirs(chunk_dir, exist_ok=True)

# # Divide images evenly across chunks
# chunk_size = len(image_files) // num_chunks
# remainder = len(image_files) % num_chunks

# # Copy images to respective chunk directories
# image_index = 0
# for i in tqdm(range(num_chunks), desc="Copying images to chunk directories..."):
#     # Determine chunk size (if remainder, add 1 to the first few chunks)
#     current_chunk_size = chunk_size + 1 if i < remainder else chunk_size
#     chunk_dir = os.path.join(rgb_dir, f'chunk{i+1}')

#     # Copy images to the current chunk directory
#     for j in range(current_chunk_size):
#         image = image_files[image_index]
#         src_path = os.path.join(euroc_image_path, image)
#         dst_path = os.path.join(chunk_dir, image)
#         shutil.copy(src_path, dst_path)
#         image_index += 1

# # Assemble images into videos for each chunk
# for i in range(num_chunks):
#     chunk_dir = os.path.join(rgb_dir, f'chunk{i+1}')
#     video_path = os.path.join(video_dir, f'video{i+1}.mp4')
#     ffmpeg_cmd = [
#         'ffmpeg',
#         '-framerate', str(frame_rate),
#         '-pattern_type', 'glob',
#         '-i', os.path.join(chunk_dir, '*.png'),
#         '-c:v', 'libx264',
#         '-pix_fmt', 'yuv420p',
#         video_path
#     ]
#     subprocess.run(ffmpeg_cmd, check=True)

# Process the video to generate depth images
depth_video_path = os.path.join(video_dir, 'depthvideo')
for i in range(1, 10):
    try:
        subprocess.run(['python', 
                        'run_infer_new.py', 
                        '--data_path', f'../autodl-tmp/MH_01_easy/cam0/data/video/video{i}.mp4', 
                        '--output_dir', depth_video_path, 
                        '--max_resolution', '376',
                        '--num_frames', '64',
                        '--decode_chunk_size', '16',
                        '--num_interp_frames', '16',
                        '--num_overlap_frames', '6'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {e}")

# # Cut the depth video into images with customized increments
# ffmpeg_cut_cmd = [
#     'ffmpeg',
#     '-i', os.path.join(depth_video_path, "video.mp4"),
#     '-start_number', first_timestamp,
#     '-vf', f'fps={frame_rate},setpts=N*{timestamp_increment}/TB',
#     os.path.join(depth_dir, '%010d.png')
# ]
# subprocess.run(ffmpeg_cut_cmd, check=True)

# # Resize depth images to the target resolution
# depth_images = [f for f in os.listdir(depth_dir) if f.lower().endswith(image_extensions)]
# for image in tqdm(depth_images, desc="Resizing depth images..."):
#     src_path = os.path.join(depth_dir, image)
#     img = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)
#     resized_img = cv2.resize(img, target_resolution, interpolation=cv2.INTER_NEAREST)
#     cv2.imwrite(src_path, resized_img)