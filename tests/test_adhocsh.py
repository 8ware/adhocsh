
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

    def testQuoted(self):
        self.skipTest("Not implemented, yet")
        #                             012345678901234567890123456789
        setup = shell.get_comp_setup('add "s p a c e s.pdf" doc/Comp', 22, 30)
        self.assertEquals(setup, (['add', 's p a c e s.pdf', 'doc/Comp'], 2))

    def testEscaped(self):
        self.skipTest("Not implemented, yet")
        #                             012345678901234567890123456789012
        setup = shell.get_comp_setup('add s\ p\ a\ c\ e\ s.pdf doc/Comp', 25, 33)
        self.assertEquals(setup, (['add', 's p a c e s.pdf', 'doc/Comp'], 2))

    def testQuotedOpen(self):
        self.skipTest("Not implemented, yet")
        #                             0123456
        setup = shell.get_comp_setup('add "a ', 4, 7)
        self.assertEquals(setup, (['add', 'a '], 1))


if __name__ == '__main__':
    unittest.main()

