#!/usr/bin/env jython

import logging
from optparse import OptionParser
from kahuna.utils.prettyprint import pprint_volumes
from org.jclouds.abiquo.predicates.cloud import VirtualMachinePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException
from storage import helper
from kahuna.abstract import AbsPlugin

log = logging.getLogger('kahuna')


class VolumePlugin(AbsPlugin):
    """ Volume plugin """
    def __init__(self):
        pass

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

    def find(self, args):
        """ Find an available volume given its name """
        # Parse user input to get the name of the volume
        parser = OptionParser(usage="volume find <options>")
        parser.add_option("-n", "--name", dest="name",
                help="The name of the volume to find")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the volume
        try:
            volume = helper.find_volume(self._context, name)
            if volume:
                pprint_volumes([volume])
            else:
                print "No volume found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def attach(self, args):
        """ Attach a volume to the given virtual machine """
        parser = OptionParser(usage="volume attach <options>")
        parser.add_option("-n", "--name", dest="name",
                help="The name of the volume to attach")
        parser.add_option("-v", "--vm", dest="name",
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
                    VirtualMachinePredicates.name(options.vm))
            if not vm:
                print "No virtual machine found with name: %s" % options.vm
                return

            log.debug("Attaching volume %s to %s..." % (options.name,
                options.vm))
            if vm.getState().existsInHypervisor():
                print "Attaching volume to a running virtual machine.",
                print "This may take some time..."

            vm.attachVolumes(volume)
            pprint_volumes([helper.refresh_volume(self._context, volume)])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def detach(self, args):
        """ Detach a volume from the given virtual machine """
        parser = OptionParser(usage="volume detach <options>")
        parser.add_option("-n", "--name", dest="name>",
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
                vm.getName()))
            if vm.getState().existsInHypervisor():
                print "Detaching volume from a running virtual machine.",
                print "This may take some time..."

            vm.detachVolumes(volume)
            pprint_volumes([helper.refresh_volume(self._context, volume)])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the current plugin """
    return VolumePlugin()
