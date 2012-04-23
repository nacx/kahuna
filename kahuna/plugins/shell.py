#!/usr/bin/env jython

# Return code to make the wrapper script open a shell
EXIT_OPEN_SHELL = 10


class ShellPlugin:
    """ Interactive shell plugin """
    def __init__(self):
        pass

    def commands(self):
        """ Returns the provided commands, mapped to handler methods """
        commands = {}
        commands['open'] = self.open
        return commands

    def open(self, args):
        """ Opens an interactive shell """
        return EXIT_OPEN_SHELL


def load():
    """ Loads the current plugin """
    return ShellPlugin()
