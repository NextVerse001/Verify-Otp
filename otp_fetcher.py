import re
from imapclient import IMAPClient
from bs4 import BeautifulSoup
import email

IMAP_SERVER = 'imap.rambler.ru'
IMAP_PORT = 993

def extract_otp_from_email(text):
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else None

def fetch_otp_with_credentials(email_user, email_pass):
    try:
        with IMAPClient(IMAP_SERVER, port=IMAP_PORT, ssl=True) as client:
            client.login(email_user, email_pass)
            client.select_folder('INBOX')
            messages = client.search(['UNSEEN'])

            if not messages:
                return None

            latest_id = messages[-1]
            raw_message = client.fetch([latest_id], ['RFC822'])[latest_id][b'RFC822']

            msg = email.message_from_bytes(raw_message)
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html = part.get_payload(decode=True).decode()
                        soup = BeautifulSoup(html, 'html.parser')
                        text = soup.get_text()
                        return extract_otp_from_email(text)
            else:
                text = msg.get_payload(decode=True).decode()
                return extract_otp_from_email(text)
    except Exception as e:
        print(f"[ERROR] OTP fetch failed: {e}")
        return None
