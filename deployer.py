#!/usr/bin/env jython

import sys

from kahuna.session import ContextLoader
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates


if len(sys.argv) == 2:
    max = int(sys.argv[1])
    context = ContextLoader().load_context()

    try:
        cloud = context.getCloudService()
        monitor = context.getMonitoringService()
        vms = cloud.listVirtualMachines()

        if len(vms) == 0:
            print "There are no virtual machines to deploy"
            exit()

        vm = vms[0]
        print "Starting %s deployments for: %s" % (max, vm.getName())

        for i in range(0, max):
            print "Deploying #%s %s" % (i + 1, vm.getName())
            vm.deploy()
            monitor.awaitCompletionDeploy(vm)

            print "Undeploying #%s %s" % (i + 1, vm.getName())
            vm.undeploy()
            monitor.awaitCompletionUndeploy(vm)

    finally:
        context.close()
else:
    print "Usage: %s <number of deployments>" % sys.argv[0]

