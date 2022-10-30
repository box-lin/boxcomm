
import socket 
import config
import threading
import os
import tqdm

class Server:

    def __init__(self) -> None:

        print("server listening")

        self.msgsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msgsocket.bind( (config.ip, config.msgport) )
        self.msgsocket.listen()
         

        self.filesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.filesocket.bind( (config.ip, config.fileport) )
        self.filesocket.listen()

        self.clientmsgsocket, self.clientmsgsocketaddress = self.msgsocket.accept()
        print("client msgsocket connected")
        self.clientfilesocket, self.clientfilesocketaddress = self.filesocket.accept()
        print("client filesocket connected")


        # two threads that listening for message and file 
        msgthread = threading.Thread(target=self.listenMsg, args=())
        msgthread.start() 

        filethread = threading.Thread(target=self.listenFile, args=())
        filethread.start()

        self.getInput()

    def listenFile(self):
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
                print(f"file {filename} received successfully, saved in {fileloc}") 

            except:
                pass
    
    def listenMsg(self):
        while True:
            cientMsg= self.clientmsgsocket.recv(config.buffer).decode(config.format)
            if cientMsg:
                print("you have received: ", cientMsg)

    def sendMessage(self):
        msg = input("send message>> \n")
        self.clientmsgsocket.send(msg.encode(config.format))

    def sendFile(self):

        filename = input("enter filename>> \n")
        filesize = os.path.getsize(filename)


        # 1) send the filename and filesize first 
        headerstr = f"{filename}{config.sep}{filesize}" 
        headerstr = headerstr.encode(config.format)

        headerlen = len(headerstr)
        headerlen = str(headerlen).encode(config.format)
        headerlen += b' '* (config.buffer - len(headerlen))

        self.clientfilesocket.send(headerlen)
        self.clientfilesocket.send(headerstr)

        with open(filename, 'rb') as f:
            cnt = 0
            while cnt < filesize:
                bytesRead = f.read(config.buffer)
                if not bytesRead:
                    break 
                self.clientfilesocket.sendall(bytesRead)
                cnt += len(bytesRead)
        print(f"{filename} sent successfully")

    
    # server running and talk
    def getInput(self) -> None:
        while True:
            print("[Menu] 1 = send message | 2 = send file ")
            cmd = input("cmd>> \n")
            if cmd.strip() == '1':
                self.sendMessage() 
            elif cmd.strip() == '2':
                self.sendFile() 


if __name__ == "__main__":
    s = Server()