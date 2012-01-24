#!/usr/bin/env jython

from plugins import __all__

class PluginManager:
    """ Manages available plugins. """
    def __init__(self):
        """ Initialize the plugin list. """
        self.__plugins = {}
    
    def load_plugins(self):
        """ Loads all declared plugins in the plugins directory. """
        for name in __all__:
            self.load_plugin(name)

    def load_plugin(self, plugin_name):
        """ Loads a single plugin given its name. """
        if not plugin_name in __all__:
            raise KeyError("Plugin " + plugin_name + " not found")
        try:
            plugin = self.__plugins[plugin_name]
        except KeyError:
            # Load the plugin only if not loaded yet
            module = __import__("plugins." + plugin_name, fromlist=["plugins"])
            plugin = module.load()
            self.__plugins[plugin_name] = plugin
        return plugin

    def call(self, plugin_name, command_name, args):
        """ Calls the given command on the given plugin. """
        try:
            plugin = self.load_plugin(plugin_name)
            if not command_name:
                self.help(plugin)
            else:
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
        commands = plugin.commands()
        tokens = plugin.__module__.split('.')
        plugin_name = tokens[len(tokens) - 1]
        print "%s" % plugin.__doc__
        for command, callback in commands.iteritems():
            print "   %s %s\t%s" % (plugin_name, command, callback.__doc__)

    def help_all(self):
        """ Prints the help for all registered plugins. """
        self.load_plugins()
        for name, plugin in sorted(self.__plugins.iteritems()):
            self.help(plugin)
            print

