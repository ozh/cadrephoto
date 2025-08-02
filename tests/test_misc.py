import os
from utils.constants import OUTPUT_FOLDER, CURRENT_PHOTO
from utils.display_next import get_current_photo

number_of_photos = len(os.listdir(OUTPUT_FOLDER))
photos = os.listdir(OUTPUT_FOLDER)
print(f"{number_of_photos} files in {OUTPUT_FOLDER}: {photos}")

# print content of current_photo.txt
try:
    with open(CURRENT_PHOTO, 'r') as f:
        image_path = f.read().strip()
        print(f"Content of {CURRENT_PHOTO} : {image_path}")
except FileNotFoundError as e:
    print(f"Error: {e}")

