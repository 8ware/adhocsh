#! /usr/bin/env python

from __future__ import print_function

import sys
from os.path import abspath, join, dirname
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from subprocess import check_output
from time import time


from bash import BashInterpreter


BASH_COMPLETION_TEMPLATE = """
        COMP_WORDS=( "{}" )
        COMP_CWORD={}
        {}
        for match in "${{COMPREPLY[@]}}"; do
            echo "$match"
        done
"""

BENCHMARK_CONFIGURATIONS = {
        'git' : {
            'init' : [
                '/usr/share/bash-completion/bash_completion',
                '/usr/share/bash-completion/completions/git',
            ],
            'fcompletion' : '_git',
            'args' : [
                'git', 'log', '--na',
            ],
            'cword' : 2,
            'expected' : [
#               '--name-only ', '--name-status ',
                'HEAD ', 'ORIG_HEAD ', 'master ', 'origin/master ',
            ],
        },
}

RUNS = 1000


interpreter = BashInterpreter()


def init_persistently(files):
    for f in files:
        interpreter.send('source "{}"\n'.format(f))
    return ''

def exec_persistently(code):
    return interpreter.eval(code)

def init_independently(files):
    initialization = ''
    for f in files:
        initialization += 'source "{}"\n'.format(f)
    return initialization

def exec_independently(code):
#   with open('/dev/null', 'w') as devnull:
#       output = check_output([ 'bash', '-c', script ], stderr=devnull)
    return check_output([ 'bash', '-c', code ])[:-1], ''

def assert_equals(iteration, output, expected):
    expected_out = "\n".join(expected)
    if output != expected_out:
        print ("[{}] Expected output not received".format(iteration))
        print ("  Expected: {}".format(expected_out.replace("\n", "\\n")))
        print ("  Actual:   {}".format(output.replace("\n", "\\n")))

def print_result(duration):
    print ("Ran function {} times in {:.4f}s; this is {:.4f}ms on average.".format(
        RUNS, duration/RUNS*1000, duration/RUNS))

def print_conclusion(elapsed_persistently, elapsed_independently):
    print ("Persistent implementation is {:.0f}x faster than the independent one".format(
        float (elapsed_independently) / elapsed_persistently))

def benchmark(execution, initialization, target):
    init = BENCHMARK_CONFIGURATIONS[target]['init']
    fcompletion = BENCHMARK_CONFIGURATIONS[target]['fcompletion']
    args = BENCHMARK_CONFIGURATIONS[target]['args']
    cword = BENCHMARK_CONFIGURATIONS[target]['cword']
    expected = BENCHMARK_CONFIGURATIONS[target]['expected']

    code = initialization(init)
    code += BASH_COMPLETION_TEMPLATE.format('" "'.join(args), cword, fcompletion)

    elapsed = 0
    for i in range(RUNS):
        print ("{}/{} ({:.0f}%)".format(i,RUNS,i*100.0/RUNS), end="\r")
        sys.stdout.flush()
        start = time()
        stdout, stderr = execution(code)
        end = time()
        elapsed += end - start
        assert_equals(i, stdout, expected):
    print ("{}/{} (100%)".format(RUNS, RUNS))

    print_result(elapsed)


benchmark(exec_persistently, init_persistently, 'git')
benchmark(exec_independently, init_independently, 'git')

