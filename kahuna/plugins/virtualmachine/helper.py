#!/usr/bin/env jython

import logging
from com.abiquo.model.enumerator import ConversionState
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.predicates.cloud \
        import VirtualMachineTemplatePredicates

log = logging.getLogger('kahuna')


def find_template_by_id(context, id):
    """ Find a template given its id """
    admin = context.getAdministrationService()
    enterprise = admin.getCurrentEnterprise()
    return enterprise.findTemplate(VirtualMachineTemplatePredicates.id(id))


def find_compatible_virtual_datacenters(context, template):
    """ Find a virtual datacenter compatible with the template. """
    cloud = context.getCloudService()
    all = cloud.listVirtualDatacenters(
            VirtualDatacenterPredicates.datacenter(template.getDatacenter()))

    def compatible(vdc):
        type = vdc.getHypervisorType()
        res = type.isCompatible(template.getDiskFormatType())
        log.debug("%s compatible with source format: %s" %
            (vdc.getName(), res))
        if not res:
            conv = template.listConversions(type, ConversionState.FINISHED)
            res = len(conv) > 0
        log.debug("%s compatible with conversions: %s" % (vdc.getName(), res))
        return res

    return filter(compatible, all)


def refresh_vm(context, vm):
    """ Refresh the given virtual machine """
    vapp = vm.getVirtualAppliance()
    return vapp.getVirtualMachine(vm.getId())


def deploy_vm(context, vm):
    """ Deploy the given virtual machine """
    monitor = context.getMonitoringService().getVirtualMachineMonitor()
    print "Deploying virtual machine %s... This may take some time." \
            % vm.getInternalName()
    vm.deploy()
    monitor.awaitCompletionDeploy(vm)
    return refresh_vm(context, vm)


def undeploy_vm(context, vm):
    """ Undeploy the given virtual machine """
    monitor = context.getMonitoringService().getVirtualMachineMonitor()
    print "Uneploying virtual machine %s... This may take some time." \
            % vm.getInternalName()
    vm.undeploy()
    monitor.awaitCompletionUndeploy(vm)
    return refresh_vm(context, vm)


def change_state_vm(context, vm, new_state):
    """ Change the state of the given virtual machine """
    monitor = context.getMonitoringService().getVirtualMachineMonitor()
    print("Changing state of virtual machine %s to %s... "
        "This may take some time." % (vm.getInternalName(), new_state.name()))
    vm.changeState(new_state)
    monitor.awaitState(new_state, vm)
    return vm
