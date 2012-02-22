#!/usr/bin/env jython

import logging
from org.jclouds.abiquo.domain.network import ExternalNetwork
from org.jclouds.abiquo.domain.network import PublicNetwork
from org.jclouds.abiquo.predicates.enterprise import EnterprisePredicates

log = logging.getLogger('kahuna')


class InfrastructureNetwork:
    """ Provides access to infrastructure network features. """

    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_public_network(self, datacenter, netname, netaddress,
            netmask, netgateway, nettag, netdns):
        """ Creates a new public network . """
        log.info(("Adding public network %s (%s) to"
            "datacenter %s...") % (netname, netaddress, datacenter.getName()))
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

    def create_external_network(self, datacenter, enterprise, netname,
            netaddress, netmask, netgateway, nettag, netdns):
        """ Creates a new external network . """
        log.info(("Adding external network %s (%s) to "
            "enterprise %s...") % (netname, netaddress, enterprise.getName()))
        network = ExternalNetwork \
                  .builder(self.__context, datacenter, enterprise) \
                  .name(netname) \
                  .address(netaddress) \
                  .mask(netmask) \
                  .gateway(netgateway) \
                  .tag(nettag) \
                  .primaryDNS(netdns) \
                  .build()
        network.save()
        return network


def create_infrastructure_network(config, context, dc):
    """ Creates the default infrastructure network entities. """
    log.info("### Configuring networking ###")
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name("Abiquo"))
    networking = InfrastructureNetwork(context)
    pubnet = networking.create_public_network(dc,
            config.get("public network", "name"),
            config.get("public network", "address"),
            config.getint("public network", "mask"),
            config.get("public network", "gateway"),
            config.getint("public network", "tag"),
            config.get("public network", "dns"))
    networking.create_external_network(dc, enterprise,
            config.get("external network", "name"),
            config.get("external network", "address"),
            config.getint("external network", "mask"),
            config.get("external network", "gateway"),
            config.getint("external network", "tag"),
            config.get("external network", "dns"))
    return pubnet


def cleanup_infrastructure_network(config, dc):
    """ Cleans up previously created infrastructure networking resources. """
    log.info("Removing networks in datacenter %s..." % dc.getName())
    for network in dc.listNetworks():
        network.delete()
