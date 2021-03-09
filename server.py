# https://www.random.org/sequences/?min=10&max=20&col=10&format=plain&rnd=new
import subprocess

########## FUNCTION TO GET LISTENING TCP AND UPD PORT NUMBERS
def getPorts():
    output = subprocess.run(["netstat", "-ltu"], capture_output=True)
    connection_list = output.stdout.decode().split('\n')
    if '' in connection_list:
        connection_list.remove('')
    connection_list = connection_list[2:]
    port_list = [connection.split()[3].split(':')[-1] for connection in connection_list]
    return port_list


port_list = getPorts()


import socket 
import threading
# import time
import traceback

host = '127.0.0.1'

message = {
    '1' : 'PUBLIC KEY REQUEST'
}
import random
def deployServer(HOST,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        pk = random.random()
        pk = str(pk).encode()
        try :
            print ('establishing server at addr :',HOST,':',PORT)
            s.bind((HOST, PORT))
            while True:
                message , address = s.recvfrom(1024)
                print ('recevied :',message,address)
                if message.decode() == '1':
                    s.sendto(pk,address)
                    # del message, address
            # s.listen()
            # conn, addr = s.accept()
            # print('Connected by', addr)
            # with conn:
            #     while True:
            #         data = conn.recv(1024)
            #         if data.decode() == '1' :
            #             conn.sendall(str(pk).encode())
            #         conn, addr = s.accept()
            #         print('Connected by', addr)
                        
        except OSError:
            print ('Port :',PORT,'taken')
        except :
            traceback.print_exc()
        finally:
            s.close()


def echoClient(HOST,R_PORT):
    try :
        if R_PORT in getPorts():
            print ('sending .... ')
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # print ('initialising client at',HOST,':',S_PORT)
                # s.bind((HOST,S_PORT))
                # s.listen()
                # s.connect((HOST, R_PORT))
                # s.sendall(b'1')
                # data = s.recv(1024)
                # print (data.decode())
                s.sendto('1'.encode(),('127.0.0.1',1111))
                print ('here')
                message , addr = s.recvfrom(1024)
                print (message)
        else :
            print ('did not find',R_PORT)

    except OSError:
        print ('Port : taken')
        # echoClient(HOST,S_PORT+2,R_PORT)
    except :
        traceback.print_exc()
    finally:
        # s.close()
        pass

server = None

if '1111' not in port_list:
    master_port = 1111
    server = threading.Thread(target=deployServer,args=(host,master_port),daemon=True)
    
else :
    port = None
    for i in range (6*10**4,6*10**4+2**12,2):
        if str(i) not in port_list:
            port = i
            break
    server = threading.Thread(target=echoClient,args=(host,'1111'),daemon=True)

server.start()
server.join()