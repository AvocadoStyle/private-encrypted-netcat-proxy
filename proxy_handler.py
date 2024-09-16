import socket
from proxy_data_manipulate import receive_from, request_handler, response_handler
from hexdump_tool import hexdump


def proxy_handler_eden(
        client_socket, remote_host: str, remote_port: int, receive_first: bool):
    # creates remote_socket for the host
    remote_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connects from the proxy to the desired host    
    remote_host_socket.connect((remote_host, remote_port))
    print(f"[debug] connected to the remotehost! IP: {remote_host} PORT: {remote_port}")

    # if specified - receive from the remote host first
    remote_host_buffer: bytes = b''
    if receive_first:
        print(f"[debug] receiving from remote server first!")
        remote_host_buffer = receive_from(socket_connection=remote_host_socket)
        hexdump(remote_host_buffer)
    # gets modified buffer if there is
    remote_host_buffer = response_handler(buffer=remote_host_buffer)
    # gets the length of the received buffer
    remote_buffer_length = len(remote_host_buffer)
    if remote_buffer_length:
        print(f"[debug] [<==] sending {remote_buffer_length} bytes from host to client")
        client_socket.send(remote_host_buffer)
    
    while True:
        print(f"[debug] regular loop")
        print(f"[debug] going to receive from client")
        client_buffer = receive_from(client_socket)
        if len(client_buffer):
            print(f"[debug] [==>] received {client_buffer} bytes from client")
            hexdump(client_buffer)
            client_buffer = request_handler(client_buffer)
            print(f"[debug] [==>] sending {len(client_buffer)} bytes from client to host")
            remote_host_socket.send(client_buffer)
        print(f"[debug] going to receive from remote server")
        remote_host_buffer = receive_from(socket_connection=remote_host_socket)
        if len(remote_host_buffer):
            print(f"[debug] [<==] received {len(remote_host_buffer)} bytes from host")
            hexdump(remote_host_buffer)
            remote_host_buffer = response_handler(remote_host_buffer)
            print(f"[debug] [<==] send to client")
            client_socket.send(remote_host_buffer)
        if not len(remote_host_buffer) or not len(client_buffer):
            client_socket.close()
            remote_host_socket.close()
            print(f"[debug] no more DATA, closing connection.")
            break
