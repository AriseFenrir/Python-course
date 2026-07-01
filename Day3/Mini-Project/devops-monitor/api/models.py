"""Data models for the DevOps Monitoring Dashboard."""

from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field


@dataclass
class Server:
    """Represents a monitored server."""

    name: str
    host: str
    port: int
    id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "unknown"

    def base_url(self) -> str:
        """Return the base URL of the server."""
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Schema for incoming server registration requests."""

    name: str
    host: str
    port: int = Field(..., ge=1, le=65535)


class ServerOut(BaseModel):
    """Schema for server responses."""

    id: str
    name: str
    host: str
    port: int
    status: str
