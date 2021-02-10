#! /usr/bin/python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

def getCredentials():
    credentials = {}
    with open(".ip_checkrc") as f:
        file_credentials = f.readlines()
        for line in file_credentials:
            if line[0] != "#":
                line = line.split("=")
                key = line[0].strip()
                value = "".join(line[1:]).strip()

                if key in ["sender_email", "sender_password", "recipient_email"]:
                    credentials[key] = value
    return credentials


def isDefaultCredentials(credentials):
    needToChange = []
    if credentials["sender_email"] == "my_email@gmail.com":
        needToChange.append(" - sender_email")
    if credentials["sender_password"] == "my_password123":
        needToChange.append(" - sender_password")
    if credentials["recipient_email"] == "my_email@gmail.com":
        needToChange.append(" - recipient_email")
    if needToChange:
        print("Please edit the file \".ip_checkrc\" and modify the following fields to your custom values:")
        print("\n".join(needToChange))
        print("Then run the program again.")

    return bool(needToChange)


credentials = getCredentials()
from_email = credentials["sender_email"]
sesame = credentials["sender_password"]
to_email = credentials["recipient_email"]
subject = "Test Email from RaspberryPi"

if isDefaultCredentials(credentials):
    exit()


def sendEmail(sender, recipient, sesame, body = "Body", subject = "No subject"):
    smtp_server = "smtp.gmail.com"
    port = 587
    msg = MIMEMultipart()

    msg['From'] = "pieBot <" + from_email + ">"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body))

    mailserver = smtplib.SMTP(smtp_server, port)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()

    mailserver.login(from_email, sesame)

    mailserver.sendmail(from_email, to_email, msg.as_string())

    mailserver.quit()


print(datetime.datetime.now())

body = '''Hello,

This is a test email. If you have received this, congrats! Your email settings are correct.

If you did not expect this email, please disregard.

-pieBot
'''

print("sending a test email from " + from_email + " to " + to_email + " ...")
sendEmail(from_email, to_email, sesame, subject=subject, body=body)

print("done.\n")
