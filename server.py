# https://www.random.org/sequences/?min=10&max=20&col=10&format=plain&rnd=new
from network import getPorts

port_list = getPorts()

import socket 
import traceback
from crypto import getKeyPairRSA,loadKeyPairRSA
import time

host = '127.0.0.1'

message = {
    '1' : 'PUBLIC KEY REQUEST'
}

import random
def deployServer(HOST,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        master_key = 'testing'
        private_key_serialized, public_key_serialized = getKeyPairRSA(serialize=True,master_key=master_key)
        try :
            print ('Establishing server at addr :',HOST,':',PORT)
            s.bind((HOST, PORT))
            if PORT==1111:
                while True:
                    message , address = s.recvfrom(1024)
                    print ('recevied :',message,address)
                    ########### ANSWER DIFFERNET MESSAGES HERE
                    if message.decode() == '1':
                        s.sendto(public_key_serialized,address)
            else:
                while True:
                    s.sendto('1'.encode(),('127.0.0.1',1111))
                    message , addr = s.recvfrom(1024)
                    discard, master_public_key = loadKeyPairRSA(message,master_key)
                    print ('public key:',master_public_key)
                    time.sleep(10)
                        
        except OSError:
            print ('Port :',PORT,'taken')
        except :
            traceback.print_exc()
        finally:
            s.close()

server = None

if '1111' not in port_list:
    port = 1111
    
else :
    port = None
    for i in range (6*10**4,6*10**4+2**12,2):
        if str(i) not in port_list:
            port = i
            break

deployServer(host,port)