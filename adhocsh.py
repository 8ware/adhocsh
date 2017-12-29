#! /usr/bin/env python

from __future__ import print_function

import sys
import readline
from os import environ, path, listdir, makedirs, getenv
from subprocess import call, check_output, Popen, PIPE
from optparse import OptionParser
import shlex
import re


HISTORY_BASE_DIR = getenv('XDG_CONFIG_HOME') + '/' + 'adhocsh'
HISTORY_PATH_TEMPLATE = HISTORY_BASE_DIR + '/{cmd:s}.history'

BASH_COMPLETION_DIR = '/usr/share/bash-completion/completions'

BASH_COMPLETION_SCRIPT_TEMPLATE = """
        # Source bash completion
        source "{completion_file:s}"

        # Prepare completion environment
        COMP_WORDS=( "{command:s}" "{quoted_args:s}" )
        COMP_CWORD={cword:d}

        # Execute completion
        {completion_function}

        # Print (return) completion results
        for match in "${{COMPREPLY[@]}}"; do
            echo "$match"
        done
"""


class AdHocShell(object):

    def __init__(self, command, completion, compfunc=None, default=None):
        self.command = command
        self.completion = completion
        self.completion_funcname = compfunc if compfunc else '_' + command
        self.default_subcommand = default
        self.history = HISTORY_PATH_TEMPLATE.format(cmd=command)

    def load_history(self):
        if path.exists(self.history):
            readline.read_history_file(self.history)

    def save_history(self):
        if not path.exists(path.dirname(self.history)):
            makedirs(path.dirname(self.history))
        readline.write_history_file(self.history)

    def get_prompt(self):
        prompt = self.command

        if self.command == 'git':
            script = 'source "{}"; __git_ps1 "{}@%s"'.format(
                    "/usr/lib/git-core/git-sh-prompt", self.command)
            prompt = check_output([ 'bash', '-c', script ])

        if self.command == 'task':
            context = check_output([ 'task', '_get', 'rc.context' ])[:-1]
            count = check_output([ 'task', 'rc.context:none',
                'rc.verbose:nothing', 'count', 'status:pending',
                'or', 'status:waiting' ])[:-1]
            info = '@' + context if context else ''
            info += '#' + count
            prompt = 'task{}'.format(info)

        return prompt + '> '

    def redraw_prompt(self, message):
        """
        Redraws the prompt after printing the given message.
        """
        print ("\r"+message)
        print (self.get_prompt()+readline.get_line_buffer(), end="")
        sys.stdout.flush()

    def complete(self, text, state):
        line = readline.get_line_buffer()
        args = line.split()
        if state == 0:  # On first trigger, build possible matches
            cword = len (args)
            # Try to complete next word (+1) if text is empty and separated
            # from the previous word by a whitespace
            cword += 0 if len (text) or len (line) and line[-1:] != ' ' else 1
            self.matches = self.get_bash_completion(args, cword)

            # Filter matches by prefix (necessary since docker completes both
            # container name and ID, e.g. docker stop ...)
            self.matches = filter (lambda m : m.startswith(text), self.matches)

            self.matches = map (lambda m : m + ('/' if path.isdir(m) else ''), self.matches)

            if not len (self.matches):
                self.matches = self.get_file_completion(text)

        if state >= len (self.matches):
            return None

        # Return match indexed by state
        match = self.matches[state]
        # Word Boundary Pattern
        wbp = re.compile('[ :=/]$') # See COMP_WORDBREAKS (git adds ':')
        if len (self.matches) == 1 and match and not wbp.search(match):
            match += ' '
        return match

    def display_matches(self, substitution, matches, longest_match_length):
        columns = int (environ.get("COLUMNS", 80))

        print ()

        tpl = "{:<" + str (int (max (map (len, matches)) * 1.2)) + "}"

        buffer = ""
        for match in matches:
            match = tpl.format(match)
            if len (buffer + match) > columns:
                print (buffer.strip())
                buffer = ""
            buffer += match

        self.redraw_prompt(buffer.strip())

    def get_bash_completion(self, args, cword):
        script = BASH_COMPLETION_SCRIPT_TEMPLATE.format(
                completion_file = self.completion,
                command = self.command, quoted_args = '" "'.join(args),
                cword = cword, completion_function = self.completion_funcname)

        completion = Popen([ 'bash', '-c', script ], stdout=PIPE, stderr=PIPE)
        stdout, stderr = completion.communicate()

        if stderr:
            self.redraw_prompt(stderr[:-1])

        matches = filter (None, stdout[:-1].split("\n"))

        return matches

    def get_file_completion(self, prefix):
        curdir = path.dirname(prefix)
        curfil = path.basename(prefix)
        filenames = []
        for entry in listdir(curdir or '.'):
            if entry.startswith(curfil):
                filepath = path.join(curdir, entry)
                if (path.isdir(filepath)):
                    filepath += '/'
                filenames.append(filepath)
        return filenames


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--default', action='store', dest='default', default=None)
    parser.add_option('-f', '--compfunc', action='store', dest='compfunc', default=None)
    parser.add_option('-D', '--no-default', action='store_false', dest='allow_default', default=True)
    parser.add_option('-c', '--completion', action='store', dest='completion')
    parser.add_option('-H', '--no-history', action='store_false', dest='enable_history', default=True)
    opts, args = parser.parse_args()

    command = args[0]
    completion = opts.completion if opts.completion else path.join(BASH_COMPLETION_DIR, command)

    shell = AdHocShell(command, completion, compfunc=opts.compfunc, default=opts.default)
    readline.set_completer_delims(' \t\n;:=')
    readline.set_completer(shell.complete)
    readline.parse_and_bind('tab: complete')
    readline.set_completion_display_matches_hook(shell.display_matches)

    print ("Ad-hoc shell for {}.".format(command))
    print ("Hit Ctrl-D to leave!")

    # Execute default command once at startup
    if opts.allow_default and opts.default:
        call([ shell.command, shell.default_subcommand ])

    if opts.enable_history:
        shell.load_history()

    while True:
        try:
            line = raw_input (shell.get_prompt())
            args = shlex.split(line)
            argc = len (args)
            if not argc and not opts.allow_default:
                continue
            if not argc and shell.default_subcommand:
                args = [ shell.default_subcommand ]
            full_command = [ shell.command ]
            full_command.extend(args)
            call(full_command)
        except ValueError as e:
            print ("Error: " + e.message)
        except KeyboardInterrupt:
            print ('^C')
        except EOFError:
            print ()
            if opts.enable_history:
                shell.save_history()
            break
