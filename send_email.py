#!/usr/bin/python3

import datetime
import smtplib
import time
from email.mime.text import MIMEText

class EmailSender:
    #https://www.cnblogs.com/rainbow-tan/p/16848236.html
    def __init__(self):
        self.mail_host = 'smtp.qq.com'
        self.mail_post = 465
        self.mail_sender = '2458858175@qq.com'
        self.password = 'uniyizazwambeajc'
        self.mail_recieiver = ['2458858175@qq.com']


    def send(self, message):
        body = message

        msg = MIMEText(body, 'plain')
        msg["Subject"] = "用于测试"
        msg["From"] = self.mail_sender
        msg["To"] = ",".join(self.mail_recieiver)

        with smtplib.SMTP_SSL(self.mail_host, self.mail_post) as smtp:
            smtp.login(self.mail_sender, self.password)
            smtp.sendmail(self.mail_sender, self.mail_recieiver, msg.as_string())
            smtp.quit()
        
        time.sleep(5)
        print("发送邮件成功! ["+body+"]")     


if __name__ == '__main__':
    sender = EmailSender()
    sender.send('测试邮件v2') 



    
