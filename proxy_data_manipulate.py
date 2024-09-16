import socket


def receive_from(socket_connection: socket.socket) -> bytes:
    """
    receives data from a client/server, Which means receives both 
     local and remote data.
    :return: the data will return as it was received, bytes.
    """
    buffer = b''
    socket_connection.settimeout(5)
    try:
        while True:
            data = socket_connection.recv(4096)
            print(f"[debug] data after receiving: {data.decode()}")
            if not data:
                break
            buffer += data
        return buffer
    except Exception as e:
        pass
    print(f"[debug] the buffer tosend is (bytes represent): {buffer}")
    return buffer


"""
Data packet modifications, If we want to create and perform any 
modifications before we're transferring the data to the
other side.
"""
def request_handler(buffer):
    """
    perform packet modifications
    """
    return buffer
def response_handler(buffer):
    """
    perform packet modifications
    """
    return buffer