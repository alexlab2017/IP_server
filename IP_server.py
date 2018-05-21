import imaplib
import smtplib
import re
from random import choice, sample, uniform
from requests import get # this is the only needed third party module
from socket import inet_aton # simple way to validate an IP address
from string import ascii_lowercase
from time import sleep, strftime
from tkinter import Tk, Button, Label


_CONSOLE = True # print debug info on console
_LOG = True # keep a log

alpha = ['o', 'd', 'z', 'm', 't', 'a', 'c', 'i', 'r', 'u']
paddingPool = 'befghjklnpqsvwxy'
encryptionFactor = -9.616013867352109

# In order to get gmail work fine I activated double factor authentication
# and I created an app-specific password for my Python script
# credits to: http://stackabuse.com/how-to-send-emails-with-gmail-using-python/

smtpServer = 'smtp.gmail.com'
imapServer = 'imap.gmail.com'

emailUser = 'youremailhere@gmail.com'
emailPassword = 'yourpasswordhere'
emailSubject = 'yoursubjecthere'

logFilePath = 'full path to you log file'
filePath = 'full path to the file you want to update'

statusWindow = None


def tryExcept(tries=5, delay=5, _exit=True):
    '''
    Decorator that wraps a function calling it for n times.
    arguments:
        tries = number of times the function has to be called if failing
        delay = number of seconds between each try
        _exit = Do you want to kill the program after n failures? In this
                case you will get a pop-up window
    '''

    def myDecorator(originalFunc):

        def wrapper(*args, **kwargs):

            for i in range(tries):
                try:
                    returnValue = originalFunc(*args, **kwargs)
                except Exception as e:
                    log('n.{0} call to \'{1}()\' failed. {2}'.format(i+1,
                                                               originalFunc.__name__,
                                                               e))
                    wait(delay)
                    pass
                else:
                    return returnValue

            if _exit:
                log('FATAL ERROR: exiting...')
                # destroy statusWindow (if any)
                if statusWindow:
                    statusWindow.destroy()
                createPopup(color='red', title='ERROR', text=None)
                exit(1)

            else:
                return False

        return wrapper

    return myDecorator


@tryExcept(tries=1, delay=0)
def log(item):
    '''
    Simple logging/debug function, it can print to console and/or keep a log file.
    It is saved by default in the same folder of this module but it can be
    moved for convenience.
    '''

    text = '{0} - {1}\n'.format(strftime('%d %b %Y %H:%M:%S'), item)
    if _CONSOLE:
        print(text)
    if _LOG:
        with open(logFilePath, 'a') as f:
            f.write(text)


@tryExcept(tries=1, delay=0)
def wait(seconds):
    '''
    Designed to wait for a number of seconds, one by one, to permit a
    KeyboardInterrupt that otherwise would be raised only after the seconds
    completey elapsed.
    '''

    log('Waiting for {} seconds...'.format(seconds))
    for second in range(seconds):
        sleep(1)


@tryExcept(tries=1, delay=1, _exit=True)
def getIP():
    '''
    This function obtains the external IP from 'https://api.ipify.org'
    validates it and returns it in a string format like '192.168.0.1'.
    '''

    req = get('https://api.ipify.org')
    assert req.status_code == 200
    ip = req.text
    assert inet_aton(ip)
    log('IP obtained: {}'.format(ip))
    return ip


def generateEncryptionParams():
    '''
    Use this function to generate new encryption parameters.
    Manually paste the returned values substituting the ones at
    the beginning of this module.
    '''

    alpha = sample(ascii_lowercase, 10)
    paddingPool = ''.join([i for i in ascii_lowercase if i not in alpha])
    encryptionFactor = uniform(-10, 10)
    log('alpha = {0}\n'
        'paddingPool = \'{1}\'\n'
        'encryptionFactor = {2}'.format(alpha, paddingPool, encryptionFactor))
    return (alpha, paddingPool, encryptionFactor)


@tryExcept(tries=5)
def encryptIP(ip):
    '''
    This function accepts a valid IP address as an argument and returns it
    "encrypted" in a string format. May be better to say "obfuscated" because
    the encryption is not really standard. The purpose is to be able to send
    the IP address via email without leaving it wide open.

    I could say that this is more an exercise, there are third party libraries
    that deals with symmetric encryption using a string as key.
    '''

    assert inet_aton(ip)

    choosenPadding = [choice(paddingPool) for i in range(4)]
    ipStr = ip.split('.')
    ipInt = [int(i) for i in ipStr]
    encryptionKeyInt = []
    encryptionKeyAlpha = []
    encryptedIP = []

    for num in ipStr:
        intArray = [int(i) for i in list(num)]
        somma = sum(intArray)
        while somma > 9:
            intArray = [int(i) for i in list(str(somma))]
            somma = sum(intArray)
        encryptionKeyInt.append(somma)

    for i in encryptionKeyInt:
        encryptionKeyAlpha.append(alpha[i])

    for i in range(len(ipInt)):
        encryptedIP.append(str(ipInt[i]*(encryptionKeyInt[i]*encryptionFactor)))

    finalIP = ''.join([''.join(i) for i in zip(encryptedIP,
                                               encryptionKeyAlpha,
                                               choosenPadding)
                       ])

    log('Encrypted IP: {}'.format(finalIP))

    return finalIP


@tryExcept(tries=5)
def decryptIP(ip):
    '''
    This function decrypts an IP that was previouslu encrypted with the
    encryptIP(ip) function and returns it in a string format like '192.168.0.1'
    '''

    encryptionKeyAlpha = re.findall('[{}]'.format(''.join(alpha)), ip)
    assert len(encryptionKeyAlpha) == 4
    encryptionKeyInt = [alpha.index(i) for i in encryptionKeyAlpha]
    encryptedIP = re.findall(r'[-+]?\d+\.\d+|\d+', ip)
    assert len(encryptedIP) == 4
    decryptedIP = []

    for i in range(len(encryptedIP)):
        decryptedIP.append(str(int(float(encryptedIP[i])/(encryptionKeyInt[i]*encryptionFactor))))

    finalIP = '.'.join(decryptedIP)

    assert inet_aton(finalIP)

    log('Decrypted IP: {}'.format(finalIP))

    return finalIP


@tryExcept(tries=5)
def sendEmail(body):
    '''
    This function is designed to send an email to yourself, the only argument
    you can pass is the body of the email that could be anything you can insert
    in a string with the .format() method.
    '''

    emailText = 'From: {0}\nTo: {0}\nSubject: {1}\n\n{2}'\
                .format(emailUser, emailSubject, body)
    serverSSL = smtplib.SMTP_SSL(smtpServer)
    serverSSL.login(emailUser, emailPassword)
    serverSSL.sendmail(emailUser, emailUser, emailText)
    serverSSL.quit()
    log('Email sent!')
    return 0


@tryExcept(tries=5)
def getEmail():
    '''
    '''
    mail = imaplib.IMAP4_SSL(imapServer)
    mail.login(emailUser, emailPassword)
    mail.select('inbox')
    obj, data = mail.search(None, '(FROM "{}")'.format(emailUser),
                                  '(SUBJECT "{}")'.format(emailSubject))
    typ, data = mail.fetch(data[0].split()[-1],  'BODY[1]')
    body = data[0][1].replace(b'\r\n', b'').decode('utf8')
    log('Last email body: \'{}\''.format(body))
    mail.close()
    return body


@tryExcept(tries=1, delay=0)
def checkIP(ip):
    with open(filePath, 'r') as f:
        data = f.read()
    regex = re.compile(r'sometexthere(IPaddresshere)someothertexthere', re.I)

    oldIP = regex.search(data).group(1)

    assert inet_aton(oldIP)

    if oldIP == ip:
        log('Checked IP is the same... no change is needed.')
        return None
    else:
        log('Checked IP is the different: it must be changed!')
        return True


@tryExcept(tries=1, delay=0)
def checkAppRunning():
    pass


@tryExcept(tries=1, delay=0)
def changeIP(ip):

    with open(filePath, 'r') as f:
        data = f.read()
   
    data = re.sub(r'(sometexthere)IPaddresshere(someothertexthere)',
                  r'\g<1>{0}\g<2>'.format(ip),
                  data)
    
    with open(filePath, 'w') as f:
        f.write(data)

    log('IP change wrote to file.')


def statusColorChange(color):
    statusWindow.configure(background=color)
    statusWindow.lift()
    statusWindow.update()


def createStatusWindow(color='grey',title='None', text=None):
    global statusWindow
    statusWindow = Tk()
    statusWindow.title(title)
##    use +Horizontal+Vertical to set the position on screen
    statusWindow.geometry('100x100+0+0')
    statusColorChange(color)
    statusWindow.update()

def createPopup(color='grey',title='None', text=None):

    def delPopup():
        runningPopup.destroy()

    global runningPopup
    runningPopup = Tk()
    runningPopup.title(title)
    popupWidth = 250
    popupHeight = 150
    screenWidth = runningPopup.winfo_screenwidth()
    screenHeight = runningPopup.winfo_screenheight()
    xCoord = int((screenWidth/2) - (popupWidth/2))
    yCoord = int((screenHeight/2) - (popupHeight/2))
    runningPopup.geometry('{0}x{1}+{2}+{3}'.format(popupWidth, popupHeight,
                                                   xCoord, yCoord))
    runningPopup.wm_attributes('-topmost', 1) # always on top
    runningPopup.configure(background=color)
    popupButton = Button(runningPopup, command=delPopup,
                            text='OK', height=2, width=7)
    popupButton.place(relx=0.5, rely=0.5, anchor='center')
    if text:
        popupLabel = Label(runningPopup, text=text)
        popupLabel.place(relx=0.5, rely=0.1, anchor='n')
    runningPopup.mainloop() # the purpose is to stop the program until user clicks OK
                            # that destroys the popup and then program exits


@tryExcept(tries=1, delay=0)
def serverMain():
    createStatusWindow(color='yellow', title='IP')
    while True:
        IP = getIP()
        if IP:
            sendEmail(encryptIP(IP))
            statusColorChange('green')
            wait(3600)
        else:
            statusColorChange('yellow')
            wait(7)


@tryExcept(tries=1, delay=0)
def clientMain():
    IP = getIP()
    if checkIP(IP):
        checkAppRunning()
        changeIP(IP)
        createPopup(color='green', title='Success!', text='success')
        exit(0)
    else:
        pass
