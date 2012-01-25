#!/usr/bin/env jython

from optparse import OptionParser
from kahuna.session import ContextLoader
from org.jclouds.abiquo.predicates.cloud import VirtualMachinePredicates
from org.jclouds.abiquo.predicates.infrastructure import MachinePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException

class VmPlugin:
    """ Virtual machine plugin. """
    def __init__(self):
        pass

    def commands(self):
        """ Returns the commands provided by the plugin, mapped to the handler methods. """
        commands = {}
        commands['list'] = self.list
        commands['find'] = self.find
        commands['deploy'] = self.deploy
        commands['undeploy'] = self.undeploy
        return commands

    def list(self, args):
        """ List all virtual machines. """
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            vms = cloud.listVirtualMachines()
            print vms
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def find(self, args):
        """ Find a virtual machine given its name. """
        # Parse user input to get the name of the virtual machine
        parser = OptionParser(usage="vm find <options>")
        parser.add_option("-n", "--name", help="The name of the virtual machine to find", action="store", dest="name")
        parser.add_option("-v", "--verbose", help="Show virtual machine extended information", action="store_true", dest="verbose")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the virtual machine
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            vm = cloud.findVirtualMachine(VirtualMachinePredicates.name(name))
            if vm:
                if options.verbose:
                    print "Found virtual machine in: "
                    print "  %s" % vm.getVirtualAppliance()
                    print "  %s" % vm.getVirtualDatacenter()
                    print "  %s" % vm.getEnterprise()
                    if vm.getState().existsInHypervisor():
                        admin = context.getAdministrationService()
                        machine = admin.findMachine(MachinePredicates.ip(vm.getVncAddress()))
                        print "  %s" % machine
                    else:
                        print "  Machine [None (VM not deployed)]"
                print vm
            else:
                print "No virtual machine found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()
    
    def deploy(self, args):
        """ Deploy an existing virtual machine given its name. """
        # Parse user input to get the name of the virtual machine
        parser = OptionParser(usage="vm deploy <options>")
        parser.add_option("-n", "--name", help="The name of the virtual machine to deploy", action="store", dest="name")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the VM
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            monitor = context.getMonitoringService().getVirtualMachineMonitor()
            vm = cloud.findVirtualMachine(VirtualMachinePredicates.name(name))
            if vm:
                print "Deploying virtual machine %s... This may take some time." % name
                vm.deploy()
                monitor.awaitCompletionDeploy(vm)
            else:
                print "No virtual machine found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()
    
    def undeploy(self, args):
        """ Undeploy an existing virtual machine given its name. """
        # Parse user input to get the name of the virtual machine
        parser = OptionParser(usage="vm undeploy <options>")
        parser.add_option("-n", "--name", help="The name of the virtual machine to undeploy", action="store", dest="name")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the virtual machine 
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            monitor = context.getMonitoringService().getVirtualMachineMonitor()
            vm = cloud.findVirtualMachine(VirtualMachinePredicates.name(name))
            if vm:
                print "Uneploying virtual machine %s..." % name
                vm.undeploy()
                monitor.awaitCompletionUndeploy(vm)
            else:
                print "No virtual machine found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

def load():
    """ Loads the current plugin. """
    return VmPlugin()

