# -*- coding: utf-8 -*-
import pytest
import mock


@pytest.mark.github('https://github.com/ansible/awx/issues/2061', ids=['a', 'd'])
@pytest.mark.parametrize("should_run", [False, True, True, False, True], ids=['a', 'b', 'c', 'd', 'e'])
def test_xfail_particular_parametrize_test_ids(should_run):
    if should_run is False:
        assert False, "This test should have been marked xfail"
