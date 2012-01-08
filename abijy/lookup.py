#!/usr/bin/env jython

from org.jclouds.abiquo.predicates.cloud import VirtualMachinePredicates
from org.jclouds.abiquo.predicates.infrastructure import MachinePredicates

class Lookup:
    """ Provides resource lookup features.
    
    This class provides complex lookup funtionality to
    find resources in the cloud
    """
    
    def __init__(self, context):
        """ Initialize with an existing context. """ 
        self.__context = context;

    def lookup_vm(self, name):
        """ Find a virtual machine given its name. """
        cloud = self.__context.getCloudService()
        vm = cloud.findVirtualMachine(VirtualMachinePredicates.name(name))
        if vm:
            print "Found virtual machine in: "
            print "  %s" % vm.getVirtualAppliance()
            print "  %s" % vm.getVirtualDatacenter()
            if vm.getVdrpIP():
                admin = self.__context.getAdministrationService()
                machine = admin.findMachine(MachinePredicates.ip(vm.getVdrpIP()))
                print "  %s" % machine
            else:
                print "  Machine: None (VM not deployed)"
        else:
            print "No virtual machine found with name: %s" % name
        
        print

        return vm

