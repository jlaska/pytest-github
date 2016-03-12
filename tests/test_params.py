# -*- coding: utf-8 -*-
import pytest
import mock
from _pytest.main import EXIT_OK, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
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


def test_param_default_cfg(testdir):
    '''verifies pytest-github loads configuration from the default configuration file'''

    with mock.patch('os.path.isfile', return_value=True):
        with mock.patch('pytest_github.plugin.open', mock.mock_open(read_data=''), create=True) as mock_open:
            result = testdir.runpytest()

    # Assert py.test exit code
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # Assert mock open called on provided file
    mock_open.assert_called_once_with('github.yml', 'r')


def test_param_missing_cfg(testdir, recwarn):
    '''Verifies pytest-github handles when no github.yml is present.'''

    with mock.patch('os.path.isfile', return_value=False) as mock_isfile:
        result = testdir.runpytest()

    # Assert py.test exit code
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # Assert mock open called on provided file
    mock_isfile.assert_called_once_with('github.yml')

    # NOTE Disabled for now b/c recwarn sets warnings.simplefilter('default') so any
    # duplicate warnings are ignored.
    if False:
        # check that only one warning was raised
        assert len(recwarn) == 1
        # check that the category matches
        record = recwarn.pop(Warning)
        assert issubclass(record.category, Warning)
        # check that the message matches
        assert str(record.message) == "No github configuration file found matching: github.yml"


def test_param_empty_cfg(testdir, recwarn):
    '''Verifies pytest-github ignores --github-cfg files that contain bogus data'''

    # mock an empty github.yml
    content = ''

    with mock.patch('os.path.isfile', return_value=True) as mock_isfile:
        with mock.patch('pytest_github.plugin.open', mock.mock_open(read_data=content), create=True) as mock_open:
            with mock.patch('pytest_github.plugin.GitHubPytestPlugin') as mock_plugin:
                result = testdir.runpytest()

    # Assert py.test exit code
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # Assert mock isfile called
    mock_isfile.assert_called_once_with('github.yml')

    # Assert mock open called on provided file
    mock_open.assert_called_once_with('github.yml', 'r')

    # Assert plugin initialized as expected
    mock_plugin.assert_called_once_with(None, None, completed_labels=[])

    # check that only one warning was raised
    assert len(recwarn) == 1
    # check that the category matches
    record = recwarn.pop(Warning)
    assert issubclass(record.category, Warning)
    # check that the message matches
    assert str(record.message).startswith("No github configuration found in file: ")


@pytest.mark.parametrize(
    "content",
    [
        # '',
        'github: {}',
        'github: []',
        'github:',
        'github: null',
        'github: 1',
        'github: "hi"',
    ]
)
def test_param_broken_cfg(testdir, content):
    '''verifies pytest-github loads completed info from provided --github-cfg parameter'''

    # create github.yml config for testing

    with mock.patch('os.path.isfile', return_value=True) as mock_isfile:
        with mock.patch('pytest_github.plugin.open', mock.mock_open(read_data=content), create=True) as mock_open:
            with mock.patch('pytest_github.plugin.GitHubPytestPlugin') as mock_plugin:
                result = testdir.runpytest()

    # Assert py.test exit code
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # Assert mock isfile called
    mock_isfile.assert_called_once_with('github.yml')

    # Assert mock open called on provided file
    mock_open.assert_called_once_with('github.yml', 'r')

    # Assert plugin initialized as expected
    mock_plugin.assert_called_once_with(None, None, completed_labels=[])


@pytest.mark.parametrize(
    "username,token,completed_labels",
    [
        ('montgomery', 'burns', ['label', 'other']),
        ('montgomery', 'burns', ['label']),
        ('montgomery', 'burns', ['']),
        ('montgomery', '', ['label']),
        ('', 'burns', ['label']),
    ],
)
def test_param_custom_cfg(testdir, username, token, completed_labels):
    '''verifies pytest-github loads completed info from provided --github-cfg parameter'''

    # create github.yml config for testing
    content = """\
    github:
        username: %s
        token: %s
        completed: %s
    """ % (repr(username), repr(token), repr(completed_labels))
    cfg_file = 'dummy.yml'

    with mock.patch('os.path.isfile', return_value=True) as mock_isfile:
        with mock.patch('pytest_github.plugin.open', mock.mock_open(read_data=content), create=True) as mock_open:
            with mock.patch('pytest_github.plugin.GitHubPytestPlugin') as mock_plugin:
                result = testdir.runpytest(*['--github-cfg', str(cfg_file)])

    # Assert py.test exit code
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # Assert mock isfile called
    mock_isfile.assert_called_once_with(str(cfg_file))

    # Assert mock open called on provided file
    mock_open.assert_called_once_with(str(cfg_file), 'r')

    # Assert plugin initialized as expected
    mock_plugin.assert_called_once_with(username, token, completed_labels=completed_labels)


def test_param_override_cfg(testdir):
    '''Verifies that pytest-github command-line parameters override values loaded from a config file.'''

    # create github.yml config for testing
    content = """\
    github:
        username: username
        token: token
        completed: [completed]
    """

    expected_username = 'montgomery'
    expected_token = 'burns'
    expected_completed = ['waylon', 'smithers']

    with mock.patch('os.path.isfile', return_value=True) as mock_isfile:
        with mock.patch('pytest_github.plugin.open', mock.mock_open(read_data=content), create=True) as mock_open:
            with mock.patch('pytest_github.plugin.GitHubPytestPlugin') as mock_plugin:
                # Build argument string
                args = [
                    '--github-username', expected_username,
                    '--github-token', expected_token,
                ]
                for c in expected_completed:
                    args.append('--github-completed')
                    args.append(c)

                # Run pytest
                result = testdir.runpytest(*args)

    # Assert py.test exit code
    assert result.ret == EXIT_NOTESTSCOLLECTED

    # Assert mock isfile called
    mock_isfile.assert_called_once_with('github.yml')

    # Assert mock open called on provided file
    mock_open.assert_called_once_with('github.yml', 'r')

    # Assert plugin initialized as expected
    mock_plugin.assert_called_once_with(
        expected_username,
        expected_token,
        completed_labels=expected_completed)


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


@pytest.mark.usefixtures('monkeypatch_github3')
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
