# Image manipulation
import math
import os
import sys

if sys.platform != "win32":
    import pyheif

from PIL import Image, ImageOps
from utils.utils import debug_log, delete_all_but_latest_XXX, rename_file_with_timestamp
from utils.constants import PALETTE, OUTPUT_FOLDER


def fix_image_orientation(path):
    pil = Image.open(path)
    pil = ImageOps.exif_transpose(pil)
    return pil


def resize_and_crop_image(image):
    new_width = 800
    ratio = new_width / image.width
    new_height = int(image.height * ratio)
    resized = image.resize((new_width, new_height), Image.LANCZOS)
    debug_log(f"Redimension : {resized.size}", 'info')

    top = max(0, (resized.height - 480) // 2)
    cropped = resized.crop((0, top, 800, top + 480))
    debug_log(f"Crop : {cropped.size}", 'info')
    return cropped


def perceptual_distance(c1, c2):
    # Pondération perceptuelle RGB (ex: luminosité humaine)
    return math.sqrt(
        0.3 * (c1[0] - c2[0]) ** 2 +
        0.59 * (c1[1] - c2[1]) ** 2 +
        0.11 * (c1[2] - c2[2]) ** 2
    )


def closest_palette_color(r, g, b):
    return min(PALETTE, key=lambda c: perceptual_distance((r, g, b), c))


def apply_floyd_steinberg_dither(image):
    """Applique un dithering Floyd–Steinberg personnalisé avec la palette Spectra6."""
    image = image.convert("RGB")
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            old_r, old_g, old_b = pixels[x, y]
            new_r, new_g, new_b = closest_palette_color(old_r, old_g, old_b)
            pixels[x, y] = (new_r, new_g, new_b)

            err_r = old_r - new_r
            err_g = old_g - new_g
            err_b = old_b - new_b

            def distribute(dx, dy, factor):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    pr, pg, pb = pixels[nx, ny]
                    pr = min(255, max(0, int(pr + err_r * factor)))
                    pg = min(255, max(0, int(pg + err_g * factor)))
                    pb = min(255, max(0, int(pb + err_b * factor)))
                    pixels[nx, ny] = (pr, pg, pb)

            distribute(1, 0, 7 / 16)
            distribute(-1, 1, 3 / 16)
            distribute(0, 1, 5 / 16)
            distribute(1, 1, 1 / 16)

    debug_log("Dithering Floyd–Steinberg appliqué.", 'info')
    return image


def convert_image_to_jpg(input_path):
    """
    Convert an image to JPG format if it is not already in that format.

    :param input_path: Path to the image file.
    :return: Path to the converted JPG file.
    """
    # Vérifie que le fichier existe
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    # Récupère l'extension en minuscule
    ext = os.path.splitext(input_path)[1].lower()
    output_path = os.path.splitext(input_path)[0] + ".jpg"

    if ext in ['.png', '.jpg', '.jpeg']:
        with Image.open(input_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(output_path, format="JPEG")
    elif ext in ['.heic', '.heif']:
        # Pour HEIC/HEIF
        heif_file = pyheif.read(input_path)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        rgb_img = image.convert("RGB")
        rgb_img.save(output_path, format="JPEG")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    debug_log(f"JPG conversion: {input_path} -> {output_path}", 'info')
    os.remove(input_path) # delete original file
    return output_path


def process_new_image(image_path, output_dithered_image):
    """
    Process a new image :
        - fix orientation
        - resize & crop
        - generate a simulated dithered image
        - return new image name and dithered image path

    :param image_path: path to the image file
    :param output_dithered_image: path to the dithered image
    :return: image file name, dithered image path
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

    # Genarate dithered image
    # first, downsize the image to 400x240
    dithered = image.resize((400, 240))
    dithered = apply_floyd_steinberg_dither(dithered)
    dithered.save(output_dithered_image)
    debug_log(f"New dithered image : {output_dithered_image}", 'info')

    return image_name, output_dithered_image
