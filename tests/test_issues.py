# -*- coding: utf-8 -*-
import pytest
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_INTERNALERROR, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
from . import assert_outcome

# pytestmark = pytest.mark.usefixtures("monkeypatch_github3")


@pytest.mark.usefixtures('monkeypatch_github3')
def test_success_without_issue(testdir):
    '''Verifies test success when no github issue is specified.'''

    src = """
        import pytest
        def test_func():
            assert True
    """
    result = testdir.inline_runsource(src)
    assert result.ret == EXIT_OK
    assert_outcome(result, passed=1)


@pytest.mark.usefixtures('monkeypatch_github3')
@pytest.mark.parametrize(
    "skip,expected_outcome",
    [
        (False, dict(xpassed=1)),
        (True, dict(skipped=1)),
    ],
)
def test_success_with_open_issue(testdir, open_issues, skip, expected_outcome):
    '''Verifies test when an open github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s'%s)
        def test_func():
            assert True
    """ % (open_issues[0], skip and ', skip=True' or '')
    result = testdir.inline_runsource(src)
    assert result.ret == EXIT_OK
    assert_outcome(result, **expected_outcome)


@pytest.mark.usefixtures('monkeypatch_github3')
@pytest.mark.parametrize(
    "skip,expected_outcome",
    [
        (False, dict(passed=1)),
        (True, dict(passed=1)),
    ],
)
def test_success_with_closed_issue(testdir, closed_issues, skip, expected_outcome):
    '''Verifies test when a closed github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s'%s)
        def test_func():
            assert True
    """ % (closed_issues[0], skip and ', skip=True' or '')
    result = testdir.inline_runsource(src)
    assert result.ret == EXIT_OK
    assert_outcome(result, passed=1)


@pytest.mark.usefixtures('monkeypatch_github3')
def test_failure_without_issue(testdir):
    '''Verifies test failure when no github issue is specified.'''

    src = """
        import pytest
        def test_func():
            assert False
    """
    result = testdir.inline_runsource(src)
    assert result.ret == EXIT_TESTSFAILED
    assert_outcome(result, failed=1)


@pytest.mark.usefixtures('monkeypatch_github3')
@pytest.mark.parametrize(
    "skip,expected_outcome",
    [
        (False, dict(xfailed=1)),
        (True, dict(skipped=1)),
    ],
)
def test_failure_with_open_issue(testdir, open_issues, skip, expected_outcome):
    '''Verifies test when an open github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s'%s)
        def test_func():
            assert False
    """ % (open_issues[0], skip and ', skip=True' or '')
    result = testdir.inline_runsource(src)
    assert result.ret == EXIT_OK
    assert_outcome(result, **expected_outcome)


@pytest.mark.usefixtures('monkeypatch_github3')
@pytest.mark.parametrize(
    "skip,expected_outcome",
    [
        (False, dict(failed=1)),
        (True, dict(failed=1)),
    ],
)
def test_failure_with_closed_issue(testdir, closed_issues, skip, expected_outcome):
    '''Verifies test when a closed github issue is specified.'''

    src = """
        import pytest
        @pytest.mark.github('%s'%s)
        def test_func():
            assert False
    """ % (closed_issues[0], skip and ', skip=True' or '')
    result = testdir.inline_runsource(src)
    assert result.ret == EXIT_TESTSFAILED
    assert_outcome(result, **expected_outcome)


@pytest.mark.parametrize(
    "issue_url, expected_result",
    [
        (None, EXIT_OK),
        ('', EXIT_OK),
        ('""', EXIT_INTERNALERROR),
        ('"asdfasdf"', EXIT_INTERNALERROR),
        ('"https://github.com"', EXIT_INTERNALERROR),
        ('"https://github.com/pytest-github/pytest-github"', EXIT_INTERNALERROR),
    ]
)
def test_with_malformed_issue_link(testdir, capsys, issue_url, expected_result):
    '''FIXME'''

    src = """
        import pytest
        @pytest.mark.github(%s)
        def test_func():
            assert True
    """ % issue_url
    result = testdir.inline_runsource(src)
    assert result.ret == expected_result

    stdout, stderr = capsys.readouterr()
    if expected_result == EXIT_OK:
        assert "Malformed github issue URL:" not in stdout
    else:
        assert "Malformed github issue URL:" in stdout


def test_with_private_issue_link(testdir, recwarn, capsys):
    '''FIXME'''

    issue_url = 'https://github.com/github/github/issues/1'
    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert False
    """ % issue_url
    with pytest.warns(None) as record:
        result = testdir.inline_runsource(src)
        assert result.ret == EXIT_TESTSFAILED

    # check that warnings are present
    assert len(record) > 0

    # Assert the expected warning is present
    found = False
    expected_warning = "Unable to inspect github issue %s" % issue_url
    for warning in record:
        # check that the category matches
        assert issubclass(warning.category, Warning)

        # check that the message matches
        if expected_warning in str(warning.message):
            found = True

    # Assert the warning was found
    assert found, "Unable to find expected warning message - %s" % expected_warning


@pytest.mark.usefixtures('monkeypatch_github3')
@pytest.mark.parametrize('mark_raises,mark_skipped,expected_outcome,expected_exit_code', [
    ('ZeroDivisionError', False, 'xfailed', EXIT_OK),
    ('ZeroDivisionError', True, 'skipped', EXIT_OK),
    ('ValueError', False, 'failed', EXIT_TESTSFAILED),
    ('ValueError', True, 'skipped', EXIT_OK),
    ('None', False, 'xfailed', EXIT_OK),
])
def test_raises_kwarg_used_with_open_issue_when_exception_is_raised(
    testdir,
    open_issues,
    mark_raises,
    mark_skipped,
    expected_outcome,
    expected_exit_code
):
    """Verifiy expected test outcome of an exception-raising test when the
    raises keyword is used
    """
    src = """
        import pytest
        @pytest.mark.github('{issue}', skip={skip}, raises={raises})
        def test_func():
            raise ZeroDivisionError
    """.format(issue=open_issues[0], skip=mark_skipped, raises=mark_raises)

    result = testdir.inline_runsource(src)

    assert result.ret == expected_exit_code
    assert_outcome(result, **{expected_outcome: 1})


@pytest.mark.usefixtures('monkeypatch_github3')
@pytest.mark.parametrize('mark_raises,mark_skipped,expected_outcome,expected_exit_code', [
    ('ZeroDivisionError', False, 'failed', EXIT_TESTSFAILED),
    ('ZeroDivisionError', True, 'failed', EXIT_TESTSFAILED),
    ('ValueError', False, 'failed', EXIT_TESTSFAILED),
    ('ValueError', True, 'failed', EXIT_TESTSFAILED),
    ('None', False, 'failed', EXIT_TESTSFAILED),
])
def test_raises_kwarg_used_with_closed_issue_when_exception_is_raised(
    testdir,
    closed_issues,
    mark_raises,
    mark_skipped,
    expected_outcome,
    expected_exit_code
):
    """Verifiy expected test outcome of an exception-raising test when the
    raises keyword is used
    """
    src = """
        import pytest
        @pytest.mark.github('{issue}', skip={skip}, raises={raises})
        def test_func():
            raise ZeroDivisionError
    """.format(issue=closed_issues[0], skip=mark_skipped, raises=mark_raises)

    result = testdir.inline_runsource(src)

    assert result.ret == expected_exit_code
    assert_outcome(result, **{expected_outcome: 1})
