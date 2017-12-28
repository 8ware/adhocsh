
import sys
from os.path import abspath, join, dirname
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

# Maybe use pytest instead
import unittest
from adhocsh import AdHocShell

import os
from tempfile import mkdtemp


BASH_COMPLETION_DIR = '/usr/share/bash-completion/completions'


class CompletionTest(unittest.TestCase):

    def setUp(self):
        self.shell = AdHocShell('git', join(BASH_COMPLETION_DIR, 'git'),
                compfunc='_git', default=None)
        self.setup_testenv()

    def setup_testenv(self):
        self.tempdir = mkdtemp(prefix='adhocsh-test.')

        os.chdir(self.tempdir)
        os.makedirs('test/foo')

        open ('baz.file', 'a').close()
        open ('test/sample.file', 'a').close()
        open ('test/foo/bar.file', 'a').close()

    def tearDown(self):
        self.cleanup_testenv()

    def cleanup_testenv(self):
        os.remove('baz.file')
        os.remove('test/sample.file')
        os.remove('test/foo/bar.file')
        os.removedirs(self.tempdir+'/test/foo')


    def test_file_completion_current_dir(self):
        matches = self.shell.get_file_completion('b')
        self.assertEqual(matches, ['baz.file'])

    def test_file_completion_subdir(self):
        matches = self.shell.get_file_completion('test/sa')
        self.assertEqual(matches, ['test/sample.file'])

        matches = self.shell.get_file_completion('test/foo/b')
        self.assertEqual(matches, ['test/foo/bar.file'])

    def test_multi_completion_current_dir(self):
        matches = self.shell.get_file_completion('test/')
        self.assertEqual(matches, ['test/sample.file', 'test/foo/'])


if __name__ == '__main__':
    unittest.main()

