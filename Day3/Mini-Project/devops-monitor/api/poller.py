"""Background health-check polling logic."""

import asyncio

import httpx

from api.models import Server


async def poll_server(server_id: str, url: str, store: dict[str, Server]) -> None:
    """Check a single server's health endpoint.

    Sets the server's status to "UP", "DEGRADED", or "DOWN".

    Args:
        server_id: The server's unique identifier.
        url: The base URL of the server.
        store: The in-memory server store (mutated in place).
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                store[server_id].status = "UP"
            else:
                store[server_id].status = "DEGRADED"
    except (httpx.RequestError, httpx.TimeoutException):
        store[server_id].status = "DOWN"


async def run_poll_loop(store: dict[str, Server], interval: int = 10) -> None:
    """Continuously poll all registered servers.

    Runs poll_server for every server concurrently, then sleeps.

    Args:
        store: The in-memory server store.
        interval: Seconds between polling rounds.
    """
    while True:
        if store:
            tasks = [
                poll_server(server_id, server.base_url(), store)
                for server_id, server in store.items()
            ]
            await asyncio.gather(*tasks)
        await asyncio.sleep(interval)
