#!/usr/bin/env jython

from environment.cloud.compute import cleanup_cloud_compute
from environment.cloud.compute import create_cloud_compute
from environment.cloud.storage import cleanup_cloud_storage
from environment.cloud.storage import create_cloud_storage
from environment.infrastructure.compute import cleanup_infrastructure_compute
from environment.infrastructure.compute import create_infrastructure_compute
from environment.infrastructure.network import create_infrastructure_network
from environment.infrastructure.storage import create_infrastructure_storage
from environment.users.tenants import cleanup_default_tenants
from environment.users.tenants import create_default_tenants
from kahuna.session import ContextLoader


class EnvironmentPlugin:
    """ Environment generator plugin. """
    def __init__(self):
        pass
    
    def info(self):
        """ Returns the plugin information. """
        info = {}
        info['name'] = "env"
        info['description'] = "Environment generator plugin"
        return info

    def commands(self):
        """ Returns the available commands in this plugin. """
        commands = {}
        commands['create'] = self.create
        commands['clean'] = self.cleanup
        return commands

    def create(self, args):
        """ Creates the environment. """
        context = ContextLoader().load_context("http://10.60.1.222/api", "admin", "xabiquo")
        try:
            dc = create_infrastructure_compute(context)
            create_infrastructure_storage(context, dc)
            create_infrastructure_network(context, dc)
            create_default_tenants(context, dc)
            vdc = create_cloud_compute(context, dc)
            create_cloud_storage(context, vdc)
        finally:
            context.close()

    def cleanup(self, args):
        """ Cleans up the environment. """
        context = ContextLoader().load_context("http://10.60.1.222/api", "admin", "xabiquo")
        try:
            cleanup_cloud_compute(context)
            cleanup_default_tenants(context)
            cleanup_infrastructure_compute(context)
        finally:
            context.close()
    
def load():
    """ Loads the environment plugin. """
    return EnvironmentPlugin()

