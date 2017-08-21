#! /usr/bin/env python

import sys
from os.path import abspath, join, dirname
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from subprocess import check_output
from time import time


from bash import BashInterpreter


BASH_COMPLETION_INIT = """
        source "/usr/share/bash-completion/completions/git"
"""

BASH_COMPLETION_SCRIPT = """
        COMP_WORDS=( "git" "log" "--na" )
        COMP_CWORD=2
        _git
        for match in "${COMPREPLY[@]}"; do
            echo "$match"
        done
"""

RUNS = 1000

interpreter = BashInterpreter()


def exec_persistently(code):
    return interpreter.eval(code)

def exec_independently(code):
#   with open('/dev/null', 'w') as devnull:
#       output = check_output([ 'bash', '-c', script ], stderr=devnull)
    return check_output([ 'bash', '-c', code ])[:-1], ''

def benchmark(function, code, expected):
    start = time()
    for i in range(RUNS):
        stdout, stderr = function(code)
        if stdout != expected:
            print ("Expected output not received")
            print ("Expected", expected)
            print ("Actual", stdout)
    end = time()

    duration = end - start
    average = duration/RUNS

    print ("Run function {} times in {}s; this is {}ms on average.".format(RUNS, duration, average*RUNS))


interpreter.send(BASH_COMPLETION_INIT)

benchmark(exec_persistently, BASH_COMPLETION_SCRIPT, '--name-only \n--name-status ')
benchmark(exec_independently, BASH_COMPLETION_INIT + "\n" + BASH_COMPLETION_SCRIPT,
        '--name-only \n--name-status ')

