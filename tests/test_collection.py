import pytest
from _pytest.main import EXIT_OK

pytestmark = pytest.mark.usefixtures("monkeypatch_github3")


def test_collection_reporter_no_issues(testdir, capsys):
    '''verifies the github collection'''

    src = """
        import pytest
        def test_foo():
            assert True
    """
    result = testdir.inline_runsource(src, *['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert "collected 0 github issues" in stdout


def test_collection_reporter_multiple_issues_one_per_test(testdir, capsys, closed_issues, open_issues):
    '''verifies the github collection when a single issue is used in the decorator'''

    src = """
        import pytest
        @pytest.mark.github('%s')
        def test_foo():
            assert True

        @pytest.mark.github('%s')
        def test_bar():
            assert True
    """ % (closed_issues[0], open_issues[0])
    result = testdir.inline_runsource(src, *['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert 'collected %s github issues' % 2 in stdout


def test_collection_with_issues_in_multiple_modules(testdir, capsys, closed_issues, open_issues):
    """verifies the github collection when multiple marked issues exist
    across more than one test module
    """
    template = '''
        import pytest
        @pytest.mark.github('{0}')
        def test_foo_fiz():
            assert True

        @pytest.mark.github('{1}')
        def test_foo_buz():
            assert True
    '''

    test_modules = {
        'test_foo': template.format(closed_issues[0], open_issues[0]),
        'test_bar': template.format(closed_issues[1], open_issues[1]),
    }

    testdir.makepyfile(**test_modules)
    
    result = testdir.runpytest_inprocess('--collectonly')
    stdout, stderr = capsys.readouterr()

    assert result.ret == EXIT_OK
    assert 'collected 4 github issues' in stdout


def test_collection_reporter_multiple_issues_per_test(testdir, capsys, closed_issues, open_issues):
    '''verifies the github collection'''

    src = """
        import pytest
        @pytest.mark.github(*%s)
        def test_foo():
            assert True

        @pytest.mark.github(*%s)
        def test_bar():
            assert True
    """ % (closed_issues, open_issues)
    result = testdir.inline_runsource(src, *['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert 'collected %s github issues' % len(closed_issues + open_issues) in stdout


def test_collection_reporter_duplicate_issues(testdir, capsys, closed_issues, open_issues):
    '''verifies the github collection'''

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
    result = testdir.inline_runsource(src, *['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert 'collected %s github issues' % (len(closed_issues) + len(open_issues)) in stdout
