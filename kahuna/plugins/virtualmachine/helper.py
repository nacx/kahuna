#!/usr/bin/env jython

from com.abiquo.model.enumerator import HypervisorType
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.predicates.cloud import VirtualMachineTemplatePredicates

def find_template_by_id(context, id):
    """ Find a template given its id. """
    admin = context.getAdministrationService()
    user = admin.getCurrentUserInfo()
    enterprise = user.getEnterprise()
    return enterprise.findTemplate(VirtualMachineTemplatePredicates.id(id))

def find_compatible_virtual_datacenter(context, template):
    """ Find a virtual datacenter compatible with the given template. """
    template_type = template.getDiskFormatType()
    cloud = context.getCloudService()
    for type in HypervisorType.values():
        if type.isCompatible(template_type):
            vdc = cloud.findVirtualDatacenter(VirtualDatacenterPredicates.type(type))
            if vdc:
                return vdc
def refresh_vm(context, vm):
    """ Refresh the given virtual machine. """
    vapp = vm.getVirtualAppliance()
    return vapp.getVirtualMachine(vm.getId())

def deploy_vm(context, vm):
    """ Deploy the given virtual machine. """
    monitor = context.getMonitoringService().getVirtualMachineMonitor()
    print "Deploying virtual machine %s... This may take some time." % vm.getName()
    vm.deploy()
    monitor.awaitCompletionDeploy(vm)
    return refresh_vm(context, vm)

def undeploy_vm(context, vm):
    """ Undeploy the given virtual machine. """
    monitor = context.getMonitoringService().getVirtualMachineMonitor()
    print "Uneploying virtual machine %s... This may take some time." % vm.getName()
    vm.undeploy()
    monitor.awaitCompletionUndeploy(vm)
    return refresh_vm(context, vm)

