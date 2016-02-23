# -*- coding: utf-8 -*-
import pytest
import mock
from _pytest.main import EXIT_OK, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED
from . import assert_outcome


def test_plugin_help(testdir):
    '''Verifies expected output from of py.test --help'''

    result = testdir.runpytest('--help')
    result.stdout.fnmatch_lines([
        # Check for the github args section header
        'pytest-github:',
        # Check for the specific args
        '* --github-cfg=GITHUB_CFG',
        '* --github-username=GITHUB_USERNAME',
        '* --github-token=GITHUB_TOKEN',
        '* --github-completed=GITHUB_COMPLETED',
        '* --github-summary *',
        # Check for the marker in --help
        '  github (args) * GitHub issue integration',
    ])


def test_plugin_markers(testdir):
    '''Verifies expected output from of py.test --markers'''

    result = testdir.runpytest('--markers')
    result.stdout.fnmatch_lines([
        '@pytest.mark.github(*args): GitHub issue integration',
    ])


@pytest.mark.parametrize(
    "required_value_parameter",
    [
        "--github-cfg",
        "--github-username",
        "--github-token",
        "--github-completed",
    ],
    ids=[
        "--github-cfg",
        "--github-username",
        "--github-token",
        "--github-completed",
    ],
)
def test_param_requires_value(testdir, option, required_value_parameter):
    '''Verifies failure when not providing a value to a required parameter'''

    result = testdir.runpytest(*[required_value_parameter])
    assert result.ret == EXIT_INTERRUPTED
    result.stderr.fnmatch_lines([
        '*: error: argument %s: expected one argument' % required_value_parameter,
    ])


def test_param_github_cfg_with_no_such_file(testdir, option, recwarn):
    '''Verifies pytest-github ignores any bogus files passed to --github-cfg'''

    result = testdir.runpytest(*['--github-cfg', 'asdfasdf'])
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # check that only one warning was raised
    assert len(recwarn) == 1
    # check that the category matches
    record = recwarn.pop(Warning)
    assert issubclass(record.category, Warning)
    # check that the message matches
    assert str(record.message) == "No github configuration file found matching: asdfasdf"


def test_param_github_cfg_containing_no_data(testdir, option, recwarn):
    '''Verifies pytest-github ignores --github-cfg files that contain bogus data'''

    # Create bogus config file for testing
    cfg_file = testdir.makefile('.txt', '')

    # Run with parameter (expect pass)
    result = testdir.runpytest(*['--github-cfg', str(cfg_file)])
    assert result.ret == EXIT_OK

    # check that only one warning was raised
    assert len(recwarn) == 1
    # check that the category matches
    record = recwarn.pop(Warning)
    assert issubclass(record.category, Warning)
    # check that the message matches
    assert str(record.message).startswith("No github configuration found in file: ")


def test_param_github_cfg(testdir, option, open_issues):
    '''verifies pytest-github loads completed info from provided --github-cfg parameter'''

    # create github.yml config for testing
    contents = '''
    github:
        username: ''
        token: ''
        completed:
            - 'state:Ready For Test'
    '''
    cfg_file = testdir.makefile('.yml', contents)

    # the following would normally xpass, but when completed=['ready_for_test'], it
    # will just pass
    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert True
        """ % open_issues[0]

    mo = mock.mock_open()
    with mock.patch('pytest_github.plugin.open', mo, create=True):
        result = testdir.inline_runsource(src, *['--github-cfg', str(cfg_file)])

    # Assert py.test exit code
    assert result.ret == EXIT_OK

    # Assert mock open called on provided file
    mo.assert_called_once_with(str(cfg_file), 'r')


def test_param_github_summary_no_issues(testdir, option, capsys, closed_issues, open_issues):
    '''verifies the --github-summary parameter when no github issues are found.'''

    src = """
        import pytest
        def test_foo():
            assert True
    """
    result = testdir.inline_runsource(src, *option.args + ['--github-summary'])
    assert_outcome(result)

    stdout, stderr = capsys.readouterr()
    assert 'No github issues collected' in stdout


def test_param_github_summary_multiple_issues(testdir, option, capsys, closed_issues, open_issues):
    '''verifies the --github-summary parameter when multiple github issues are found.'''

    src = """
        import pytest
        @pytest.mark.github(*%s)
        def test_foo():
            assert True

        @pytest.mark.github(*%s)
        def test_bar():
            assert True

        @pytest.mark.github(*%s)
        def test_baz():
            assert True
    """ % (closed_issues, open_issues, open_issues + closed_issues)
    # (items, result) = testdir.inline_genitems(src, *option.args)
    result = testdir.inline_runsource(src, *option.args + ['--github-summary'])
    assert_outcome(result)

    stdout, stderr = capsys.readouterr()
    assert 'collected %s github issues' % len(closed_issues + open_issues) in stdout
