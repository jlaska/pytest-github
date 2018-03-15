import os
import sys
import glob
import shutil
import codecs
from setuptools import setup, Command
from setuptools.command.test import test as TestCommand
from pytest_github import __doc__, __version__, __author__, __author_email__


class ToxTestCommand(TestCommand):

    """Test command which runs tox under the hood."""

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        """Initialize options and set their defaults."""
        TestCommand.initialize_options(self)
        self.tox_args = '--recreate'

    def finalize_options(self):
        """Add options to the test runner (tox)."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Invoke the test runner (tox)."""
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)


class CleanCommand(Command):
    description = "Custom clean command that forcefully removes dist/build directories"
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd

        # List of things to remove
        rm_list = list()

        # Find any .pyc files or __pycache__ dirs
        for root, dirs, files in os.walk(self.cwd, topdown=False):
            for fname in files:
                if fname.endswith('.pyc') and os.path.isfile(os.path.join(root, fname)):
                    rm_list.append(os.path.join(root, fname))
            if root.endswith('__pycache__'):
                rm_list.append(root)

        # Find egg's
        for egg_dir in glob.glob('*.egg') + glob.glob('*egg-info'):
            rm_list.append(egg_dir)

        # Zap!
        for rm in rm_list:
            if self.verbose:
                print("Removing '%s'" % rm)
            if os.path.isdir(rm):
                if not self.dry_run:
                    shutil.rmtree(rm)
            else:
                if not self.dry_run:
                    os.remove(rm)


dirname = os.path.dirname(__file__)


long_description = (
    codecs.open(os.path.join(dirname, "README.md"), encoding="utf-8").read() + "\n" +
    codecs.open(os.path.join(dirname, "HISTORY.md"), encoding="utf-8").read() + "\n"
)


setup(
    name="pytest-github",
    version=__version__,
    description=__doc__,
    # long_description=long_description,
    long_description_markdown_filename='README.md',
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jlaska/pytest-github',
    license='MIT',
    keywords='py.test pytest testing github issues',
    platforms='any',
    packages=['pytest_github'],
    include_package_data=True,
    entry_points={
        'pytest11': [
            'pytest-github = pytest_github.plugin'
        ],
    },
    # zip_safe=False,
    setup_requires=[
        'pypandoc',
        'setuptools-markdown'
    ],
    tests_requires=[
        'tox',
    ],
    install_requires=[
        'pytest',
        'PyYAML',
        'github3.py',
    ],
    cmdclass={
        'test': ToxTestCommand,
        'clean': CleanCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ] + [("Programming Language :: Python :: %s" % x) for x in "2.7 3.3 3.4 3.5".split()],
)
