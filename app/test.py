import pytest
from aiohttp import web

from utils import transform, select_db, custom_encode


async def main(request):
    if request.method == 'POST':
        data = await request.post()
        request.app['url_input'] = data['url_input']
        request.app['custom_input'] = data['custom_input']
        if data['custom_input'] !='':
            short_link = await custom_encode(data)
        else:
            short_link = await transform(data['url_input'])
        return web.Response(body=short_link)

@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.router.add_get('/', main)
    app.router.add_post('/', main)
    return loop.run_until_complete(aiohttp_client(app))

async def test_encode(cli):
    data = {'url_input':'SOME_URL', 'custom_input':''}
    resp = await cli.post('/', data=data)
    assert resp.status == 200
    assert cli.server.app['url_input'] == 'SOME_URL'
    assert await resp.text() == 'http://short/red/b'

async def test_custom_encode(cli):
    data = {'url_input':'Another_URL', 'custom_input':'somePage'}
    resp = await cli.post('/', data=data)
    assert resp.status == 200
    assert cli.server.app['url_input'] == 'Another_URL'
    assert cli.server.app['custom_input'] == 'somePage'
    assert await resp.text() == 'http://short/red/somePage'