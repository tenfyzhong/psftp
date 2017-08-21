#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pexpect import spawn


__all__ = ['psftp']


class psftp(spawn):

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
        super(self, psftp).__init__(
            self,
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
        self.options = options
