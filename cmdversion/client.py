import socket 
import config
import threading
import os

class Client:

    def __init__(self) -> None:

        print("client running")
        self.msgsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.filesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.msgsocket.connect( (config.ip, config.msgport) )
        print("server msgsocket connected")

        self.filesocket.connect( (config.ip, config.fileport) )
        print("server filesocket connected")

        msgthread = threading.Thread(target=self.listenMsg, args=())
        msgthread.start() 

        filethread = threading.Thread(target=self.listenFile, args=())
        filethread.start()


        self.getInput()
    
    def listenFile(self):
 
        while True: 
            try:

                headerlen = int(self.filesocket.recv(config.buffer).decode(config.format))
                headerstr = str(self.filesocket.recv(headerlen).decode(config.format))
                filename, filesize = headerstr.split(config.sep)
                filesize = int(filesize)
                print("Received filename: ", filename)
                print("Received filesize: ", filesize)

                fileloc = config.clientfolder + filename
                with open(fileloc, 'wb') as f:
                    cnt = 0
                    while cnt < filesize:
                        bytesRead = self.filesocket.recv(config.buffer)
                        if not bytesRead:
                            break
                        print("Received data: ", bytesRead)
                        f.write(bytesRead)
                        f.flush()
                        cnt += len(bytesRead)
                print(f"file {filename} received successfully, saved in {fileloc}") 

            except:
                pass

         
    def listenMsg(self):
        while True:
            serverMsg = self.msgsocket.recv(config.buffer).decode(config.format)
            if serverMsg:
                print("you have received: ", serverMsg)

    def sendMessage(self):
        msg = input("send message>> \n")
        self.msgsocket.send(msg.encode(config.format))

    def sendFile(self):

        filename = input("enter filename>> \n")
        filesize = os.path.getsize(filename)


        # 1) send the filename and filesize first 
        headerstr = f"{filename}{config.sep}{filesize}" 
        headerstr = headerstr.encode(config.format)

        headerlen = len(headerstr)
        headerlen = str(headerlen).encode(config.format)
        headerlen += b' '* (config.buffer - len(headerlen))

        self.filesocket.send(headerlen)
        self.filesocket.send(headerstr)

        with open(filename, 'rb') as f:
            cnt = 0
            while cnt < filesize:
                bytesRead = f.read(config.buffer)
                if not bytesRead:
                    break 
                self.filesocket.sendall(bytesRead)
                cnt += len(bytesRead)
        print(f"{filename} sent successfully")

    def getInput(self):
        while True:
            print("[Menu] 1 = send message | 2 = send file ")
            cmd = input("cmd>>> \n")
            if cmd.strip() == '1':
                self.sendMessage() 
            elif cmd.strip() == '2':
                self.sendFile() 

if __name__ == "__main__":
    c = Client()