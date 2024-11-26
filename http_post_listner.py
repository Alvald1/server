from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse
import json
from redis import Redis

from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives import serialization  
from cryptography.hazmat.primitives.asymmetric import rsa  

# This module converts binary data to hexadecimal
from binascii import hexlify
app = FastAPI()

main_redis = Redis(host='localhost', port=6581, db=1)

auth_redis = Redis(host='localhost', port=6581, db=2)

@app.post("/api", response_class=PlainTextResponse)
async def result(
    request: Request,
    foo: str = Form(None),  # Сделать параметры необязательными
    bar: str = Form(None),  # Сделать параметры необязательными
    key: str = Form(None),  # Сделать параметры необязательными
    status: str = Form(None),  # Сделать параметры необязательными
):
    # Получаем все параметры из тела запроса
    form_data = await request.form()
    form_keys = set(form_data.keys())

    # Проверяем сценарий для foo и bar
    if {"foo", "bar"}.issubset(form_keys):
        if form_keys - {"foo", "bar"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected parameters: {', '.join(form_keys - {'foo', 'bar'})}"
            )
        # Сохраняем данные
        data = {"foo": foo, "bar": bar}
        with open("data.json", "a") as f:
            json.dump(data, f)
            f.write("\n")
        return "Processed foo and bar"

    # Проверяем сценарий для key и status
    elif {"key", "status"}.issubset(form_keys):
        if form_keys - {"key", "status"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected parameters: {', '.join(form_keys - {'key', 'status'})}"
            )
        # Сохраняем данные
        if status=='on':
            if auth_redis.exists(key):
                return json.dumps({'massege': 'already auth', 'code': 1})
            else:
                private_key = rsa.generate_private_key(  
                    public_exponent=65537,  
                    key_size=1024,  
                    backend=default_backend()  
                )  
                pem_priv = private_key.private_bytes(  
                    encoding=serialization.Encoding.PEM,  
                    format=serialization.PrivateFormat.PKCS8,  
                    encryption_algorithm=serialization.NoEncryption()  
                ).decode('utf-8')   
                public_key = private_key.public_key()
                pem_pub = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')  
                auth_redis.hset(key, mapping={'pem_priv': pem_priv, 'pem_pub': pem_pub})
            return json.dumps({'massege': pem_pub, 'code': 0})
        elif status=='off':
            if not auth_redis.exists(key):
                return json.dumps({'massege': 'not found', 'code': 2})
            else:
                auth_redis.hdel(key,'pem_pub','pem_priv')
                return json.dumps({'massege': 'deleted', 'code': 0})

    # Если параметры не соответствуют ни одному из ожидаемых сценариев
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid parameters. Expected either 'foo' and 'bar' or 'key' and 'status'."
        )

