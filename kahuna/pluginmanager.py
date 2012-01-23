#!/usr/bin/env jython

from plugins import *
from plugins import __all__


class PluginManager:
    """ Manages available CLI plugins. """
    def __init__(self):
        pass
    
    def load_plugins(self):
        """ Loads the plugins in the given OptionParser. """
        for name in __all__:
            plugin = eval(name).load()
            plugin_info = plugin.info()
            print "Loaded %s plugin: %s" % (plugin_info['name'], plugin_info['description'])
            plugin.call()

