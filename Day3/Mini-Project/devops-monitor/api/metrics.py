"""System metrics helper using psutil."""

import psutil


def get_system_metrics() -> dict:
    """Return a snapshot of current system metrics.

    Returns:
        dict with cpu_percent, memory_percent, memory_used_gb, disk_percent.
    """
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "disk_percent": disk.percent,
    }
