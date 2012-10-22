#!/usr/bin/env jython

import atexit
import logging

from config import Config
from java.util import Properties
from org.jclouds import ContextBuilder
from org.jclouds.abiquo import AbiquoApiMetadata, AbiquoContext
from org.jclouds.logging.slf4j.config import SLF4JLoggingModule
from org.jclouds.sshj.config import SshjSshClientModule

log = logging.getLogger('kahuna')


class ContextLoader:
    """ Sets the context to call Abiquo's API.

    This class must be the first one to be instantiated when we want to
    start a session with Abiquo's API. Just initialize it and call the
    load() method.
    """

    def __init__(self, overrides=None):
        """ Sets the properties and context builders """
        self.__context = None
        self.__config = Config()
        if overrides:
            log.debug("Overriding default config values")
            for property in sorted(overrides.iterkeys()):
                setattr(self.__config, property, overrides[property])

    def __del__(self):
        """ Closes the context before destroying """
        if self.__context:
            log.debug("Disconnecting from %s" % self.__context. \
                    getApiContext().getEndpoint())
            self.__context.close()

    def load(self):
        """ Creates and configures the context """
        if not self.__context:     # Avoid loading the same context twice
            props = self._load_config()
            endpoint = "http://" + self.__config.address + "/api"
            log.debug("Connecting to %s as %s" % (endpoint,
                self.__config.user))
            self.__context = ContextBuilder.newBuilder(AbiquoApiMetadata()) \
                .endpoint(endpoint) \
                .credentials(self.__config.user, self.__config.password) \
                .modules([SshjSshClientModule(), SLF4JLoggingModule()]) \
                .overrides(props) \
                .buildView(AbiquoContext)
            # Close context automatically when exiting
            atexit.register(self.__del__)
            return self.__context

    def _load_config(self):
        """ Returns the default jclouds client configuration """
        props = Properties()
        [props.put(name, value)
                for (name, value) in self.__config.client_config]
        return props
