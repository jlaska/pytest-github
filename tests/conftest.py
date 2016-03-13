import pytest


pytest_plugins = 'pytester',


@pytest.fixture()
def open_issues(request):
    return [
        'https://github.com/pytest-github/open/issues/1',
        'https://github.com/pytest-github/open/issues/2',
        'https://github.com/pytest-github/open/issues/3',
    ]


@pytest.fixture()
def closed_issues(request):
    return [
        'https://github.com/pytest-github/closed/issues/4',
        'https://github.com/pytest-github/closed/issues/5',
        'https://github.com/pytest-github/closed/issues/6',
    ]


@pytest.fixture(autouse=True)
def no_requests(request, monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture()
def monkeypatch_github3(request, monkeypatch):
    monkeypatch.setattr('github3.login', lambda x, y: FakeGitHub(x, y))


class FakeGitHub(object):
    def __init__(self, *args, **kwargs):
        self.username = args[0]
        self.password = args[1]

    def issue(self, username, repository, number):
        return FakeIssue(username, repository, number)


class FakeIssue(object):
    def __init__(self, *args, **kwargs):
        self.html_url = "https://github.com/{0}/{1}/issues/{2}".format(*args)
        self.title = 'Mock issue title'

    def is_closed(self):
        return 'closed' in self.html_url.lower() and True or False

    @property
    def state(self):
        if self.is_closed():
            return 'closed'
        else:
            return 'open'

    @property
    def labels(self):
        return [FakeLabel()]


class FakeLabel(object):
    def __init__(self, *args, **kwargs):
        self.name = 'state:Ready For Test'
