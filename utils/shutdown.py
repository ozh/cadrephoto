import os
import time

from PIL import Image, ImageDraw, ImageFont

from utils.constants import SHUTDOWN_MESSAGE_LINE1, SHUTDOWN_MESSAGE_LINE2, TMP_DOWNLOAD_FOLDER
from utils.eink import send_to_eink
from utils.utils import debug_log, exit_program
from utils.led import led_off, led_on

led_on()

FONT_PATH = "assets/fonts/FiraCode.ttf"
SHUTDOWN_SCREEN_FILE = 'shutdown_screen.jpg'


def create_shutdown_image():
    # Create new PIL image with a white background
    image = Image.new('RGB', (800, 480), 'white')
    draw = ImageDraw.Draw(image)
    # shapes
    draw.ellipse((150, 150, 300, 300), fill='yellow')
    draw.ellipse((500, 150, 550, 200), fill='blue')
    draw.ellipse((350, 350, 400, 400), fill='black')
    # Messages
    font = ImageFont.truetype(FONT_PATH, 62)
    message = SHUTDOWN_MESSAGE_LINE1
    _, _, w, h = font.getbbox(message)
    x = (800 / 2) - (w / 2)
    y = (480 / 2) - (h / 2) - 100
    draw.text((x, y), message, 'red', font)
    font = ImageFont.truetype(FONT_PATH, 42)
    message = SHUTDOWN_MESSAGE_LINE2
    _, _, w, h = font.getbbox(message)
    x = (800 / 2) - (w / 2)
    y = (480 / 2) - (h / 2)
    draw.text((x, y), message, 'red', font)
    # FINAL DISPLAY
    image.save(TMP_DOWNLOAD_FOLDER + '/' + SHUTDOWN_SCREEN_FILE)


# check if SHUTDOWN_SCREEN_FILE exists, create it otherwise
if not os.path.exists(TMP_DOWNLOAD_FOLDER + '/' + SHUTDOWN_SCREEN_FILE):
    create_shutdown_image()
send_to_eink(SHUTDOWN_SCREEN_FILE, is_debug=True)
time.sleep(1)

# Shutdown LED if it was on
try:
    led_off()
except Exception as e:
    debug_log(f"Could not turn LED off : {e}", "critical")

# Shutdown the system
try:
    debug_log("sudo shutdown -h now", 'info')
    os.system("sudo shutdown -h now")
    exit_program(0)
except Exception as e:
    debug_log(f"Could not shutdown : {e}", 'critical')
    exit_program(1)
