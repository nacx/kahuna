#!/usr/bin/env jython

import logging
from optparse import OptionParser
from kahuna.session import ContextLoader
from kahuna.utils.prettyprint import pprint_vms
from virtualmachine import helper
from com.abiquo.model.enumerator import HypervisorType
from org.jclouds.abiquo.domain.cloud import VirtualAppliance
from org.jclouds.abiquo.domain.cloud import VirtualMachine
from org.jclouds.abiquo.predicates.cloud import VirtualAppliancePredicates
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.predicates.cloud import VirtualMachinePredicates
from org.jclouds.abiquo.predicates.cloud import VirtualMachineTemplatePredicates
from org.jclouds.abiquo.predicates.infrastructure import MachinePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException

log = logging.getLogger('kahuna')

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
        commands['create'] = self.create
        commands['delete'] = self.delete
        return commands

    def list(self, args):
        """ List all virtual machines. """
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            vms = cloud.listVirtualMachines()
            pprint_vms(vms)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def find(self, args):
        """ Find a virtual machine given its name. """
        # Parse user input to get the name of the virtual machine
        parser = OptionParser(usage="vm find <options>")
        parser.add_option("-n", "--name", help="The name of the virtual machine to find", dest="name")
        parser.add_option("-v", "--verbose", help="Show virtual machine extended information",
                action="store_true", dest="verbose")
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
                pprint_vms([vm])
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
        parser.add_option("-n", "--name", help="The name of the virtual machine to deploy", dest="name")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the VM
        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            vm = cloud.findVirtualMachine(VirtualMachinePredicates.name(name))
            if vm:
                vm = helper.deploy_vm(context, vm)
                pprint_vms([vm])
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
        parser.add_option("-n", "--name", help="The name of the virtual machine to undeploy", dest="name")
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
                vm = helper.undeploy_vm(context, vm)
                pprint_vms([vm])
            else:
                print "No virtual machine found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def create(self, args):
        """ Creates a virtual machine based on a given template. """
        # Parse user input to get the name of the virtual machine
        parser = OptionParser(usage="vm create <options>")
        parser.add_option("-t", "--template-id", help="The id of the template to use",
                type="int", dest="template")
        parser.add_option("-c", "--cpu", help="The number of cores", type="int", dest="cpu")
        parser.add_option("-r", "--ram", help="The RAM in MB", type="int", dest="ram")
        parser.add_option("-d", "--deploy", help="Deploy the virtual machine after creating it",
                action="store_true", dest="deploy")
        (options, args) = parser.parse_args(args)
        if not options.template:
            parser.print_help()
            return

        context = ContextLoader().load_context()
        try:
            template = helper.find_template_by_id(context, options.template)
            if not template:
                print "No template was found with id %s" % options.template
                return
            log.debug("Using template: %s" % template.getName())

            vdc = helper.find_compatible_virtual_datacenter(context, template)
            if not vdc:
                print "No virtual datacenter found for: %s" % template.getDiskFormatType()
                return
            log.debug("Using virtual datacenter: %s" % vdc.getName())

            name = "Kahuna-" + context.getIdentity()
            vapp = vdc.findVirtualAppliance(VirtualAppliancePredicates.name(name))
            if not vapp:
                log.debug("Virtual appliance %s not found. Creating it..." % name)
                vapp = VirtualAppliance.builder(context, vdc).name(name).build()
                vapp.save()

            builder = VirtualMachine.builder(context, vapp, template)
            if options.cpu:
                builder.cpu(options.cpu)
            if options.ram:
                builder.ram(options.ram)

            vm = builder.build()
            vm.save()

            if options.deploy:
                vm = helper.deploy_vm(context, vm)

            pprint_vms([vm])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def delete(self, args):
        """ Delete a virtual machine given its name. """
        # Parse user input to get the name of the virtual machine
        parser = OptionParser(usage="vm delete <options>")
        parser.add_option("-n", "--name", help="The name of the virtual machine to delete", dest="name")
        parser.add_option("-u", "--undeploy", help="undeploy the virtual machine before deleting it",
                action="store_true", dest="undeploy")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        context = ContextLoader().load_context()
        try:
            cloud = context.getCloudService()
            vm = cloud.findVirtualMachine(VirtualMachinePredicates.name(name))
            if vm:
                state = vm.getState()
                if not options.undeploy and state.existsInHypervisor():
                    print "Virtual machine is deployed. Undeploy it before deleting."
                elif options.undeploy and state.existsInHypervisor():
                    vm = helper.undeploy_vm(context, vm)
                    vm.delete()
                else:
                    vm.delete()
            else:
                print "No virtual machine found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

def load():
    """ Loads the current plugin. """
    return VmPlugin()

