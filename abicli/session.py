#!/usr/bin/env jython
from abicli.constants import *

from java.util import Properties
from org.jclouds.abiquo import *

class ContextLoader:
    """ Sets the context to call Abiquo's API.

    This class must be the first one to instantiate when we want to
    start a session with Abiquo's API. Just initialize it and call
    the method 'load_context()'.
    """

    def __init__(self):
        """ Just the constructor. """
        self.__context = None

    def load_context(self, endpoint=ABQ_ENDPOINT, user=ABQ_USER, password=ABQ_PASS):
        """ Loads the context for the connection.

        If no specify parameters it will use the ABQ_ENDPOINT, ABQ_USER, ABQ_PASS
        constants from the 'constants.py' module.
        """
        if not self.__context:     # avoid to load the same context two times...
            config = Properties()
            config.put("abiquo.endpoint", endpoint)
            self.__context = AbiquoContextFactory().createContext(user, password, config);
        return self.__context

