#!/usr/bin/python3
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

        no_update_time = int((time-measure_time).total_seconds() + result[1])

        if (file[3] == 0 or file[3] == -2) and no_update_time >= 10800:
            curSt.execute("UPDATE files SET status = -2 WHERE id = :file",{'file':file[0]})
            files.append(file[1]+'-'+file[2])
        elif (file[3] == -1 or file[3] == -2) and no_update_time < 10800:
            curSt.execute("UPDATE files SET status = 0 WHERE id = :file",{'file':file[0]})

    conn.commit()
    conn.close()

    return files

def checkUpdateTime(files,conn):
    tables = []

    cur = conn.cursor()

    for file in files:
        cur.execute("SELECT measure_time, last_update_in_s FROM updates WHERE file_id = :file ORDER BY id DESC LIMIT 1",{'file':file[0]})
        result = cur.fetchone()

        time = datetime.datetime.utcnow()
        measure_time = datetime.datetime.strptime(result[0],'%Y-%m-%dT%H:%M:%S')

        no_update_time = int((time-measure_time).total_seconds() + result[1])

        if (file[3] == 0 or file[3] == -2) and no_update_time >= 10800:
            tables.append(file)
        elif (file[3] == -1 or file[3] == -2) and no_update_time < 10800:
            cur.execute("UPDATE files SET status = 0 WHERE id = :file",{'file':file[0]})

    conn.commit()

    return tables

def updateStatus(files,conn):
    tables = []

    cur = conn.cursor()

    for file in files:
        cur.execute("UPDATE files set status = -2 WHERE id = :file",{'file':file[0]})
        tables.append(file[1]+'-'+file[2])

    conn.commit()

    return tables

def checkDB2(DBPath):
    errorTables = []

    conn = sqlite3.connect(DBPath)

    cur = conn.cursor()

    cur.execute("SELECT DISTINCT local FROM files")
    campi = cur.fetchall()

    for campus in campi:
        #inversores
            cur.execute("SELECT * FROM files WHERE local = :local AND (tab_ou_tech LIKE 'mon%' OR tab_ou_tech LIKE 'pol%' OR tab_ou_tech = 'cdte' OR tab_ou_tech = 'cigs')",{'local':campus[0]})
            files = cur.fetchall()
            tables = checkUpdateTime(files,conn)
            if len(tables) >= 6:
                errorTables = errorTables + updateStatus(tables,conn)

        #inversores bidir
            cur.execute("SELECT * FROM files WHERE local = :local AND tab_ou_tech LIKE 'bi%'",{'local':campus[0]})
            files = cur.fetchall()
            tables = checkUpdateTime(files,conn)
            if len(tables) >= 2:
                errorTables = errorTables + updateStatus(tables,conn)

        #dataloggers
            cur.execute("SELECT * FROM files WHERE local = :local AND (tab_ou_tech LIKE 'ep%' OR tab_ou_tech LIKE 'so%' OR tab_ou_tech = 'temp')",{'local':campus[0]})
            files = cur.fetchall()
            tables = checkUpdateTime(files,conn)
            if len(tables) >= 4:
                errorTables = errorTables + updateStatus(tables,conn)

    conn.close()

    return errorTables

def getMailAddresses():
    mailAddresses = []

    #Provisoriamente, os emais são salvos no arquivo mail.txt
    with open('mails.txt','r') as mailsFile:
        for mail in mailsFile:
            if not mail == '' and not mail == '\n':
                mailAddresses.append(mail.split('\n')[0])

    return mailAddresses

def main():
    files = checkDB2('database.db')

    if not files == []:
        mailAddresses = getMailAddresses()

        if not mailAddresses == []:

            msgHtml = renderHTML('email-prob-com.html',{'tabelas':files})

            sendMailHTML('servidor.de.email',465,'email@de.origem','senha',mailAddresses,'Assunto',msgHtml)

if __name__ == '__main__':
    main()
