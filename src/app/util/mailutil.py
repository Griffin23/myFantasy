#-*- coding: utf-8 -*- 
from app import app
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def sendMail(fromEmail, subject, content):
	mail_host = app.config['MAIL_HOST']
	mail_user = app.config['MAIL_USERNAME']
	mail_pass = app.config['MAIL_PASSWORD']
	
	sender = mail_user
	receivers = mail_user
	message = MIMEText(content, 'plain', 'utf-8')
	message['From'] = Header(fromEmail, 'utf-8')
	message['To'] =  Header("我", 'utf-8')
	message['Subject'] = Header(subject, 'utf-8')
	
	smtpObj = smtplib.SMTP_SSL(mail_host, 465)
	smtpObj.login(mail_user,mail_pass)  
	smtpObj.sendmail(sender, receivers, message.as_string())