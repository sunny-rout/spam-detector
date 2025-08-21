import imaplib
import email
import pandas as pd
import re
import string

conn = imaplib.IMAP4_SSL('imap.gmail.com')
conn.login('your_email@gmail.com', 'your_password')
conn.select('inbox')
def fetch_emails():
    result, data = conn.search(None, 'ALL')
    email_ids = data[0].split()
    emails = []

    for email_id in email_ids:
        result, msg_data = conn.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        subject = msg['subject']
        from_ = msg['from']
        date_ = msg['date']
        body = get_email_body(msg)
        emails.append({'Subject': subject, 'From': from_, 'Date': date_, 'Body': body})

    return pd.DataFrame(emails)