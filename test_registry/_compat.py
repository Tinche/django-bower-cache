"""Python 2/3 compatibility module - test version."""
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    import mock
    from mock import MagicMock
else:
    from unittest import mock
    from unittest.mock import MagicMock