# -*- coding: utf-8 -*-
import pytest  # NOQA
import re  # NOQA
from _pytest.main import EXIT_OK, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
from . import assert_outcome  # NOQA


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
