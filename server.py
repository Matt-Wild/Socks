import socket
import threading

import timestamp
import bridge

debug = False

VERSION = '0.5.6'

print(f"Version: {VERSION}")
print("[STARTING] Attempting to start server...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if debug:
    s.bind(('127.0.0.1', 9696))
else:
    s.bind(('192.168.1.82', 9696))
s.listen(1024)


class Server:

    def __init__(self):
        self.clients = []

    def run(self):
        print("[LISTENING] Listening for new connections...")
        while True:
            self.receive_connections()

    def receive_connections(self):
        client_socket, address = s.accept()
        if not self.check_for_client(address):
            self.add_client(client_socket, address)
        else:
            self.client_returned(client_socket, address)
        client_thread = threading.Thread(target=self.client_thread, args=(client_socket, address))
        client_thread.start()

    def client_thread(self, client_socket, address):
        client = self.get_client(address)

        while client.connected:
            update = True

            try:
                received = bridge.receive_message(client_socket).split("|")
                header = received[0]
                received.pop(0)
                body = ''.join(received)
                if header == "SEND":
                    message = "\n" + body
                    sender = client.username
                    if not sender:
                        sender = address[0]
                    for external_client in self.clients:
                        if external_client != client:
                            external_client.messages.append((sender, message))
                        else:
                            external_client.messages.append(("LOCAL", message))
                elif header == "USERNAME":
                    print(f"[{timestamp.get()}NAME CHANGE] {address[0]} -> {body}")
                    client.username = body
                    for current_client in self.clients:
                        current_client.conns_update = True
                elif header == "RETRIEVE":
                    update = False
                    if body == "USERNAME":
                        bridge.send_message(client_socket, client.username)
                elif header == "ERROR":
                    client.messages.append((header, body))

                if update:
                    response = client.get_update()
                    if response:
                        bridge.send_message(client_socket, response)
            except ConnectionResetError:
                for external_client in self.clients:
                    if external_client != client:
                        external_client.conns_update = True
                        external_client.disconnections.append(client.username)

                print(f"[{timestamp.get()}DISCONNECTED] {address[0]}")
                client.connected = False

        client_socket.close()

    def add_client(self, client_socket, address):
        print(f"[{timestamp.get()}NEW CONNECTION] {address[0]}")
        bridge.send_message(client_socket, f"Server version: {VERSION}\nWelcome {address[0]}, connection successfully "
                                           f"established!")
        self.clients.append(Client(self.clients, address[0]))

        for client in self.clients:
            client.conns_update = True
            if client.username != address[0]:
                client.new_connections.append(address[0])

    def client_returned(self, client_socket, address):
        client = self.get_client(address)

        for external_client in self.clients:
            external_client.conns_update = True
            if external_client != client:
                external_client.returned_connections.append(client.username)

        print(f"[{timestamp.get()}CONNECTION RETURNED] {address[0]}")
        bridge.send_message(client_socket, f"Welcome back {client.username}!")
        client.connected = True

    def check_for_client(self, address):
        for client in self.clients:
            if client.address == address[0]:
                return True
        return False

    def get_client(self, address):
        for client in self.clients:
            if client.address == address[0]:
                return client
        return None


class Client:

    def __init__(self, clients, address):
        self.clients = clients

        self.address = address
        self.username = address

        self.connected = True

        self.conns_update = False

        self.new_connections = []
        self.returned_connections = []
        self.disconnections = []
        self.messages = []

    def get_update(self):
        response = ""

        if len(self.new_connections) > 0:   # New user joined
            response = f"MSG|[{timestamp.get()}JOINED] {self.new_connections[0]}"
            self.new_connections.pop(0)
            return response

        if len(self.returned_connections) > 0:   # User returned
            response = f"MSG|[{timestamp.get()}RETURNED] {self.returned_connections[0]}"
            self.returned_connections.pop(0)
            return response

        if len(self.disconnections) > 0:   # User discord
            response = f"MSG|[{timestamp.get()}DISCONNECTED] {self.disconnections[0]}"
            self.disconnections.pop(0)
            return response

        if len(self.messages) > 0:  # Message received
            response = f"MSG|[{timestamp.get()}{self.messages[0][0]}] {self.messages[0][1]}"
            self.messages.pop(0)
            return response

        if self.conns_update:
            response = "CONNS|"
            for client in self.clients:
                if client.connected:
                    response += f" - {client.username}"
                    if client == self:
                        response += " (You)"
                    response += "\n"
            self.conns_update = False
            return response

        return response     # No update required


server = Server()
server.run()
