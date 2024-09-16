import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),
    stderr=subprocess.STDOUT)
    return output.decode()  


class NetCat:
    LISTEN_CLIENTS = 5
    def __init__(self, args, buffer=None):
        """
        :param args:
            self.args.execute
            self.args.command
            self.args.listen
            self.args.port
            self.args.target
            self.args.upload
        Example: 
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        """
        self.args = args
        self.buffer: bytes = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def run(self):
        if self.args.listen:
            print(f"[debug] server-listen mode")
            self.listen()
        else:
            print(f"[debug] client-sender mode")
            self.send()
    
    def send(self):
        """
        Sends data and waits for response untill EOD or KeyboardInterrupt raised.
        Will print the response after the data has sent.
        """
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            print(f"[debug] Will send buffer as echo to the client, The buffer: {self.buffer.decode()}")
            # sends encoded
            self.socket.send(self.buffer)
        try:
            while True:
                # min startpoint recv len and empty response 
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(f"[debug] response is: {response}")
                    # set the input from the stdin and add `\n` for return statment inorder to run it inside the listener and sends the buffer.
                    buffer = input(">")
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("[debug] User Terminated.")
            self.socket.close()
            sys.exit()


    def listen(self):
        """
        When the user pick -l argument option we'll create a listener, And will send the the client_socket connection to the handler
        to handle the client.
        """
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(self.LISTEN_CLIENTS)
        print(f"[debug] bind to - IP: {self.args.target}, PORT: {self.args.port}")
        print(f"[debug] Listening to {self.LISTEN_CLIENTS} clients at most")
        while True:
            print(f"[debug] Waiting for client connection")
            client_socket, client_address = self.socket.accept()
            print(f"[debug] client connected, IP&PORT: {client_address}")
            client_thread = threading.Thread(target=self.handler, args=(client_socket,))
            client_thread.start()
    
    def handler(self, client_socket):
        """
        there are 3 situations to handle, Which are:
            1. execute
            2. command
            3. upload
        """
        print(f"[debug] Inside the handler will chose to:\n1.execute, 2.command, 3.upload")
        if self.args.execute:
            """
            Will execute specified command through the shell
            """
            print(f"[debug] execute chose - One command execution")
            execution_output = execute(cmd=self.args.execute)
            # sends to the client encoded (in bytes as b'...').
            client_socket.send(execution_output.encode())
        elif self.args.command:
            print(f"[debug] command chose - Interactive command")
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd=cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e :
                    print(f'server killed {e}')
                    client_socket.close()
                    self.socket.close()
                    sys.exit()
        elif self.args.upload:
            print(f"[debug]upload chose - upload file with file content")
            file_buffer = b''
            file_name = self.args.upload
            while True:
                data = client_socket.rescv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(file_name, 'wb') as f:
                f.write(file_buffer)
            message_to_client: bytes = f'Saved file name: {file_name}'.encode()
            self.client_socket.send(message_to_client)


        

        
        
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BHP Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''Example: 
                                        netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
                                        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
                                        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
                                        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
                                        netcat.py -t 192.168.1.108 -p 5555 # connect to server
                                        '''))
    # optional arguments with the suffix of `--`:
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    
    # creating the args as variables 
    args = parser.parse_args()
    # -l or --listen
    if args.listen: 
        buffer = ''
    # anything else will read from the buffer 
    else:
        print(f"[debug] client read from stdin; press ctrl+D to finish recording the buffer")
        buffer = sys.stdin.read()
    print(f"buffer value is: {buffer}")
    
    # TODO: what is here?
    nc = NetCat(args, buffer.encode())
    nc.run()
