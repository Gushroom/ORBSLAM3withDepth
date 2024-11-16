import csv

euroc_path = '../autodl-tmp/MH_01_easy/cam0/data.csv'
output_path = '../autodl-tmp/MH_01_easy/cam0/association.txt'

with open(euroc_path, 'r') as file, open(output_path, 'w', newline='') as output_file:
    reader = csv.reader(file)
    writer = csv.writer(output_file)
    
    # Skip the first line
    next(reader)
    
    for row in reader:
        timestamp = row[0]
        rgb_filename = f'rgb/{timestamp}.png'
        depth_filename = f'depth/{timestamp}.png'
        output_file.write(f"{timestamp} {rgb_filename} {timestamp} {depth_filename}\n")