from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import json


def gen_pub_key_pem(private_key) -> str:
    public_key = private_key.public_key()
    pem_pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    return pem_pub.replace("\n", "")


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
    return pem_priv.replace("\n", "")


def gen_pair_pem(size: int):
    priv_key = gen_priv_key(size)
    priv_key_pem = gen_priv_key_pem(priv_key)
    pub_key_pem = gen_pub_key_pem(priv_key)
    return {'pem_priv': priv_key_pem, 'pem_pub': pub_key_pem}


def decrypt_message_(encrypted_data: dict, pem_private_key: str) -> str:
    # Загрузка закрытого ключа
    private_key = load_pem_private_key(
        pem_private_key.encode('utf-8'), password=None)

    # Расшифровка AES-ключа
    encrypted_key = base64.b64decode(encrypted_data["encryptedKey"])
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Расшифровка сообщения с использованием AES
    iv = base64.b64decode(encrypted_data["iv"])
    ciphertext = base64.b64decode(encrypted_data["ciphertext"])

    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_message.decode('utf-8')


def decrypt_message(encrypted_data_json: str, pem_private_key: str):
    encrypted_data = json.loads(encrypted_data_json)
    return decrypt_message_(encrypted_data, pem_private_key)


json_ = '{"encryptedKey":"ppHBI8ZJzSIztvYi58tgqhE6PHvj/WWodj+xOiSoZre3Wrth/pzOtjxrc8G/PTUc+siVdKfdCqmhXT3wdpR0BeRK9dhVojoQwrBAeIX/fVJNXfHdoAZUnkDR5qJojsfvBn8JgKD8ehj7qt2uh07d8OGPJbdqrjKkLgta6WEZ2Icz1moINdOPqRhsrJLYV8+mFxSDbv/Ysu2hUVegcWJFC7XozrwIo4dJ5cWzh7o3PjIipJ7tEWe5uRAENvCzbMfmAXxYl3snYIieY0p44mnA4jzbaGwCBGoRmwBniaa5gT4m9dCxtieX3RchPFkzEZtK3w4GYEc6ZxGH+qJsQRI8ZQ==","iv":"k+JgB4SHIRZ4C5MPYCC6sQ==","ciphertext":"RfWCtTzuZl27AocoonR02BCWcJBpN+eSyljYCkIYAJE="}'


priv = '''-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDaFuEPJ04hpWRDFs7Jv/FXfSFzo3UKhM7Hh5gjBc3J2RZY7PGGdW8J4LSAj0ju2CW9ihhhjRem9PNRrTDbMQQ78jsAg8ysjZFXP/Zcsq/P4EGcUgb0cVQsm7l8nfZmOBWgm6MGHKVdhFGcapOoe6xjtpELzubrW2lcufRd/4tW4HwYxbJZX+9E5zTDreOIJ3kxj4tBtfFd6SIH4vfUfkqPSwUQ7BNvRg8oGPBjC7VqSHUhpP3LO0PBSRQHLZclJfXZHPCBDmw6/+zZkvZHAz/FVEuVt7BNKFLE9OXWb4FN9iCgbvlxsL2+GN9gRKo+SFoozVaayilSEOU6KR4qb2dlAgMBAAECggEAHJp+lyG1FiWekkwGACD8Etj3D7cjDSehBTtsAT/sHyqpSy18egGh+B4wHmJskuLnhEX976F1NjEPTqmT7FOv9frNsUIYEJOaueJKOhs3guCrSkjZ36qTeyxLdiQzonF9qKxxA8azC6Jkn8q8pg7ea8+Qk4dl8v1wwrgi7Ecta83UXZsnjkobMQC+XRSYwJ4zpSeC67BTAmoiEIa32KYDHs4OnlfMBk4fNtcdNbFlINESMYlmqJ8l4ZGUB66WlE54hHCo/gj5AsEK7j6Pv2Gg4ZXH30Uq5gG6u4vxHOSj3rtyCyWD4lX5Zt9xEzVpDYBHFNp/w91MwTtpuD4+BALxywKBgQD/a3QS2KdyyOvUtojD7N4CGWh8kaCJ6zq86uEVdF6cwjeHGg25HgKK87L5F9gPfPxoXcrYZUmQ8TlDEJ44GNlSJXZk8Qdnk1AjbcmgGxgAPZdv95JWgOyRujzUPJvbbYzR69Rr7e6r4DJ8/9/zVt/iyxbTGoPWGdoGoKwj6KMZuwKBgQDalbcWyRas98MaqYHQLwq7/J0ONJDsXM0lhZUAV1eLOnqSyR/VsMnWWO6rKMEq4w+Hy6cIWB2dDL7z0QAIXiByWpvihfJoLuKXVRO/7ssADmWYSq2DhMPmaU4Bs6BPH1kvxefpzURNy3gKK2y7s57VLb63Ik6s+EPi2phTWGthXwKBgDQcfTsXHtrJaWwlrbOjkQwGmQ3JPGLHLl264h9ZdbAv49pZk3EwUT5+SAaQOdG3I1w7vpX13FOJE7C+JDm3wCcFY6lmj6cvJAuGa7uRq4zpBAuhDCc/+IQm5iA7GWVkbXWq0tUOX0KL5GEiZ1OjZtxDqS163GkDLzto7pYI8bXfAoGAbuzPLwb5NOm+3wbqU6Wrwt5dLVpLuUcW7FWv2a55RLR2g4sBVsYSh242IDHcZVE5Dmaw6zEcRhizxrNnWte5i46j0P68l1ZDsxx/m0UpS2wC7pfnGfkEGSeTaJWpYr272tyJ5kI+yWPaFP8YfOCYWAKQ6ArG9kw+1x6rcpBKXe0CgYEAkiCw1+Gz6ZpyYrmEqxdx++5aWdGQquAVlvf+zC0iUcYYUB+60hyK64WQ97zlYd6Hmu8LqsIgXZWAT6HpYB1aVqgNjOZ8wVwXCLE0YcKaMeqJAe7tZq/DfZXhJpLmGfHgkJnKP7Jz4ZYB6GhPFaTqxpkqYsXRyvV3/uU1DT2s+Qw=
-----END PRIVATE KEY-----'''
