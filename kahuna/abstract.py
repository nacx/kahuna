#!/usr/bin/env jython


class AbsPlugin:
    """ Abstract plugin. """
    def _commands(self):
        """ Get the list of commands for the current plugin.
        By default all public methods in the plugin implementation
        will be used as plugin commands. This method can be overriden
        in subclasses to customize the available command list. """
        attrs = filter(lambda attr: not attr.startswith('_'), dir(self))
        commands = {}
        for attr in attrs:
            method = getattr(self, attr)
            commands[attr] = method
        return commands

    def _load_context(self, context):
        """ Set the context of the execution.

        It should be called only from the plugin manager once
        it has the context loaded.
        """
        self._context = context
