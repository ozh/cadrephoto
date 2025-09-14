import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from utils.constants import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, OWNER_EMAIL, EMAIL_OWNER_SUBJECT, \
    EMAIL_OWNER_BODY, EMAIL_CONFIRMATION_SUBJECT, EMAIL_CONFIRMATION_BODY
from utils.utils import debug_log


def send_email_plaintext(to_email='', subject='', body=''):
    """
    Send an email in plain text.

    :param to_email: string
    :param from_email: string
    :param subject: string
    :param body: string
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = format_email_address(SMTP_USER)
    msg['To'] = format_email_address(to_email)

    try:
        send_email_raw(msg)
        debug_log(f"📧 Mail sent to {to_email}", 'info')
    except Exception as e:
        debug_log(f"Error sending plain text email : {e}", 'critical')


def format_email_address(email):
    """
    format an email address to be used in email headers so that joe@domain becomes Joe <joe@domain>

    :param email:
    :return: string
    """
    name_part = email.split('@')[0]
    name_part = name_part.replace('.', ' ').replace('_', ' ').title()
    return f"{name_part} <{email}>"


def tell_owner(sender_email, owner_email=OWNER_EMAIL):
    """
    Send a message to the owner (Grandma) with the sender's email.

    :param sender_email: Email of the sender.
    :param owner_email: Owner email (default: OWNER_EMAIL)
    """
    debug_log(f"📧 Sending email to {owner_email} about new photo from {sender_email}", 'info')
    body = render_email_template(EMAIL_OWNER_BODY, {'sender_email': sender_email})
    subject = render_email_template(EMAIL_OWNER_SUBJECT, {'sender_email': sender_email})
    send_email_plaintext(to_email=owner_email, subject=subject, body=body)


def tell_sender(to_email, image_path=''):
    """
    Send a message to the photo sender

    :param to_email: Email of the sender.
    :param image_path: Path to the image that was received.
    """
    debug_log(f"📧 Sending email to {to_email} about the photo they sent", 'info')
    send_email_plaintext(to_email=to_email, subject=EMAIL_CONFIRMATION_SUBJECT, body=EMAIL_CONFIRMATION_BODY)


def send_email_with_attachment(to_email, image_path):
    # Create message
    msg = MIMEMultipart('related')
    msg['Subject'] = EMAIL_CONFIRMATION_SUBJECT
    msg['From'] = format_email_address(SMTP_USER)
    msg['To'] = format_email_address(to_email)
    html = EMAIL_CONFIRMATION_BODY

    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_text = MIMEText(html, 'html', 'utf-8')
    msg_alternative.attach(msg_text)

    # Read image file
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()
    mime_img = MIMEImage(img_data)
    mime_img.add_header('Content-ID', '<image1>')
    mime_img.add_header('Content-Disposition', 'inline', filename=Path(image_path).name)
    msg.attach(mime_img)

    # send via SMTP
    try:
        send_email_raw(msg)
        debug_log(f"📧 Mail sent to {to_email}", 'info')
    except Exception as e:
        debug_log(f"❌ Error sending email with attachment : {e}", 'critical')


def send_email_raw(msg):
    """
    Send a raw email message.

    :param msg: The email message to send.
    """
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)


def render_email_template(template: str, context: dict) -> str:
    """
    Render a template string with the provided context.

    :param template: The template string with placeholders.
    :param context: A dictionary containing values to replace in the template.
    :return: The rendered string with placeholders replaced by context values.
    """
    for key, value in context.items():
        placeholder = '{' + key + '}'
        template = template.replace(placeholder, value)
    return template

