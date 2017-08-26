#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pexpect import spawn, TIMEOUT, EOF, ExceptionPexpect
import os


__all__ = ['psftp', 'ExceptionPsftpLocal', 'ExceptionPsftpInteraction']


# Exception classes used by this module.
class ExceptionPsftpLocal(ExceptionPexpect):
    '''Raised for local exceptions.
    '''


class ExceptionPsftpInteraction(ExceptionPexpect):
    '''Raised for interactive exceptions.
    '''
    def __init__(self, error, expect):
        super(ExceptionPsftpInteraction, self).__init__(error)
        self._expect = expect

    def expect(self):
        return self._expect


class psftp(spawn):
    _exception_permission_deined = ExceptionPsftpInteraction(
        'Permission deined',
        '(?i)permission denied')
    _exception_no_such_file = ExceptionPsftpInteraction(
        'No such file or directory',
        "Couldn't stat remote file: No such file or directory"
    )
    _exception_file_no_found = ExceptionPsftpInteraction(
        'File no found',
        'File .* not found\.'
    )
    _exception_non_regular_file = ExceptionPsftpInteraction(
        'Cannot download non-regular file',
        'Cannot download non-regular file'
    )
    _exception_not_directory = ExceptionPsftpInteraction(
        'Not a directory',
        'Not a directory'
    )
    _exception_file_exists = ExceptionPsftpInteraction(
        'File exists',
        'File exists'
    )
    _exception_could_not_link = ExceptionPsftpInteraction(
        "Couldn't link file",
        "Couldn't link file"
    )
    _exception_create_directory_failure = ExceptionPsftpInteraction(
        "Couldn't create directory: Failure",
        "Couldn't create directory: Failure"
    )
    _exception_delete_failure = ExceptionPsftpInteraction(
        "Couldn't delete file: Failure",
        "Couldn't delete file: Failure"
    )
    _exception_remove_directory_failed = ExceptionPsftpInteraction(
        "Couldn't remove directory: Failure",
        "Couldn't remove directory: Failure"
    )
    _exception_ls_not_found = ExceptionPsftpInteraction(
        "Can't ls. Not found",
        "Can't ls:.* not found"
    )
    _exception_invalid_option = ExceptionPsftpInteraction(
        'ls: invalid option',
        'ls: invalid option'
    )
    _exception_lumask_failed = ExceptionPsftpInteraction(
        'You must supply a numeric argument to the lumask command.',
        'You must supply a numeric argument to the lumask command.'
    )

    """ This class extends pexpect.spawn to specialize setting up sftp
    connections. This add methods for login, logout, interactive commands and
    expecting the shell prompt. It does various tricky things to handle many
    situations in the sftp login process and interactive commands process.
    For example, if the session is you first login, the psftp automatically
    accepts the remote certificate, or if you have public key authenticate
    setup then pxssh won't wait for the password prompt.

    Example that runs a few commands on a remote server and prints the result::

        import psftp
        import getpass
        try:
            s = psftp.sftp()
            hostname = raw_input('hostname: ')
            username = raw_input('username: ')
            password = getpass.getpass('password: ')
            s.login(hostname, username, password)
            s.pwd()
            s.lpwd()
            s.lls()
            s.ls()
            s.put('./hello.txt')
            s.ls()
        except:
            pass

    Example showing how to specify ssh options::

        import psftp
        s = psftp.psftp(options={
            "StrictHostKeyChecking": "no",
            "UserKnownHostsFile": "/dev/null"}
        )
        # ...

    Note that if you have ssh-agent running while doing development with psftp
    then this can lead to a lot of confusion. Many X display managers (xdm,
    gdm, kdm, etc.) will automatically start a GUI agent. You may see a GUI
    dialog box popup asking for a password during development. You should turn
    off any key agents during testing. The 'force_password' attribute will turn
    off public key authentication. This will only work if the remote SSH server
    is configured to allow password logins. Example of useing 'force_password'
    attribute::

        s = psftp.psftp()
        s.force_password = True
        hostname = raw_input('hostname: ')
        username = raw_input('username: ')
        password = getpass.getpass('password: ')
        s.login (hostname, username, password)
    """

    def __init__(
            self,
            timeout=60,
            maxread=100,
            searchwindowsize=None,
            logfile=None,
            cwd=None,
            env=None,
            ignore_sighup=True,
            echo=True,
            options={},
            encoding=None,
            codec_errors='strict'):
        super(psftp, self).__init__(
            None,
            timeout=timeout,
            maxread=maxread,
            searchwindowsize=searchwindowsize,
            logfile=logfile,
            cwd=cwd,
            env=env,
            ignore_sighup=ignore_sighup,
            echo=echo,
            encoding=encoding,
            codec_errors=codec_errors)
        self.name = '<psftp>'
        self.force_password = False
        self.PROMPT = r"sftp> "

        self.SSH_OPTS = ("-o'RSAAuthentication=no'"
                         + " -o 'PubkeyAuthentication=no'")
        self.force_password = False

        # User defined SSH options, eg,
        # ssh.otions = dict(StrictHostKeyChecking="no",
        # UserKnownHostsFile="/dev/null")
        self.options = options

    def login(
            self,
            server,
            username,
            password='',
            terminal_type='ansi',
            login_timeout=10,
            port=None,
            ssh_key=None,
            quiet=True,
            sync_multiplier=1,
            check_local_ip=True):
        '''This logs the user into the given server.
        '''
        ssh_options = ''.join([" -o '%s=%s'" % (o, v) for
                               (o, v) in self.options.items()])
        if quiet:
            ssh_options += ' -q'
        if not check_local_ip:
            ssh_options += " -o'NoHostAuthenticationForLocalhost=yes'"
        if self.force_password:
            ssh_options += ' ' + self.SSH_OPTS
        if port is not None:
            ssh_options += ' -P %s' % (str(port))
        if ssh_key is not None and os.path.isfile(ssh_key):
            ssh_options = ssh_options + ' -i %s' % (ssh_key)

        cmd = "sftp %s %s@%s" % (ssh_options, username, server)
        super(psftp, self)._spawn(cmd)

        first_phase_expect = [
            "(?i)are you sure you want to continue connecting",
            self.PROMPT,
            "(?i)(?:password)|(?:passphrase for key)",
            "(?i)permission denied",
            "(?i)terminal type",
            TIMEOUT,
            "(?i)connection closed by remote host",
            EOF]
        i = self.expect(first_phase_expect)

        second_phase_expect = [
            "(?i)are you sure you want to continue connecting",
            self.PROMPT,
            "(?i)(?:password)|(?:passphrase for key)",
            "(?i)permission denied",
            "(?i)terminal type",
            TIMEOUT]

        # First phase
        if i == 0:
            # New certificate -- always accept it.
            # This is what you get if SSH does not have the remote host's
            # public key stored in the 'known_hosts' cache.
            self.sendline("yes")
        if i == 2:  # password or passphrase
            self.sendline(password)
            i = self.expect(second_phase_expect)
        if i == 4:
            self.sendline(terminal_type)
            i = self.expect(second_phase_expect)
        if i == 7:
            self.close()
            raise ExceptionPsftpLocal('Could not establish connection to host')

        # Second phase
        if i == 0:
            # This is weird. This should not happen twice in a row.
            self.close()
            raise ExceptionPsftpLocal(
                'Weird error. Got "are you sure" prompt twice.')
        elif i == 1:
            # can occur if you have a public key pair set to authenticate.
            pass
        elif i == 2:
            # password prompt again
            # For incorrect passwords, some ssh servers will
            # ask for the password again, others return 'denied' right away.
            # If we get the password prompt again then this means
            # we didn't get the password right the first time.
            self.close()
            raise ExceptionPsftpLocal('password refused')
        elif i == 3:
            # permission denied -- password was bad.
            self.close()
            raise ExceptionPsftpLocal('permission denied')
        elif i == 4:
            # terminal type again?
            self.close()
            raise ExceptionPsftpLocal(
                'Weird error. Got "terminal type" prompt twice.')
        elif i == 5:
            # Timeout
            # This is tricky. I presume that we are at the command-line prompt.
            # It may be that the shell prompt was so weird that we couldn't
            # match it. Or it may be that we couldn't log in for some other
            # reason. I can't be sure, but it's safe to guess that we did
            # login because if # I presume wrong and we are not logged in then
            # this should be caught later when I try to set the shell prompt.
            pass
        elif i == 6:
            # Connection closed by remote host
            self.close()
            raise ExceptionPsftpLocal('connection closed')
        else:
            # Unexpected
            self.close()
            raise ExceptionPsftpLocal('unexpected login response')
        return True

    def logout(self):
        '''Sends exit to the remote shell.

        If there are stopped jobs then this automatically sends exit twice.
        '''
        self.sendline("exit")
        self.expect(EOF)
        self.close()

    def prompt(self, timeout=-1):
        '''Match the next shell prompt.
        This is little more than a short-cut to the
        :meth:`~pexpect.spawn.expect` method.
        Note that if you called :meth:`login` with

        Calling :meth:`prompt` will erase the contents of the :attr:`before`
        attribute even if no prompt is ever matched. If timeout is not given or
        it is set to -1 then self.timeout is used.

        :return: True if the shell prompt was matched, False if the timeout was
                 reached.
        '''

        if timeout == -1:
            timeout = self.timeout
        i = self.expect([self.PROMPT, TIMEOUT], timeout=timeout)
        if i == 1:
            return False
        return True

    def cd(self, path):
        """Change remote directory to path.
        """
        cmd = 'cd %s' % path
        self._exec(cmd, [psftp._exception_no_such_file])

    def chgrp(self, grp, path):
        """Change group of file path to grp. path may contain glob(3)
        characters and may match multiple files. grp must be a numeric GID.
        """
        cmd = 'chgrp %d %s' % (grp, path)
        self._exec(cmd, [psftp._exception_permission_deined,
                         psftp._exception_no_such_file])

    def chmod(self, mode, path):
        """Change permissions of file path to mode. path may contain glob(3)
        characters and may match multiple files.
        """
        cmd = 'chmod %s %s' % (str(mode), path)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_no_such_file])

    def df(self, path='', options=''):
        """Display usage information for the filesystem holding the current
        directory (of path if specified).

        *attention* This function is only supported on servers that implement
        the "statvfs@openssh.com" extension.

        :options: every char is one of 'hi'.
        -h the capacity information will be displayed using human-readable
        suffixes.
        -i display of inode information in addition to capacity information.

        :return: tuple, the first value is the item list
        the second is the value list
        """
        base_options = 'hi'
        valid_options = self._options(base_options, options)
        cmd = 'df %s' % valid_options
        self._exec(cmd)
        output = self._output(self.before, '\r\n')
        lines = output.split('\r\n')
        if len(lines) < 2:
            return (None, None)
        title = lines[0].split()
        value = lines[1].split()
        return (title, value)

    def get(
            self,
            remote_path,
            local_path='',
            options=''):
        """Retrieve the remote-path and store it on the local machine. If the
        local path name is not specified, it is given the same name it has on
        the remote machine. rempte-path may contain glob(3) characters and may
        match multiple files. If it does and local-path is specified, then
        local-path must specify a directory.

        :options: every char is one of 'afPpr'.
        -a attempt to resume partial transfers of existing files.
        Note that resumption assumes that any partial copy of the local file
        matches the remote copy. If the remote file contents differ from the
        partial local copy then the resultant file is likely to corrupt.
        -f fsync(2) will be called after the file transfer has completed
        to flush the file to disk.
        -P,-p full file permissions and access times are copied too.
        -r directories will be copied recursively. Note that sftp
        does not follow symbolic links when performing recursive transfers.
        """
        base_options = 'afPpr'
        valid_options = self._options(base_options, options)
        cmd = 'get %s %s %s' % (valid_options, remote_path, local_path)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_file_no_found,
            psftp._exception_non_regular_file])

    def help(self):
        """Display help text.
        """
        self._exec('help')
        return self._output(self.before, 'help\r\n')

    def lcd(self, path):
        """Change local directory to path
        """
        cmd = 'lcd %s' % path
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_not_directory,
            psftp._exception_no_such_file])

    def ls(self, path='', options=''):
        """Display a remote directory listing of either path or the current
        directory if path is not specified. path may contain glob(3) characters
        and may match multiple files.

        :options: every char is one of '1afhlnrSt'.
        -1 Produce single columnar output.
        -a List files begining with a dot ('.').
        -f Do not sort the listing. The default sort order is lexicographical.
        -h When used with a long format option, use unit suffixes: Byte,
           Kilobyte, Megabyte, Gigabyte, Terabyte, Petabyte, and Exabyte in
           order to reduce the number of digits to four or fewer using powers
           of 2 for sizes (K=1024, M=1048576, etc.).
        -l Display additional details includeing permissions and ownership
           information.
        -n Produce a long listing with user and group information presented
           numerically.
        -r Reverse the sort order of the listing.
        -S Sort the listing by file size.
        -t Sort the listing by last modification time.

        :return: lines of output
        """
        base_options = '1afhlnrSt'
        valid_options = self._options(base_options, options)
        cmd = 'ls %s %s' % (valid_options, path)
        self._exec(cmd, [psftp._exception_ls_not_found])
        output = self._output(self.before, cmd+'\r\n')
        lines = output.split()
        lines = [line.strip() for line in lines]
        return lines

    def lmkdir(self, path):
        """Create local directory specified by path.
        """
        cmd = 'lmkdir %s' % path
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_file_exists])

    def ln(self, oldpath, newpath, options=''):
        """Create a link from oldpath to newpath in remote server.

        :options: every char is one of 's'.
        -s created link is a symbolic link, otehrwise it's a hard link.
        """
        base_options = 's'
        valid_options = self._options(base_options, options)
        cmd = 'ln %s %s %s' % (valid_options, oldpath, newpath)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_could_not_link,
            psftp._exception_no_such_file])

    def lpwd(self):
        """Get local working directory.
        """
        self._exec('lpwd')
        pwd = self.before.strip()
        prefix = 'Local working directory: '
        return self._output(pwd, prefix)

    def lls(self, path='', options=''):
        """Display local directory listing of either path or current directory
        if path is not specified. options may contain any flags supported by
        the local system's ls(1) command. path may contain glob(3) characters
        and may match multiple files.

        :returns: lines of output
        """
        cmd = 'lls %s %s' % (options, path)
        self._exec(cmd, [
            psftp._exception_invalid_option,
            psftp._exception_no_such_file])
        output = self._output(self.before, cmd+'\r\n')
        lines = output.split()
        lines = [line.strip() for line in lines]
        return lines

    def lumask(self, umask):
        """Set localumask to umask
        """
        cmd = 'lumask %s' % str(umask)
        self._exec(cmd, [psftp._exception_lumask_failed])

    def mkdir(self, path):
        """Create remote directory specified by path.
        """
        cmd = 'mkdir %s' % path
        self._exec(cmd, [
            psftp._exception_create_directory_failure,
            psftp._exception_permission_deined])

    def progress(self):
        """Toggle display of progress meter.
        """
        self._exec('progress')

    def put(
            self,
            local_path,
            remote_path='',
            options=''):
        """Upload local-path and store it on the remote machine. If the remote
        path name is not specified, it is given the same name it has on the
        local machine. local-path may contain glob(3) characters and may match
        multiple files. If it does and remote-path is specified, then
        remote-path speciff a directory.

        :options: every char is one of 'afPpr'.
        -a attempt to resume partial transfers of existing files.
        Note that resumption assumes that any partial copy of the remote file
        matches the local copy. If the local file contents differ from the
        remote local copy then the resultant file is likely to the corrupt.
        -f a request will be send to the server to call fsync(2) after the
        file has been transferred. Note that this is only supported by servers
        that implement the "fsync@openssh.com" extension.
        -P,-p full file permissions and access times are copied too.
        -r directories will be copied recursively. Note that sftp
        does not follow symbolic links when performing recursive transfers.
        """
        base_options = 'hi'
        valid_options = self._options(base_options, options)
        cmd = 'put %s %s %s' % (valid_options, local_path, remote_path)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_non_regular_file])

    def pwd(self):
        """Get remote working directory.
        """
        self._exec('pwd')
        pwd = self.before.strip()
        prefix = 'Remote working directory: '
        return self._output(pwd, prefix)

    def rename(self, oldpath, newpath):
        """Rename remote file from oldpath to newpath
        """
        cmd = 'rename %s %s' % (oldpath, newpath)
        self._exec(cmd, [psftp._exception_no_such_file])

    def reget(
            self,
            remote_path,
            local_path='',
            options=''):
        """Resume download of remote-path.
        Equivalent to get with the -a flag set.

        :options: every char is one of 'Ppr'.
        -P,-p full file permissions and access times are copied too.
        -r directories will be copied recursively. Note that sftp
        does not follow symbolic links when performing recursive transfers.
        """
        base_options = 'hi'
        valid_options = self._options(base_options, options)
        cmd = 'reget %s %s %s' % (valid_options, remote_path, local_path)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_file_no_found,
            psftp._exception_non_regular_file])

    def reput(
            self,
            remote_path,
            local_path='',
            options=''):
        """Resume upload of local_path.
        Equivalent to put with the -a flag set.

        :options: every char is one of '1afhlnrSt'.
        -P,-p full file permissions and access times are copied too.
        -r directories will be copied recursively. Note that sftp
        does not follow symbolic links when performing recursive transfers.
        """
        base_options = 'hi'
        valid_options = self._options(base_options, options)
        cmd = 'put %s %s %s' % (valid_options, local_path, remote_path)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_non_regular_file])

    def rm(self, path):
        """Delete remote file specified by path
        """
        cmd = 'rm %s' % path
        self._exec(cmd, [
            psftp._exception_no_such_file,
            psftp._exception_delete_failure])

    def rmdir(self, path):
        """Remote remote directory specified by path.
        """
        cmd = 'rmdir %s' % path
        self._exec(cmd, [
            psftp._exception_no_such_file,
            psftp._exception_remove_directory_failed])

    def symlink(self, oldpath, newpath):
        """Create a symbolic link from oldpath to newpath.
        """
        cmd = 'symlink %s %s' % (oldpath, newpath)
        self._exec(cmd, [
            psftp._exception_permission_deined,
            psftp._exception_could_not_link,
            psftp._exception_no_such_file])

    def version(self):
        """Display the sftp protocol version.
        """
        self._exec('version')
        return self._output(self.before, 'version\r\n')

    def local_command(self, command):
        """Execute command in local shell
        """
        cmd = '!'+command
        self._exec(cmd)
        return self._output(self.before, cmd+'\r\n')

    def _exec(self, cmd, error_and_exceptions=[]):
        self.sendline(cmd)
        expect = [ee.expect() for ee in error_and_exceptions] + [self.PROMPT]
        i = self.expect(expect)
        if i != len(expect)-1:
            raise error_and_exceptions[i]

    def _output(self, raw, prefix):
        raw.strip()
        index = raw.find(prefix)
        if index == -1:
            raise ExceptionPsftpLocal('result invalid')
        return raw[index+len(prefix):]

    def _options(self, base_options, options):
        valid_options = ''.join(c for c in options if c in base_options)
        return '-' + valid_options if valid_options else ''

    @classmethod
    def _interaction_exception(cls, error):
        return ExceptionPsftpInteraction(
            error,
            cls.__interactive_error_expect[error])
