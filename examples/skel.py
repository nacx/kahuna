#!/usr/bin/env jython

# This is an example plugin that can be used as a
# skeleton for new plugins.
# To test it just rename it as desired, place it in the
# kahuna/plugins folder and run kahuna. You will see the
# new plugin in the help.

# The documentation string in the plugin class will be used to
# print the help of the plugin.

from kahuna.abstract import AbsPlugin


class SkeletonPlugin(AbsPlugin):
    """ An example plugin that prints dummy messages. """
    def __init__(self):
        pass

    # Public methods will be considered plugin commands.
    # The name of the command will be the method name.
    # The documentation string in command methods will be used to
    # print the help of the command.
    # The arguments are the options given to the command itself
    def dummy(self, args):
        """ Prints a dummy message. """
        print "This is the print_handler in the example plugin"


# Each plugin must provide a load method at module level that will be
# used to instantiate the plugin
def load():
    """ Loads the current plugin. """
    return SkeletonPlugin()
