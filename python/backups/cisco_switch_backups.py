#!/usr/bin/python3

#
# Runs via cron on backups.test.lab to back up cisco switch configs into minio
# 
# backups user must have exchanged ssh keys with the remote switches servers
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
import io
from common import cleanup, cli_exec, putfile

now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")

ssh_username = "backups"
bucketname = "devops"
ssh_private_key_file = "/root/.ssh/id_ecdsa"
prefix = 'cisco_switches'

switches = [
    'agg-a.test.lab',
    'agg-b.test.lab',
    'core-a.test.lab',
    'core-b.test.lab',
    'rack7-10g-sw1.test.lab',
    'rack7-10g-sw2.test.lab',
    'rack2-10g-sw1.test.lab'
]

minioClient = Minio('minio.test.lab',
                    access_key='devops',
                    secret_key='secretkey',
                    secure=True)

for switch in switches:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.ECDSAKey.from_private_key_file(ssh_private_key_file)
    ssh.connect(switch, 22, ssh_username, pkey=pkey )
    result = cli_exec(ssh, "show running-config")
    filename = now + '_' + switch + ".gz"
    with gzip.open(filename, 'wt') as f:
        f.write(result['stdout'])
    
    putfile(minioClient, filename, bucketname, prefix, filename)
    os.remove(filename)               

cleanup(minioClient, bucketname, prefix)

