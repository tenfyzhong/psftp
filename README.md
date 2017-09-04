# Psftp
Psftp is a Python module for spawning sftp application and controlling
automatically.

# Example
```python
import psftp
import getpass
try:
    s = psftp.psftp()
    hostname = raw_input('hostname: ')
    username = raw_input('username: ')
    password = getpass.getpass('password: ')
    s.login(hostname, username, password)
    print s.pwd()
    print s.lpwd()
    print s.lls()
    print s.ls()
    s.put('./hello.txt')
    print s.ls()
except:
    pass
```
