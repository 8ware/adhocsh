#! /usr/bin/env python

from os import O_NONBLOCK
from subprocess import Popen, PIPE
from fcntl import fcntl, F_SETFL
import time
import sys

from select import select


def wait_passively(channels, timeout = None):
    r,w,x = select(channels, [], [], timeout)
    return r

def wait_actively(channels, timeout = 0):
    r,w,x = [], [], []
    while not r:
        r,w,x = select(channels, [], [], timeout)
    return r

def read_naively(channel):
    output = ''
    while True:
        try:
#           output += channel.readline()
            output += channel.read()
        except IOError:
            break
    return output.rstrip("\n")

def read_carefully(channel):
    output = ''
    while wait_passively([ channel ], .000001):
        try:
#           output += channel.readline()
            output += channel.read()
        except IOError:
            # TODO Try break
            pass
    return output.rstrip("\n")

class BashInterpreter(object):

    def __init__(self, wait, timeout, read):
        self.wait = wait
        self.timeout = timeout
        self.read = read

        self.process = Popen([ 'bash' ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        fcntl(self.process.stdout.fileno(), F_SETFL, O_NONBLOCK)
        fcntl(self.process.stderr.fileno(), F_SETFL, O_NONBLOCK)

    def ready(self, timeout):
        return self.wait([ self.process.stdout, self.process.stderr ], timeout)

    def eval(self, code):
        if not code.strip():
            return '', ''

        self.send(code)

        ready = self.ready(self.timeout)

        stdout = self.receive(self.process.stdout, ready)
        stderr = self.receive(self.process.stderr, ready)

        return stdout, stderr

    def send(self, code):
        self.process.stdin.write(code + "\n")
#       self.process.stdin.flush()

    def receive(self, channel, ready):
        if not channel in ready:
            return ''
        return self.read(channel)


if __name__ == '__main__':
    bash = BashInterpreter(wait_passively, None, read_carefully)
    while True:
        stdout, stderr = bash.eval(raw_input("bash> "))
        print ("OUT: " + stdout)
        print ("ERR: " + stderr)

