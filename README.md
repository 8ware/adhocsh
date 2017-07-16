
adhocsh - An ad-hoc shell for subcommand-based CLI programs
===========================================================

Are you tired of always typing `git`? Do you curse 'cause `systemctl` is awful
to enter? Then this is for you! Start an ad-hoc shell and use subcommands as
first level commands.

Implementation
--------------

*There are two implementations: Bash and Python. Until a final decision is made
development of both implementations will be continued.*

### Bash

```
$ ADHOCSH_COMMAND=git \
  ADHOCSH_COMPLETION=/usr/share/bash-completion/completions/git \
  ADHOCSH_SUBCOMMANDS=$(
      source $ADHOCSH_COMPLETION
      __git_list_all_commands
  ) \
  bash --rcfile adhocrc
Ad-hoc shell for git.
Hit Ctrl-D to leave!
git> status
git> add README.md
git> commit -m "Updated README.md"
git> push
```
See `recipes/` for some examples.

### Python

```
$ adhocsh git -d status
git> <Enter> # Inspect status
git> diff README.md
git> add README.md
git> commit -m "Updated README"
git> push
```

