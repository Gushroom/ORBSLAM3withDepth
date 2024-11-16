import os
import shutil
import subprocess
from tqdm import tqdm
import cv2

# Path to the folder containing images
euroc_image_path = '../autodl-tmp/MH_01_easy/cam0/data'

# Create the rgb and depth directories if they don't exist
os.makedirs(f"{euroc_image_path}/rgb", exist_ok=True)
os.makedirs(f"{euroc_image_path}/depth", exist_ok=True)

# List of image extensions to consider
image_extensions = ('.png')

# Get the list of image files
image_files = [f for f in os.listdir(euroc_image_path) if f.lower().endswith(image_extensions)]

# Iterate over all image files with tqdm for progress tracking
for image in tqdm(image_files, desc="Generating Depth Images..."):
    src_path = os.path.join(euroc_image_path, image)

    # Move the image to the rgb directory
    dst_path = os.path.join(euroc_image_path, 'rgb', image)
    shutil.move(src_path, dst_path)

    # Process the image by running the infer script
    depth_dir = os.path.join(euroc_image_path, 'depth')
    try:
        subprocess.run(['python', 'run_infer_new.py', '--data_path', dst_path, '--output_dir', depth_dir, '--max_resolution', '752'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing image {image}: {e}")
        continue

    # Move the processed image to the depth directory
    processed_image = os.path.join(depth_dir, image)
    if os.path.exists(processed_image):
        # Load the processed depth image
        depth_image = cv2.imread(processed_image, cv2.IMREAD_UNCHANGED)

        # Resize the depth image to match the resolution of the grayscale image
        target_resolution = (752, 480)
        resized_depth_image = cv2.resize(depth_image, target_resolution, interpolation=cv2.INTER_NEAREST)

        # Save the resized depth image
        cv2.imwrite(processed_image, resized_depth_image)
        shutil.move(processed_image, os.path.join(depth_dir, image))
    else:
        print(f"Processed image not found: {processed_image}")