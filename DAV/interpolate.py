import os
import subprocess
import cv2
import numpy as np

video_dir = 'interpolation'
num_chunks = 9
frame_rate = 20

# Extract frames from each video
frames_dir = os.path.join(video_dir, 'frames')
os.makedirs(frames_dir, exist_ok=True)

for i in range(num_chunks):
    video_path = os.path.join(video_dir, f'depthvideos/video{i+1}.mp4')
    output_dir = os.path.join(frames_dir, f'video{i+1}')
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', video_path,
        os.path.join(output_dir, 'frame%04d.png')
    ]
    subprocess.run(ffmpeg_cmd, check=True)

# Reassemble frames in the desired order
reordered_frames_dir = os.path.join(video_dir, 'reordered_frames')
os.makedirs(reordered_frames_dir, exist_ok=True)

# Calculate the total number of frames considering the discrepancy
frame_count = len(os.listdir(os.path.join(frames_dir, f'video1')))  # video1 has 410 frames
total_frames = frame_count * num_chunks

target_size = (752, 480)

# # Time-axis convolution parameters
# kernel_size = 3  # Kernel size for time-axis convolution
# padding_method = 'replicate'  # Padding method: 'zero', 'replicate', 'circular'

# # Function to apply time-axis convolution
# def time_axis_convolution(frames, kernel_size, padding_method):
#     half_kernel = kernel_size // 2
#     padded_frames = np.zeros((frames.shape[0] + 2 * half_kernel, *frames.shape[1:]), dtype=frames.dtype)
    
#     if padding_method == 'zero':
#         padded_frames[half_kernel:-half_kernel] = frames
#     elif padding_method == 'replicate':
#         padded_frames[half_kernel:-half_kernel] = frames
#         padded_frames[:half_kernel] = frames[0]
#         padded_frames[-half_kernel:] = frames[-1]
#     elif padding_method == 'circular':
#         padded_frames[half_kernel:-half_kernel] = frames
#         padded_frames[:half_kernel] = frames[-half_kernel:]
#         padded_frames[-half_kernel:] = frames[:half_kernel]
    
#     smoothed_frames = np.zeros_like(frames)
#     for i in range(frames.shape[0]):
#         smoothed_frames[i] = np.mean(padded_frames[i:i+kernel_size], axis=0)
    
#     return smoothed_frames

# # Load all frames into a numpy array
# all_frames = []
# for frame_index in range(frame_count):
#     for i in range(num_chunks):
#         frame_file = f'frame{frame_index+1:04d}.png'
#         src_path = os.path.join(frames_dir, f'video{i+1}', frame_file)
#         try: 
#             image = cv2.imread(src_path)
#             resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
#             all_frames.append(resized_image)
#         except:
#             continue

# all_frames = np.array(all_frames)

# # Apply time-axis convolution
# smoothed_frames = time_axis_convolution(all_frames, kernel_size, padding_method)

# # Save the smoothed frames
# for frame_index in range(frame_count):
#     for i in range(num_chunks):
#         dst_path = os.path.join(reordered_frames_dir, f'frame{frame_index*num_chunks + i + 1:04d}.png')
#         # Ensure the index is within bounds
#         if frame_index * num_chunks + i < len(smoothed_frames):
#             cv2.imwrite(dst_path, smoothed_frames[frame_index * num_chunks + i])

# Assemble the reordered frames into a final video with smooth transitions
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