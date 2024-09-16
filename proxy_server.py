import socket
import sys
import threading
import argparse
import textwrap
from proxy_handler import proxy_handler_eden

NUM_OF_CLIENTS = 1

def server_loop(localhost_ip, localhost_port,
                remote_ip, remote_port, receive_first):
    print(f"[debug] localhost_ip={localhost_ip}, localhost_port={localhost_port}, remote_ip={remote_ip}, remote_port={remote_port}, receive_first={receive_first}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((localhost_ip, localhost_port))
    except Exception as e:
        print(f"[error] cannot bind connection to ip={localhost_ip}, port={localhost_port}")
        sys.exit(0)
    server.listen(NUM_OF_CLIENTS)
    print(f"[debug] binded to the ip={localhost_ip}, port={localhost_port} and listening to a connection")
    print(f"[debug] waiting for clients connection...")
    while True:
        client_socket, client_address = server.accept()
        print(f"[debug] received incoming connection from: ({client_address[0]}, {client_address[1]})")
        conn_thread = threading.Thread(
            target=proxy_handler_eden, args=(
                client_socket, remote_ip, remote_port, receive_first))
        conn_thread.start()

if '__main__' == __name__:
    print(f"[debug] started")
    execution_name: str = sys.argv[1]
    parameters: list = sys.argv[1:]
    num_of_parameters = len(parameters)
    if not(4 <= num_of_parameters <= 5):
        print(f"[info] The quantity of the parameters {num_of_parameters} is not valid")
        sys.exit(0)

    parser = argparse.ArgumentParser(description='Proxy Server Communication Tool', formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=textwrap.dedent('''Example: 
                                    proxy_server.py --localhost 192.168.1.34 --localport 5555 --remoteip ftp.sun.ac.za --remoteport 21 --receivefirst
                                    '''))
    parser.add_argument('--localhost')
    parser.add_argument('--localhostport', type=int)
    parser.add_argument('--remoteip')
    parser.add_argument('--remoteport', type=int)
    parser.add_argument('--receivefirst', action='store_true', help='receive from remote first')

    args = parser.parse_args()
    server_loop(localhost_ip=args.localhost, 
                localhost_port=args.localhostport,
                remote_ip=args.remoteip,
                remote_port=args.remoteport,
                receive_first=args.receivefirst)