#!/usr/bin/python3
import envios
import mail
import settings

def main():
    files = envios.checkDB2(settings.DBPath+'/database.db')

    if not files == []:
        mailAddresses = mail.getMailAddresses()

        if not mailAddresses == []:

            msgHtml = mail.renderHTML('email-prob-com.html',{'tabelas':files})

            mail.sendMailHTML(settings.mailServer['serverAddress'],settings.mailServer['serverPort'],settings.mailServer['user'],settings.mailServer['passwd'],mailAddresses,'Monitoramento EPESOLs',msgHtml)

if __name__ == '__main__':
    main()
