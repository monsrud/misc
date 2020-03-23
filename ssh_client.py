import logging
import warnings
import paramiko

warnings.filterwarnings(action='ignore',module='.*paramiko.*')
logging.getLogger("paramiko").setLevel(logging.WARNING)

"""
A simple ssh client to send commands to a server and get stderr, stdout and exit status.
"""

class ssh_client:
    """ An ssh client """

    def __init__(self, hostname, username, password):
        """ Open an ssh connection """
        self.hostname = hostname
        self.username = username
        self.password = password

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.ssh.connect(self.hostname, 22, self.username, 
                         password=self.password, look_for_keys=False, pkey=None, key_filename=None )


    def cli_exec(self, command):
        """ Execute a command and return the results """
        stdin, stdout, stderr = self.ssh.exec_command(command)
        status = stdout.channel.recv_exit_status()
        return {'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'status': status}
