import paramiko
from minio import Minio
from minio.error import ResponseError
import datetime
import re
import os
import warnings
import logging


warnings.filterwarnings(action='ignore',module='.*paramiko.*')
logging.getLogger("paramiko").setLevel(logging.WARNING)

def cli_exec(ssh, command):
        """ Execute a command and return the results """
        stdin, stdout, stderr =  ssh.exec_command(command)
        status = stdout.channel.recv_exit_status()
        return {'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'status': status}

def cleanup(minioClient, bucket, prefix):
    # Keep backup files for 90 days 
    objects = minioClient.list_objects('devops', prefix, recursive=True)
    last_month = datetime.datetime.now() + datetime.timedelta(-90)
    for o in objects:
        result = re.search('[\d]{4}-[\d]{2}-[\d]{2}', o.object_name)
        if result:
            parts = result.group(0).split('-')
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])

            file_date = datetime.datetime(year, month, day)
            if file_date < last_month:
                print(o.object_name)
                minioClient.remove_object(bucketname, o.object_name)


def putfile(client, local_filename, bucketname, prefixname, remote_filename):
    try:
        with open(local_filename, 'rb') as file_data:
            file_stat = os.stat(local_filename)
            client.put_object(bucketname, prefixname + '/' + remote_filename,file_data, file_stat.st_size)
    except ResponseError as err:
        print(err)
