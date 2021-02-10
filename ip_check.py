#! /usr/bin/python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import subprocess
import argparse
import os
from os.path import expanduser
home = expanduser("~") + "/"

__author__ = "Kyle Cheng"
__github__ = "kcheng0222"

parser = argparse.ArgumentParser(description="Emails user when RaspberryPi IP address changes upon reboot.")
parser.add_argument("-f", "--forced", dest='forced', action="store_true", help="force sending email message, even if IP has not changed")
args = parser.parse_args()
forced = args.forced

filename = home + "/.ip_check_last_ip.txt"
SEND_LIMIT = 10


def getCount():
    with open(home + "/.ip_check_count.txt") as f:
        lines = f.readlines()
        for line in lines:
            if line[0] != "#":
                if line.isdigit():
                    return int(line)
    return 0


def writeCount(n):
    with open(home + "/.ip_check_count.txt", 'w') as f:
        f.write(str(n))


def createCountFile():
    with open(home + "/.ip_check_count.txt", "w"):
        pass


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



def writeIP(filename, ip_address):
    with open(filename, 'w') as f:
        print("saving new IP to file...")
        f.write(current_ip)


def getFileIP(filename):
    with open(filename, "r") as f:
        data = f.readline().strip()
    return data


def createIPFile(filename):
    with open(filename, "w"):
        pass


def getOSIP():
    tmp = []
    for _ in str(subprocess.check_output(['hostname', '-I']).strip()).split(' '):
        tmp.append(_.strip().replace("'", "").replace("b", ""))
    return " ".join(tmp)


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


credentials = getCredentials()
from_email = credentials["sender_email"]
sesame = credentials["sender_password"]
to_email = credentials["recipient_email"]

if isDefaultCredentials(credentials):
    exit()

if os.path.exists(filename):
    last_ip = getFileIP(filename)
else:
    print("last ip file does not exist. creating a new one...")
    createIPFile(filename)
    last_ip = ""

print(datetime.datetime.now())
print("last IP:", last_ip)

current_ip = getOSIP()

print("current IP:", current_ip)
#print("sending us an email...")

if os.path.exists(home + "/.ip_check_count.txt"):
    n = getCount()
else:
    #print("creating count file...")
    createCountFile()
    n = 0

underTen = True
if not forced and n > SEND_LIMIT:
    underTen = False

if not underTen and last_ip == current_ip and not forced:
    print("ip of pi has not changed.")
    print()
    exit()

subject = 'New Pi IP: ' + current_ip

body = '''Hello,

It appears the IP address for the Pi has changed. Here is the new IP address:

{}

was:

{}

-pieBot{}
'''.format("\n".join(current_ip.split()), "Unknown" if len(last_ip) == 0 else "\n".join(last_ip.split()), "\n\nYou will receive emails for the next " + str(SEND_LIMIT-n) + " times you run the script for testing purposes. After that, it will only send an email if the IP changes." if underTen else "")

print(body)
#print(credentials)

print("sending...")
sendEmail(from_email, to_email, sesame, subject=subject, body=body)
writeCount(n + 1)
writeIP(filename, current_ip)

#print("n", n)

print("done.\n")
