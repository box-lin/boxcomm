import socket 
import config
import threading
import os, sys

class Client:

    def __init__(self) -> None:

        # Initializing the sockets 
        # 1) message socket 
        # 2) file socket 
        print("client running")
        self.msgsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.filesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to server
        self.msgsocket.connect( (config.ip, config.msgport) )
        print("server msgsocket connected")

        self.filesocket.connect( (config.ip, config.fileport) )
        print("server filesocket connected")


        # Thread 2 message listening 
        self.msgthread = threading.Thread(target=self.listenMsg, args=())
        self.msgthread.start() 


        # Thread 3 file listening 
        self.filethread = threading.Thread(target=self.listenFile, args=())
        self.filethread.start()

        # Thread 1 program itself taking user inputs
        self.getInput()
    

    """
    Keep listening file coming from filesocket
    @ How it works:
        1. get the header length
        2. get the header 
        3. get the file data in bytes
        4. create the file and write the file data into it

    @ Why using Try Except:
        1. the headerlen received sometimes become a data (I think it is because of the thread execution random order)
           it then throws exception because data cannot be parse into int
    """
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

    
    """
    Keep listening message coming from msgsocket
    @ How it works:
        1 Just receive and print it to console
    """
    def listenMsg(self):
        while True:
            serverMsg = self.msgsocket.recv(config.buffer).decode(config.format)
            if serverMsg:
                print("you have received: ", serverMsg)

    """
    Send message using msgsocket
    """
    def sendMessage(self):
        msg = input("send message>> \n")
        self.msgsocket.send(msg.encode(config.format))

    """
    Send file using filesocket
    @ How it works:
        1. 
    """
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


    """
    Thread 1 = the program itself that processing user inputs
    """
    def getInput(self):
        while True:
            print("[Menu] 1 = send message | 2 = send file | 3 = quit")
            cmd = input("cmd>>> \n")
            if cmd.strip() == '1':
                self.sendMessage() 
            elif cmd.strip() == '2':
                self.sendFile() 
            elif cmd.strip() == '3':
                self.msgsocket.close()
                self.filesocket.close()
                self.msgthread.join()
                self.filethread.join()
                sys.exit() 
            else:
                continue

if __name__ == "__main__":
    c = Client()