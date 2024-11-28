from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse
import json
from redis import Redis

from rsa_manager import gen_pair_pem
from mysql_site import find_name

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
        if status == 'on':
            if auth_redis.exists(key):
                return json.dumps({'message': 'already auth', 'code': 1})
            else:
                user_id = key[:23]
                device_id = key[23:]
                name = find_name(user_id, device_id)
                if name:
                    pair_pem = gen_pair_pem(1024)
                    auth_redis.hset(key, mapping=pair_pem)
                    return json.dumps({'message': pair_pem.get(
                        'pem_pub'), 'code': 0, 'name': name})
                return json.dumps({'message': 'not found', 'code': 2})
        elif status == 'off':
            if not auth_redis.exists(key):
                return json.dumps({'message': 'not found', 'code': 2})
            else:
                auth_redis.hdel(key, 'pem_pub', 'pem_priv')
                return json.dumps({'message': 'deleted', 'code': 0})

    # Если параметры не соответствуют ни одному из ожидаемых сценариев
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid parameters. Expected either 'foo' and 'bar' or 'key' and 'status'."
        )
