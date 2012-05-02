#!/usr/bin/env jython

from environment.cloud.compute import cleanup_cloud_compute
from environment.cloud.compute import create_cloud_compute
from environment.cloud.storage import create_cloud_storage
from environment.config.sysconfig import apply_default_configuration
from environment.infrastructure.compute import cleanup_infrastructure_compute
from environment.infrastructure.compute import create_infrastructure_compute
from environment.infrastructure.network import create_infrastructure_network
from environment.infrastructure.storage import create_infrastructure_storage
from environment.users.tenants import cleanup_default_tenants
from environment.users.tenants import create_default_tenants
from kahuna.abstract import AbsPlugin
from kahuna.config import ConfigLoader
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException


class EnvironmentPlugin(AbsPlugin):
    """ Environment generator plugin """
    def __init__(self):
        self.__config = ConfigLoader().load("env.conf", "config/env.conf")

    def create(self, args):
        """ Creates the environment """
        try:
            apply_default_configuration(self.__config, self._context)
            dc = create_infrastructure_compute(self.__config, self._context)
            create_infrastructure_storage(self.__config, self._context, dc)
            create_infrastructure_network(self.__config, self._context, dc)
            create_default_tenants(self.__config, self._context, dc)
            vdc = create_cloud_compute(self.__config, self._context, dc)
            create_cloud_storage(self.__config, self._context, vdc)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def clean(self, args):
        """ Cleans up the environment """
        try:
            cleanup_cloud_compute(self.__config, self._context)
            cleanup_default_tenants(self.__config, self._context)
            cleanup_infrastructure_compute(self.__config, self._context)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the environment plugin """
    return EnvironmentPlugin()
