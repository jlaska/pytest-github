import pytest


pytest_plugins = 'pytester',


class PyTestOption(object):

    def __init__(self, config):
        self.config = config

    @property
    def args(self):
        args = list()
        args.append('-v')
#         if self.config.getoption('github_api_key') is not None:
#             args.append('--github-api-key')
#             args.append(self.config.getoption('github_api_key'))
#         if self.config.getoption('github_api_token') is not None:
#             args.append('--github-api-token')
#             args.append(self.config.getoption('github_api_token'))
#         for completed in self.config.getoption('github_completed'):
#             args.append('--github-completed')
#             args.append('"%s"' % completed)
        return args


@pytest.fixture()
def option(request):
    return PyTestOption(request.config)


@pytest.fixture()
def open_issues(request):
    return [
        'https://github.com/jlaska/open/issues/1',
        'https://github.com/jlaska/open/issues/2',
        'https://github.com/jlaska/open/issues/3',
    ]


@pytest.fixture()
def closed_issues(request):
    return [
        'https://github.com/jlaska/closed/issues/4',
        'https://github.com/jlaska/closed/issues/5',
        'https://github.com/jlaska/closed/issues/6',
    ]


def mock_github_issue_is_closed(self):
    '''Returns JSON representation of an github card.'''
    return True


@pytest.fixture(autouse=True)
def no_requests(request, monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture(autouse=True)
def monkeypatch_github3(request, monkeypatch):
    monkeypatch.setattr('github3.login', lambda x, y: FakeGitHub(x, y))


class FakeGitHub(object):
    def __init__(self, *args, **kwargs):
        pass

    def issue(self, username, repository, number):
        return FakeIssue(username, repository, number)


class FakeIssue(object):
    def __init__(self, *args, **kwargs):
        self.url = "https://github.com/{0}/{1}/issues/{2}".format(*args)
        self.title = 'Mock issue title'

    def is_closed(self):
        return 'closed' in self.url.lower() and True or False

    @property
    def state(self):
        if self.is_closed():
            return 'closed'
        else:
            return 'open'

    def labels(self):
        return []
