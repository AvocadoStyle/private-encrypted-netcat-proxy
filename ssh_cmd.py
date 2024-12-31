import paramiko


def ssh_command(ip, port, user, passwd, cmd):
    """
    Makes the connection to SSH server.
    The policy of the ssh connection will be with user name & password, We're doing so with the 
        - client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) policy
    Create the SSH connection to the server with the following parameters:
    :param ip: host IP
    :param port: host PORT
    :param user: host user
    :param passwd: host password
    :param cmd: the command line to be executed in host
    """
    # create client paramiko ssh client.
    client = paramiko.SSHClient()
    
    # password policy 
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # creates the connection client -> server.
    client.connect(ip, port=port, username=user, password=passwd)
    
    # assuming the connection established and execute the command
    _, stdout, stderr = client.exec_command(cmd)
    
    # prints the command stdout & stderr output in a readable pattern
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("[debug] ----Output----")
        # print the output without whitespaces
        for line in output:
            print(line.strip())
        

if __name__ == '__main__':
    import getpass
    # user = getpass.getuser()  
    user = input('Username: ')
    password = getpass.getpass()

    ip = input('Enter IP: ') or '192.'
    port = input('Enter Port: ') or 2222
    cmd = input('Enter Command: ') or 'id' 

    ssh_command(ip, port, user, password, cmd)