"""
Einstein AI V2 — Foundation Tests
"""

import einstein_v2


def test_version_exists():
    assert hasattr(einstein_v2, "__version__")


def test_version():
    assert einstein_v2.__version__ == "0.1.0"
