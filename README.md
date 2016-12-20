# pytest-github

[![Build Status](https://img.shields.io/travis/jlaska/pytest-github.svg)](https://travis-ci.org/jlaska/pytest-github)
[![Coverage Status](https://img.shields.io/coveralls/jlaska/pytest-github.svg)](https://coveralls.io/r/jlaska/pytest-github)
[![Requirements Status](https://requires.io/github/jlaska/pytest-github/requirements.svg?branch=master)](https://requires.io/github/jlaska/pytest-github/requirements/?branch=master)
[![Version](https://img.shields.io/pypi/v/pytest-github.svg)](https://pypi.python.org/pypi/pytest-github/)
[![Downloads](https://img.shields.io/pypi/dm/pytest-github.svg)](https://pypi.python.org/pypi/pytest-github/)
[![License](https://img.shields.io/pypi/l/pytest-github.svg)](https://pypi.python.org/pypi/pytest-github/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/pytest-github.svg)](https://pypi.python.org/pypi/pytest-github/)

Plugin for py.test that integrates with github using markers.  Integration
allows tests to xfail (or skip) based on the status of linked github issues.

## Installation

Install the plugin using ``pip``

```bash
pip install pytest-github
```

## Usage

1. Once installed, the following ``py.test`` command-line parameters are available.

```bash
py.test \
	[--github-cfg=GITHUB_CFG] \
	[--github-username=GITHUB_USERNAME] \
	[--github-token=GITHUB_TOKEN] \
	[--github-completed=GITHUB_COMPLETED] \
	[--github-summary]
```

2. Next, create a configure file called ``github.yml`` that contains your GitHub username and [personal api token](https://github.com/blog/1509-personal-api-tokens).  A sample file is included below.

```yaml
github:
    username: j.doe
    token: XXXXXXXXXXXXX
```

### Marker

The following ``py.test`` marker is available:

```python
@pytest.mark.github(*args): GitHub issue integration
```

The marker can be used to influence the outcome of tests.  See the examples below for guidance.

### Example: xfail

Often, when a test fails, one might file a GitHub issue to track the resolution of the problem.  Alternatively, you could use the built-in ``xfail`` marker.  This is where ``pytest-github`` can be of use.  To avoid having to review known failures with each test run, and to avoid always using ``xfail``, consider the ``github`` marker to dynamically influence the test outcome based on the state of the GitHub issue.

The following example demonstrates using the ``github`` marker to influence the outcome of a known failing test.

```python
@pytest.mark.github('https://github.com/some/open/issues/1')
def test_will_xfail():
	assert False
```

Running this test with ``py.test`` will produce the following output:

```bash
test.py::test_will_xfail xfail
```

### Example: Anticipating specific exceptions with the 'raises' keyword

To avoid masking additional failures that might be uncovered by a test while a github issue is being resolved, you can restrict expected failures to specific exceptions using the `raises` keyword argument:


```python
@pytest.mark.github('https://github.com/some/open/issues/1', raises=ZeroDivisionError)
def test_will_xfail():
    foo = 1/0


@pytest.mark.github('https://github.com/some/open/issues/1', raises=ValueError)
def test_will_fail():
    # This test has been marked with an open issue but it will still fail
    # because the exception raised is different from the one indicated by
    # the 'raises' keyword.
    foo = 1/0
```

Running this test with ``py.test`` will produce the following output:

```bash
collected 2 items
collected 1 github issues

test.py::test_will_xfail xfail
test.py::test_will_fail FAILED
```


### Example: XPASS

The following example demonstrates a test that succeeds, despite being associated with an _open_ GitHub issue.

```python
@pytest.mark.github('https://github.com/some/open/issues/1')
def test_will_xpass():
    assert True
```

In this example, the ``XPASS`` outcome (a.k.a. unexpected pass) is used.

```
test.py::test_will_xpass XPASS
```

### Example: PASSED

The following example demonstrates a test that succeeds, while it is associated with a _closed_ GitHub issue.
When a test associated with a GitHub 
```python
@pytest.mark.github('https://github.com/some/closed/issues/2')
def test_will_pass():
    assert True
```

In this example, the ``PASSED`` outcome is used.
```
test.py::test_will_pass PASSED
```

### Example: FAILED

The following example demonstrates a test that fails, while it is associated with a _closed_ GitHub issue.

```python
@pytest.mark.github('https://github.com/some/closed/issues/2')
def test_will_fail():
    assert False
```

In this example, the ``FAILED`` outcome is used.

```
test.py::test_will_fail FAILED
```

### Example: SKIPPED

The following example demonstrates a test that fails, while it is associated with an _open_ GitHub issue.

```python
@pytest.mark.github('https://github.com/some/open/issues/1', skip=True)
def test_will_skip():
    assert False
```

In this example, the ``SKIPPED`` outcome is used.

```
test.py::test_will_skip SKIPPED
```

