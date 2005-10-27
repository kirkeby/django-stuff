import os, sys, errno

def daemonize():
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    if os.fork():
        os._exit(0)

    # decouple from parent environment
    os.setsid() 
    os.umask(0) 

    # do second fork
    if os.fork():
        # exit second parent
        os._exit(0) 

    # close all open file-descriptors and make sure 0, 1 and 2 are
    # redirected properly
    fdmax = os.sysconf('SC_OPEN_MAX')
    for fd in range(fdmax):
        try:
            os.close(fd)
        except OSError, (eno, _):
            if not eno == errno.EBADF:
                raise

    sys.stdin = open('/dev/zero', 'r', 0)
    sys.stdout = open('/dev/null', 'w', 0)
    sys.stderr = open('/dev/null', 'w', 0)
