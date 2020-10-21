package test.utils;
import com.jcabi.ssh.Shell;
import com.jcabi.ssh.SshByPassword;
import java.io.*;
import java.net.UnknownHostException;

/*
This is an ssh client that can be used to connect to an ssh server.
It returns stdout,stderr and exit status from an ssh command.

Usage Example:

        SshClient client = new SshClient("10.10.10.144", "username", "password");
        SshClient.CommandResult commandResult = client.Exec("ls");
        System.out.println(commandResult.getStdout());
        System.out.println(commandResult.getStderror());
        System.out.println(commandResult.getexitStatus());

 */

public class SshClient {

    Shell shell;

    public SshClient (String address, int port, String username, String password) {
        try {
            this.shell = new SshByPassword(address, port, username, password);
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
    }

    public SshClient (String address, String username, String password) {
        try {
            this.shell = new SshByPassword(address, 22, username, password);
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
    }

    public CommandResult Exec (String command) {

        try {
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            ByteArrayOutputStream errorStream = new ByteArrayOutputStream();
            ByteArrayInputStream inputStream = new ByteArrayInputStream(command.getBytes());

            int result = new Shell.Verbose(shell).exec(command, inputStream, outputStream,errorStream);
            return new CommandResult(outputStream.toString(), errorStream.toString(), result);
        } catch (IOException e) {
            e.printStackTrace();
        }
        System.out.println("GOT HERE");
        return null;
    }

    class CommandResult {

        private String outputStream;
        private String errorStream;
        private int exitStatus;

        public CommandResult(String outputStream, String errorStream, int exitStatus) {
            this.outputStream = outputStream;
            this.errorStream = errorStream;
            this.exitStatus = exitStatus;
        }

        public String getStdout() {
            return this.outputStream;
        }

        public String[] getStdoutAsArray() {
            return this.outputStream.split("\n");
        }

        public String getStderror() {
            return this.errorStream;
        }

        public String[] getStderrorAsArray() {
            return this.errorStream.split("\n");
        }

        public int getExitStatus() {
            return this.exitStatus;
        }
    }

}
