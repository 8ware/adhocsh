
from os import path
import re


GUARD = '[ADHOCSH] '

# Log compopt usage on stderr to apply effects afterwards
# TODO Maybe communicate via sockets instead of stdout/stderr
BASH_COMPLETION_COMPOPT_REDIRECT = """
        # Replace non-working compopt
        compopt () {{
            echo "{guard:s}$*" >&2
        }}
""".format(guard=GUARD)

BASH_COMPLETION_COMPOPT_OPTIONS = {
        # Add trailing slash if directory, supress trailing space,
        # escape special characters (maybe not necessary in adhocsh?)
        'filenames' : lambda e : slash(escape(e))
}

def escape(filename):
    return filename.replace(' ', '\\ ')

def slash(filename):
    return filename + '/' if path.isdir(filename) else filename


def prepare(script):
    return BASH_COMPLETION_COMPOPT_REDIRECT + script

def parse(log):
    filter_hints = lambda l : l.startswith(GUARD)
    remove_prefix = lambda l : l[len (GUARD):]

    postprocessors = []
    for line in map (remove_prefix, filter (filter_hints, log.split("\n"))):
        for setting in re.findall('([+-])o\s+(\w+)', line):
            enable = setting[0] == '-'
            option = setting[1]
            if enable:
                postprocessors.append(BASH_COMPLETION_COMPOPT_OPTIONS[option])

    return postprocessors

def postprocess(matches, postprocessors):
    for postprocessor in postprocessors:
        matches = map (postprocessor, matches)

    return matches

