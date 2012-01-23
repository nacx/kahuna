#!/usr/bin/env jython


class VmPlugin:
    """ Virtual machine plugin. """
    def __init__(self):
        pass

    def info(self):
        """ Get the information of the plugin. """
        return {'name': 'vm', 'description': 'Virtual machine management features'}

    def call(self):
        """ Invoke plugin methods to handle user requests. """
        print "Called vm plugin"


def load():
    """ Loads the current plugin. """
    return VmPlugin()

