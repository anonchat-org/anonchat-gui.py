import argparse, sys, socket
import threading, json

import tkinter as tk
from tkinter import *
from tkinter.scrolledtext import ScrolledText

VERSION = "v0.1"

class Commands:
    def __init__(self):
        self.cmds = {
                "help": self.help,
                "nick": self.chname
            }

    def help(self, args, CLI):
        return """[CLIENT] -----
[CLIENT] Server Version: Unknown (Not implemented)
[CLIENT] Client Version: %s
[CLIENT] -----
[CLIENT] Commands:
[CLIENT] help
[CLIENT] nick
[CLIENT] -----""" % VERSION

    def chname(self, args, CLI):
        if len(args.split(" ")) <= 1:
            return "[CLIENT] No name passed."
        name = "".join(args.split(" ")[1:])
        CLI.name = name

        return f"[CLIENT] Your name changed to {name}"
        

commands = Commands()

def CommandProcess(command, name, CLI):
    if command.strip().split(" ")[0] in commands.cmds:
        text = commands.cmds[command.strip().split(" ")[0]](command.strip(), CLI)
        text = f"\n<{name}> /{command}\n"+text
        return True, text
    else:
        return False, ""

class GUI:
    def __init__(self, socket, ip = "example.com:8080", name = "Anon"):
        self.window = tk.Tk()

        self.ip = ip
        self.name = name
        self.socket = socket
        
        self.window.title(f"AnonChat: {ip}")
        self.window.geometry(f"600x600")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.exit)

        self.prepare_layout()
        self.pack()

        
        self.request = threading.Thread(target=self.th_request, args=())
        self.request.start()
        
        self.window.mainloop()

    def th_request(self):
        while True:
            if self.socket.fileno() != -1:
                try:
                    message = self.socket.recv(1024)
                except:
                    break
                
            if not message:
                break

            try:
                message = message.decode()
                try:
                    message = json.loads(message.strip())
                except:
                    message = {"user": "V1-Message", "msg": message}
                    
            except:
                message = ({"user": "[CLIENT]", "msg": "Message was recieved, but the contents cannot be decoded :("})

            self.text['state'] = 'normal'

            spaces = len("<"+message['user']+"> ")*" "
            self.text.insert(tk.END, "\n" + f'<{message["user"]}> ' + message["msg"].replace("\n", f"\n{spaces}"))
            self.text['state'] = 'disabled'

    def prepare_layout(self):
        self.t_text = tk.StringVar()
        
        self.text = ScrolledText(self.window, height=33, wrap=WORD, bg="#dcdcdc", state='disabled')
        self.entry = tk.Entry(self.window, width=100)
        self.label = tk.Label(self.window, text="Your Text:", anchor='w')
        self.button = tk.Button(self.window, text="Send", anchor="w", command=self.send)

    def send(self, enter=None):
        text = self.entry.get()

        if not text.strip():
            return

        send = False
        
        if text.startswith("/"):
            send, text = CommandProcess(text[1:], self.name, self)

            if send:
                self.text['state'] = 'normal'
                self.text.insert(tk.END, text)
                self.text['state'] = 'disabled'
            
        if not send:
            message = {"user": self.name, "msg": text}                    
            self.socket.send(json.dumps(message, ensure_ascii=False).encode())

        self.entry.delete(0, 'end')
            

    def pack(self):
        self.text.pack()

        self.text['state'] = 'normal'
        self.text.insert("1.0", f"[CLIENT] Welcome to the AnonChat!\n[CLIENT] You are connected to the {self.ip} server.\n[CLIENT] Your nickname is {self.name}\n[CLIENT] Try to use /help, to see !LOCAL! commands.")
        self.text.focus()
        self.text.bind("<1>", lambda event: self.text.focus_set())
        self.text['state'] = 'disabled'
        
        self.label.pack(fill="both")
        
        self.entry.pack()
        self.entry.insert("0", "Hello World!")


        self.window.bind('<Return>', lambda event=None: self.button.invoke())
        self.button.pack(fill="both")


    def exit(self):
        self.socket.close()
        self.window.destroy()
        sys.exit()

class Client:
    def __init__(self):
        self.messages = []
        
        self.parser()
        self.start()

    def parser(self):
        parser = argparse.ArgumentParser(
        prog="anonchat-cli",
        description = "Connect to the anonchat",
        epilog="---- Oh, hello there!")
 
        parser.add_argument("ip", help = "IP of anonchat-server", type=str)
        parser.add_argument("-n", "--name", help = "Your name?", type=str, default = "Anon")
        
        args = parser.parse_args()

        ip = args.ip.split(":")
        ip.append(6969)

        self.ip = ip[0]
        self.name = args.name
        
        try:
            self.port = int(ip[1])
        except:
            print(f"Cannot parse port {ip[1]} as number. Aborting.")
            sys.exit()

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        
        self.gui = GUI(self.socket, f"{self.ip}:{self.port}", self.name)
        


if __name__ == "__main__":
    cli = Client()
        
        
