import socket
import time
import tkinter as tk
import threading

import bridge

server_ip = input("Enter server IP: ")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((server_ip, 9696))


class ClientData:

    def __init__(self):
        self.nickname = None


def receive_loop():
    connected = True
    while connected:
        try:
            received = bridge.receive_message(server)
            if received:
                received = received.split("|")
                if received[0] == "MSG":
                    received = "".join(received[1:])
                    chat_log.configure(state="normal")
                    chat_log.insert(tk.END, received + "\n")
                    chat_log.see('end')
                    chat_log.configure(state="disabled")
                elif received[0] == "CONNS":
                    connections_log.configure(state="normal")
                    connections_log.delete('0.0', tk.END)
                    connections_log.insert(tk.END, received[1])
                    connections_log.configure(state="disabled")
        except ConnectionResetError:
            connected = False
            chat_log.configure(state="normal")
            chat_log.delete('0.0', tk.END)
            chat_log.insert(tk.END, "Server connection lost...")
            chat_log.configure(state="disabled")


def update_loop():
    connected = True
    while connected:
        try:
            bridge.send_message(server, "UPDATE|")

            time.sleep(0.1)
        except ConnectionResetError:
            connected = False


def gui_update_loop():
    while True:
        update_nickname_colour()

        time.sleep(0.1)


def from_rgb(rgb):
    return "#%02x%02x%02x" % rgb


def update_nickname_colour():
    if nickname_entry.get() == CD.nickname:
        nickname_entry.configure(fg=uif_dark)
    else:
        nickname_entry.configure(fg=uif_colour)


def send_message(event=None):
    message = message_entry.get()
    if message:
        message_entry.delete(0, 'end')
        bridge.send_message(server, "SEND|" + message)


def send_nickname(event=None):
    new_nickname = nickname_entry.get()
    if new_nickname:
        bridge.send_message(server, "USERNAME|" + new_nickname)
        CD.nickname = new_nickname


CD = ClientData()

bg_colour = from_rgb((20, 20, 20))
ui_colour = from_rgb((40, 40, 40))
uif_colour = from_rgb((200, 200, 200))
uif_dark = from_rgb((100, 100, 100))

window = tk.Tk()
window.title("Socks")
window.iconbitmap('icon.ico')
window.configure(background=bg_colour)

tk.Label(window, text="Nickname:", bg=bg_colour, fg="white", font="none 10").grid(row=0, column=0, sticky=tk.W, padx=(10, 0), pady=(5, 0))

nickname_entry = tk.Entry(window, width=25, bg=ui_colour, fg=uif_colour, font="none 16")
nickname_entry.grid(row=1, column=0, sticky=tk.W, padx=(10, 5), pady=(0, 10))
nickname_entry.bind('<Return>', send_nickname)

tk.Label(window, text="Message:", bg=bg_colour, fg="white", font="none 10").grid(row=2, column=0, sticky=tk.W, padx=(10, 0))

message_entry = tk.Entry(window, width=30, bg=ui_colour, fg=uif_colour, font="none 16")
message_entry.grid(row=3, column=0, sticky=tk.NW, padx=(10, 5), pady=(0, 10))
message_entry.bind('<Return>', send_message)

tk.Button(window, text="SEND", width=6, height=1, command=send_message).grid(row=3, column=1, sticky=tk.NW, padx=(0, 10), pady=(0, 10))

tk.Label(window, text="Connections:", bg=bg_colour, fg="white", font="none 10").grid(row=4, column=0, sticky=tk.W, padx=(10, 0))

connections_log = tk.Text(window, width=45, wrap=tk.WORD, background=ui_colour, fg=uif_colour, state="disabled")
connections_log.grid(row=5, column=0, sticky=tk.NW, padx=(10, 5))

tk.Label(window, text="Chat Log:", bg=bg_colour, fg="white", font="none 10").grid(row=0, column=2, sticky=tk.W)

chat_log = tk.Text(window, width=70, height=50, wrap=tk.WORD, background=ui_colour, fg=uif_colour)
chat_log.grid(row=1, column=2, sticky=tk.NW, pady=(0, 10), rowspan=5)
chat_scrollbar = tk.Scrollbar(window, command=chat_log.yview)
chat_scrollbar.grid(row=1, column=3, rowspan=5, padx=(0, 10), pady=(0, 10), sticky='nsew')
chat_log.config(yscrollcommand=chat_scrollbar.set)

window.grid_rowconfigure(0, weight=0)
window.grid_rowconfigure(1, weight=0)
window.grid_rowconfigure(2, weight=0)
window.grid_rowconfigure(3, weight=0)
window.grid_rowconfigure(4, weight=0)
window.grid_rowconfigure(5, weight=1)

# Getting welcome response
welcome_response = bridge.receive_message(server)
chat_log.insert(tk.END, welcome_response + "\n")

# Getting nickname
bridge.send_message(server, "RETRIEVE|USERNAME")
CD.nickname = bridge.receive_message(server)
nickname_entry.insert(tk.END, CD.nickname)

chat_log.configure(state="disabled")

receive_thread = threading.Thread(target=receive_loop)
receive_thread.start()

update_thread = threading.Thread(target=update_loop)
update_thread.start()

gui_update_thread = threading.Thread(target=gui_update_loop)
gui_update_thread.start()

window.mainloop()
