import os

base_url = 'http://robotics.ethz.ch/~asl-datasets/ijrr_euroc_mav_dataset/machine_hall/'
datasets = ['MH_01_easy']

target_dir = '../autodl-tmp'
os.chdir(target_dir)

for dataset in datasets:
    os.system(f'wget {base_url}{dataset}/{dataset}.zip')
    os.system(f'unzip {dataset}.zip')
    os.system(f'rm {dataset}.zip')
    os.system(f'mv mav0 {dataset}')