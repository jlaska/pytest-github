# -*- coding: utf-8 -*-
import pytest  # NOQA
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
from . import assert_outcome  # NOQA


def test_version():
    '''Verifies the module has a '__version__' attribue.'''

    import pytest_github
    assert hasattr(pytest_github, '__version__')
    assert isinstance(pytest_github.__version__, str)
