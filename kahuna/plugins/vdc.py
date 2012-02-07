#!/usr/bin/env jython

from optparse import OptionParser
from kahuna.session import ContextLoader
from kahuna.utils.prettyprint import pprint_vdcs
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException

class VirtualDatacenterPlugin:
    """ Virtual datacenter plugin. """
    def __init__(self):
        pass

    def commands(self):
        """ Returns the commands provided by the plugin, mapped to the handler methods. """
        commands = {}
        commands['list'] = self.list
        commands['find'] = self.find
        return commands

    def list(self, args):
        """ List all available virtual datacenters. """
        context = ContextLoader().load()
        try:
            cloud = context.getCloudService()
            vdcs = cloud.listVirtualDatacenters()
            pprint_vdcs(vdcs)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def find(self, args):
        """ Find a virtual datacenter given its name. """
        # Parse user input to get the name of the virtual datacenter
        parser = OptionParser(usage="vdc find <options>")
        parser.add_option("-n", "--name",
                help="The name of the virtual datacenter to find", dest="name")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the virtual datacenter
        context = ContextLoader().load()
        try:
            cloud = context.getCloudService()
            vdc = cloud.findVirtualDatacenter(VirtualDatacenterPredicates.name(name))
            if vdc:
                pprint_vdcs([vdc])
            else:
                print "No virtual datacenter found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

def load():
    """ Loads the current plugin. """
    return VirtualDatacenterPlugin()

