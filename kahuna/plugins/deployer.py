#!/usr/bin/env jython

import time
from optparse import OptionParser
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException
from kahuna.abstract import AbsPlugin


class DeployerPlugin(AbsPlugin):
    """ Massive deployer plugin. """
    def __init__(self):
        pass

    def start(self, args):
        """ Deploys and undeploys the first virtual appliance N times. """
        # Parse user input to get the number of deployments and undeployments
        parser = OptionParser(usage="deployer start <options>")
        parser.add_option("-n", "--num", dest="num",
                help="The number of deployments to execute")
        (options, args) = parser.parse_args(args)
        if not options.num:
            parser.print_help()
            return

        # Once user input has been read, find the VM
        max = int(options.num)
        try:
            cloud = self._context.getCloudService()
            monitor = self._context.getMonitoringService() \
                    .getVirtualApplianceMonitor()

            vdc = cloud.listVirtualDatacenters()[0]
            vapp = vdc.listVirtualAppliances()[0]
            num_vms = len(vapp.listVirtualMachines())

            print "Starting %s deployment iterations for %s (%s vms)" % (max,
                    vapp.getName(), num_vms)

            for i in range(0, max):
                print "Iteration #%s" % (i + 1)
                print "  Deploying %s (%s vms)" % (vapp.getName(), num_vms)
                vapp.deploy()
                monitor.awaitCompletionDeploy(vapp)

                # Bypass current issues with state by waiting a bit
                # before undeploying
                time.sleep(5)

                print "  Undeploying %s (%s vms)" % (vapp.getName(), num_vms)
                vapp.undeploy()
                monitor.awaitCompletionUndeploy(vapp)

                # Currently there is a minor issue when undeploying that puts
                # the vm in state UNKNOWN. Wait a bit so it gets in
                # NOT_ALLOCATED state before deploying again
                time.sleep(5)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the deployer plugin. """
    return DeployerPlugin()
