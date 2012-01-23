#!/usr/bin/env jython


class VmPlugin:
    """ Virtual machine plugin. """
    def __init__(self):
        pass

    def info(self):
        """ Get the information of the plugin. """
        info = {}
        info['name'] = "vm"
        info['description'] = "Virtual machine management features"
        return info

    def commands(self):
        """ Get the commands provided by the plugin, mapped to the handler methods. """
        commands = {}
        commands['list'] = self.list
        return commands

    def list(self, args):
        """ List all virtual machines. """
        print "Called plugin vm:list with args: %s" % args


def load():
    """ Loads the current plugin. """
    return VmPlugin()

