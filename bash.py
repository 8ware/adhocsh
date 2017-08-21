#! /usr/bin/env python

from os import O_NONBLOCK
from subprocess import Popen, PIPE
from fcntl import fcntl, F_SETFL
import time
import sys


class BashInterpreter(object):

    def __init__(self, delay = .03):
        self.delay = delay
        self.process = Popen([ 'bash' ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        fcntl(self.process.stdout.fileno(), F_SETFL, O_NONBLOCK)
        fcntl(self.process.stderr.fileno(), F_SETFL, O_NONBLOCK)

    def eval(self, code):
        self.send(code)
        time.sleep(self.delay)
        stdout = self.receive(self.process.stdout)
        stderr = self.receive(self.process.stderr)
        return stdout, stderr

    def send(self, code):
        self.process.stdin.write(code + "\n")
#       self.process.stdin.flush()

    def receive(self, channel):
        output = ''
        while True:
            try:
#               output += channel.readline()
                output += channel.read()
            except IOError:
                break
        return output.rstrip("\n")


if __name__ == '__main__':
    bash = BashInterpreter()
    while True:
        stdout, stderr = bash.eval(raw_input("bash> "))
        print ("OUT: " + stdout)
        print ("ERR: " + stderr)

