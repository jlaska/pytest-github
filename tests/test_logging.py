# -*- coding: utf-8 -*-
import logging
from _pytest.main import EXIT_OK, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA


def assert_fnmatch_lines(output, matches):
    if isinstance(output, str):
        output = output.split('\n')
    missing = []
    for match in matches:
        if match not in output:
            missing.append(match)
    assert len(missing) == 0, "The following matches were not found:\n - %s" % '\n - '.join(missing)


def test_debug_logging(testdir, capsys):
    '''verifies pytest-github loads configuration from the default configuration file'''

    # setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create stderr StreamHandler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    # add handler to logger
    logger.addHandler(sh)

    src = """\
    def test_foo():
        pass
    """
    result = testdir.inline_runsource(src)

    # Assert py.test exit code
    assert result.ret == EXIT_OK

    (stdout, stderr) = capsys.readouterr()
    fnmatch_lines = [
        'DEBUG - pytest_cmdline_main() called',
        'DEBUG - pytest_configure() called',
        'DEBUG - GitHubPytestPlugin initialized',
        'DEBUG - pytest_runtest_setup() called',
    ]
    # Assert stderr logging
    assert_fnmatch_lines(stderr, fnmatch_lines)
