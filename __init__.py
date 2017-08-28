"""psftp is a Python module for spawning sftp application and controlling
automatically.
"""

from .psftp import psftp, ExceptionPsftpLocal, ExceptionPsftpInteraction

__version__ = '0.0.2'
__revision__ = ''
__all__ = [
    'psftp',
    'ExceptionPsftpLocal',
    'ExceptionPsftpInteraction',
    '__version__',
    '__revision__']
