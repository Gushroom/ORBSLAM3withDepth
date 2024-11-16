import os
import cv2
import numpy as np
from tqdm import tqdm
import torch

# Model setup
model_dir = '/root/autodl-tmp/models'
# model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_small', pretrain=True, model_dir=model_dir)
model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_giant2', pretrain=True, model_dir=model_dir)
model.cuda().eval()

# Path to the images
image_path = '/root/autodl-tmp/cam0/data/'

# Output directories
rgb_output_dir = '/root/autodl-tmp/cam0/rgb/'
depth_output_dir = '/root/autodl-tmp/cam0/depth/'

os.makedirs(rgb_output_dir, exist_ok=True)
os.makedirs(depth_output_dir, exist_ok=True)

# Intrinsic parameters
fx, fy, cx, cy = 458, 457, 367, 248  # px
intrinsic = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

# Input size for the model
input_size = (616, 1064)  # Model-specific input size

max_depth = 0
min_depth = 0

# Process images
for image_name in tqdm(os.listdir(image_path), desc="Processing images"):
    image_full_path = os.path.join(image_path, image_name)
    if not os.path.isfile(image_full_path):
        continue

    # Load the RGB image
    rgb_origin = cv2.imread(image_full_path)[:, :, ::-1]  # Convert BGR to RGB
    h, w = rgb_origin.shape[:2]

    # Adjust input size to fit the pre-trained model
    scale = min(input_size[0] / h, input_size[1] / w)
    rgb = cv2.resize(rgb_origin, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)

    # Scale intrinsic parameters
    scaled_intrinsic = [fx * scale, fy * scale, cx * scale, cy * scale]

    # Pad the image to match the input size
    padding = [123.675, 116.28, 103.53]
    h, w = rgb.shape[:2]
    pad_h = input_size[0] - h
    pad_w = input_size[1] - w
    pad_h_half = pad_h // 2
    pad_w_half = pad_w // 2
    rgb = cv2.copyMakeBorder(
        rgb, pad_h_half, pad_h - pad_h_half, pad_w_half, pad_w - pad_w_half, cv2.BORDER_CONSTANT, value=padding
    )
    pad_info = [pad_h_half, pad_h - pad_h_half, pad_w_half, pad_w - pad_w_half]

    # Normalize the image
    mean = torch.tensor([123.675, 116.28, 103.53]).float()[:, None, None]
    std = torch.tensor([58.395, 57.12, 57.375]).float()[:, None, None]
    rgb_tensor = torch.from_numpy(rgb.transpose((2, 0, 1))).float()
    rgb_tensor = torch.div((rgb_tensor - mean), std)
    rgb_tensor = rgb_tensor[None, :, :, :].to('cuda')

    # Perform inference
    with torch.no_grad():
        pred_depth, _, _ = model.inference({'input': rgb_tensor})

    # Remove padding
    pred_depth = pred_depth.squeeze()
    pred_depth = pred_depth[
        pad_info[0]:pred_depth.shape[0] - pad_info[1],
        pad_info[2]:pred_depth.shape[1] - pad_info[3]
    ]

    # Upsample to original size
    pred_depth = torch.nn.functional.interpolate(pred_depth[None, None, :, :], rgb_origin.shape[:2], mode='bilinear').squeeze()

    # Convert from canonical camera space to real-world metric space
    canonical_to_real_scale = scaled_intrinsic[0] / 1000.0  # 1000.0 is the focal length of canonical camera
    pred_depth = pred_depth * canonical_to_real_scale  # now the depth is metric
    pred_depth = torch.clamp(pred_depth, 0, 300)

    # Convert the predicted depth to a numpy array
    depth_data = pred_depth.cpu().numpy()
    # max_depth = np.max(depth_data)
    # min_depth = np.min(depth_data)

# print(f'max depth: {max_depth}')
# print(f'min depth: {min_depth}')
    # # Save the RGB and Depth images
    # rgb_save_path = os.path.join(rgb_output_dir, image_name)
    # depth_save_path = os.path.join(depth_output_dir, os.path.splitext(image_name)[0] + '.png')

    # cv2.imwrite(rgb_save_path, cv2.imread(image_full_path))  # Save the original RGB image

    # scale_factor = 5000  # Scale factor to convert meters to integer (1 unit = 0.2 mm)
    # depth_map_scaled = (depth_data * scale_factor).astype(np.uint16)
    # cv2.imwrite(depth_save_path, depth_map_scaled)  # Save the depth map

    # Define the desired depth range 
    min_depth = 0.1 # avoid divide by 0 also we arent crashing into walls
    max_depth = 30

    import matplotlib.pyplot as plt

    # Normalize the depth data to [0, 1]
    normalized_depth = (depth_data - min_depth) / (max_depth - min_depth)

    # Create a colormap
    colormap = plt.get_cmap('viridis')

    # Apply the colormap
    depth_color_map = (colormap(normalized_depth) * 255).astype(np.uint8)

    # Save the RGB and Depth images
    rgb_save_path = os.path.join(rgb_output_dir, image_name)
    depth_save_path = os.path.join(depth_output_dir, os.path.splitext(image_name)[0] + '.png')

    cv2.imwrite(rgb_save_path, cv2.imread(image_full_path))  # Save the original RGB image
    cv2.imwrite(depth_save_path, depth_color_map[:, :, :3]) 
