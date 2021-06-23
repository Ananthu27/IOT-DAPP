from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
# from urllib.request import urlopen

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO
from functools import wraps

crypto_logger = createLogger(name='Crypto',level=INFO,state='DEVELOPMENT')

########## WRAPPER FOR LOGGER
def logExceptionsWrapper(function):
    @wraps(function)
    def logExceptions(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except:
            print ('################# CRYPTO ERROR ###############')
            crypto_logger.exception('exception in crypto.py.%s'%(function.__name__))
            print ('exception in crypto.py.%s'%(function.__name__))
            print ('################# CRYPTO ERROR ###############')
    return logExceptions

############ FUNCTION RETURNS PUBLIC PRIVATE KEY PAIR FOR RSA
@logExceptionsWrapper
def getKeyPairRSA(serialize=False,master_key=None):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
        )
    public_key = private_key.public_key() 

    if not serialize or master_key is None:
        return private_key, public_key
    else:
        public_key_serialized = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
        )
        private_key_serialized = private_key.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm = serialization.BestAvailableEncryption(master_key.encode())
        )
        return private_key_serialized, public_key_serialized

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

############# FUNCTION TO UNSERIALIZE RSA KEY PAIR GENERATED WITH getKeyPairRSA()
@logExceptionsWrapper
def loadKeyPairRSA(publick_key_serialized,master_key,private_key_serialized=None):
    if type(master_key) == type(''):
        master_key = master_key.encode()
    private_key = None
    if private_key_serialized is not None:
        private_key = load_pem_private_key(private_key_serialized,master_key)
    public_key = load_pem_public_key(publick_key_serialized)
    return private_key, public_key

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

############# FUNCTION TO SIGN MESSAGE WITH RSA PRIVATE KEY
@logExceptionsWrapper
def signRSA(private_key,message):
    signed_message = None
    if type(message) == type(''):
        message = message.encode()
    ########## ADD JSON TO BYTES ALSO THAT IS DICT TO JSON TO BYTES
    signed_message = private_key.sign(
        message,
        padding.PSS(
            mgf = padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
        )
    return signed_message

from cryptography.exceptions import InvalidSignature

############ FUNCTION TO VERIFY A MESSAGE SIGNED WITH RSA PRIVATE KEY
@logExceptionsWrapper
def verifySignRSA(public_key,signed_message,message):
    result = None
    try:
        public_key.verify(
            signed_message,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        result = True
    except InvalidSignature:
        result = False
    finally :
        return result

########## FUNCTION TO ENCRYPT MESSAGE USING RSA PUBLIC KEY
@logExceptionsWrapper
def encryptRSA(public_key,message):
    ciphertext = None
    if type(message) == type(''):
        message = message.encode()
    ########## ADD JSON TO BYTES ALSO THAT IS DICT TO JSON TO BYTES
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

########## FUNCTION TO DECRYPT MESSAGE ENCRYPTED WITH encryptRSA() USING CORRESPONDING PRIVATE KEY
@logExceptionsWrapper
def decryptRSA(private_key,ciphertext):
    plaintext = None
    try :
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        plaintext = plaintext.decode()
    except Exception as e:
        ########### Log here
        pass
    finally:
        return plaintext

from os import listdir
from json import load

########### FUNCTION TO CREATE KEY IF NOT ALREADY PRESENT 
@logExceptionsWrapper
def retrieveKeyPairRsa(master_key,serialize=False):
    config = None
    with open('config.json') as f:
        config = load(f)
    
    ############ if key is created and stored: retrieve
    if 'public_key_serialized' in listdir(config['data_path']+'DeviceSpecific/Device_data/'):
        public_key_serialized, private_key_serialized = None, None
        with open (config['data_path']+'DeviceSpecific/Device_data/public_key_serialized','rb') as f:
            public_key_serialized = f.read()
        with open (config['data_path']+'DeviceSpecific/Device_data/private_key_serialized','rb') as f:
            private_key_serialized = f.read()

    ############ key is not created and stored: create and store then return
    else:
        private_key_serialized, public_key_serialized = getKeyPairRSA(serialize=True,master_key=master_key)
        with open(config['data_path']+'DeviceSpecific/Device_data/public_key_serialized','wb') as f:
            f.write(public_key_serialized)
        with open(config['data_path']+'DeviceSpecific/Device_data/private_key_serialized','wb') as f:
            f.write(private_key_serialized)
    
    if serialize:
        return private_key_serialized, public_key_serialized
    else :
        private_key, public_key = loadKeyPairRSA(
            public_key_serialized,
            master_key,
            private_key_serialized
        )
        return private_key, public_key