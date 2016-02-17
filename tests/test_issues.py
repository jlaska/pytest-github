# -*- coding: utf-8 -*-
import pytest
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
from . import assert_outcome

pytestmark = pytest.mark.usefixtures("monkeypatch_github3")


def test_success_without_issue(testdir, option):
    '''Verifies test success when no github issue is specified.'''

    src = """
        import pytest
        def test_func():
            assert True
    """
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_OK
    assert_outcome(result, passed=1)


def test_success_with_open_issue(testdir, option, open_issues):
    '''Verifies test when an open github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert True
    """ % open_issues[0]
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_OK
    assert_outcome(result, xpassed=1)


def test_success_with_closed_issue(testdir, option, closed_issues):
    '''Verifies test when a closed github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert True
    """ % closed_issues[0]
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_OK
    assert_outcome(result, passed=1)


def test_failure_without_issue(testdir, option):
    '''Verifies test failure when no github issue is specified.'''

    src = """
        import pytest
        def test_func():
            assert False
    """
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_TESTSFAILED
    assert_outcome(result, failed=1)


def test_failure_with_open_issue(testdir, option, open_issues):
    '''Verifies test when an open github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert False
    """ % open_issues[0]
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_OK
    assert_outcome(result, xfailed=1)


def test_failure_with_closed_issue(testdir, option, closed_issues):
    '''Verifies test when a closed github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert False
    """ % closed_issues[0]
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_TESTSFAILED
    assert_outcome(result, failed=1)
