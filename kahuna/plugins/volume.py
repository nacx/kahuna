#!/usr/bin/env jython

import logging
from optparse import OptionParser
from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_volumes
from org.jclouds.abiquo.predicates.cloud import VirtualDiskPredicates
from org.jclouds.abiquo.predicates.cloud import VirtualMachinePredicates
from org.jclouds.abiquo.domain.cloud import Volume
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException
from storage import helper

log = logging.getLogger('kahuna')


class VolumePlugin(AbsPlugin):
    """ Volume plugin """

    def list(self, args):
        """ List all available volumes """
        try:
            cloud = self._context.getCloudService()
            vdcs = cloud.listVirtualDatacenters()
            volumes = []
            [volumes.extend(vdc.listVolumes()) for vdc in vdcs]
            pprint_volumes(volumes)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def create(self, args):
        """ Create a volume in a given tier """
        parser = OptionParser(usage="volume create <options>")
        parser.add_option("-n", "--name", dest="name",
                help="The name of the volume to create")
        parser.add_option("-v", "--vdc-id", dest="vdc", type="int",
                help="The id of the virtual datacenter where the volume"
                "will be created")
        parser.add_option("-s", "--size", dest="size", type="int",
                help=("The size in MB of the volume to create"))
        parser.add_option("-t", "--tier-id", dest="tier", type="int",
                help=("The id of the tier where the volume "
                "should be created"))
        (options, args) = parser.parse_args(args)
        if not options.name or not options.vdc \
            or not options.size or not options.tier:
            parser.print_help()
            return

        try:
            api_context = self._context.getApiContext()
            cloud = self._context.getCloudService()
            vdc = cloud.getVirtualDatacenter(options.vdc)
            if not vdc:
                print "Virtual datacenter %s does not exist" % options.vdc
                return
            tier = vdc.getStorageTier(options.tier)
            if not tier:
                print "Tier %s does not exist in the virtual datacenter" \
                    % options.tier
                return

            volume = Volume.builder(api_context, vdc, tier) \
                .name(options.name) \
                .sizeInMb(options.size) \
                .build()
            volume.save()

            pprint_volumes([volume])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def delete(self, args):
        """ Delete a given volume """
        parser = OptionParser(usage="volume delete <options>")
        parser.add_option("-n", "--name", dest="name",
                help="The name of the volume to delete")
        (options, args) = parser.parse_args(args)
        if not options.name:
            parser.print_help()
            return

        try:
            cloud = self._context.getCloudService()
            vdcs = cloud.listVirtualDatacenters()
            for vdc in vdcs:
                volume = vdc.findVolume(
                    VirtualDiskPredicates.name(options.name))
                if volume:
                    volume.delete()
                    return

            print "No volume found with name: %s" % options.name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def attach(self, args):
        """ Attach a volume to the given virtual machine """
        parser = OptionParser(usage="volume attach <options>")
        parser.add_option("-n", "--name", dest="name",
                help="The name of the volume to attach")
        parser.add_option("-v", "--vm", dest="vm",
                help=("The name of the virtual machine "
                "where the volume will be attached"))
        (options, args) = parser.parse_args(args)
        if not options.name or not options.vm:
            parser.print_help()
            return

        try:
            volume = helper.find_volume(self._context, options.name)
            if not volume:
                print "No volume found with name: %s" % options.name
                return
            cloud = self._context.getCloudService()
            vm = cloud.findVirtualMachine(
                    VirtualMachinePredicates.internalName(options.vm))
            if not vm:
                print "No virtual machine found with name: %s" % options.vm
                return

            log.debug("Attaching volume %s to %s..." % (options.name,
                options.vm))
            if vm.getState().existsInHypervisor():
                print "Attaching volume to a running virtual machine.",
                print "This may take some time..."

            disks = list(vm.listVirtualDisks())
            disks.append(volume)
            vm.setVirtualDisks(disks)

            pprint_volumes([helper.refresh_volume(self._context, volume)])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def detach(self, args):
        """ Detach a volume from the given virtual machine """
        parser = OptionParser(usage="volume detach <options>")
        parser.add_option("-n", "--name", dest="name",
                help="The name of the volume to detach")
        (options, args) = parser.parse_args(args)
        if not options.name:
            parser.print_help()
            return

        try:
            volume = helper.find_volume(self._context, options.name)
            if not volume:
                print "No volume found with name: %s" % options.name
                return

            vm = helper.get_attached_vm(self._context, volume)
            if not vm:
                print ("Volume %s is not attached "
                        "to any virtual machine") % options.name
                return

            log.debug("Detaching volume %s from %s..." % (options.name,
                vm.getInternalName()))
            if vm.getState().existsInHypervisor():
                print "Detaching volume from a running virtual machine.",
                print "This may take some time..."

            disks = [disk for disk in vm.listVirtualDisks()
                    if disk.getId() != volume.getId()]
            vm.setVirtualDisks(disks)

            pprint_volumes([helper.refresh_volume(self._context, volume)])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the current plugin """
    return VolumePlugin()
