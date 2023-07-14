import logging
import os
import asyncio

from usdk.clients.external.sirena.requests import GetOrder, PlainRequest
from usdk.clients.external.sirena import SirenaClient, SirenaClientConfig

logging.basicConfig(level=logging.DEBUG)

PROJECT_ROOT = os.path.realpath(os.path.abspath(os.curdir))

SIRENA_APC = {
    'host': '1.1.1.1',
    'port': 1,
    'client_id': 1,
    'private_key_path': os.path.join(PROJECT_ROOT, '../.keys', 'sirena.pem'),
}


config = SirenaClientConfig(**SIRENA_APC)
client = SirenaClient(config)

get_order = GetOrder(
    rloc='PNR123',
    last_name='Lastname'
)

plain_request = PlainRequest(
    body={
        'regnum': {
            '#text': "PNR123",
            '@version': "ignore"
        },
        'surname': 'Lastname',
        'request_params': {},
        'answer_params': {}
    }, method='order'
)


async def run_a():
    async with client as c:
        order_1 = await c.query(get_order, silent=True)
        order_2 = await c.query(plain_request, silent=True)
        print(order_1, order_2)


def run_s():
    a = SirenaClient(config)
    with client as c:
        order_1 = c.query(get_order, silent=True)
        order_2 = c.query(plain_request, silent=True)
        print(order_1, order_2)


async def run_all():
    run_s()
    await run_a()


asyncio.run(run_all())
