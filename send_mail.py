#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from email.header import Header


mail_host = 'smtp.163.com'
mail_user = 'dr_tyler@163.com'
mail_pass = 'PROSFMFIBZPGXEDF'

sender = 'dr_tyler@163.com'
receivers = ['dr_tyler@163.com']


def send(mail_msg: str):
    message = MIMEText(mail_msg, 'plain', 'utf-8')
    message['From'] = Header('eve_market<dr_tyler@163.com>', 'utf-8')
    message['To'] = Header('163_receiver<dr_tyler@163.com>', 'utf-8')
    message['Subject'] = Header('auto_monitor_script', 'utf-8')
    try:
        smtpobj = smtplib.SMTP_SSL(mail_host, 994)
        smtpobj.login(mail_user, mail_pass)
        smtpobj.sendmail(sender, receivers, message.as_string())
        smtpobj.close()
        print('sendmail succeeded')
    except Exception as e:
        print(e)
        print('sendmail failed')


if __name__ == '__main__':
    pass