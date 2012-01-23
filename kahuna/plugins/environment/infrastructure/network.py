#!/usr/bin/env jython

from kahuna.plugins.environment.constants import *
from org.jclouds.abiquo.domain.network import *
from org.jclouds.abiquo.predicates.enterprise import *


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

    def create_external_network(self, datacenter, enterprise, netname=EXT_NAME, netaddress=EXT_ADDRESS, netmask=EXT_MASK, netgateway=EXT_GATEWAY, nettag=EXT_TAG, netdns=EXT_DNS):
        """ Creates a new external network .  

        If the parameters are not specified, the 'EXT_NAME', 'EXT_ADDRESS',
        'EXT_MASK', 'EXT_GATEWAY', 'EXT_TAG', and 'EXT_DNS' variables from the
        'constants' module will be used.
        """
        print "Adding external network %s (%s) to enterprise %s..." % (netname, netaddress, enterprise.getName())
        network = ExternalNetwork.builder(self.__context, datacenter, enterprise) \
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
    """ Creates the default infrastructure network entities.
    
    Creates the default infrastructure network entities using the
    'constants' module properties.
    This is just an example of how to use this class.
    """
    print "### Configuring networking ###"
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name("Abiquo"))
    networking = InfrastructureNetwork(context)
    pubnet = networking.create_public_network(dc)
    external = networking.create_external_network(dc, enterprise)
    return pubnet

def cleanup_infrastructure_network(dc):
    """ Cleans up previously created infrastructure networking resources. """
    print "Removing networks in datacenter %s..." % dc.getName()
    for network in dc.listNetworks():
        network.delete()

