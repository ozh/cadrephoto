import os
import time

from font_fredoka_one import FredokaOne
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from utils.utils import debug_log, exit_program
from utils.led import led_off, led_on

led_on()

inky_display = auto()

# Create new PIL image with a white background
image = Image.new("P", (inky_display.width, inky_display.height), inky_display.WHITE)
draw = ImageDraw.Draw(image)

# shapes
draw.ellipse((150, 150, 300, 300), fill=inky_display.YELLOW)
draw.ellipse((450, 50, 500, 100), fill=inky_display.BLUE)
draw.ellipse((350, 350, 400, 400), fill=inky_display.BLACK)

# Messages
font = ImageFont.truetype(FredokaOne, 62)
message = "Système éteint."
_, _, w, h = font.getbbox(message)
x = (inky_display.width / 2) - (w / 2)
y = (inky_display.height / 2) - (h / 2) -100
draw.text((x, y), message, inky_display.RED, font)

font = ImageFont.truetype(FredokaOne, 42)
message = "Rebrancher pour redémarrer !"
_, _, w, h = font.getbbox(message)
x = (inky_display.width / 2) - (w / 2)
y = (inky_display.height / 2) - (h / 2)
draw.text((x, y), message, inky_display.RED, font)

# FINAL DISPLAY
inky_display.set_image(image)
inky_display.set_border(inky_display.RED)
inky_display.show()

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
