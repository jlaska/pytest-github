# -*- coding: utf-8 -*-
import pytest
from _pytest.main import EXIT_OK


@pytest.mark.usefixtures('monkeypatch_github3')
def test_xfail_particular_parametrize_test_ids(testdir, capsys):
    src = """
import pytest
@pytest.mark.github('https://github.com/some/open/issues/1', ids=['even2', 'even4'])
@pytest.mark.parametrize("count", [1, 2, 3, 4], ids=["odd1", "even2", "odd3", "even4"])
def test_will_xfail(count):
    assert count % 2
    """
    result = testdir.inline_runsource(src)
    stdout, stderr = capsys.readouterr()
    assert '2 xfailed' in stdout
    assert '2 passed' in stdout
    assert result.ret == EXIT_OK
