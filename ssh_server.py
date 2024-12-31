import os 
import paramiko 
import socket 
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    USERNAME = 'armando'
    PASSWORD = 'root'
    def __init__(self):
        self.event = threading.Event()
    
    def __check_auth(self, username, password) -> bool:
        return username == self.USERNAME and password == self.PASSWORD

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return 1
        return 2
    
        
if __name__ == '__main__':
    server = '192.168.1.34'
    ssh_port = 2345
    try:
        # socket listener
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    # if except will exit and terminate the connection
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    # if didn't except will continue after accepted the connection
    else:
        print('[+] Got a connection!', client, addr)
        # makes the server to be encrypted ssh transport layer.
        bhSession = paramiko.Transport(client)
        print(f"[debug] created Transport. ")   
        bhSession.add_server_key(HOSTKEY)
        server = Server()
        # starts the trasport session which handles incoming authentication requests.
        bhSession.start_server(server=server)
        chan = bhSession.accept(20)
        if chan is None:
            print('*** No channel.')
            sys.exit(1)
        print('[+] Authenticated!')
        print(chan.recv(1024))
        chan.send('Welcome to bh_ssh')
        try:
            while True:
                command = input("Enter command: ")
                if command != 'exit':
                    chan.send(command)
                    r = chan.recv(8192)
                    print(r.decode())
                else:
                    chan.send('exit')
                    print('exiting')
                    bhSession.close()
                    break
        except KeyboardInterrupt:
            bhSession.close()
