import socket
import time
import tkinter as tk
import threading

import bridge

server_ip = input("Enter server IP: ")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((server_ip, 9696))


def receive_loop():
    while True:
        received = bridge.receive_message(server)
        if received:
            chat_log.insert(tk.END, received + "\n")


def update_loop():
    while True:
        bridge.send_message(server, "UPDATE|")

        time.sleep(0.1)


def from_rgb(rgb):
    return "#%02x%02x%02x" % rgb


def send_message(event=None):
    message = message_entry.get()
    if message:
        message_entry.delete(0, 'end')
        bridge.send_message(server, "SEND|" + message)


def send_nickname(event=None):
    new_nickname = nickname_entry.get()
    if nickname:
        bridge.send_message(server, "USERNAME|" + new_nickname)


bg_colour = from_rgb((20, 20, 20))
ui_colour = from_rgb((40, 40, 40))
uif_colour = from_rgb((200, 200, 200))

window = tk.Tk()
window.title("Socks")
window.iconbitmap('icon.ico')
window.configure(background=bg_colour)
window.grid_rowconfigure(1, weight=0)
window.grid_rowconfigure(2, weight=0)
window.grid_rowconfigure(3, weight=0)
window.grid_rowconfigure(3, weight=1)

tk.Label(window, text="Nickname:", bg=bg_colour, fg="white", font="none 10").grid(row=0, column=0, sticky=tk.W, padx=(10, 0), pady=(5, 0))

nickname_entry = tk.Entry(window, width=25, bg=ui_colour, fg=uif_colour, font="none 16")
nickname_entry.grid(row=1, column=0, sticky=tk.W, padx=(10, 5), pady=(0, 10))
nickname_entry.bind('<Return>', send_nickname)

tk.Label(window, text="Message:", bg=bg_colour, fg="white", font="none 10").grid(row=2, column=0, sticky=tk.W, padx=(10, 0))

message_entry = tk.Entry(window, width=30, bg=ui_colour, fg=uif_colour, font="none 16")
message_entry.grid(row=3, column=0, sticky=tk.N, padx=(10, 5), pady=(0, 10))
message_entry.bind('<Return>', send_message)

tk.Button(window, text="SEND", width=6, height=1, command=send_message).grid(row=3, column=1, sticky=tk.N, padx=(0, 10), pady=(0, 10))

chat_log = tk.Text(window, width=70, height=50, wrap=tk.WORD, background=ui_colour, fg=uif_colour)
chat_log.grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(0, 10), rowspan=3)

# Getting welcome response
welcome_response = bridge.receive_message(server)
chat_log.insert(tk.END, welcome_response + "\n")

# Getting nickname
bridge.send_message(server, "RETRIEVE|USERNAME")
nickname = bridge.receive_message(server)
nickname_entry.insert(tk.END, nickname)

receive_thread = threading.Thread(target=receive_loop)
receive_thread.start()

update_thread = threading.Thread(target=update_loop)
update_thread.start()

window.mainloop()
