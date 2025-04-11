import os
import email
from email.header import decode_header
from datetime import datetime

from imapclient import IMAPClient
import email

GR_FILE = 'Job GR_WH_IBE, Step 1.htm'
PO_FILE = 'Job PO_LAST_YEAR, Step 1.htm'


def imap() -> IMAPClient:
    client = IMAPClient(os.getenv('AVL_SMTP_HOST'), use_uid=True)
    client.login(os.getenv('AVL_SMTP_USERNAME'), os.getenv('AVL_SMTP_PASSWORD'))
    client.select_folder('INBOX', readonly=True)
    return client

def fetch_files(filename: str, since: datetime = None):
    since = since or datetime.now().date()
    server = imap()
    messages = server.fetch(server.search(['SINCE', since]), ['ENVELOPE'])
    files = {}
    for msg_id, raw in messages.items():
        subject = raw[b'ENVELOPE'].subject
        date = raw[b'ENVELOPE'].date
        rfc822 = server.fetch([msg_id], ['RFC822'])
        message = email.message_from_bytes(rfc822[msg_id][b'RFC822'])
        for part in message.walk():
            part_filename = part.get_filename()
            if filename == part_filename:
                files[date] = part.get_payload(decode=True)
    return files

