
adhocsh - An ad-hoc shell for subcommand-based CLI programs
===========================================================

Are you tired of always typing `git`? Do you curse 'cause `systemctl` is awful
to enter? Then this is for you! Start an ad-hoc shell and use subcommands as
first level commands.

```
$ adhocsh git -d status
git> <Enter> # Inspect status
git> diff README.md
git> add README.md
git> commit -m "Updated README"
git> push
```

