# -*- coding: utf-8 -*-
import pytest
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_INTERNALERROR, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
from . import assert_outcome

# pytestmark = pytest.mark.usefixtures("monkeypatch_github3")


@pytest.mark.usefixtures('monkeypatch_github3')
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


@pytest.mark.usefixtures('monkeypatch_github3')
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


@pytest.mark.usefixtures('monkeypatch_github3')
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


@pytest.mark.usefixtures('monkeypatch_github3')
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


@pytest.mark.usefixtures('monkeypatch_github3')
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


@pytest.mark.usefixtures('monkeypatch_github3')
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


def test_with_malformed_issue_link(testdir, option, capsys):
    '''FIXME'''

    src = """
        import pytest
        @pytest.mark.github('https://github.com')
        def test_func():
            assert False
    """
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_INTERNALERROR

    stdout, stderr = capsys.readouterr()
    assert "Malformed github issue URL: https://github.com" in str(stdout)


def test_with_private_issue_link(testdir, option, recwarn, capsys):
    '''FIXME'''

    import pytest_github
    pytest_github._issue_cache = {}
    issue_url = 'https://github.com/github/github/issues/1'
    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert False
    """ % issue_url
    result = testdir.inline_runsource(src, *option.args)
    assert result.ret == EXIT_TESTSFAILED

    stdout, stderr = capsys.readouterr()

    # check that only one warning was raised
    assert len(recwarn) == 1
    # check that the category matches
    record = recwarn.pop(Warning)
    assert issubclass(record.category, Warning)
    # check that the message matches
    assert str(record.message) == "Unable to inspect github issue %s" % issue_url
