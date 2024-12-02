from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse
import json
from redis import Redis
import hashlib

from rsa_manager import gen_pair_pem, decrypt_message
from mysql_site import find_name

# This module converts binary data to hexadecimal


from binascii import hexlify
app = FastAPI()

main_redis = Redis(host='localhost', port=6581, db=1)

auth_redis = Redis(host='localhost', port=6581, db=2)


@app.post("/api", response_class=PlainTextResponse)
async def result(
    request: Request,
    message: str = Form(None),  # Сделать параметры необязательными
    key: str = Form(),  # Сделать параметры необязательными
    status: str = Form(None),  # Сделать параметры необязательными
):
    # Получаем все параметры из тела запроса
    form_data = await request.form()
    form_keys = set(form_data.keys())

    user_id = key[:23]
    device_id = key[23:]

    if {"message"}.issubset(form_keys):
        if form_keys - {"key", "message"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected parameters: {', '.join(form_keys - {'key', 'message'})}"
            )
        if not auth_redis.exists(key):
            return json.dumps({'message': 'not found', 'code': 2})
        pem_priv = auth_redis.hget(key, 'pem_priv')
        data = json.loads(decrypt_message(message, pem_priv))
        minute = data.pop('minute', None)
        data = json.dumps(data)

        hash_object = hashlib.sha256(data.encode())
        hash_hex = hash_object.hexdigest()

        fields = {
            'data': data,
            'minute': minute
        }
        if main_redis.hset(hash_hex, mapping=fields):
            return json.dumps({'message': 'delivered', 'code': 0})
        else
        return json.dumps({'message': 'dupplicate', 'code': 1})

    elif {"status"}.issubset(form_keys):

        if form_keys - {"key", "status"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected parameters: {', '.join(form_keys - {'key', 'status'})}"
            )
        # Сохраняем данные

        if status == 'on':
            if auth_redis.exists(key):
                return json.dumps({'message': 'already auth', 'code': 1})
            else:
                name = find_name(user_id, device_id, 'online')
                if name:
                    pair_pem = gen_pair_pem(2048)
                    auth_redis.hset(key, mapping=pair_pem)
                    return json.dumps({'message': pair_pem.get(
                        'pem_pub'), 'code': 0, 'name': name})
                return json.dumps({'message': 'not found', 'code': 2})
        elif status == 'off':
            if not auth_redis.exists(key):
                return json.dumps({'message': 'not found', 'code': 2})
            else:
                find_name(user_id, device_id, 'offline')
                auth_redis.hdel(key, 'pem_pub', 'pem_priv')
                return json.dumps({'message': 'deleted', 'code': 0})

    # Если параметры не соответствуют ни одному из ожидаемых сценариев
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid parameters. Expected either 'key' and 'message' or 'key' and 'status'."
        )
