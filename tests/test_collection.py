from _pytest.main import EXIT_OK


def test_collection_reporter_no_issues(testdir, option, capsys):
    '''verifies the github collection'''

    src = """
        import pytest
        def test_foo():
            assert True
    """
    result = testdir.inline_runsource(src, *option.args + ['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert "collected 0 github issues" in stdout


def test_collection_reporter_multiple_issues(testdir, option, capsys, closed_issues, open_issues):
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
    result = testdir.inline_runsource(src, *option.args + ['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert 'collected %s github issues' % len(closed_issues + open_issues) in stdout


def test_collection_reporter_duplicate_issues(testdir, option, capsys, closed_issues, open_issues):
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
    result = testdir.inline_runsource(src, *option.args + ['--collectonly'])
    assert result.ret == EXIT_OK

    stdout, stderr = capsys.readouterr()
    assert 'collected %s github issues' % (len(closed_issues) + len(open_issues)) in stdout
