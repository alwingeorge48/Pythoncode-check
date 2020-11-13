import imaplib, time, email
from datetime import datetime
import re
import subprocess

class Mail():
    def __init__(self, username, password):
        self.user = username
        self.password = password
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com', '993')
        self.mail.login(self.user, self.password)
        
    def checkMail(self):
        self.mail.select('test-filter')
        self.unread = self.mail.search(None, 'UnSeen')
        self.unread_mail_index = [str(int(i)) for i in self.unread[1][0].split()]
    
    def mapper(self, payload):
        commands = [r'c:\Users\Administrator\AppData\Local\UiPath\app-20.10.0-beta0511\UiRobot.exe execute --file "C:\Users\Administrator\.nuget\packages\Portal1\1.0.2\portal1.1.0.2.nupkg"',
                r'c:\Users\Administrator\AppData\Local\UiPath\app-20.10.0-beta0511\UiRobot.exe execute --file "C:\Users\Administrator\.nuget\packages\Portal2\1.0.2\portal2.1.0.2.nupkg"',
                r'c:\Users\Administrator\AppData\Local\UiPath\app-20.10.0-beta0511\UiRobot.exe execute --file "C:\Users\Administrator\.nuget\packages\Portal3\1.0.2\portal3.1.0.2.nupkg"']
        payload = payload[:payload.find('<html>')].strip() if payload.find('<html>') != -1 else payload.strip()
        payload = payload[:payload.find('________________________')].strip() if payload.find('________________________') != -1 else payload.strip()
        payload = [x for x in payload.split() if x]
        if not payload:
            return None
        else:
            for command in commands:
                if re.search(".*"+".*".join(payload)+".*", command, re.IGNORECASE):
                    subprocess.run(command)
                    return "command "+command
            return "Not command "+" ".join(payload)

    def printData(self):
        for i in self.unread_mail_index:
            data = self.mail.fetch(i, '(RFC822)')[1]
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1].decode("utf-8"))
                    if msg.is_multipart():
                        for payload in msg.get_payload():
                            print(self.mapper(payload.get_payload()))
                    else:
                        print(self.mapper(msg.get_payload()))
        
email_check = Mail('username', 'passwords')

while 1:
    print(f'----------Checking----------{datetime.now()}')
    email_check.checkMail()
    email_check.printData()
    time.sleep(20)
