#!/usr/bin/env jython

from optparse import OptionParser
from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_tiers
from kahuna.utils.prettyprint import pprint_vdcs
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException


class VirtualDatacenterPlugin(AbsPlugin):
    """ Virtual datacenter plugin """

    def list(self, args):
        """ List all available virtual datacenters """
        try:
            cloud = self._context.getCloudService()
            vdcs = cloud.listVirtualDatacenters()
            pprint_vdcs(vdcs)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def tiers(self, args):
        """ List the tiers available in a virtual datacenter """
        parser = OptionParser(usage="vdc tiers <options>")
        parser.add_option("-n", "--name",
                help="The name of the virtual datacenter", dest="name")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the virtual datacenter
        try:
            cloud = self._context.getCloudService()
            vdc = cloud.findVirtualDatacenter(
                    VirtualDatacenterPredicates.name(name))
            if vdc:
                tiers = vdc.listStorageTiers()
                pprint_tiers(tiers)
            else:
                print "No virtual datacenter found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the current plugin """
    return VirtualDatacenterPlugin()
