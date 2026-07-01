"""Unit tests for api/metrics.py."""

from api.metrics import get_system_metrics


def test_metrics_returns_required_keys():
    """Verify the returned dict contains the expected keys."""
    result = get_system_metrics()
    assert "cpu_percent" in result
    assert "memory_percent" in result
    assert "disk_percent" in result
    assert "memory_used_gb" in result


def test_cpu_percent_in_range():
    """CPU percent should be between 0 and 100."""
    result = get_system_metrics()
    assert 0 <= result["cpu_percent"] <= 100


def test_memory_percent_in_range():
    """Memory percent should be between 0 and 100."""
    result = get_system_metrics()
    assert 0 <= result["memory_percent"] <= 100


def test_disk_percent_in_range():
    """Disk percent should be between 0 and 100."""
    result = get_system_metrics()
    assert 0 <= result["disk_percent"] <= 100


def test_memory_used_gb_positive():
    """Memory used in GB should be positive."""
    result = get_system_metrics()
    assert result["memory_used_gb"] > 0
