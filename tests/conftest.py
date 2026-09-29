"""Shared local HTTP server fixture."""

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer


@pytest.fixture
async def serve():
    servers = []

    async def start(handler):
        app = web.Application()
        app.router.add_route("*", "/{path:.*}", handler)
        server = TestServer(app)
        servers.append(server)
        await server.start_server()
        return str(server.make_url("/"))

    yield start
    for server in servers:
        await server.close()
