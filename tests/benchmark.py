#! /usr/bin/env python

from __future__ import print_function

import sys
from os.path import abspath, join, dirname
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from subprocess import check_output
from time import time


from bash import BashInterpreter, wait_passively, wait_actively, read_naively, read_carefully


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


# TODO Find best combination in terms of error rate and performance
interpreter = BashInterpreter(wait_passively, None, read_carefully)
#interpreter = BashInterpreter(wait_passively, None, read_naively)
#interpreter = BashInterpreter(wait_actively, 0, read_carefully)
#interpreter = BashInterpreter(wait_actively, 0, read_naively)


def init_stateful(files):
    for f in files:
        interpreter.send('source "{}"\n'.format(f))
    return ''

def exec_stateful(code):
    return interpreter.eval(code)

def init_stateless(files):
    initialization = ''
    for f in files:
        initialization += 'source "{}"\n'.format(f)
    return initialization

def exec_stateless(code):
#   with open('/dev/null', 'w') as devnull:
#       output = check_output([ 'bash', '-c', script ], stderr=devnull)
    return check_output([ 'bash', '-c', code ])[:-1], ''

def assert_equals(iteration, output, expected, verbose = False):
    expected_out = "\n".join(expected)
    if output != expected_out:
        if verbose:
            print ("[{}] Expected output not received".format(iteration))
            print ("  Expected: {}".format(expected_out.replace("\n", "\\n")))
            print ("  Actual:   {}".format(output.replace("\n", "\\n")))
        return False
    return True

def print_result(duration, errors):
    print ("Ran function {} times in {:.4f}s; this is {:.4f}ms on average.".format(
        RUNS, duration/RUNS*1000, duration/RUNS))
    print ("Encountered {} output errors ({:.2f}%).".format(errors, float (errors)*100/RUNS))

def print_conclusion(elapsed_stateful, elapsed_stateless):
    factor = float (elapsed_stateless) / elapsed_stateful
    adverb = 'faster'
    if factor < 1:
        factor = 1 / factor
        adverb = 'slower'
    print ("Stateful implementation is {:.0f}x {} than the stateless one".format(
        factor, adverb))

def benchmark(execution, initialization, target):
    init = BENCHMARK_CONFIGURATIONS[target]['init']
    fcompletion = BENCHMARK_CONFIGURATIONS[target]['fcompletion']
    args = BENCHMARK_CONFIGURATIONS[target]['args']
    cword = BENCHMARK_CONFIGURATIONS[target]['cword']
    expected = BENCHMARK_CONFIGURATIONS[target]['expected']

    code = initialization(init)
    code += BASH_COMPLETION_TEMPLATE.format('" "'.join(args), cword, fcompletion)

    elapsed = 0
    errors = 0
    for i in range(RUNS):
        print ("{}/{} ({:.0f}%)".format(i,RUNS,i*100.0/RUNS), end="\r")
        sys.stdout.flush()
        start = time()
        stdout, stderr = execution(code)
        end = time()
        elapsed += end - start
        if not assert_equals(i, stdout, expected):
            errors += 1
    print ("{}/{} (100%)".format(RUNS, RUNS))

    print_result(elapsed, errors)

    return elapsed

e1 = benchmark(exec_stateful, init_stateful, 'git')
e2 = benchmark(exec_stateless, init_stateless, 'git')

print_conclusion(e1, e2)

