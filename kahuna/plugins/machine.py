#!/usr/bin/env jython

import logging
import ConfigParser
from kahuna.session import ContextLoader
from kahuna.config import ConfigLoader
from kahuna.utils.prettyprint import pprint_machines
from optparse import OptionParser
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.abiquo.domain.infrastructure import Datacenter,Rack
from org.jclouds.abiquo.predicates.infrastructure import MachinePredicates,DatacenterPredicates,RackPredicates
from org.jclouds.abiquo.reference import AbiquoEdition
from org.jclouds.rest import AuthorizationException
from com.abiquo.model.enumerator import HypervisorType

log = logging.getLogger("kahuna")

class MachinePlugin:
    """ Physical machines plugin. """
    def __init__(self):
        pass

    def commands(self):
        """ Returns the commands provided by the plugin, mapped to the handler methods. """
        commands = {}
        commands['check'] = self.checkMachines
        commands['create'] = self.createMachine
        commands['delete'] = self.deleteMachine
        return commands

    def checkMachines(self, args):
        """ Check state from physical machine. """
        parser = OptionParser(usage="machine check <options>")
        parser.add_option("-n","--name",help="the name of the physical machine",action="store",dest="name")
        parser.add_option("-i","--host",help="the ip of the physical machine",action="store",dest="host")
        parser.add_option("-a","--all",help="check all machines",action="store_true",dest="a")
        (options, args) = parser.parse_args(args)
        all_true = options.a
        name = options.name
        host = options.host

        if not name and not host and not all_true:
            parser.print_help()
            return

        try:
            context = ContextLoader().load()
            admin =  context.getAdministrationService()
            if all_true:
                machines = admin.listMachines()
                log.debug("%s machines found." % str(len(machines)))
                for machine in machines:
                    self.checkMachine(machine)
                pprint_machines(machines)
            else:
                if name:
                    machine = admin.findMachine(MachinePredicates.name(name))
                else:
                    machine = admin.findMachine(MachinePredicates.ip(host))
                self.checkMachine(machine)
                pprint_machines([machine]);
        except (AbiquoException, AuthorizationException), ex:
            print "Error %s" % ex.getMessage()
        finally:
            context.close()

    def checkMachine(self, machine):
        try:
            if not machine:
                raise Exception("machine not found")
            state = machine.check()
            machine.setState(state)
            log.debug("%(mch)s - %(st)s" % {"mch":machine.getName(), "st":state})
        except (AbiquoException, AuthorizationException), ex:
            log.error("Error %s" % ex.getMessage())

    def createMachine(self, args):
        """ Create a physical machine in abiquo.
        \t\tThis method uses configurable constats for default values."""
        parser = OptionParser(usage="machine create --host <host> <options>")

        # create options
        parser.add_option("-i","--host",help="ip or hostname from machine to create in abiquo",action="store",dest="host")
        parser.add_option("-u","--user",help="user to loggin in the machine",action="store",dest="user")
        parser.add_option("-p","--psswd",help="password to loggin in the machine",action="store",dest="psswd")
        parser.add_option("-c","--port",help="port from machine",action="store",dest="port")
        parser.add_option("-t","--type",help="hypervisor type of the machine",action="store",dest="hypervisor")
        parser.add_option("-r","--rsip",help="ip from remote services",action="store",dest="remoteservicesip")
        (options, args) = parser.parse_args(args)
        
        # parse options
        host = options.host
        if not host:
            parser.print_help()
            return

        config = ConfigLoader().load("machine.conf","config/machine.conf")
        user = self.getConfig(config,options,"user")
        psswd = self.getConfig(config,options,"psswd")
        rsip = self.getConfig(config,options,"remoteservicesip")
        hypervisor = options.hypervisor

        try:
            context = ContextLoader().load()
            admin = context.getAdministrationService()

            # search or create datacenter
            log.debug("searching for the datacenter 'kahuna'.")
            dc = admin.findDatacenter(DatacenterPredicates.name('kahuna'))
            if not dc:
                log.debug("no datacenter 'kahuna' found.")
                dc = Datacenter.builder(context).name('kahuna').location('terrassa').remoteServices(rsip,AbiquoEdition.ENTERPRISE).build()
                dc.save()
                rack = Rack.builder(context,dc).name('rack').build()
                rack.save()
                log.debug("new datacenter 'kahuna' created.")
            else:
                rack = dc.findRack(RackPredicates.name('rack'))
                if not rack:
                    rack = Rack.builder(context,dc).name('rack').build()
                    rack.save()
                log.debug("datacenter 'kahuna' found")
        
            # discover machine
            if not hypervisor:
                hypTypes = HypervisorType.values()
            else:
                hypTypes = [HypervisorType.valueOf(hypervisor)]

            for hyp in hypTypes:
                try:
                    log.debug("trying for hypervisor %s" % hyp.name())
                    machine = dc.discoverSingleMachine(host, hyp, user, psswd)
                    break
                except (AbiquoException), ex:
                    log.debug(ex.getMessage().replace("\n",""))

            log.debug("machine %(mch)s of type %(hyp)s found" % {"mch":machine.getName(),"hyp":machine.getType().name()})

            # save machine
            for datastore in machine.getDatastores():
                datastore.setEnabled(True)

            machine.setRack(rack)
            machine.save()
            log.debug("machine saved")
            pprint_machines([machine])

        except (AbiquoException,AuthorizationException), ex:
            print ex.getMessage()

    def deleteMachine(self, args):
        """ Remove a physical machine from abiquo. """
        parser = OptionParser(usage="machine delete <options>")
        parser.add_option("-n","--name",help="the name of the physical machine",action="store",dest="name")
        parser.add_option("-i","--host",help="the ip of the physical machine",action="store",dest="host")
        (options, args) = parser.parse_args(args)
        name = options.name
        host = options.host

        if not name and not host:
            parser.print_help()
            return

        try:
            context = ContextLoader().load()
            admin =  context.getAdministrationService()
            if name:
                machine = admin.findMachine(MachinePredicates.name(name))
            else:
                machine = admin.findMachine(MachinePredicates.ip(host))
            if not machine:
                raise Exception("machine not found")
            name=machine.getName()
            machine.delete()
            log.info("machine %s deleted succesfully" % name)

        except (AbiquoException, AuthorizationException), ex:
            print "Error %s" % ex.getMessage()
        finally:
            context.close()

    def getConfig(self,config, options, prop):
        """ gets a value from config or options """
        p = eval("options.%s" % prop)
        if not p:
            p = config.get("create",prop)
            if p:
                return p
            else:
                raise Exception("%s not defined" % prop)
        else:
            return p

def load():
    """ Loads the current plugin. """
    return MachinePlugin()

