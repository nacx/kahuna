#!/usr/bin/env jython


class AbsPlugin:
    """ Abstract plugin. """

    def load_context(self, context):
        """ Set the context of the execution.

        It should be called only from the plugin manager once
        it has the context loaded.
        """
        self._context = context
