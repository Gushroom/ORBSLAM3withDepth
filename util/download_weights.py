from huggingface_hub import hf_hub_download

# 定义模型名称和文件路径
repo_id = "hhyangcs/depth-any-video"
files_to_download = [
    "vae/config.json",
    "vae/diffusion_pytorch_model.safetensors",
    "scheduler/scheduler_config.json",
    "unet/config.json",
    "unet/diffusion_pytorch_model.safetensors",
    "unet_interp/config.json",
    "unet_interp/diffusion_pytorch_model.safetensors"
]

# 下载文件到指定目录
local_dir = "/root/autodl-tmp/dav/models"  # 指定目标目录
for file in files_to_download:
    hf_hub_download(repo_id=repo_id, filename=file, local_dir=local_dir)