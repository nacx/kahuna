#!/usr/bin/env jython

import logging
from com.abiquo.model.enumerator import HypervisorType
from org.jclouds.abiquo.domain.cloud import VirtualDatacenter
from org.jclouds.abiquo.domain.network import PrivateNetwork
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.predicates.cloud \
        import VirtualMachineTemplatePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException

log = logging.getLogger('kahuna')


def find_template_by_id(context, id):
    """ Find a template given its id """
    admin = context.getAdministrationService()
    enterprise = admin.getCurrentEnterprise()
    return enterprise.findTemplate(VirtualMachineTemplatePredicates.id(id))


def find_compatible_virtual_datacenters(context, type, datacenter):
    """ Find a virtual datacenter compatible with the type and datacenter. """
    cloud = context.getCloudService()
    all = cloud.listVirtualDatacenters(
            VirtualDatacenterPredicates.datacenter(datacenter))
    return filter(lambda vdc: vdc.getHypervisorType().isCompatible(type), all)


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


def get_virtual_datacenter_for_template(context, template):
    """ Get a virtual datacenter where the given template can be deployed """
    datacenter = template.getDatacenter()
    api_context = context.getApiContext()
    vdcs = find_compatible_virtual_datacenters(context,
            template.getDiskFormatType(), datacenter)
    pattern = "Kahuna-%s-" + api_context.getIdentity()
    vdcs = filter(lambda vdc: vdc.getName() ==
            (pattern % vdc.getHypervisorType().name()), vdcs)

    if len(vdcs) == 0:
        log.debug("No default virtual datacenter was found. Creating it...")

        admin = context.getAdministrationService()
        enterprise = admin.getCurrentEnterprise()

        network = PrivateNetwork.builder(api_context) \
            .name("Kahuna-" + api_context.getIdentity()) \
            .gateway("192.168.1.1") \
            .address("192.168.1.0") \
            .mask(24) \
            .build()
        vdc = VirtualDatacenter.builder(api_context, datacenter, enterprise) \
            .network(network) \
            .build()

        for type in HypervisorType.values():
            if type.isCompatible(template.getDiskFormatType()):
                try:
                    log.debug(("Trying to create virtual "
                        "datacenter of type %s") % type.name())
                    vdc.setName(pattern % type.name())
                    vdc.setHypervisorType(type)
                    vdc.save()
                    return vdc
                except AbiquoException, ex:
                    # Just catch the error thrown when no hypervisors of
                    # the given type are available in the datacenter
                    if ex.hasError("VDC-1"):
                        # Check if we can create a VDC with other
                        # compatible type
                        continue
                    else:
                        raise ex
        return None
    else:
        vdc = vdcs[0]

    return vdc
