from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import jinja2
import os
import sqlite3
import datetime

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

def checkDB(DBPath):
    files = []

    conn = sqlite3.connect(DBPath)

    cur = conn.cursor()
    curUp = conn.cursor()
    curSt = conn.cursor()

    cur.execute("SELECT * FROM files")

    for file in cur.fetchall():
        curUp.execute("SELECT measure_time, last_update_in_s FROM updates WHERE file_id = :file ORDER BY id DESC LIMIT 1",{'file':file[0]})
        result = curUp.fetchone()

        time = datetime.datetime.utcnow()
        measure_time = datetime.datetime.strptime(result[0],'%Y-%m-%dT%H:%M:%S')

        no_update_time = (time - measure_time).seconds + result[1]

        if file[3] == 0 and no_update_time >= 3600:
            curSt.execute("UPDATE files SET status = -1 WHERE id = :file",{'file':file[0]})
            files.append(file[1]+'-'+file[2])
        elif file[3] == -1 and no_update_time < 3600:
            curSt.execute("UPDATE files SET status = 0 WHERE id = :file",{'file':file[0]})

    conn.commit()
    conn.close()

    return files

print(checkDB('db.db'))
