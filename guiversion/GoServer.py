
import sys
import tkinter
import tkinter.font as tkFont
import socket
import threading
import time
from tkinter import filedialog as fd
import os
import config

class GoServer:
    
    def __init__(self):
        self.initGUI()

       # msg socket 
        self.msgsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        self.msgsocket.bind((config.ip,config.msgport))
       

        # file socket
        self.filesocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        self.filesocket.bind((config.ip,config.fileport))
        
        self.msgsocket.listen() 
        self.filesocket.listen()

        self.isConnect = False 
        self.chatText.insert(tkinter.END,f'<SYSTEM WARNING>: {config.askquit}')
        self.chatText.insert(tkinter.END,'<SYSTEM WARNING>: server is running......')
        
        self.startThreadListenMsg()
        self.startThreadListenFile()

    """
    Some GUI Templates
    """
    def initGUI(self):
        self.root=tkinter.Tk()
        self.root.title('BoxComm [Server]')
        # 4 panel frames
        self.frame=[tkinter.Frame(),tkinter.Frame(),tkinter.Frame(),tkinter.Frame()]

        # shown msg scrrent scroll bar
        self.chatTextScrollBar=tkinter.Scrollbar(self.frame[0])
        self.chatTextScrollBar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        
        # shown msg box
        ft=tkFont.Font(family='Fixdsys',size=11)
        self.chatText=tkinter.Listbox(self.frame[0],width=70,height=18,font=ft)
        self.chatText['yscrollcommand']=self.chatTextScrollBar.set
        self.chatText.pack(expand=1,fill=tkinter.BOTH)
        self.chatTextScrollBar['command']=self.chatText.yview()
        self.frame[0].pack(expand=1,fill=tkinter.BOTH)

        # labels to seperate [shown msg box] and [type msg box]
        label=tkinter.Label(self.frame[1],height=2)
        label.pack(fill=tkinter.BOTH)
        self.frame[1].pack(expand=1,fill=tkinter.BOTH)

        # [type msg box]
        self.inputTextScrollBar=tkinter.Scrollbar(self.frame[2])
        self.inputTextScrollBar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        ft=tkFont.Font(family='Fixdsys',size=11)
        self.inputText=tkinter.Text(self.frame[2],width=70,height=8,font=ft)
        self.inputText['yscrollcommand']=self.inputTextScrollBar.set
        self.inputText.pack(expand=1,fill=tkinter.BOTH)
        self.inputTextScrollBar['command']=self.chatText.yview()
        self.frame[2].pack(expand=1,fill=tkinter.BOTH)

        # [send message button]
        self.sendButton=tkinter.Button(self.frame[3],text='Send Message',width=10,command=self.sendMessage)
        self.sendButton.pack(expand=1,side=tkinter.BOTTOM and tkinter.RIGHT,padx=25,pady=5)
        
        # [close app button]
        self.closeButton = tkinter.Button(self.frame[3], text='Close App', width=10, command=self.close)
        self.closeButton.pack(expand=1, side=tkinter.RIGHT, padx=25, pady=5)
        self.frame[3].pack(expand=1,fill=tkinter.BOTH)
        
        # [browse and send file button]
        self.browseButton = tkinter.Button(self.frame[3], text='Send File', width=10, command=self.sendFile)
        self.browseButton.pack(expand=1, side=tkinter.LEFT, padx=25, pady=5)

    # ------------------------------- Message Handling ---------------------------------------------- #

    def sendMessage(self):
        msg = self.inputText.get('1.0',tkinter.END)
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        
        self.chatText.insert(tkinter.END, 'Server Said ' + curtime + ' :\n')
        self.chatText.insert(tkinter.END, '  ' + msg+'\n')
        self.inputText.delete(0.0,msg.__len__()-1.0)

        # send 
        if self.isConnect:
            self.clientmsgsocket.send(msg.encode(config.format))
        else:
            self.chatText.insert(tkinter.END,f'<SYSTEM WARNING>: You did not connect to a client\n')

    def recMsg(self):
        while True:
            self.clientmsgsocket, self.clientmsgsocketaddr = self.msgsocket.accept()
            self.clientfilesocket, self.clientfilesocketaddr = self.filesocket.accept()
            self.isConnect = True 
            self.chatText.insert(tkinter.END,'server connected to client!')

            while self.isConnect:
                clientmsg = self.clientmsgsocket.recv(config.buffer).decode(config.format)
                if clientmsg:
                    if clientmsg.strip() == config.askquit:
                        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                        self.chatText.insert(tkinter.END,'<SYSTEM WARNING>: Client quited at '+curtime)
                        self.isConnect = False 
                        self.clientfilesocket.close()
                        self.clientmsgsocket.close()
                    else:
                        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                        self.chatText.insert(tkinter.END,'Client Sent '+curtime+' :\n')
                        self.chatText.insert(tkinter.END,'  '+ clientmsg)

    def startThreadListenMsg(self):
        thread=threading.Thread(target=self.recMsg,args=())
        thread.daemon = True
        thread.start()

    # ------------------------------------------------------------------------------------------------------------ # 

    # ----------------------------------- File Handling ---------------------------------------------------------- #

    def sendFile(self):
        filepath = fd.askopenfilename()
        filesize = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        # 1) header string
        headerstr = f"{filename}{config.sep}{filesize}" 
        headerstr = headerstr.encode(config.format)

        # 2) measure the header length and append to 1024 bits
        headerlen = len(headerstr)
        headerlen = str(headerlen).encode(config.format)
        headerlen += b' '* (config.buffer - len(headerlen))

        # 3) tell client the headerlen first then headerstr
        self.clientfilesocket.send(headerlen)
        self.clientfilesocket.send(headerstr)


        # 4) get file bytes and sendall
        with open(filepath, 'rb') as f:
            cnt = 0
            while cnt < filesize:
                bytesRead = f.read(config.buffer)
                if not bytesRead:
                    break 
                self.clientfilesocket.sendall(bytesRead)
                cnt += len(bytesRead)

        theTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        self.chatText.insert(tkinter.END, f'{config.fileactstr}Server' + theTime + ' said:\n')
        self.chatText.insert(tkinter.END, f'  File at {filepath} sent' ) 
        
    def recFile(self):
        while True:
            try:
                headerlen = int(self.clientfilesocket.recv(config.buffer).decode(config.format))
                headerstr = str(self.clientfilesocket.recv(headerlen).decode(config.format))
                filename, filesize = headerstr.split(config.sep)
                filesize = int(filesize)

                print("Received filename: ", filename)
                print("Received filesize: ", filesize)

                fileloc = config.serverfolder + filename
                with open(fileloc, 'wb') as f:
                        cnt = 0
                        while cnt < filesize:
                            bytesRead = self.clientfilesocket.recv(config.buffer)
                            if not bytesRead:
                                break
                            print("Received data: ", bytesRead)
                            f.write(bytesRead)
                            f.flush()
                            cnt += len(bytesRead)

                theTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                self.chatText.insert(tkinter.END, f'{config.fileactstr}Server' + theTime + ' said:\n')
                self.chatText.insert(tkinter.END, f'{config.space}Received a file and stored at {fileloc}' ) 
            except:
                continue

    def startThreadListenFile(self):
        thread = threading.Thread(target=self.recFile, args=())
        thread.daemon = True
        thread.start()
    # ------------------------------------------------------------------------------------------------------------ # 

    def close(self):
        sys.exit()

if __name__ == '__main__':
    server = GoServer()
    server.root.mainloop()
