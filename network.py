import subprocess

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO
from functools import wraps

network_logger = createLogger(name='Network',level=INFO,state='DEVELOPMENT')

########## WRAPPER FOR LOGGER
def logExceptionsWrapper(function):
    @wraps(function)
    def logExceptions(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except:
            print ('################# NETWORK ERROR ###############')
            network_logger.exception('exception in network.py.%s'%(function.__name__))
            print ('exception in network.py.%s'%(function.__name__))
            print ('################# NETWORK ERROR ###############')
    return logExceptions

import platform
os_name = platform.system()

########## FUNCTION TO GET PRIVATE AND PUBLIC IP
@logExceptionsWrapper
def getPublicPirvateIp():
    private_ip, public_ip = None, None

    if os_name == 'Linux':
        output = subprocess.run(['hostname','-I'],capture_output=True)
        private_ip, public_ip, discard = output.stdout.decode().split(' ')
        del discard
    
    elif os_name == 'Windows':
        ########### ADD CODE FOR WINDOWS HERE
        pass

    return private_ip,public_ip

########## FUNCTION TO GET LISTENING TCP AND UPD PORT NUMBERS
@logExceptionsWrapper
def getPorts():
    port_list = []

    if os_name == 'Linux':
        output = subprocess.run(["netstat", "-ltu"], capture_output=True)
        connection_list = output.stdout.decode().split('\n')
        if '' in connection_list:
            connection_list.remove('')
        connection_list = connection_list[2:]
        port_list = [connection.split()[3].split(':')[-1] for connection in connection_list]

    elif os_name == 'Windows':
        ########### ADD CODE FOR WINDOWS HERE
        pass
    
    return port_list
