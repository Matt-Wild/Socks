HEADER = 64
FORMAT = 'utf-8'


def send_message(socket, message):
    message_length = str(len(message))
    message_length += " " * (HEADER - len(message_length))
    data = message_length + message
    socket.send(data.encode(FORMAT))


def receive_message(socket):
    message_length = socket.recv(HEADER).decode(FORMAT)
    if message_length:
        try:
            message_length = int(message_length)
            try:
                message = socket.recv(message_length).decode(FORMAT)
            except OverflowError:
                return "ERROR|ERROR SENDING MESSAGE... RETRYING"
        except ValueError:
            return "ERROR|ERROR SENDING MESSAGE... RETRYING"
        return message
    else:
        return None
