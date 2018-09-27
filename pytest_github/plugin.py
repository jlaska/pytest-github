"""Pytest-github is a py.test plugin to skip/xfail tests based on github issue status.

:copyright: see LICENSE for details
:license: MIT, see LICENSE for more details.
"""

import logging
import os
import re
import warnings
import yaml

import pytest
from _pytest.resultlog import generic_path
import github3

# Import, or define, NullHandler
try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        """No-op handler."""

        def emit(self, record):
            """Intentionally do nothing."""
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())

# Maintain a list of github labels to consider issues "finished".  Any issues
# associated with these labels will be considered "done".
GITHUB_COMPLETED_LABELS = []


def pytest_addoption(parser):
    """Add options to control github integration."""
    group = parser.getgroup('pytest-github')
    group.addoption('--github-cfg',
                    action='store',
                    dest='github_cfg_file',
                    default='github.yml',
                    metavar='GITHUB_CFG',
                    help='GitHub configuration file (default: %(default)s')
    group.addoption('--github-username',
                    action='store',
                    dest='github_username',
                    metavar='GITHUB_USERNAME',
                    help='GitHub username (defaults to value supplied in GITHUB_CFG)')
    group.addoption('--github-token',
                    action='store',
                    dest='github_token',
                    metavar='GITHUB_TOKEN',
                    help='GitHub Personal Access token (defaults to value ' +
                    'supplied in GITHUB_CFG). Refer to ' +
                    'https://github.com/blog/1509-personal-api-tokens')
    group.addoption('--github-completed',
                    action='append',
                    dest='github_completed',
                    metavar='GITHUB_COMPLETED',
                    default=[],
                    help='Any issues in GITHUB_COMPLETED will be treated as '
                    'done (default: %s)' % GITHUB_COMPLETED_LABELS)
    group.addoption('--github-summary',
                    action='store_true',
                    dest='show_github_summary',
                    default=False,
                    help='Show a summary of all GitHub markers and their associated tests')

    # Add github marker to --help
    parser.addini("github", "GitHub issue integration", "args")


def pytest_configure(config):
    """Validate --github-* parameters."""
    log.debug("pytest_configure() called")

    # Add marker
    config.addinivalue_line("markers", "github(*args): GitHub issue integration")

    # Initialize parameters
    github_cfg_file = config.getoption('github_cfg_file')
    github_username = None
    github_token = None
    github_completed = []

    # If not --help or --showfixtures ...
    if not (config.option.help or config.option.showfixtures or config.option.markers):
        # Load config file, if available
        if os.path.isfile(github_cfg_file):
            # Load configuration file ...
            with open(github_cfg_file, 'r') as fd:
                github_cfg = yaml.load(fd)

            if isinstance(github_cfg, dict) and 'github' in github_cfg and isinstance(github_cfg['github'], dict):
                github_username = github_cfg['github'].get('username', None)
                github_token = github_cfg['github'].get('token', None)
                github_completed = github_cfg['github'].get('completed', [])
            else:
                errstr = "No github configuration found in file: %s" % os.path.realpath(github_cfg_file)
                warnings.warn(errstr, Warning)

        # Override with command-line parameters
        if config.getoption('github_username'):
            github_username = config.getoption('github_username')
        if config.getoption('github_token'):
            github_token = config.getoption('github_token')
        if config.getoption('github_completed'):
            github_completed = config.getoption('github_completed')

        # Register pytest plugin
        assert config.pluginmanager.register(
            GitHubPytestPlugin(github_username, github_token, completed_labels=github_completed),
            'github_helper'
        )


def pytest_cmdline_main(config):
    """Check show_github_summary option to display all github fixtures."""
    log.debug("pytest_cmdline_main() called")
    if config.option.show_github_summary:
        from _pytest.main import wrap_session
        wrap_session(config, __show_github_summary)
        return 0


class IssueWrapper(object):
    
    def __init__(self, issue, gh_plugin):
        self.issue = issue
        self._gh_plugin = gh_plugin

    @property
    def is_closed(self):
        return self.issue.is_closed()

    @property
    def labels(self):
        try:
            labels = iter(self.issue.labels)
        except TypeError:  # github3.py 1.0.0+ uses instance method
            labels = self.issue.labels()
        return [l.name for l in labels]

    @property
    def is_resolved(self):
        # if the issue is open and isn't considered "completed" by any of the issue labels ...
        if not self.is_closed and not set(self._gh_plugin.completed_labels).intersection(self.labels):
            return False
        return True

    @property
    def html_url(self):
        return self.issue.html_url

    @property
    def state(self):
        return self.issue.state

    @property
    def title(self):
        return self.issue.title


def __show_github_summary(config, session):
    """Generate a report that includes all linked GitHub issues, and their status."""
    # collect tests
    session.perform_collect()

    issue_cache = config.pluginmanager.get_plugin('github_helper')._issue_cache

    # For each item, collect github markers and a generic_path for the item.
    unresolved_issue_map = dict()
    resolved_issue_map = dict()
    for item in filter(lambda i: i.get_marker("github") is not None, session.items):
        marker = item.get_marker('github')
        issue_urls = tuple(sorted(set(marker.args)))  # (O_O) for caching
        for issue_url in issue_urls:

            issue = issue_cache[issue_url]
            if not issue.is_resolved:
                if issue_url not in unresolved_issue_map:
                    unresolved_issue_map[issue_url] = list()
                unresolved_issue_map[issue_url].append(generic_path(item))
            if issue.is_resolved:
                if issue_url not in resolved_issue_map:
                    resolved_issue_map[issue_url] = list()
                resolved_issue_map[issue_url].append(generic_path(item))

    # Print a summary report
    reporter = config.pluginmanager.getplugin("terminalreporter")
    if reporter:
        reporter.section("github issue report")
        if unresolved_issue_map:
            reporter.write_line("Unresolved Issues", bold=True)
            for issue_url, gpaths in sorted(unresolved_issue_map.items(), key=lambda k: int(k[0].split('/')[-1])):
                reporter.write_line("{0}".format(issue_url), bold=True)
                for gpath in gpaths:
                    reporter.write_line(" - %s" % gpath)
        if resolved_issue_map:
            if unresolved_issue_map:
                reporter.write_line("")
            reporter.write_line("Resolved Issues", bold=True)
            for issue_url, gpaths in sorted(resolved_issue_map.items(), key=lambda k: int(k[0].split('/')[-1])):
                reporter.write_line("{0}".format(issue_url), bold=True)
                for gpath in gpaths:
                    reporter.write_line(" - %s" % gpath)
        if not unresolved_issue_map and not resolved_issue_map:
            reporter.write_line("No github issues collected")


class GitHubPytestPlugin(object):

    """GitHub Plugin class."""

    def __init__(self, username, password, completed_labels=GITHUB_COMPLETED_LABELS):
        """Initialize attributes."""
        log.debug("GitHubPytestPlugin initialized")

        # initialize issue cache
        self._issue_cache = {}

        # Process parameters
        self.username = username
        self.password = password
        self.completed_labels = completed_labels

        # Initialize github api connection
        self.api = github3.login(self.username, self.password)

    def __parse_issue_url(self, url):
        # Parse the github URL
        match = re.match(r'https?://github.com/([^/]+)/([^/]+)/(?:issues|pull)/([0-9]+)$', url)
        try:
            return match.groups()
        except AttributeError:
            errstr = "Malformed github issue URL: '%s'" % url
            raise Exception(errstr)


    def pytest_runtest_setup(self, item):
        """Handle github marker by calling xfail or skip, as needed."""
        log.debug("pytest_runtest_setup() called")
        if 'github' not in item.keywords:
            return

        github_marker = item.get_marker('github')

        '''
        github marker may specify ids=['foo', 'bar']. By specifying ids, only
        test cases that match those ids will be considered by github marker
        logic.
        '''
        github_marker_ids = github_marker.kwargs.get('ids', [])
        if github_marker_ids:
            param_marker = item.get_marker('parametrize')
            param_marker_ids = []
            if param_marker:
                param_marker_ids = param_marker.kwargs.get('ids', [])
            current_test_id = item.callspec.id

            if current_test_id not in github_marker_ids:
                return

        unresolved_issues = []
        issue_urls = item.funcargs["github_issues"]
        for issue_url in issue_urls:
            if issue_url not in self._issue_cache:
                continue
                # warnings.warn(errstr, Warning)

            issue = self._issue_cache[issue_url]
            if not issue.is_resolved:
                unresolved_issues.append(issue)

        if unresolved_issues:
            # TODO - Add support for skip vs xfail
            skip = item.get_marker('github').kwargs.get('skip', False)
            raises = item.get_marker('github').kwargs.get('raises')

            if skip:
                pytest.skip("Skipping due to unresolved github issues:\n{0}".format(
                    "\n ".join(["{0} [{1}] {2}".format(i.html_url, i.state, i.title) for i in unresolved_issues])))
            else:
                item.add_marker(pytest.mark.xfail(
                    reason="Xfailing due to unresolved github issues: \n{0}".format(
                        "\n ".join(["{0} [{1}] {2}".format(i.html_url, i.state, i.title) for i in unresolved_issues])),
                    raises=raises))

    def pytest_collection_modifyitems(self, session, config, items):
        """Report number of github issues collected."""
        reporter = config.pluginmanager.getplugin("terminalreporter")
        if reporter:
            reporter.write_line("collected {0} github issues".format(len(self._issue_cache)), bold=True)

    def pytest_itemcollected(self, item):
        """While collecting items, cache any github issues."""
        marker = item.get_closest_marker('github')

        if marker is not None and hasattr(item, 'funcargs'):
            issue_urls = tuple(sorted(set(marker.args)))  # (O_O) for caching
            for url in issue_urls:
                # add uncached issues to issue cache
                if url is not None and url not in self._issue_cache:
                    (username, repository, number) = self.__parse_issue_url(url)
                    try:
                        self._issue_cache[url] = IssueWrapper(self.api.issue(username, repository, number), self)
                    except (AttributeError, github3.exceptions.GitHubError) as e:
                        errstr = "Unable to inspect github issue %s - %s" % (url, str(e))
                        warnings.warn(errstr, Warning)

            item.funcargs["github_issues"] = issue_urls
