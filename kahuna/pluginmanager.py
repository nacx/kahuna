#!/usr/bin/env jython

from plugins import *
from plugins import __all__


class PluginManager:
    """ Manages available plugins. """
    def __init__(self):
        """ Initialize the plugin list. """
        self.__plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """ Loads all declared plugins in the plugins directory. """
        for name in __all__:
            plugin = eval(name).load()
            plugin_info = plugin.info()
            self.__plugins[plugin_info['name']] = plugin

    def call(self, plugin_name, command_name, args):
        """ Calls the given command on the given plugin. """
        try:
            plugin = self.__plugins[plugin_name]
            try:
                command = plugin.commands()[command_name]
                return command(args)
            except KeyError:
                # Command not found in plugin. Print only plugin help
                self.help(plugin)
        except KeyError:
            # Plugin not found, pring generic help
            self.help_all()

    def help(self, plugin):
        """ Prints the help for the given plugin. """
        info = plugin.info()
        commands = plugin.commands()
        print "%s usage:" % info['description']
        for name, callback in commands.iteritems():
            print "  %s %s\t%s" % (info['name'], name, callback.__doc__)

    def help_all(self):
        """ Prints the help for all registered plugins. """
        for name, plugin in sorted(self.__plugins.iteritems()):
            self.help(plugin)
            print

