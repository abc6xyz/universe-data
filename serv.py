import socket
import threading
import json

client_a = None

client_b = {}

def handle_b(mac_addr):
    global client_a
    global client_b
    while True:
        try:
            command = client_b[mac_addr].recv(1500)
            try:
                client_a.send(command)
            except:
                client_b[mac_addr].send(json.dumps({"success":False}))
                print("Client A disconnected")
        except ConnectionResetError:
            print(f"client_b['{mac_addr}'] closed the connection")
            del client_b[mac_addr]
            break

def handle_a():
    global client_a
    global client_b
    while True:
        try:
            command = client_a.recv(1024)
            try:
                data = json.loads(command.decode())
                if data['mac'] == "00:00:00:00:00:00":
                    for key, client in client_b.items():
                        client.send(command)
                else:
                    client_b[data['mac']].send(command)
            except:
                print("Command data format error")
        except ConnectionResetError:
            print("Client A closed the connection")
            client_a = None
            break

def handle_socket(client_socket):
    global client_a
    global client_b
    try:
        command = client_socket.recv(1024)
        data = json.loads(command.decode())
        if data["role"] == "admin" and data["pwd"] == "0x1e8ad7c":
            client_a = client_socket
            client_socket.send(json.dumps({"success":True}).encode())
            threading.Thread(target=handle_a).start()
            print('Client A connected')
        elif data["role"] == "client":
            try:
                client_b[data['mac']]
                client_socket.send(json.dumps({"success":False}).encode())
            except:
                client_b[data['mac']] = client_socket
                client_socket.send(json.dumps({"success":True}).encode())
                threading.Thread(target=handle_b, args=(data['mac'],)).start()
                print(f"Client B['{data['mac']}'] connected")
        else:
            client_socket.send(json.dumps({"success":False}).encode())
            client_socket.close()
    except ConnectionResetError:
        client_socket.send(json.dumps({"success":False}).encode())
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 1234))
    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        threading.Thread(target=handle_socket, args=(client_socket,)).start()

start_server()