import imaplib
import email
import sys

from utils.utils import *
from utils.image_manipulation import convert_image_to_jpg

from utils.constants import IMAP_SERVER, SMTP_USER, SMTP_PASSWORD, TMP_DOWNLOAD_FOLDER

from utils.utils import debug_log


def check_mail_and_download_attachments():
    """
    Checks mails.
    - Return False if no new mail or no image
    - Returns: from_email, attachment_path

    :return: false, or from_email, attachment_path
    """

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SMTP_USER, SMTP_PASSWORD)
    mail.select("INBOX")

    status, response = mail.search(None, 'UNSEEN')
    unread_msg_nums = response[0].split()

    if not unread_msg_nums:
        debug_log("📭 No unread mail", 'info')
        return False

    debug_log("📭 New mail(s) !", 'info')

    attachment_path = None
    from_email = None
    to_delete = []

    for msg_id in unread_msg_nums:
        status, full_data = mail.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            continue

        msg = email.message_from_bytes(full_data[0][1])
        from_email_candidate = email.utils.parseaddr(msg.get('From'))[1]

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if filename:
                filepath = os.path.join(TMP_DOWNLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                attachment_path = filepath
                from_email = from_email_candidate
                break

        to_delete.append(msg_id)

        if attachment_path:
            break  # we found an attachment, no need to check further

    # Delete all unread messages
    for msg_id in unread_msg_nums:
       mail.store(msg_id, '+FLAGS', '\\Deleted')
    mail.expunge()
    debug_log(f"{len(to_delete)} mail(s) deleted", 'info')

    mail.logout()

    if attachment_path:
        # Check if the attachment is an image
        if not attachment_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.heif', '.heic')):
            debug_log(f"❌ Unsupported attachment : {attachment_path}", 'critical')
            return False

        # If the image is not JPG, convert it to JPG
        if not attachment_path.lower().endswith('.jpg'):
            try:
                attachment_path = convert_image_to_jpg(attachment_path)
            except Exception as e:
                debug_log(f"❌ Error converting attachment : {e}", 'critical')
                return False

        debug_log(f"📥 Attachment downloaded : {attachment_path}", 'info')
        return from_email, attachment_path
    else:
        debug_log("Mail(s) had no attachment (and all mails deleted)", 'info')
        return False