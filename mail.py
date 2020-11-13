from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import jinja2
import psycopg2
import settings

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

    conn = psycopg2.connect(host=settings.mailList['serverAddress'],user=settings.mailList['user'],password=settings.mailList['passwd'],database=settings.mailList['db'])
    cur = conn.cursor()
    cur.execute("SELECT usuarios.email FROM usuarios, roles WHERE usuarios.id_grupo = roles.id AND roles.name = 'admin' AND usuarios.ativo = 't' AND usuarios.email IS NOT NULL AND usuarios.nome != 'admin' GROUP BY usuarios.email;")
    result = cur.fetchall()

    mailAddresses = [m[0] for m in result]
    conn.close()

    return mailAddresses
