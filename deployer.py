#!/usr/bin/env jython

import sys
import time

from kahuna.session import ContextLoader


if len(sys.argv) == 2:
    max = int(sys.argv[1])
    if max < 1:
        print "The number of deployments must be > 0"
        exit()

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
            time.sleep(10)

            print "  Undeploying %s (%s vms)" % (vapp.getName(), num_vms)
            vapp.undeploy()
            monitor.awaitCompletionUndeploy(vapp)

            # Currently there is a minor issue when undeploying that puts the vm in state
            # UNKNOWN. Wait a bit so it gets in NOT_ALLOCATED state before deploying again
            time.sleep(10)

    finally:
        context.close()
else:
    print "Usage: %s <number of deployments>" % sys.argv[0]
