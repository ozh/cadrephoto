"""
Logs !

First screen :
    - Free space on SD card / CPU temperature
    - uptime
    - IP and broadcast address
    - Wifi diagnostics
    - test IMAP and SMTP connection to server
    - Service status of the cadrephoto service

Second screen :
    - last N lines of logs:

"""
import imaplib
import smtplib
import time
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

from utils.constants import OUTPUT_FOLDER, IMAP_SERVER, SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT, CURRENT_PHOTO, \
    TMP_DOWNLOAD_FOLDER

# Values for Pimoroni Impressions Spectra 7.3''
CHARS_PER_LINE = 88
MAX_LINES = 34
FONT_SIZE = 14
FONT_PATH = "assets/fonts/FiraCode.ttf"

def logs_to_image_first_screen() -> str:
    """
    Create an image with the first screen of logs, including wifi strength, number of images,
    IMAP and SMTP connection tests, and systemd service status.

    :return: string: image file name
    """

    # IMAP connection test
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(SMTP_USER, SMTP_PASSWORD)
        mail.select("INBOX")
        mail.close()
        mail.logout()
        imap = "IMAP OK"
    except Exception as e:
        imap = f"IMAP failed: {e}"

    # SMTP connection test
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.quit()
        smtp = "SMTP OK"
    except Exception as e:
        smtp = f"SMTP failed: {e}"

    lines = [
        [ "General status of the system :", (255, 0, 0) ],
    ]
    lines += get_general_info()
    lines += [
        [ "-----", (0, 255, 0) ],
        [ f"$ iwconfig wlan0", (255, 0, 0) ],
    ]
    lines += get_wifi_signal()
    lines += [
        [ "-----", (0, 255, 0) ],
        [ "IMAP and SMTP server tests :", (255, 0, 0) ],
        [ f"{imap} / {smtp}", (0, 0, 0) ],
        [ "-----", (0, 255, 0) ],
        ["$ systemctl status cadrephoto.service", (255, 0, 0)],
    ]
    lines += get_systemctl_status()

    return _text_to_image(lines, 'debug_screen_img1.png')


def get_general_info():
    """
    Get general information about the system, including IP address, uptime, temperature,
    and free space on the SD card.

    :return: list of lines with general information
    """
    if sys.platform == "win32":
        # Dummy output
        general_info = [
            [ "SD Card use: 11% -- CPU temp=41.9'C", (0, 0, 0) ],
            [ " 12:00:06 up 6 days, 17:02,  3 users,  load average: 0.05, 0.03, 0.00", (0, 0, 0) ],
            [ "IP:  192.168.1.193/24  Broadcast:  192.168.1.255", (0, 0, 0) ],
        ]
    else:
        general_info = get_command_output("FREEMEM=$(df -h -T | awk '/ext4 / {print $6}') && echo -n \"SD Card use: $FREEMEM -- CPU \" && vcgencmd measure_temp", (0, 0, 0))
        general_info += get_command_output("uptime", (0, 0, 0))
        general_info += get_command_output("ip addr show wlan0 | awk '/inet / {print \"IP: \",$2,\" Broadcast: \",$4}'", (0, 0, 0))

    return general_info

def get_systemctl_status():
    # Systemd service status -- just the header, since the journal will be on the second screen
    if sys.platform == "win32":
        # Dummy output
        service_status = [
            [ "○ cadrephoto.service - Cadrephoto", (0,0,0)  ],
            [ "     Loaded: loaded (/etc/systemd/system/cadrephoto.service; disabled; preset: enabled)", (0,0,0)  ],
            [ "     Active: inactive (dead)", (0,0,0)  ],
        ]
    else:
        service_status_full = get_command_output("systemctl status cadrephoto.service", (0,0,0) )
        # keep lines till the first empty line
        service_status = []
        for line in service_status_full:
            if line and (line[0].strip() == ""):
                break
            service_status.append(line)
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

    # get the last XX lines of logs from systemd journal
    if sys.platform == "win32":
        command = "dir" # meh just get some output
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
    Execute a shell command and return its output as a list of lines.

    :param command: str: shell command to execute
    :param line_color: tuple: RGB color for the lines, if None, default colors will be used
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

    debug_screen_img.save(TMP_DOWNLOAD_FOLDER + '/' + image_name)
    return image_name
