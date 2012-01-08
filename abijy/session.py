#!/usr/bin/env jython

import atexit

from abijy.constants import *
from java.lang import System
from java.util import Properties
from org.jclouds.abiquo import *


class ContextLoader:
    """ Sets the context to call Abiquo's API.

    This class must be the first one to be instantiated when we want to
    start a session with Abiquo's API. Just initialize it and call
    the method 'load_context()'.
    """

    def __init__(self):
        """ Sets the properties and context builders. """
        context_builder="org.jclouds.abiquo.AbiquoContextBuilder"
        props_builder="org.jclouds.abiquo.AbiquoPropertiesBuilder"
        System.setProperty("abiquo.contextbuilder", context_builder)
        System.setProperty("abiquo.propertiesbuilder", props_builder)
        self.__context = None

    def __del__(self):
        """ Closes the context before destroying. """
        if self.__context:
            self.__context.close()

    def load_context(self, endpoint=ABQ_ENDPOINT, user=ABQ_USER, password=ABQ_PASS):
        """ Creates and configures the context.

        If no parameters are given, the ABQ_ENDPOINT, ABQ_USER, ABQ_PASS
        constants from the 'constants.py' module will be used.
        """
        if not self.__context:     # Avoid loading the same context twice
            config = Properties()
            config.put("abiquo.endpoint", endpoint)
            self.__context = AbiquoContextFactory().createContext(user, password, config);
            atexit.register(self.__del__)  # Close context automatically when exiting
        return self.__context

