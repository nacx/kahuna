#!/usr/bin/env jython

import logging
from kahuna.session import ContextLoader

log = logging.getLogger('kahuna')


class AbsPlugin:
    """ Abstract plugin """
    def __init__(self):
        """ Initialized basic plugin stuff. """
        self._context = None

    def _commands(self):
        """ Get the list of commands for the current plugin.
        By default all public methods in the plugin implementation
        will be used as plugin commands. This method can be overriden
        in subclasses to customize the available command list """
        attrs = filter(lambda attr: not attr.startswith('_'), dir(self))
        commands = {}
        for attr in attrs:
            method = getattr(self, attr)
            commands[attr] = method
        return commands

    def _config_overrides(self):
        """ Custom properties to override default configuration """
        return {}

    def _load_context(self):
        """ Set the context of the execution.

        It should be called only from the plugin manager once
        it has the context loaded.
        """
        log.debug("Loading context for plugin execution")
        self._context = ContextLoader(self._config_overrides()).load()

    def _close_context(self):
        """ Closes the context after plugin execution.

        It should be called only from the plugin manager.
        """
        if self._context:
            log.debug("Context closed after plugin execution")
            self._context.close()
            self._context = None
