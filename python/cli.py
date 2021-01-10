import paramiko
import time

"""
This is a paramiko ssh library for the CLI commands for a product I was testing. 
A handle to the cli is opened via Paramikio and SSH. Commands are sent to the 
CLI and the stdout, stderr and exit status is returned.

"""

class Cli:
    """ This is the cli"""
    ip = None
    username = None
    password = None
    ssh = None
    stdin = None # this is not used...

    def __init__(self, ip=ip, username=username, password=password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.ssh.connect(ip, 22, username=username,
                           password=password, look_for_keys=False, pkey=None, key_filename=None )

    def _send_control_command(self, command):
        """ send a control command """
        channel = self.ssh.invoke_shell()
        channel.send('control\n')
        stdin = channel.makefile('wb')
        stdout = channel.makefile('r')
        channel.send(command + '\n')
        channel.send('\n')

        start = False
        output = ''
        for line in stdout:
            if line == None:
                print("line = none")
            
            if start:
                if line.find('>') >= 0:
                    break # done
                output += line

            if not start:
                if line.find('> ' + command) >= 0:
                    start = True   

        channel.send('exit\n')  
        stdout.close()
        stdin.close()   
        return {'status':0, 'stdout':output, 'stderr':''}  

    # TODO: control functions for clock, control_ethernet, control_ethernet_poe,
    # control_mgmt_if, control_process, control_wireless,  kb_restore_defaults,
    # kb_set, passwd, software     

    def control_id(self):
        return self._send_control_command('id')

    def control_scan(self):
        return self._send_control_command('scan')   

    def control_reboot(self):
        return self._send_control_command('reboot')  

    def control_locate_device(self):
        return self._send_control_command('locate_device') 

    def control_link_unlock(self):
        return self._send_control_command('link_unlock')   

    def control_link_lock(self):
        return self._send_control_command('link_lock')        

    def control_link_lock_status(self):
        return self._send_control_command('link_lock_status') 

    def control_link_bump(self):
        return self._send_control_command('link_bump')  

    def control_kb_show(self):
        return self._send_control_command('kb_show') 

    def control_kb_changes(self):
        return self._send_control_command('kb_changes')  

    def control_kb_commit(self):
        return self._send_control_command('kb_commit')  

    def control_locate_device(self):
        return self._send_control_command('locate_device')                       

    def dmesg_show(self):
        stdin, stdout, stderr = self.ssh.exec_command("dmesg_show")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def dmesg_clear(self):
        stdin, stdout, stderr = self.ssh.exec_command("dmesg_clear")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def help(self):
        stdin, stdout, stderr = self.ssh.exec_command("help")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def id(self):
        stdin, stdout, stderr = self.ssh.exec_command("id")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def ip_addr(self):
        stdin, stdout, stderr = self.ssh.exec_command("ip_addr")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def ip_rout(self):
        stdin, stdout, stderr = self.ssh.exec_command("ip_route")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def iperf_client(self):
        # TODO: needs work
        pass

    def iperf_server(self):
        # TODO: needs work
        pass

    def kb_bridge_fdb(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_bridge_fdb")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_browse(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_browse")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_devices(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_devices")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_eth_status(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_eth_status")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_find_root(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_find_root")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_lan_peers(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_lan_peers")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_node_id(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_node_id")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_radio_peers(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_radio_peers")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kb_stp_info(self):
        stdin, stdout, stderr = self.ssh.exec_command("kb_stp_info")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def kbssh(self):
        # TODO: needs work
        pass

    def kbssh_lan(self):
        # TODO: needs work
        pass

    def kbssh_radio(self):
        # TODO: needs work
        pass

    def exit(self):
        stdin, stdout, stderr = self.ssh.exec_command("exit")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def logout(self):
        stdin, stdout, stderr = self.ssh.exec_command("logout")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def ping(self, ip):
        stdin, stdout, stderr = self.ssh.exec_command("ping " + ip)
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def ps(self):
        stdin, stdout, stderr = self.ssh.exec_command("ps")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def show_statistics(self):
        stdin, stdout, stderr = self.ssh.exec_command("show_statistics")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def syslog_clear(self):
        stdin, stdout, stderr = self.ssh.exec_command("syslog_clear")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}

    def syslog_event_tail(self):
        pass

    def syslog_tail(self):
        pass

    def syslog_show(self):
        stdin, stdout, stderr = self.ssh.exec_command("syslog_show")
        exit_status = stdout.channel.recv_exit_status()
        return {'status':exit_status, 'stdout':stdout.read().decode('utf-8'), 'stderr':stderr.read().decode('utf-8')}
