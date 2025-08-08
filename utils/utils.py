# Misc utilities
import os
import pathlib
import time
import logging

from utils.constants import DEBUG, CURRENT_PHOTO, NUMBER_OF_PHOTOS_TO_KEEP
from utils.led import stop_blinking_led, led_off

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.CRITICAL,
    format='%(levelname)s: %(asctime)s - %(message)s',
    datefmt='%H:%M:%S',
)


def exit_program(code=0):
    """
    Exit the program gracefully

    :param code: exit code, default is 0
    """
    debug_log(f"Exiting program with code {code}", 'critical')

    try:
        stop_blinking_led()
    except:
        pass

    try:
        led_off()
    except:
        pass

    # We're not using sys.exit() because it does not work (maybe due to LED blinking threading issues ?)
    os._exit(code)


def debug_log(msg, level='info'):
    """
    Log a debug message if DEBUG is True, or log a critical message anyway.

    :param level:
    :param msg:
    """
    _log_levels = {
        'debug': logging.debug,
        'info': logging.info,
        'warning': logging.warning,
        'error': logging.error,
        'critical': logging.critical,
    }
    log_func = _log_levels.get(level.lower(), logging.debug)
    log_func(msg)


def delete_all_but_latest_XXX(directory):
    """
    Deletes all files in the given directory except the 5 most recently modified files.

    Parameters:
        directory (str or Path): Path to the directory where files will be deleted.
    """
    dir_path = pathlib.Path(directory)

    # Ensure the directory exists
    if not dir_path.is_dir():
        debug_log(f"Error: '{directory}' is not a valid directory.", 'critical')
        return False

    # Get list of files sorted by modification time (newest first)
    files = [f for f in dir_path.iterdir() if f.is_file() and not f.name.startswith('.')]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    number_of_files = len(files)

    # Keep the NUMBER_OF_PHOTOS_TO_KEEP most recent files
    files_to_delete = files[NUMBER_OF_PHOTOS_TO_KEEP:]
    number_of_files_to_delete = len(files_to_delete)
    debug_log(f"Deleting {number_of_files_to_delete} files out of {number_of_files})", 'info')

    is_ok = True

    for file in files_to_delete:
        try:
            file.unlink()
            debug_log(f"Deleted: {file}", 'info')
        except Exception as e:
            debug_log(f"Error deleting {file}: {e}", 'critical')
            is_ok = False

    return is_ok


def rename_file_with_timestamp(file_path):
    """
    Rename a file to YYYY-MM-DD-HHMMSS.ext

    :param file_path: file path
    :return: new file path
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"❌ File '{file_path}' does not exist.")

    timestamp = os.path.getmtime(file_path)

    # Get timestamp, file path and extension
    date_str = time.strftime("%Y-%m-%d-%H%M%S", time.localtime(timestamp))
    dir_name = os.path.dirname(file_path)
    ext = os.path.splitext(file_path)[1]

    # Rename
    new_filename = f"{date_str}{ext}"
    new_path = os.path.join(dir_name, new_filename)
    os.rename(file_path, new_path)

    debug_log(f"Filename timestamped: {new_path}", 'info')
    return new_path


def write_photo_name(image_name):
    # Save new image path into current_photo.txt
    image_name = os.path.basename(image_name)  # Keep only the filename, not the full path
    try:
        with open(CURRENT_PHOTO, 'w') as f:
            f.write(image_name)
        debug_log(f"Photo name written to {CURRENT_PHOTO}: {image_name}", 'info')
        return True
    except:
        debug_log(f"Error writing current photo name to {CURRENT_PHOTO}", 'critical')
        return False

