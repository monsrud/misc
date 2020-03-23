#!/usr/bin/python3

#
# Runs via cron on backups.test.lab to back up remote mysql databases to minio
# 
# root must have a .my.cnf in their home directory on the database servers
# root must have exchanged ssh keys with the remote database servers
#

import paramiko
import logging
import warnings
import pprint
from minio import Minio
from minio.error import ResponseError
import os
import datetime
import gzip
import shutil
import re
from common import cleanup, cli_exec 

now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
logging.getLogger("paramiko").setLevel(logging.WARNING)

username = "root"
bucketname = "devops"
ssh_private_key_file = "/root/.ssh/id_ecdsa"

backuplist = [
    ['snipe-it.test.lab', 'snipeit', 'snipe-it'],
    ['orangehrm.test.lab', 'orangehrm_mysql', 'orangehrm'],
    ['passbolt.test.lab', 'passbolt', 'passbolt']

]

minioClient = Minio('minio.test.lab',
                    access_key='devops',
                    secret_key='secretkey',
                    secure=True)

def cli_exec(ssh, command):
        """ Execute a command and return the results """
        stdin, stdout, stderr =  ssh.exec_command(command)
        status = stdout.channel.recv_exit_status()
        return {'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'status': status}

def putfile(client, local_filename, bucketname, prefixname, remote_filename):
    try:
        with open(local_filename, 'rb') as file_data:
            file_stat = os.stat(local_filename)
            client.put_object(bucketname, prefixname + '/' + remote_filename,file_data, file_stat.st_size)
    except ResponseError as err:
        print(err)

for backup in backuplist:
    hostname = backup[0]
    tablename = backup[1]
    prefix = backup[2]

    filename = now + "_" + tablename
    filename_gz = filename + ".gz"
    filename_sql = filename + ".sql"
   
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.ECDSAKey.from_private_key_file(ssh_private_key_file)
    ssh.connect(hostname, 22, username, pkey=pkey )

    command = "mysqldump " + tablename + " > " + filename_sql
    cli_exec(ssh, command)
    sftp = ssh.open_sftp()
    sftp.get(filename_sql,filename_sql)
    sftp.close()
    command = "rm " +  filename_sql
    cli_exec(ssh, command)

    with open(filename_sql, 'rb') as f_in:
        with gzip.open(filename_gz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out) 
    os.remove(filename_sql)               

    putfile(minioClient, filename_gz, bucketname, prefix, filename_gz)
    os.remove(filename_gz)

    cleanup(minioClient, bucketname, prefix)
    

