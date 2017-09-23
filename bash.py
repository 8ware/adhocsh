#! /usr/bin/env python

from os import O_NONBLOCK
from subprocess import Popen, PIPE
from fcntl import fcntl, F_SETFL
import time
import sys

from select import select


class BashInterpreter(object):

    def __init__(self):
        self.process = Popen([ 'bash' ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        fcntl(self.process.stdout.fileno(), F_SETFL, O_NONBLOCK)
        fcntl(self.process.stderr.fileno(), F_SETFL, O_NONBLOCK)

    def ready(self, timeout = None):
        r,w,x = select([ self.process.stdout, self.process.stderr ], [], [], timeout)
        return len (r)

    def eval(self, code):
        if not code.strip():
            return '', ''

        self.send(code)

        self.ready()

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

