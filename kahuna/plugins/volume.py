#!/usr/bin/env jython

from optparse import OptionParser
from kahuna.session import ContextLoader
from kahuna.utils.prettyprint import pprint_volumes
from org.jclouds.abiquo.predicates.cloud import VolumePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException

class VolumePlugin:
    """ Volume plugin. """
    def __init__(self):
        pass

    def commands(self):
        """ Returns the commands provided by the plugin, mapped to the handler methods. """
        commands = {}
        commands['list'] = self.list
        commands['find'] = self.find
        return commands

    def list(self, args):
        """ List all available volumes. """
        context = ContextLoader().load()
        try:
            cloud = context.getCloudService()
            vdcs = cloud.listVirtualDatacenters()
            volumes = []
            [volumes.extend(vdc.listVolumes()) for vdc in vdcs]
            pprint_volumes(volumes)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def find(self, args):
        """ Find an available volume given its name. """
        # Parse user input to get the name of the volume
        parser = OptionParser(usage="volume find <options>")
        parser.add_option("-n", "--name", help="The name of the volume to find", dest="name")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the volume
        context = ContextLoader().load()
        try:
            cloud = context.getCloudService()
            vdcs = cloud.listVirtualDatacenters()
            for vdc in vdcs:
                volume = vdc.findVolume(VolumePredicates.name(name))
                if volume:
                    break
            if volume:
                pprint_volumes([volume])
            else:
                print "No volume found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

def load():
    """ Loads the current plugin. """
    return VolumePlugin()

