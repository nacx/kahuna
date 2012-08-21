#!/usr/bin/env jython

import logging

log = logging.getLogger('kahuna')


class CloudNetwork:
    """ Provides access to cloud networking features """

    def purchase_public_ips(self, vdc, count):
        """ Purchases the given amount of public ips """
        available = vdc.listAvailablePublicIps()
        to_purchase = count if count < len(available) else len(available)

        log.info("Purchasing %s public ips for virtual datacenter %s..."
                % (to_purchase, vdc.getName()))

        for ip in available[:to_purchase]:
            vdc.purchasePublicIp(ip)


def setup_cloud_network(config, context, vdc):
    """ Configures the cloud networking resources """
    log.info("### Adding public ip addresses ###")
    network = CloudNetwork()
    network.purchase_public_ips(vdc, 5)
