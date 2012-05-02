#!/usr/bin/env jython

from __future__ import with_statement  # jython 2.5.2 issue
import logging
from plugins import __all__
from kahuna.session import ContextLoader
from contextlib import contextmanager

log = logging.getLogger('kahuna')


class PluginManager:
    """ Manages available plugins. """
    def __init__(self):
        """ Initialize the plugin list. """
        self.__plugins = {}

    def load_plugin(self, plugin_name):
        """ Loads a single plugin given its name. """
        if not plugin_name in __all__:
            raise KeyError("Plugin " + plugin_name + " not found")
        try:
            plugin = self.__plugins[plugin_name]
        except KeyError:
            # Load the plugin only if not loaded yet
            log.debug("Loading plugin: %s" % plugin_name)
            module = __import__("plugins." + plugin_name, fromlist=["plugins"])
            plugin = module.load()
            self.__plugins[plugin_name] = plugin
        return plugin

    def call(self, plugin_name, command_name, args):
        """ Encapsulate the call into a context already loaded.
        """
        with opencontext() as context:
            return self._call(context, plugin_name, command_name, args)

    def _call(self, context, plugin_name, command_name, args):
        """ Calls the given command on the given plugin. """
        try:
            plugin = self.load_plugin(plugin_name)
            plugin._load_context(context)
            if not command_name:
                self.help(plugin)
            else:
                try:
                    command = plugin._commands()[command_name]
                    return command(args)
                except KeyError:
                    # Command not found in plugin. Print only plugin help
                    self.help(plugin)
        except KeyError:
            # Plugin not found, pring generic help
            self.help_all()

    def help(self, plugin):
        """ Prints the help for the given plugin. """
        commands = plugin._commands()
        tokens = plugin.__module__.split('.')
        plugin_name = tokens[len(tokens) - 1]
        print "%s" % plugin.__doc__
        for command in sorted(commands.iterkeys()):
            print "   %s %s\t%s" % (plugin_name, command,
                    commands[command].__doc__)

    def help_all(self):
        """ Prints the help for all registered plugins. """
        for name in sorted(__all__):
            plugin = self.load_plugin(name)
            self.help(plugin)
            print


@contextmanager
def opencontext():
    """ Loads the context each plugin needs to be initialized
    in order to be executed. """
    log.debug("Loading context for plugin execution")
    context = ContextLoader().load()
    yield context
    log.debug("Context closed after plugin execution")
    context.close()
