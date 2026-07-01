"""FastAPI application entry point for the DevOps Monitoring Dashboard."""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop

# In-memory server store
servers: dict[str, Server] = {}

# Background polling task reference
poll_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: start and stop the poll loop."""
    global poll_task
    poll_task = asyncio.create_task(run_poll_loop(servers))
    yield
    poll_task.cancel()
    try:
        await poll_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="DevOps Monitoring Dashboard", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> dict:
    """Return current system metrics."""
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket) -> None:
    """Stream system metrics via WebSocket every second."""
    await websocket.accept()
    try:
        while True:
            data = get_system_metrics()
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.post("/servers", status_code=201)
async def create_server(
    server_in: ServerIn, _: str = Depends(verify_api_key)
) -> ServerOut:
    """Register a new server to monitor."""
    server = Server(name=server_in.name, host=server_in.host, port=server_in.port)
    servers[server.id] = server
    return ServerOut(
        id=server.id,
        name=server.name,
        host=server.host,
        port=server.port,
        status=server.status,
    )


@app.get("/servers")
async def list_servers(status: Optional[str] = Query(None)) -> list[ServerOut]:
    """List all monitored servers, optionally filtered by status."""
    result = []
    for server in servers.values():
        if status is None or server.status == status:
            result.append(
                ServerOut(
                    id=server.id,
                    name=server.name,
                    host=server.host,
                    port=server.port,
                    status=server.status,
                )
            )
    return result


@app.get("/servers/{server_id}")
async def get_server(server_id: str) -> ServerOut:
    """Get a single server by ID."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    server = servers[server_id]
    return ServerOut(
        id=server.id,
        name=server.name,
        host=server.host,
        port=server.port,
        status=server.status,
    )


@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(server_id: str, _: str = Depends(verify_api_key)) -> None:
    """Remove a monitored server."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    del servers[server_id]


@app.post("/servers/{server_id}/check")
async def check_server(server_id: str, background_tasks: BackgroundTasks) -> dict:
    """Trigger an immediate health check for a specific server."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    server = servers[server_id]
    background_tasks.add_task(poll_server, server_id, server.base_url(), servers)
    return {"message": f"Health check triggered for server '{server.name}'"}
