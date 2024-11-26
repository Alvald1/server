from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives import serialization  
from cryptography.hazmat.primitives.asymmetric import rsa


def gen_pub_key_pem(private_key) -> str:
    public_key = private_key.public_key()
    pem_pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    return pem_pub

def gen_priv_key(size: int):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=size,
        backend=default_backend()
    )
    return private_key

def gen_priv_key_pem(private_key) -> str:
    pem_priv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    return pem_priv

def gen_pair_pem(size: int):
    priv_key=gen_priv_key(size)
    priv_key_pem=gen_priv_key_pem(priv_key)
    pub_key_pem=gen_pub_key_pem(priv_key)
    return {'pem_priv':priv_key_pem, 'pem_pub': pub_key_pem}
