#!/usr/bin/env jython

import atexit
import logging

from config import Config
from java.lang import System
from java.util import Properties
from com.google.common.collect import ImmutableSet
from org.jclouds.abiquo import AbiquoContextFactory
from org.jclouds.logging.config import NullLoggingModule

log = logging.getLogger('kahuna')


class ContextLoader:
    """ Sets the context to call Abiquo's API.

    This class must be the first one to be instantiated when we want to
    start a session with Abiquo's API. Just initialize it and call the
    load() method.
    """

    def __init__(self):
        """ Sets the properties and context builders """
        context_builder = "org.jclouds.abiquo.AbiquoContextBuilder"
        props_builder = "org.jclouds.abiquo.AbiquoPropertiesBuilder"
        System.setProperty("abiquo.contextbuilder", context_builder)
        System.setProperty("abiquo.propertiesbuilder", props_builder)
        self.__context = None
        self.__config = Config()

    def __del__(self):
        """ Closes the context before destroying """
        if self.__context:
            log.debug("Disconnecting from %s" % self.__context.getEndpoint())
            self.__context.close()

    def load(self):
        """ Creates and configures the context """
        if not self.__context:     # Avoid loading the same context twice
            props = self._load_config()
            log.debug("Connecting to %s as %s" %
                    (props.getProperty("abiquo.endpoint"),
                        self.__config.user))
            self.__context = AbiquoContextFactory().createContext(
                    self.__config.user, self.__config.password,
                    ImmutableSet.of(NullLoggingModule()), props)
            # Close context automatically when exiting
            atexit.register(self.__del__)
            return self.__context

    def _load_config(self):
        """ Returns the default jclouds client configuration """
        endpoint = "http://" + self.__config.address + "/api"
        props = Properties()
        props.put("abiquo.endpoint", endpoint)
        [props.put(name, value)
                for (name, value) in self.__config.client_config]
        return props
