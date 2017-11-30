#! /usr/bin/env python

from os import O_NONBLOCK
from subprocess import Popen, PIPE
from fcntl import fcntl, F_SETFL
import time
import sys

from select import select


def wait_passively(channels, timeout = None):
    """
    Waits until the given channels are ready for reading. If no timeout is
    given execution will be blocked passively, i.e. by the select function.

    Parameters
    ----------
    * channels (list): The file descriptors to wait for
    * timeout (float): The time to wait before continuing anyway (optional,
                       defaults to None which causes to wait infinitely)

    Discussion
    ----------
    * Uses the built-in waiting functionality which might be more precise
    * In constrast to `wait_actively` no CPU load is produced (?)
    """

    r,w,x = select(channels, [], [], timeout)
    return r

def wait_actively(channels, timeout = 0):
    """
    Waits until the given channels are ready for reading. If no timeout is
    given execution will be blocked actively, i.e. by an infinite while loop.

    Parameters
    ----------
    * channels (list): The file descriptors to wait for
    * timeout (float): The time to wait before continuing anyway (optional,
                       defaults to 0 which causes to wait not at all)

    Discussion
    ----------
    * Uses an infinite while loop to block functional call
    * In constrast to `wait_passively` CPU load is produced by the while loop
    """
    r,w,x = [], [], []
    while not r:
        r,w,x = select(channels, [], [], timeout)
    return r

# read_serve (does not excuse discontinuities)
def read_naively(channel):
    """
    Reads the given channel (i.e. file descriptor) until end indicated by an
    IOError, i.e. non-readiness of the channel.

    Parameters
    ----------
    * channel (int): The file descriptor to be read until end

    Discussion
    ----------
    * Aborts reading immediately if the channel does not provide more data
      thus might be stop reading too early if the data producer (i.e. the
      completion script) lacks for a short amount of time, e.g.
      ```sh
      echo "some completion item"
      do_some_computational_intense_stuff # sleep 1
      echo "some other item"
      ```
    """
    output = ''
    while True:
        try:
#           output += channel.readline()
            output += channel.read()
        except IOError:
            break
    return output.rstrip("\n")

# read_robustly (excuses discontinuities)
def read_carefully(channel):
    """
    Reads the given channel (i.e. file descriptor) until end indicated by the
    non-readiness of the channel. The read operation is assumed to be one
    self-contained continuous operation, i.e. the output to be read will be
    produced all at once w/o (temporal) discontinuation.

    Parameters
    ----------
    * channel (int): The file descriptor to be read until end

    Discussion
    ----------
    * Aborts if waiting for the channel's readiness fails, i.e. the channel is
      not ready anymore. Since the readiness check is carried out by using the
      `wait_passively` function very short discontinuations might be forgivable.
    """
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

