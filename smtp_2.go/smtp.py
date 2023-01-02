#SCRIPT EM PYTHON PRA RODAR NO SMTP GLOBO (NO AUTH)

import smtplib

fromaddr = 'allanpay-testando@g.globo'
toaddrs = ['allan.cordeiro@g.globo']
msg = '''
    From: {fromaddr}
    To: {toaddr}
    Testando tarefa
    .
'''

msg = msg.format(fromaddr=fromaddr, toaddr=toaddrs[0])
server = smtplib.SMTP('smtp.globoi.com:25')
#server.starttls()
server.ehlo("gmail.com")
server.mail(fromaddr)
server.rcpt(toaddrs[0])
server.data(msg)
server.quit()