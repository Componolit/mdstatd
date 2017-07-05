#!/usr/bin/env python3

import socket
import json
import mdstat

class MD_Base:

    def get_mdstat(self):
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

class MD(MD_Base):

    def get_mdstat(self):
        return mdstat.parse()

    def send_error(self, error):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        s.connect("/tmp/blinkd.socket")
        s.sendall(json.dumps({'led':1, 'status': error}).encode('utf-8'))
        s.close()

if __name__ == "__main__":
    md = MD()
    md.load()
    status = md.determine_state()
    if status:
        md.send_error(status)

