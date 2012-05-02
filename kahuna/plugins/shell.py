#!/usr/bin/env jython
from kahuna.abstract import AbsPlugin

# Return code to make the wrapper script open a shell
EXIT_OPEN_SHELL = 10


class ShellPlugin(AbsPlugin):
    """ Interactive shell plugin. """
    def __init__(self):
        pass

    def open(self, args):
        """ Opens an interactive shell. """
        return EXIT_OPEN_SHELL


def load():
    """ Loads the current plugin. """
    return ShellPlugin()
