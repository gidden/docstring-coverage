# docstring-coverage

This is a fork of Alexey Strelkov's execellent tool on
[bitbucket](https://bitbucket.org/DataGreed/docstring-coverage) (pull requests
seem to be disabled)

# Usage

```
$ docstring-coverage -h
Usage: python coverage.py [options] <pythonsourcefile or directory>

Prints a rundown of the classes, functions, and methods in the given module
that have not been given a docstring.

Shows statistics on docstring coverage.


Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v LEVEL, --verbose=LEVEL
                        verbose level <0-3>, default 3
  -m, --nomagic         don't count docstrings for __magic__ methods
  -p, --noprivate       don't count docstrings for _private methods
  -l, --followlinks     follow symlinks
```
