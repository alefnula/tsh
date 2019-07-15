# tee-shell

Tee shell is a set of utilities for running other applications.

It enables you to run shell commands in various modes and has an api for fine
tuning your running processes.


## Usage

```pycon
>>> import tsh
>>> ls = tsh.Command("ls")
>>> ls = ls.bake("-1")
>>> process = ls("tsh")
>>> process.wait()
True
>>> print(process.read())
__init__.py
__pycache__
command.py
consts.py
contexts.py
decorators.py
errors.py
process.py
shell.py
types.py
```
