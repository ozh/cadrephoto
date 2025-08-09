import shutil
from utils.constants import CURRENT_PHOTO, OUTPUT_FOLDER
from utils.eink import send_to_eink
from utils.utils import *
from utils.utils import debug_log


def get_current_photo():
    """
    Get current photo name from current_photo.txt

    :return: string
    """
    try:
        with open(CURRENT_PHOTO, 'r') as f:
            image_path = f.read().strip()
            debug_log(f"Current photo: {image_path}", 'info')
            return image_path
    except FileNotFoundError:
        debug_log(f"Could not open or read {CURRENT_PHOTO}", 'critical')
        return None


def delete_current_photo():
    """
    Delete current photo file

    :return: None
    """
    current_photo = get_current_photo()
    if current_photo:
        try:
            os.remove(os.path.join(OUTPUT_FOLDER, current_photo))
            debug_log(f"Deleted current photo: {current_photo}", 'info')
        except Exception as e:
            debug_log(f"Error deleting current photo: {e}", 'critical')
    else:
        debug_log("No current photo to delete.", 'info')


def get_next_photo():
    """
    Return next photo filename

    :return: string: filename of the next photo to display
    """

    photos_folder = pathlib.Path(OUTPUT_FOLDER)
    photos = [os.path.basename(x) for x in photos_folder.glob('*.jpg')]

    if not photos:
        # Copy /assets/samples/sample_photo.jpg to OUTPUT_FOLDER
        sample_photo = pathlib.Path(__file__).parent.parent / 'assets' / 'samples' / 'sample_photo.jpg'
        if sample_photo.exists():
            debug_log(f"No photos found. Copying sample photo from {sample_photo} to {OUTPUT_FOLDER}", 'critical')
            shutil.copy(sample_photo, OUTPUT_FOLDER)
            photos = [os.path.basename(sample_photo)]
        else:
            debug_log("No photo found in the photo folder. Get one sent by email !", 'critical')
            exit_program(1)

    if current_photo := get_current_photo():
        try:
            current_index = photos.index(current_photo)
            next_index = (current_index + 1) % len(list(photos_folder.glob('*.jpg')))
        except ValueError:
            debug_log("Current image not found in the photos folder.", 'info')
            next_index = 0
    else:
        next_index = 0

    return photos[next_index]


def display_next_image():
    next_image = get_next_photo()
    debug_log(f"Next image to display: {next_image}", 'info')
    send_to_eink(next_image)

