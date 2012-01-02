#!/usr/bin/env jython

from abicli.constants import *
from org.jclouds.abiquo.domain.network import *


class InfrastructureNetwork:
    """ Provides access to infrastructure network features.

    This class creates and manages the networking elements
    of the infrastructure that will be exposed as a cloud.
    """
    
    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_public_network(self, datacenter, netname=PN_NAME, netaddress=PN_ADDRESS, netmask=PN_MASK, netgateway=PN_GATEWAY, nettag=PN_TAG, netdns=PN_DNS):
        """ Creates a new public network .  

        If the parameters are not specified, the 'PN_NAME', 'PN_ADDRESS',
        'PN_MASK', 'PN_GATEWAY', 'PN_TAG', and 'PN_DNS' variables from the
        'constants' module will be used.
        """
        print "Adding public network %s (%s) to datacenter %s..." % (netname, netaddress, datacenter.getName())
        network = PublicNetwork.builder(self.__context, datacenter) \
                  .name(netname) \
                  .address(netaddress) \
                  .mask(netmask) \
                  .gateway(netgateway) \
                  .tag(nettag) \
                  .primaryDNS(netdns) \
                  .build()
        network.save()
        return network

def create_infrastructure_network(context, dc):
    """ Creates the standard infrastructure network entities.
    
    Creates the standard infrastructure network entities using the
    'constants' module properties.
    This is just an example of how to use this class.
    """
    print "### Configuring  networking ###"
    networking = InfrastructureNetwork(context)
    pubnet = networking.create_public_network(dc)
    return pubnet

def cleanup_infrastructure_network(dc):
    """ Cleans up previously created infrastructure networking resources. """
    print "### Cleaning up networking ###"
    for network in dc.listNetworks():
        print "Removing network %s (%s)..." % (network.getName(), network.getAddress())
        network.delete()

