import logging
import os
import asyncio

from utair.clients.external.sirena.requests import GetOrder, PlainRequest

logging.basicConfig(level=logging.DEBUG)

PROJECT_ROOT = os.path.realpath(os.path.abspath(os.curdir))

SIRENA_APC = {
    'host': '1.1.1.1',
    'port': 1,
    'client_id': 1,
    'private_key_path': os.path.join(PROJECT_ROOT, '../.keys', 'sirena.pem'),
    'redis_url': 'redis://127.0.0.1:32773',
}

RLOC = 'PNR123'
LAST_NAME = 'Lastname'

get_order = GetOrder(
    rloc=RLOC,
    last_name=LAST_NAME
)

plain_request = PlainRequest(
    body={
        'regnum': {
            '#text': RLOC,
            '@version': "ignore"
        },
        'surname': LAST_NAME,
        'request_params': {},
        'answer_params': {}
    }, method='order'
)


async def run_a():
    from utair.clients.external.sirena import SirenaClientConfig
    from utair.clients.external.sirena.async_client import SirenaClient
    config = SirenaClientConfig(**SIRENA_APC)
    client = SirenaClient(config)

    async with client as c:
        order_1 = await c.query(get_order, silent=True)
        order_2 = await c.query(plain_request, silent=True)
        batch = await c.batch_query([get_order, get_order, get_order])
        print(order_1, order_2)
        print(batch)


def run_s():
    from utair.clients.external.sirena import SirenaClientConfig
    from utair.clients.external.sirena.sync import SirenaClient
    config = SirenaClientConfig(**SIRENA_APC)
    client = SirenaClient(config)

    with client as c:
        order_1 = c.query(get_order, silent=True)
        order_2 = c.query(plain_request, silent=True)
        batch = c.batch_query([get_order, get_order, get_order])
        print(order_1, order_2)
        print(batch)


async def run_all():
    run_s()
    await run_a()


asyncio.run(run_all())
