
adhocsh - An ad-hoc shell for subcommand-based CLI programs
===========================================================

Are you tired of always typing `git`? Do you curse 'cause `systemctl` is awful
to enter? Then this is for you! Start an ad-hoc shell and use subcommands as
first level commands.

```
$ adhocsh git -d 'status --column .'
git> <Enter> # Inspect status
git> diff README.md
git> add README.md
git> commit -m "Updated README"
git> push
```

The default (sub)command can consist of multiple arguments which have to be
enquoted. Alternatively, an alias can be used.


Dependencies
------------

* Bash completion, e. g. `bash-completion` for Debian
* Python packges: see `requirements.txt`

