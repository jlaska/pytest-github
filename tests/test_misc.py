# -*- coding: utf-8 -*-
import pytest  # NOQA
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
from . import assert_outcome  # NOQA


def test_bad_github_issue_urls(request):
    '''Verifies the __parse_issue_url() method handles unexpected issue URLs.'''

    plugin = request.config.pluginmanager.getplugin("github_helper")

    for bad_url in ['', 'http://google.com', 'https://github.com/pytest-github/pytest-github']:
        with pytest.raises(Exception):
            plugin._GitHubPytestPlugin__parse_issue_url(bad_url)


def test_version():
    '''Verifies the module has a '__version__' attribue.'''

    import pytest_github
    assert hasattr(pytest_github, '__version__')
    assert isinstance(pytest_github.__version__, str)
