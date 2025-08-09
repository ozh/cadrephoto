import os
import sys
from PIL import Image
from utils.constants import OUTPUT_FOLDER, TMP_DOWNLOAD_FOLDER
from utils.utils import debug_log, write_photo_name

if sys.platform != "win32":
    from inky.auto import auto
else:
    # On windows, we will use tkinter to display the image
    from tkinter import *
    from PIL import ImageTk, Image

def send_to_eink(image_filename, is_debug=False):
    """
    Display image on the Pimoroni e-ink
    Use basename of the image in the OUTPUT_FOLDER

    :param image_filename: filename of the image to display
    :param is_debug: if True, use temp DOWNLOAD_FOLDER instead of OUTPUT_FOLDER for temp image, and do not write photo name
    :return: False if error, True if success
    """

    if is_debug:
        image_filename = TMP_DOWNLOAD_FOLDER + "/" + image_filename
    else:
        image_filename = OUTPUT_FOLDER + "/" + image_filename

    if not os.path.exists(image_filename):
        debug_log(f"error : file {image_filename} does not exist", 'info')
        return False

    if not is_debug:
        write_photo_name(image_filename)

    try:
        inky = auto()
    except Exception as e:
        if sys.platform == "win32":
            try:
                windows_display_image(image_filename)
            except Exception as e:
                debug_log(f"Could not display {image_filename} on Windows : {e}", "critical")
                return False
            return True # kind of...

        debug_log(f"Could not initialize Inky : {e}", "critical")
        return False

    image = Image.open(image_filename)
    resizedimage = image.resize(inky.resolution)

    try:
        inky.set_image(resizedimage)
        inky.show()
        debug_log(f"Displaying : {image_filename}", 'info')
    except Exception as e:
        debug_log(f"Could not display {image_filename} : {e}", "critical")
        return False

    return True

def windows_display_image(image_filename):
    """
    Display image on Windows (for testing purposes)
    :param image_filename: filename of the image to display
    :return: False if error, True if success
    """
    debug_log(f"✨✨✨ Windows displaying {image_filename} ✨✨✨", 'info')

    root = Tk()
    canv = Canvas(root, width=800, height=480, bg='white')
    canv.grid(row=2, column=3)
    img = ImageTk.PhotoImage(Image.open(image_filename))  # PIL solution
    canv.create_image(0, 0, anchor=NW, image=img)
    root.mainloop()
