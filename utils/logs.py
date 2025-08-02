"""

Logs.

Get wifi signal strength with python code:
    import os
    import subprocess
    def get_wifi_signal_strength():
        try:
            result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'Link Quality' in line:
                    return line.strip()
        except Exception as e:
            return f"Error getting wifi signal: {e}"


First screen :

    - Wifi strength :
    $ iwconfig wlan0 | grep Link
              Link Quality=70/70  Signal level=-29 dBm
    - Number of images in the output folder. Python code to get this :
    print(len([f for f in os.listdir('./photos') if f.endswith('.jpg')]))

    - test IMAP connection to server
    - test SMTP connection to server

    - $ systemctl status cadrephoto.service :
    ● cadrephoto.service - Cadrephoto
     Loaded: loaded (/etc/systemd/system/cadrephoto.service; enabled; preset: enabled)
     Active: active (running) since Sat 2025-08-02 19:20:06 CEST; 14h ago
    Main PID: 1717 (python)
      Tasks: 11 (limit: 166)
        CPU: 1h 2min 30.892s
     CGroup: /system.slice/cadrephoto.service
             └─1717 /home/ozh/.virtualenvs/pimoroni/bin/python /home/ozh/cadrephoto/app.py


Second screen :

    Print the last N lines of logs:
    $ journalctl -u cadrephoto.service -n 24 --no-pager

Kill service with Ctrl-C:
    $ kill -SIGINT $(ps -ef | grep cadre | xargs | awk '{print $2}')


"""
import imaplib
import smtplib
import time
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageType

from utils.constants import OUTPUT_FOLDER, IMAP_SERVER, SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT, CURRENT_PHOTO, \
    TMP_DOWNLOAD_FOLDER
from utils.image_manipulation import apply_floyd_steinberg_dither
from utils.utils import debug_log

# Values for Pimoroni Impressions Spectra 7.3''
CHARS_PER_LINE = 88
MAX_LINES = 34
FONT_SIZE = 14
FONT_PATH = "fonts/FiraCode.ttf"

def logs_to_image_first_screen() -> str:
    """
    Create an image with the first screen of logs, including wifi strength, number of images,
    IMAP and SMTP connection tests, and systemd service status.

    :return: string: image file name
    """

    # Photo count and list
    number_of_photos = len(os.listdir(OUTPUT_FOLDER))
    photo_list = os.listdir(OUTPUT_FOLDER)

    # IMAP connection test
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(SMTP_USER, SMTP_PASSWORD)
        mail.select("INBOX")
        mail.close()
        mail.logout()
        imap = "IMAP OK."
    except Exception as e:
        imap = f"IMAP failed: {e}"

    # SMTP connection test
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.quit()
        smtp = "SMTP OK."
    except Exception as e:
        smtp = f"SMTP failed: {e}"

    # Content of current_photo.txt
    try:
        with open(CURRENT_PHOTO, 'r') as f:
            image_path = f.read().strip()
        cur_photo = f"Content of {CURRENT_PHOTO} : {image_path}"
    except FileNotFoundError as e:
        cur_photo = f"Error with {CURRENT_PHOTO} : {e}"


    lines = [
        [ f"$ iwconfig wlan0", (255, 0, 0) ],
    ]
    lines += get_wifi_signal()
    lines += [
        [ "-----", (0, 255, 0) ],
        [ f"{number_of_photos} files in {OUTPUT_FOLDER}", (255, 0, 0) ],
        [ f"{photo_list}" ],
        [ "Current photo :", (255, 0, 0) ],
        [ cur_photo ],
        [ "-----", (0, 255, 0) ],
        [ "IMAP and SMTP server tests :", (255, 0, 0) ],
        [ imap ],
        [ smtp ],
        [ "-----", (0, 255, 0) ],
        ["$ systemctl status cadrephoto.service", (255, 0, 0)],
    ]
    lines += get_system_status()

    return _text_to_image(lines, 'debug_screen_img1.png')


def get_system_status():
    # Systemd service status -- just the header, since the journal will be on the second screen
    if sys.platform == "win32":
        # Dummy output
        service_status = [
            [ "○ cadrephoto.service - Cadrephoto", (0,0,0)  ],
            [ "     Loaded: loaded (/etc/systemd/system/cadrephoto.service; disabled; preset: enabled)", (0,0,0)  ],
            [ "     Active: inactive (dead)", (0,0,0)  ],
        ]
    else:
        service_status = get_command_output("systemctl status cadrephoto.service | awk 'NF==0 {exit} {print}'", (0,0,0) )
    return service_status


def get_wifi_signal():
    if sys.platform == "win32":
        # Dummy output
        wifi_signal = [
            [ "wlan0     IEEE 802.11  ESSID: DummyNetwork", (0,0,0) ],
            [ "Mode:Managed  Frequency:2.437 GHz  Access Point: 34:27:92:A7:4C:58", (0,0,0) ],
            [ "Bit Rate=72.2 Mb/s   Tx-Power=31 dBm", (0,0,0) ],
            [ "Retry short limit:7   RTS thr:off   Fragment thr:off", (0,0,0) ],
            [ "Power Management:on", (0,0,0) ],
            [ "Link Quality=70/70  Signal level=-27 dBm", (0,0,0) ],
            [ "Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0", (0,0,0) ],
            [ "Tx excessive retries:0  Invalid misc:0   Missed beacon:0", (0,0,0) ],
        ]
    else:
        wifi_signal = get_command_output("iwconfig wlan0", (0,0,0))
    return wifi_signal


def logs_to_image_second_screen() :
    """
    Second screen of logs : last N lines of logs.

    :return: string: image file name
    """

    # get the last 24 lines of logs from systemd journal
    if sys.platform == "win32":
        command = "dir" # meh
    else:
        command = f"journalctl -u cadrephoto.service -n {MAX_LINES} --no-pager  | fold -s -w {CHARS_PER_LINE} | tail -n {MAX_LINES}"

    lines = get_command_output(command)

    # Keep only the last (MAX_LINES-1) lines of logs and prepend the command
    lines = lines[-(MAX_LINES-1):]
    lines = [
        [ f"$ journalctl -u cadrephoto.service -n {MAX_LINES} --no-pager", (255, 0, 0) ]
    ] + lines

    return _text_to_image(lines, 'debug_screen_img2.png')


def get_command_output(command, line_color=None):
    """

    :param line_color:
    :param command:
    :return:
    """
    lines = []
    try:
        proc = subprocess.Popen(f"{command}", stdout=subprocess.PIPE, shell=True)
        for line in proc.stdout.readlines():
            if line_color:
                lines = lines + [[line.decode("utf-8").rstrip(), line_color]]
            else:
                lines = lines + [[line.decode("utf-8").rstrip()]]
        return lines
    except Exception as e:
        return [[f"Error executing command: {e}"]]


def _text_to_image(lines, image_name):
    """
    Convert a list of text lines into a PIL image, applying text-wrappin
    List strructure: line of text, or line of text and tuple of RGB values
        [
            [ "Line 1" ],
            [ "Line 2" ],
            [ "Line 3", (10,10,20) ],
            ...
        ]
    If no colors are provided, the lines will be black and blue alternating.

    :param lines: list of strings
    :param image_name: image file name
    :return: string: image file name
    """

    # Create a blank white image
    debug_screen_img = Image.new('RGB', (800, 480), 'white')
    draw = ImageDraw.Draw(debug_screen_img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Write out each line into a PIL image, accounting for text-wrapping. Stop
    # if we exceed the max number of lines permitted on the screen.
    line_index = 0
    lines_consumed = 0
    even = True
    while lines_consumed < MAX_LINES and line_index < len(lines):
        even = not even

        curr_line = lines[line_index][0]
        text_color = False
        if len(lines[line_index]) > 1:
            text_color = lines[line_index][1]

        # split the line into chunks of CHARS_PER_LINE characters if it is too long
        if len(curr_line) > CHARS_PER_LINE:
            # Split the line into chunks of CHARS_PER_LINE characters
            curr_line = [curr_line[i:i + CHARS_PER_LINE] for i in range(0, len(curr_line), CHARS_PER_LINE)]
            line_index += len(curr_line) - 2
            curr_line = ' '.join(curr_line)

        while curr_line and lines_consumed < MAX_LINES:
            if not text_color:
                if even:
                    text_color = (0, 0, 0) # black
                else:
                    text_color = (0, 0, 255) # blue

            # Write out the first CHARS_PER_LINE characters, then slice it out.
            line_to_write = curr_line[:CHARS_PER_LINE].strip()
            draw.text((5, lines_consumed * FONT_SIZE), line_to_write,
                      font=font, fill=text_color)
            curr_line = curr_line[CHARS_PER_LINE:]
            lines_consumed += 1
        line_index += 1

    # debug_screen_img = apply_floyd_steinberg_dither(debug_screen_img)
    debug_screen_img.save(TMP_DOWNLOAD_FOLDER + '/' + image_name)
    debug_log(f'Transformed logs to image at {image_name}', 'info')
    return image_name

