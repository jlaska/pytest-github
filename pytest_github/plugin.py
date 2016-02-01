import os
import logging
import yaml
import pytest
import py
import github3
import warnings
import requests.exceptions
from _pytest.python import getlocation
from _pytest.resultlog import generic_path

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler
    class NullHandler(Handler):
        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())

"""
pytest-github
~~~~~~~~~~~~

pytest-github is a plugin for py.test that allows tests to reference github
cards for skip/xfail handling.

:copyright: see LICENSE for details
:license: MIT, see LICENSE for more details.
"""

# Cache the github issues to reduce duplicate lookups
_issue_cache = {}

# Maintain a list of github labels to consider issues "finished".  Any issues
# associated with these labels will be considered "done".
GITHUB_COMPLETED_LABELS = []


def pytest_addoption(parser):
    '''Add options to control github integration.'''

    group = parser.getgroup('pytest-github')
    group.addoption('--github-cfg',
                    action='store',
                    dest='github_cfg_file',
                    default='github.yml',
                    metavar='GITHUB_CFG',
                    help='GitHub configuration file (default: %default)')
    group.addoption('--github-username',
                    action='store',
                    dest='github_username',
                    default=None,
                    metavar='GITHUB_USERNAME',
                    help='GitHub username (defaults to value supplied in GITHUB_CFG)')
    group.addoption('--github-api-token',
                    action='store',
                    dest='github_api_token',
                    metavar='GITHUB_API_TOKEN',
                    default=None,
                    help='GitHub Personal Access token (defaults to value ' \
                    'supplied in GITHUB_CFG). Refer to ' \
                    'https://github.com/blog/1509-personal-api-tokens')
    group.addoption('--github-completed',
                    action='append',
                    dest='github_completed',
                    metavar='GITHUB_COMPLETED',
                    default=[],
                    help='Any issues in GITHUB_COMPLETED will be treated as done (default: %s)' % GITHUB_COMPLETED_LABELS)
    group.addoption('--github-summary',
                    action='store_true',
                    dest='show_github_summary',
                    default=False,
                    help='Show a summary of all GitHub markers and their associated tests')

    # Add github marker to --help
    parser.addini("github", "GitHub issue integration", "args")


def pytest_configure(config):
    '''
    Validate --github-* parameters.
    '''
    log.debug("pytest_configure() called")

    # Add marker
    config.addinivalue_line("markers", "github(*args): GitHub issue integration")

    # Sanitize key and token
    github_cfg_file = config.getoption('github_cfg_file')
    github_username = config.getoption('github_username')
    github_api_token = config.getoption('github_api_token')
    github_completed = config.getoption('github_completed')

    # If not --help or --collectonly or --showfixtures ...
    if not (config.option.help or config.option.collectonly or config.option.showfixtures):
        # Warn if file does not exist
        if not os.path.isfile(github_cfg_file):
            errstr = "No github configuration file found matching: %s" % github_cfg_file
            log.warning(errstr)
            warnings.warn(errstr, Warning)

        # Load configuration file ...
        if os.path.isfile(github_cfg_file):
            github_cfg = yaml.load(open(github_cfg_file, 'r'))
            try:
                github_cfg = github_cfg.get('github', {})
            except AttributeError:
                github_cfg = {}
                errstr = "No github configuration found in file: %s" % github_cfg_file
                log.warning(errstr)
                warnings.warn(errstr, Warning)

            if github_username is None:
                github_username = github_cfg.get('key', None)
            if github_api_token is None:
                github_api_token = github_cfg.get('token', None)
            if github_completed is None or github_completed == []:
                github_completed = github_cfg.get('completed', [])

        # Initialize github api connection
        api = github3.login(github_username, github_api_token)

        # If completed is still empty, load default ...
        if github_completed is None or github_completed == []:
            github_completed = GITHUB_COMPLETED_LABELS

        # Register pytest plugin
        assert config.pluginmanager.register(
            GitHubPytestPlugin(api, completed_labels=github_completed),
            'github_helper'
        )


def pytest_cmdline_main(config):
    '''Check show_fixture_duplicates option to show fixture duplicates.'''
    log.debug("pytest_cmdline_main() called")
    if config.option.show_github_summary:
        from _pytest.main import wrap_session
        wrap_session(config, __show_github_summary)
        return 0


def __show_github_summary(config, session):
    '''Generate a report that includes all linked GitHub issues, and their status.'''
    session.perform_collect()
    curdir = py.path.local()

    github_helper = config.pluginmanager.getplugin("github_helper")

    card_cache = dict()
    for i, item in enumerate(filter(lambda i: i.get_marker("github") is not None, session.items)):
        cards = item.funcargs.get('cards', [])
        for card in cards:
            if card not in card_cache:
                card_cache[card] = list()
            card_cache[card].append(generic_path(item))

    reporter = config.pluginmanager.getplugin("terminalreporter")
    reporter.section("github card report")
    if card_cache:
        for card, gpaths in card_cache.items():
            reporter.write("{0} ".format(card.url), bold=True)
            reporter.write_line("[{0}] {1}".format(card.list.name, card.name))
            for gpath in gpaths:
                reporter.write_line(" * %s" % gpath)
    else:
        reporter.write_line("No github issues collected")


class GitHub_Issue(object):
    '''Object representing a github issue.
    '''

    def __init__(self, api, url):
        self.api = api
        self.url = url
        self._card = None

    @property
    def id(self):
        return os.path.basename(self.url)

    @property
    def card(self):
        if self._card is None:
            try:
                self._card = self.api.cards.get(self.id)
            except ValueError, e:
                log.warning("Failed to retrieve card:%s - %s" % (self.id, e))
                pass
        return self._card

    @property
    def name(self):
        return self.card['name']

    @property
    def idList(self):
        return self.card['idList']

    @property
    def list(self):
        return TrelloList(self.api, self.idList)


class TrelloList(object):
    '''Object representing a trello list.
    '''

    def __init__(self, api, id):
        self.api = api
        self.id = id
        self._list = None

    @property
    def name(self):
        if self._list is None:
            try:
                self._list = self.api.lists.get(self.id)
            except ValueError, e:
                log.warning("Failed to retrieve list:%s - %s" % (self.id, e))
                pass
        return self._list['name']


class TrelloCardList(object):
    '''Object representing a list of trello cards.'''
    def __init__(self, api, *cards, **kwargs):
        self.api = api
        self.cards = cards
        self.xfail = kwargs.get('xfail', True) and not ('skip' in kwargs)

    def __iter__(self):
        for card in self.cards:
            if card not in _card_cache:
                _card_cache[card] = GitHub_Issue(self.api, card)
            yield _card_cache[card]


class GitHubPytestPlugin(object):
    def __init__(self, api, **kwargs):
        log.debug("GitHubPytestPlugin initialized")
        self.api = api
        self.completed_labels = kwargs.get('completed_labels', [])

    def pytest_runtest_setup(self, item):
        log.debug("pytest_runtest_setup() called")
        if 'github' not in item.keywords:
            return

        incomplete_issues = []
        issues = item.funcargs["issues"]
        for issue in issues:
            try:
                if issue.list.name not in self.completed_labels:
                    incomplete_issues.append(issue)
            except requests.exceptions.HTTPError, e:
                log.warning("Error accessing issue:%s - %s" % (issue.id, e))
                continue

        # item.get_marker('github').kwargs
        if incomplete_issues:
            if issues.xfail:
                item.add_marker(pytest.mark.xfail(
                    reason="Xfailing due to incomplete github issues: \n{0}".format(
                        "\n ".join(["{0} [{1}] {2}".format(issue.url, issue.list.name, issue.name) for issue in incomplete_issues]))))
            else:
                pytest.skip("Skipping due to incomplete github issues:\n{0}".format(
                    "\n ".join(["{0} [{1}] {2}".format(issue.url, issue.list.name, issue.name) for issue in incomplete_issues])))

    def pytest_collection_modifyitems(self, session, config, items):
        log.debug("pytest_collection_modifyitems() called")
        reporter = config.pluginmanager.getplugin("terminalreporter")
        reporter.write("collected", bold=True)
        for i, item in enumerate(filter(lambda i: i.get_marker("github") is not None, items)):
            marker = item.get_marker('github')
            issues = tuple(sorted(set(marker.args)))  # (O_O) for caching
            for issue in issues:
                if issue not in _issue_cache:
                    _issue_cache[issue] = GitHub_Issue(self.api, issue)
            # FIXME - item.funcargs["cards"] = TrelloCardList(self.api, *cards, **marker.kwargs)
            item.funcargs["issues"] = ['FIXME',]
        reporter.write(" {0} github markers\n".format(len(_issue_cache)), bold=True)
