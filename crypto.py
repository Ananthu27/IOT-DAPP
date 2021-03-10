from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from urllib.request import urlopen

############ FUNCTION RETURNS PUBLIC PRIVATE KEY PAIR FOR RSA
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
def loadKeyPairRSA(private_key_serialized,publick_key_serialized,master_key):
    private_key = load_pem_private_key(private_key_serialized,master_key.encode())
    public_key = load_pem_public_key(publick_key_serialized)
    return private_key, public_key

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

############# FUNCTION TO SIGN MESSAGE WITH RSA PRIVATE KEY
def signRSA(private_key,message):
    signed_message = None
    if type(message) == type(b''):
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