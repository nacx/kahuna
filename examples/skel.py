#!/usr/bin/env jython

# This is an example plugin that can be used as a
# skeleton for new plugins.

class SkeletonPlugin:
    """ An example plugin that prints dummy messages. """
    def __init__(self):
        pass

    def info(self):
        """ Returns the information of the plugin. """
        info = {}
        info['name'] = "example"  # The name to be used in the CLI
        info['description'] = "Example plugin" # A brief description
        return info

    def commands(self):
        """ Returns the commands provided by the plugin, mapped to the handler methods. """
        commands = {}
        # Bind the 'show' plugin command to the 'show_handler' method
        commands['print'] = self.print_handler
        return commands

    # The documentation string in command methods will be used to
    # print the help of the command.
    def print_handler(self, args):
        """ Prints a dummy message. """
        print "This is the print_handler in the example plugin"

# Each plugin must provide a load method at module level that will be
# used to instantiate the plugin
def load():
    """ Loads the current plugin. """
    return SkeletonPlugin()

