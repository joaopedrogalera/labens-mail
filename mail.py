from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import jinja2

def sendMailHTML(server,port,user,password,to,subject,html):
    msg = MIMEMultipart()
    msg['From'] = user
    msg['Subject'] = subject

    msg.attach(MIMEText(html,'html','utf-8'))

    smtp = smtplib.SMTP_SSL(server,port)
    smtp.login(user,password)
    smtp.sendmail(user,to,msg.as_string())

    smtp.quit()


def renderHTML(fileName,content):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
    template = env.get_template(fileName)
    output = template.render(content)

    return output

def getMailAddresses():
    mailAddresses = []

    #Provisoriamente, os emais são salvos no arquivo mail.txt
    with open('mails.txt','r') as mailsFile:
        for mail in mailsFile:
            if not mail == '' and not mail == '\n':
                mailAddresses.append(mail.split('\n')[0])

    return mailAddresses
