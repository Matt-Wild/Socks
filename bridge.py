HEADER = 16
PACKET = 64
FORMAT = "utf-8"


def send_message(socket, message):
    # Encoding data
    data = message.encode(FORMAT)

    # Splitting into packets
    while len(data) > PACKET:
        packet = data[:PACKET]
        data = data[PACKET:]

        # Getting packet header
        header = "CNTU" + str(PACKET)
        while len(header) < HEADER:
            header += " "

        # Sending packet header and body
        socket.send(header.encode(FORMAT))
        socket.send(packet)

    # Sending final packet
    # Getting header
    header = "FNAL" + str(len(data))
    while len(header) < HEADER:
        header += " "

    # Sending packet header and body
    socket.send(header.encode(FORMAT))
    socket.send(data)


def receive_message(socket):
    # Getting header and packet length
    header = socket.recv(HEADER).decode(FORMAT)
    packet_length = int(header[4:])
    header = header[:4]

    # Getting first packet
    data = socket.recv(packet_length)

    # Looping until all the packets have been received
    while header == "CNTU":
        # Getting header and packet length
        header = socket.recv(HEADER).decode(FORMAT)
        packet_length = int(header[4:])
        header = header[:4]

        # Getting first packet
        data += socket.recv(packet_length)

    return data.decode(FORMAT)
