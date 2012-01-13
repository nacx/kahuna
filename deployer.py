#!/usr/bin/env jython

import sys
import time

from kahuna.session import ContextLoader
from org.jclouds.abiquo.domain.cloud import VirtualMachine
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates


if len(sys.argv) == 2:
    max = int(sys.argv[1])
    if max < 1:
        print "The number of deployments must be > 0"
        exit()

    context = ContextLoader().load_context()

    try:
        cloud = context.getCloudService()
        monitor = context.getMonitoringService()
        vms = cloud.listVirtualMachines()

        if len(vms) == 0:
            print "There are no virtual machines to deploy"
            exit()

        vm = vms[0]
        print "Starting %s deployment iterations for %s" % (max, vm.getName())

        for i in range(0, max):
            print "Iteration #%s" % (i + 1)
            print "  Deploying %s" % vm.getName()
            vm.deploy()
            monitor.awaitCompletionDeploy(vm)

            print "  Undeploying %s" % vm.getName()
            vm.undeploy()
            monitor.awaitCompletionUndeploy(vm)

            # Currently there is a minor issue when undeploying that puts the vm in state
            # UNKNOWN. Wait a bit so it gets in NOT_ALLOCATED state before deploying again
            time.sleep(1)

    finally:
        context.close()
else:
    print "Usage: %s <number of deployments>" % sys.argv[0]

