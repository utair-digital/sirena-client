# SirenaTravel Client

## Requirements
- xmltodict~=0.12.0
- pycryptodome=3.10.1
- pydantic
- ASYNC:
  - aioredis==1.3.1 
  - asyncio~=3.4.3 
  - aiofile~=3.7.2
- SYNC
  - redis==4.0.2
  
## Полезная информация
[Примеры использования](examples)

[Реализованные запросы](sirena_client/requests)


## Конфигурация SirenaClient

```python
from sirena_client import SirenaClientConfig

config = SirenaClientConfig(
    host="127.0.0.1",
    port=65536,
    client_id=42,
    private_key_path="path/to/sirena.pem",
    use_connection_pool=True,               # Влияет только на асинхронный клиент
    redis_url="redis://127.0.0.1"
)


```
### Важно!
Для хранения симметричного ключа в редисе нужно предоставить redis_url 
Иначе перед каждым запросом клиент будет регистрировать симметричный ключ.

## Как пользоваться Асинхронной версией

```python
from sirena_client import SirenaClient
from sirena_client import SirenaClientConfig
from sirena_client.requests import GetOrder
from sirena_client.exceptions import SirenaPnrAndSurnameDontMatch
config = SirenaClientConfig(
    host="127.0.0.1",
    port=65536,
    client_id=42,
    private_key_path="path/to/sirena.pem",
    use_connection_pool=True,
    redis_url="redis://127.0.0.1"
)
request = GetOrder(
    rloc='VN88T5',
    last_name='Тестфам'
)

client = SirenaClient(config)
async with client as session:
    try:
        basic_response = await session.query(request)             # Один запрос, кинет ошибку если будет
    except SirenaPnrAndSurnameDontMatch:
        pass
    silent_response = await session.query(request, silent=True)   # сохранит ошибку в ответ
    silent_response.raise_for_error()   # Или bool(silent_response) == False
    batch_results = await session.batch_query([request, request, request]) # Асинхронный запрос пачкой

```

## Как пользоваться Синхронной версией
```python
from sirena_client import SirenaClient
from sirena_client import SirenaClientConfig
from sirena_client.requests import GetOrder
from sirena_client.exceptions import SirenaPnrAndSurnameDontMatch
config = SirenaClientConfig(
    host="127.0.0.1",
    port=65536,
    client_id=42,
    private_key_path="path/to/sirena.pem",
    redis_url="redis://127.0.0.1"
)
request = GetOrder(
    rloc='VN88T5',
    last_name='Тестфам'
)

client = SirenaClient(config)
with client as session:
    try:
        basic_response = session.query(request)             # Один запрос, кинет ошибку если будет
    except SirenaPnrAndSurnameDontMatch:
        pass
    silent_response = session.query(request, silent=True)   # сохранит ошибку в ответ
    silent_response.raise_for_error()   # Или bool(silent_response) == False
    batch_results = session.batch_query([request, request, request]) # Асинхронный запрос пачкой

```
