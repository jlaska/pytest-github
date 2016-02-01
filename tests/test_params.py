# -*- coding: utf-8 -*-
import pytest
import inspect
import exceptions
import re
from _pytest.main import EXIT_OK, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED


def assert_outcome(result, passed=0, failed=0, skipped=0, xpassed=0, xfailed=0):
    '''This method works around a limitation where pytester assertoutcome()
    doesn't support xpassed and xfailed.
    '''

    actual_count = dict(passed=0, failed=0, skipped=0, xpassed=0, xfailed=0)

    reports = filter(lambda x: hasattr(x, 'when'), result.getreports())
    for report in reports:
        if report.when == 'setup':
            if report.skipped:
                actual_count['skipped'] += 1
        elif report.when == 'call':
            if hasattr(report, 'wasxfail'):
                if report.failed:
                    actual_count['xpassed'] += 1
                elif report.skipped:
                    actual_count['xfailed'] += 1
            else:
                actual_count[report.outcome] += 1
        else:
            continue

    assert passed == actual_count['passed']
    assert failed == actual_count['failed']
    assert skipped == actual_count['skipped']
    assert xfailed == actual_count['xfailed']
    assert xpassed == actual_count['xpassed']


def test_plugin_help(testdir):
    '''Verifies expected output from of py.test --help'''

    result = testdir.runpytest('--help')
    result.stdout.fnmatch_lines([
		# Check for the github args section header
        'pytest-github:',
		# Check for the specific args
        '* --github-cfg=GITHUB_CFG',
        '* --github-username=GITHUB_USERNAME',
        '* --github-api-token=GITHUB_API_TOKEN',
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
		"--github-api-token",
		"--github-completed",
	],
	ids=[
		"--github-cfg",
		"--github-username",
		"--github-api-token",
		"--github-completed",
	],
)
def test_param_requires_value(testdir, option, monkeypatch_github, required_value_parameter):
    '''Verifies failure when not providing a value to a required parameter'''

    result = testdir.runpytest(*[required_value_parameter])
    assert result.ret == EXIT_INTERRUPTED
    result.stderr.fnmatch_lines([
        '*: error: argument %s: expected one argument' % required_value_parameter,
    ])


def test_param_github_cfg_with_no_such_file(testdir, option, monkeypatch_github, recwarn):
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


def test_param_github_cfg_containing_no_data(testdir, option, monkeypatch_github, recwarn):
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


def test_param_github_cfg(testdir, option, monkeypatch_github):
    '''verifies pytest-github loads completed info from provided --github-cfg parameter'''

    # create github.yml config for testing
    contents = '''
    github:
        username: ''
        token: ''
        completed:
            - 'not_done'
    '''
    cfg_file = testdir.makefile('.yml', contents)

    # the following would normally xpass, but when completed=['not_done'], it
    # will just pass
    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_func():
            assert true
        """ % OPEN_ISSUES[0]
    result = testdir.inline_runsource(src, *['--github-cfg', str(cfg_file)])
    assert result.ret == exit_ok
    assert_outcome(result, passed=1)


# def test_param_trello_api_key_without_value(testdir, option, monkeypatch_trello, capsys):
#     '''verifies failure when not passing --trello-api-key an option'''
# 
#     # run without parameter (expect fail)
#     result = testdir.runpytest(*['--trello-api-key'])
#     assert result.ret == 2
#     result.stderr.fnmatch_lines([
#         '*: error: argument --trello-api-key: expected one argument',
#     ])
# 
# 
# def test_param_trello_api_key_with_value(testdir, option, monkeypatch_trello, capsys):
#     '''verifies success when passing --trello-api-key an option'''
# 
#     result = testdir.runpytest(*['--trello-api-key', 'asdf'])
#     assert result.ret == exit_notestscollected
# 
#     # todo - would be good to assert some output
# 
# def test_param_trello_api_token_without_value(testdir, option, monkeypatch_trello, capsys):
#     '''verifies failure when not passing --trello-api-token an option'''
# 
#     result = testdir.runpytest(*['--trello-api-token'])
#     assert result.ret == 2
#     result.stderr.fnmatch_lines([
#         '*: error: argument --trello-api-token: expected one argument',
#     ])
# 
# 
# def test_param_trello_api_token_with_value(testdir, option, monkeypatch_trello, capsys):
#     '''verifies success when passing --trello-api-token an option'''
# 
#     result = testdir.runpytest(*['--trello-api-token', 'asdf'])
#     assert result.ret == exit_notestscollected
# 
#     # todo - would be good to assert some output
# 
# 
# def test_pass_without_trello_card(testdir, option):
#     '''verifies test success when no trello card is supplied'''
# 
#     testdir.makepyfile("""
#         import pytest
#         def test_func():
#             assert true
#         """)
#     result = testdir.runpytest(*option.args)
#     assert result.ret == exit_ok
#     assert result.parseoutcomes()['passed'] == 1
# 
# 
# def test_fail_without_trello_card(testdir, option):
#     '''verifies test failure when no trello card is supplied'''
# 
#     testdir.makepyfile("""
#         import pytest
#         def test_func():
#             assert false
#         """)
#     result = testdir.runpytest(*option.args)
#     assert result.ret == 1
#     assert result.parseoutcomes()['failed'] == 1
# 
# 
# def test_success_with_open_card(testdir, option, monkeypatch_trello):
#     '''verifies when a test succeeds with an open trello card'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello('%s')
#         def test_func():
#             assert true
#         """ % open_cards[0]
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == exit_ok
#     # assert result.parseoutcomes()['xpassed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, xpassed=1)
# 
# 
# def test_success_with_open_cards(testdir, option, monkeypatch_trello):
#     '''verifies when a test succeeds with open trello cards'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello(*%s)
#         def test_func():
#             assert true
#         """ % open_cards
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == exit_ok
#     # assert result.parseoutcomes()['xpassed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, xpassed=1)
# 
# 
# def test_failure_with_open_card(testdir, option, monkeypatch_trello):
#     '''verifies when a test fails with an open trello card'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello('%s')
#         def test_func():
#             assert false
#         """ % open_cards[0]
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == exit_ok
#     # assert result.parseoutcomes()['xfailed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, xfailed=1)
# 
# 
# def test_failure_with_open_cards(testdir, option, monkeypatch_trello):
#     '''verifies when a test fails with open trello cards'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello(*%s)
#         def test_func():
#             assert false
#         """ % open_cards
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == exit_ok
#     # assert result.parseoutcomes()['xfailed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, xfailed=1)
# 
# 
# def test_failure_with_closed_card(testdir, option, monkeypatch_trello):
#     '''verifies when a test fails with a closed trello card'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello('%s')
#         def test_func():
#             assert false
#         """ % closed_cards[0]
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == 1
#     # assert result.parseoutcomes()['failed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, failed=1)
# 
# 
# def test_failure_with_closed_cards(testdir, option, monkeypatch_trello):
#     '''verifies when a test fails with closed trello cards'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello(*%s)
#         def test_func():
#             assert false
#         """ % closed_cards
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == 1
#     # assert result.parseoutcomes()['failed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, failed=1)
# 
# 
# def test_failure_with_open_and_closed_cards(testdir, option, monkeypatch_trello):
#     '''verifies test failure with open and closed trello cards'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello(*%s)
#         def test_func():
#             assert false
#         """ % all_cards
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == exit_ok
#     # assert result.parseoutcomes()['xfailed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, xfailed=1)
# 
# 
# def test_skip_with_open_card(testdir, option, monkeypatch_trello):
#     '''verifies skipping with an open trello card'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello('%s', skip=true)
#         def test_func():
#             assert false
#         """ % open_cards[0]
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == exit_ok
#     # assert result.parseoutcomes()['skipped'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, skipped=1)
# 
# 
# def test_skip_with_closed_card(testdir, option, monkeypatch_trello):
#     '''verifies test failure (skip=true) with a closed trello card'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello('%s', skip=true)
#         def test_func():
#             assert false
#         """ % closed_cards[0]
#     # testdir.makepyfile(src)
#     # result = testdir.runpytest(*option.args)
#     # assert result.ret == 1
#     # assert result.parseoutcomes()['failed'] == 1
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, failed=1)
# 
# 
# def test_collection_reporter(testdir, option, monkeypatch_trello, capsys):
#     '''verifies trello marker collection'''
# 
#     src = """
#         import pytest
#         @pytest.mark.trello(*%s)
#         def test_foo():
#             assert true
# 
#         @pytest.mark.trello(*%s)
#         def test_bar():
#             assert false
#         """ % (closed_cards, open_cards)
#     # (items, result) = testdir.inline_genitems(src, *option.args)
#     result = testdir.inline_runsource(src, *option.args)
#     assert_outcome(result, passed=1, xfailed=1)
# 
#     stdout, stderr = capsys.readouterr()
#     assert 'collected %s trello markers' % (len(closed_cards) + len(open_cards)) in stdout
# 
# 
# def test_show_trello_report_with_no_cards(testdir, option, monkeypatch_trello, capsys):
#     '''verifies when a test succeeds with an open trello card'''
# 
#     src = """
#         import pytest
#         def test_func():
#             assert true
#         """
# 
#     # run pytest
#     args = option.args + ['--show-trello-cards',]
#     result = testdir.inline_runsource(src, *args)
# 
#     # assert exit code
#     assert result.ret == exit_ok
# 
#     # assert no tests ran
#     assert_outcome(result)
# 
#     # assert expected trello card report output
#     stdout, stderr = capsys.readouterr()
#     assert '= trello card report =' in stdout
#     assert 'no trello cards collected' in stdout
# 
# 
# def test_show_trello_report_with_cards(testdir, option, monkeypatch_trello, capsys):
#     '''verifies when a test succeeds with an open trello card'''
# 
#     # used for later introspection
#     cls = 'test_foo'
#     module = inspect.stack()[0][3]
#     method = 'test_func'
# 
#     src = """
#         import pytest
#         class test_class():
#             @pytest.mark.trello(*%s)
#             def test_method():
#                 assert true
# 
#         @pytest.mark.trello(*%s)
#         def test_func():
#             assert true
#         """ % (closed_cards, open_cards)
# 
#     # run pytest
#     args = option.args + ['--show-trello-cards',]
#     result = testdir.inline_runsource(src, *args)
# 
#     # assert exit code
#     assert result.ret == exit_ok
# 
#     # assert no tests ran
#     assert_outcome(result)
# 
#     # assert expected trello card report output
#     stdout, stderr = capsys.readouterr()
# 
#     # assert expected banner
#     assert re.search(r'^={1,} trello card report ={1,}', stdout, re.multiline)
# 
#     # assert expected cards in output
#     for card in closed_cards:
#         assert re.search(r'^%s \[done\]' % card, stdout, re.multiline)
#     for card in open_cards:
#         assert re.search(r'^%s \[not done\]' % card, stdout, re.multiline)
# 
#     # this is weird, oh well
#     assert ' * {0}0/{0}.py:test_class().test_method'.format(module) in stdout
#     assert ' * {0}0/{0}.py:test_func'.format(module) in stdout
