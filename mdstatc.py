#!/usr/bin/env python3

import os
import socket
import json
import sys
import smtplib
import mdstat
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MD_Base:

    RAID_STATUS = ["ok", "warning", "error"]

    def get_mdstat(self):
        raise NotImplementedError

    def get_raw_mdstat(self):
        raise NotImplementedError

    def get_user(self):
        raise NotImplementedError

    def get_hostname(self):
        raise NotImplementedError

    def send_error(self):
        raise NotImplementedError
    
    def load(self):
        self.md_data = self.get_mdstat()
    
    def check_disk(self, disk):
        if disk['faulty']:
            return 2
        return 0

    def check_device(self, device):
        status = 0
        if False in device['status']['synced']:
            if device['resync']:
                status = 1
            else:
                status = 2
        for disk in device['disks']:
            status = max(self.check_disk(device['disks'][disk]), status)
        return status

    def determine_state(self):
        status = 0
        for device in self.md_data['devices']:
            status = max(self.check_device(self.md_data['devices'][device]), status)
        return status

    def generate_message(self, mail, status):
        message = MIMEMultipart()
        message['Subject'] = "mdstatc: RAID {}".format(self.RAID_STATUS[status])
        message['From'] = "{}@{}".format(self.get_user(), self.get_hostname())
        message['To'] = mail
        message.attach(MIMEText(self.get_raw_mdstat()))
        return message

class MD(MD_Base):

    def get_mdstat(self):
        return mdstat.parse()

    def get_raw_mdstat(self):
        with open("/proc/mdstat", "r") as pm:
            return pm.read()

    def get_user(self):
        return os.getenv("USER")

    def get_hostname(self):
        return socket.getfqdn()

    def send_error(self, error):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        s.connect("/tmp/blinkd.socket")
        s.sendall(json.dumps({'led':1, 'status': error}).encode('utf-8'))
        s.close()

    def send_mail(self, mail, status):
        if mail:
            message = self.generate_message(mail, status)
            with smtplib.SMTP('localhost') as smtp:
                smtp.send_message(message)

if __name__ == "__main__":
    md = MD()
    md.load()
    status = md.determine_state()
    mail = sys.argv[1] if len(sys.argv) > 1 else None
    if status:
        md.send_error(status)
        md.send_mail(mail, status)

