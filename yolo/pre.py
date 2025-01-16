import os
from math import ceil
import shutil 

INPUT_DIR = "C:\\Users\\mimal\\Downloads\\Guerin(1)\\Guerin(1)"
OUTPUT_DIR = ".\\Guerin"

QUAN = 0.7

# _, _, files = next(os.walk(INPUT_DIR))
# print(len(files))

_, _, files = next(os.walk(INPUT_DIR))

for i in range(len(files)):
    file_path = INPUT_DIR + "\\" + files[i]
    xml_path = INPUT_DIR + "\\page\\" + files[i].split(".")[0] + ".xml"
    new_file_dir = OUTPUT_DIR + "\\val\\images"
    new_xml_dir = OUTPUT_DIR + "\\val\\page"

    shutil.move(file_path, new_file_dir)
    shutil.move(xml_path, new_xml_dir)