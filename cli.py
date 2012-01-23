#!/usr/bin/env jython

from kahuna.pluginmanager import PluginManager


class CLI:
    """ Main command line interface. """
    def __init__(self):
        """ Initialize the main command line interface. """
        self.__pluginmanager = PluginManager()

    def run(self):
        """ Parses user input and calls the plugins. """
        self.__pluginmanager.load_plugins()

if __name__ == "__main__":
    cli = CLI()
    cli.run()

