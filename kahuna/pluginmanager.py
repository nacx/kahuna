#!/usr/bin/env jython

from plugins import *
from plugins import __all__


class PluginManager:
    """ Manages available plugins. """
    def __init__(self):
        """ Initialize the plugin list. """
        self.__plugins = {}
    
    def load_plugins(self):
        """ Loads all declared plugins in the plugins directory. """
        for name in __all__:
            plugin = eval(name).load()
            plugin_info = plugin.info()
            self.__plugins[plugin_info['name']] = plugin

    def call(self, plugin_name, command, *args):
        """ Calls the given command on the given plugin. """
        plugin = self.__plugins[plugin_name]
        command = plugin.commands()[command]
        command(args)

