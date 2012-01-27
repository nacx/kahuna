#!/usr/bin/env jython

import atexit

from config import Config
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
        self.__config = Config()

    def __del__(self):
        """ Closes the context before destroying. """
        if self.__context:
            self.__context.close()

    def load_context(self):
        """ Creates and configures the context. """
        if not self.__context:     # Avoid loading the same context twice
            endpoint = "http://" + self.__config.address + "/api"
            props = Properties()
            props.put("abiquo.endpoint", endpoint)
            props.put("jclouds.max-retries", "0")     # Do not retry on 5xx errors
            props.put("jclouds.max-redirects", "0")   # Do not follow redirects on 3xx responses
            # Wait at most 2 minutes in Machine discovery
            props.put("jclouds.timeouts.InfrastructureClient.discoverSingleMachine", "120000");
            props.put("jclouds.timeouts.InfrastructureClient.discoverMultipleMachines", "120000");
            print "Connecting to: %s" % endpoint
            self.__context = AbiquoContextFactory().createContext(self.__config.user,
                    self.__config.password, props);
            atexit.register(self.__del__)  # Close context automatically when exiting
        return self.__context

