import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from utils.constants import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, OWNER_EMAIL, EMAIL_OWNER_SUBJECT, \
    EMAIL_OWNER_BODY, EMAIL_CONFIRMATION_SUBJECT, EMAIL_CONFIRMATION_BODY
from utils.utils import debug_log


def tell_owner(sender_email):
    """
    Send a message to the owner (Mamie) with the sender's email.

    :param sender_email: Email of the sender.
    """
    debug_log(f"📧 Sending email to {OWNER_EMAIL} about new photo from {sender_email}", 'info')
    send_email_plaintext(sender_email, EMAIL_OWNER_SUBJECT, EMAIL_OWNER_BODY)


def send_email_plaintext(from_email, subject, body):
    """
    Send a notification email to Grandma with the sender's email.

    :param from_email:
    :param subject:
    :param body:
    """
    body = render_email_template(body, {'sender_email': from_email})
    subject = render_email_template(subject, {'sender_email': from_email})
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = OWNER_EMAIL

    try:
        send_email_raw(msg)
        debug_log(f"📧 Mail sent to {OWNER_EMAIL} : new photo from {from_email}", 'info')
    except Exception as e:
        debug_log(f"Erreur lors de l'envoi du mail plaintext : {e}", 'critical')


def tell_sender(to_email, image_path):
    """
    Send a message to the photo sender

    :param to_email: Email of the sender.
    :param image_path: Path to the image that was received.
    """
    debug_log(f"📧 Sending email to {to_email} about the photo they sent", 'info')
    send_email_with_attachment(to_email, image_path)


def send_email_with_attachment(to_email, image_path):
    # Create message
    msg = MIMEMultipart('related')
    msg['Subject'] = EMAIL_CONFIRMATION_SUBJECT
    msg['From'] = SMTP_USER
    msg['To'] = to_email
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
        debug_log(f"✅ Mail sent to {to_email}", 'info')
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

