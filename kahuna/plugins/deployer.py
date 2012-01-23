#!/usr/bin/env jython

import time
from optparse import OptionParser

from kahuna.session import ContextLoader


class DeployerPlugin:
    """ Massive deployer plugin. """
    def __init__(self):
        pass

    def info(self):
        """ Returns the plugin information. """
        info = {}
        info['name'] = "deployer"
        info['description'] = "Massive virtual machine deployer"
        return info

    def commands(self):
        """ Returns the available commands for this plugin. """
        commands = {}
        commands['start'] = self.start
        return commands

    def start(self, args):
        """ Deploys and undeploys the first virtual appliance N times. """
        # Parse user input to get the number of deployments and undeployments
        parser = OptionParser(usage="deployer start <options>")
        parser.add_option("-n", "--num", help="The number of deployments to execute", action="store", dest="num")
        (options, args) = parser.parse_args(args)
        if not options.num:
            parser.print_help()
            return

        # Once user input has been read, find the VM
        max = int(options.num)
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            monitor = context.getMonitoringService().getVirtualApplianceMonitor()

            vdc = cloud.listVirtualDatacenters()[0]
            vapp = vdc.listVirtualAppliances()[0]
            num_vms = len(vapp.listVirtualMachines())

            print "Starting %s deployment iterations for %s (%s vms)" % (max, vapp.getName(), num_vms)

            for i in range(0, max):
                print "Iteration #%s" % (i + 1)
                print "  Deploying %s (%s vms)" % (vapp.getName(), num_vms)
                vapp.deploy()
                monitor.awaitCompletionDeploy(vapp)

                # Bypass current issues with state by waiting a bit before undeploying
                time.sleep(5)

                print "  Undeploying %s (%s vms)" % (vapp.getName(), num_vms)
                vapp.undeploy()
                monitor.awaitCompletionUndeploy(vapp)

                # Currently there is a minor issue when undeploying that puts the vm in state
                # UNKNOWN. Wait a bit so it gets in NOT_ALLOCATED state before deploying again
                time.sleep(5)
        finally:
            context.close()

def load():
    """ Loads the deployer plugin. """
    return DeployerPlugin()

