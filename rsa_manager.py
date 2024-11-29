from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
import base64
from cryptography.hazmat.primitives import padding
import json


def gen_pub_key_pem(private_key) -> str:
    public_key = private_key.public_key()
    pem_pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    return pem_pub.replace(
        "\n",
        "").replace(
        '-----BEGIN PUBLIC KEY-----',
        '-----BEGIN PUBLIC KEY-----\n').replace(
            '-----END PUBLIC KEY-----',
        '\n-----END PUBLIC KEY-----')


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
    return pem_priv.replace(
        "\n",
        "").replace(
        '-----BEGIN PRIVATE KEY-----',
        '-----BEGIN PRIVATE KEY-----\n').replace(
            '-----END PRIVATE KEY-----',
        '\n-----END PRIVATE KEY-----')


def gen_pair_pem(size: int):
    priv_key = gen_priv_key(size)
    priv_key_pem = gen_priv_key_pem(priv_key)
    pub_key_pem = gen_pub_key_pem(priv_key)
    return {'pem_priv': priv_key_pem, 'pem_pub': pub_key_pem}


def decrypt_message_(encrypted_data: dict, pem_private_key: str) -> str:
    try:
        # Преобразуем ключ в bytes, если это строка
        if isinstance(pem_private_key, str):
            pem_private_key = pem_private_key.encode('utf-8')

        # Загрузка закрытого ключа
        try:
            private_key = load_pem_private_key(pem_private_key, password=None)
        except ValueError as e:
            raise ValueError(
                "Ошибка загрузки закрытого ключа: проверьте формат или содержание ключа.") from e

        # Расшифровка AES-ключа
        try:
            encrypted_key = base64.b64decode(encrypted_data["encryptedKey"])
            aes_key = private_key.decrypt(
                encrypted_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except (InvalidKey, ValueError, TypeError) as e:
            raise ValueError(
                "Ошибка расшифровки AES-ключа: проверьте зашифрованные данные и ключ.") from e

        # Расшифровка сообщения с использованием AES (CBC)
        try:
            iv = base64.b64decode(encrypted_data["iv"])
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])

            # Инициализация AES с CBC
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded_message = decryptor.update(
                ciphertext) + decryptor.finalize()
        except (ValueError, KeyError) as e:
            raise ValueError(
                "Ошибка расшифровки сообщения: проверьте IV или зашифрованный текст.") from e

        # Удаление padding (PKCS5)
        try:
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_message = unpadder.update(
                padded_message) + unpadder.finalize()
        except ValueError as e:
            raise ValueError(
                "Ошибка удаления padding: зашифрованные данные некорректны.") from e

        return decrypted_message.decode('utf-8')

    except Exception as e:
        # Общий обработчик ошибок
        return f"Ошибка расшифровки: {str(e)}"


def decrypt_message(encrypted_data_json: str, pem_private_key: str):
    encrypted_data = json.loads(encrypted_data_json)
    return decrypt_message_(encrypted_data, pem_private_key)
