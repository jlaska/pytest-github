import pytest


pytest_plugins = 'pytester',


class PyTestOption(object):

    def __init__(self, config):
        self.config = config

    @property
    def args(self):
        args = list()
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


def mock_github_card_get(self, card_id, **kwargs):
    '''Returns JSON representation of an github card.'''
    if card_id.startswith("closed"):
        is_closed = True
    else:
        is_closed = False

    return {
        "labels": [],
        "pos": 33054719,
        "manualCoverAttachment": False,
        "badges": {},
        "id": "550c37c5226dd7241a61372f",
        "idBoard": "54aeece5d8b09a1947f34050",
        "idShort": 334,
        "shortUrl": "https://github.com/c/%s" % card_id,
        "closed": False,
        "email": "nospam@boards.github.com",
        "dateLastActivity": "2015-03-20T15:12:29.735Z",
        "idList": "%s53f20bbd90cfc68effae9544" % (is_closed and 'closed' or 'open'),
        "idLabels": [],
        "idMembers": [],
        "checkItemStates": [],
        "name": "mock github card - %s" % (is_closed and 'closed' or 'open'),
        "desc": "mock github card - %s" % (is_closed and 'closed' or 'open'),
        "descData": {},
        "url": "https://github.com/c/%s" % card_id,
        "idAttachmentCover": None,
        "idChecklists": []
    }


def mock_github_list_get(self, list_id, **kwargs):
    '''Returns JSON representation of a github list containing open cards.'''
    if list_id.startswith("closed"):
        is_closed = True
    else:
        is_closed = False

    return {
        "pos": 124927.75,
        "idBoard": "54aeece5d8b09a1947f34050",
        "id": list_id,
        "closed": False,
        "name": is_closed and "Done" or "Not Done"
    }


@pytest.fixture()
def monkeypatch_github(request, monkeypatch):
    monkeypatch.delattr("requests.get")
    monkeypatch.delattr("requests.sessions.Session.request")
    # FIXME
    # monkeypatch.setattr('github.cards.Cards.get', mock_github_card_get)
    # monkeypatch.setattr('github.lists.Lists.get', mock_github_list_get)
