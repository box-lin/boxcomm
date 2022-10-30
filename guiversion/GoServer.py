import sys
import tkinter
import tkinter.font as tkFont
import socket
import threading
import time
from tkinter import filedialog as fd
import os

class GoServer:
    
    def __init__(self):
        self.initGUI()
    
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

    def sendMessage(self):
        pass 
    def close(self):
        sys.exit()
    def sendFile(self):
        pass
    
if __name__ == '__main__':
    server = GoServer()
    server.root.mainloop()