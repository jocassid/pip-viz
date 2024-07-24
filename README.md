It doesn't look like pip has an API (e.g. I can't do a `from pip import pip_list` and rock and roll) instead I've got to run pip subprocesses and parse through the `stdout`.
