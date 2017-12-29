
import testenv
from adhocsh import AdHocShell

import unittest


shell = AdHocShell('foo', None, None, None)

class CommandLineParserTest(unittest.TestCase):

    def testSingleton(self):
        #                             01234567890123
        setup = shell.get_comp_setup('add  doc/Comp ', 0, 3)
        self.assertEquals(setup, (['add', 'doc/Comp'], 0))

    def testRepeated(self):
        #                             0123456
        setup = shell.get_comp_setup('add add', 4, 7)
        self.assertEquals(setup, (['add', 'add'], 1))

    def testRepeatedTrailing(self):
        #                             0123456789012345678
        setup = shell.get_comp_setup('add        add  xxx', 11, 14)
        self.assertEquals(setup, (['add', 'add', 'xxx'], 1))

    def testRepeatedInbetween(self):
        #                             01234567890123
        setup = shell.get_comp_setup('add  xxx   add', 11, 14)
        self.assertEquals(setup, (['add', 'xxx', 'add'], 2))

    def testNextWord(self):
        #                             01234567890123
        setup = shell.get_comp_setup('add  doc/Comp ', 14, 14)
        self.assertEquals(setup, (['add', 'doc/Comp'], 2))


if __name__ == '__main__':
    unittest.main()

