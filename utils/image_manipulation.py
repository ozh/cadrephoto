# Image manipulation
import math
import os
from pillow_heif import HeifImagePlugin

from PIL import Image, ImageOps
from utils.utils import debug_log, delete_all_but_latest_XXX, rename_file_with_timestamp
from utils.constants import OUTPUT_FOLDER


def fix_image_orientation(path):
    """
    Fix the orientation of an image based on its EXIF data.
    :param path:  Path to the image file.
    :return:  image object (PIL.Image)
    """
    pil = Image.open(path)
    pil = ImageOps.exif_transpose(pil)
    return pil


def resize_and_crop_image(image: Image) -> Image:
    """
    Resize the image to a width of 800 pixels

    :param image: an image object (PIL.Image)
    :return:  a resized and cropped image object
    """
    new_width = 800
    ratio = new_width / image.width
    new_height = int(image.height * ratio)
    resized = image.resize((new_width, new_height), Image.LANCZOS)
    debug_log(f"Redimension : {resized.size}", 'info')

    top = max(0, (resized.height - 480) // 2)
    cropped = resized.crop((0, top, 800, top + 480))
    debug_log(f"Crop : {cropped.size}", 'info')
    return cropped


def convert_image_to_jpg(input_path='', preserve_original=False):
    """
    Convert an image to JPG format if it is not already in that format.

    :param input_path: Path to the image file
    :param preserve_original: If True, the original file will not be deleted after conversion.
    :return: Path to the converted JPG file.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    # lower case ext
    ext = os.path.splitext(input_path)[1].lower()
    output_path = os.path.splitext(input_path)[0] + ".jpg"

    if ext in ['.png', '.jpg', '.jpeg', '.heic', '.heif', '.webp', ]:
        with Image.open(input_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(output_path, format="JPEG")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    debug_log(f"JPG conversion: {input_path} -> {output_path}", 'info')
    # delete original file unless stated otherwise
    if not preserve_original:
        os.remove(input_path)
    return output_path


def process_new_image(image_path):
    """
    Process a new image :
        - fix orientation
        - resize & crop
        - return new image name

    :param image_path: path to the image file
    :return: image file name
    """

    image_path = rename_file_with_timestamp(image_path)

    image = fix_image_orientation(image_path)
    image = resize_and_crop_image(image)

    # Save the processed image to the output folder, delete original image
    image_name = os.path.basename(image_path)
    image.save(f"{OUTPUT_FOLDER}/{image_name}")
    os.remove(image_path)

    # Keep only XXX most recent images
    delete_all_but_latest_XXX(OUTPUT_FOLDER)

    return image_name
