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
from org.jclouds.http import HttpResponseException
from com.abiquo.model.enumerator import HypervisorType

log = logging.getLogger("kahuna")

class MachinePlugin:
    """ Physical machines plugin """
    def __init__(self):
        self.__config = ConfigLoader().load("machine.conf","config/machine.conf")

    def commands(self):
        """ Returns the commands provided by the plugin, mapped to the handler methods """
        commands = {}
        commands['check'] = self.checkMachines
        commands['create'] = self.createMachine
        commands['delete'] = self.deleteMachine
        commands['list'] = self.listMachines
        return commands

    def checkMachines(self, args):
        """ Check state from physical machine """
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

        context = ContextLoader().load()
        try:
            admin =  context.getAdministrationService()
            if all_true:
                machines = admin.listMachines()
                log.debug("%s machines found." % str(len(machines)))
                [self._checkMachine for machine in machines]
                pprint_machines(machines)
            else:
                if name:
                    machine = admin.findMachine(MachinePredicates.name(name))
                else:
                    machine = admin.findMachine(MachinePredicates.ip(host))
                self._checkMachine(machine)
                pprint_machines([machine]);
        except (AbiquoException, AuthorizationException), ex:
            print "Error %s" % ex.getMessage()
        finally:
            context.close()

    def _checkMachine(self, machine):
        try:
            if not machine:
                raise Exception("machine not found")
            state = machine.check()
            machine.setState(state)
            log.debug("%s - %s" % (machine.getName(), state))
        except (AbiquoException, AuthorizationException), ex:
            print "Error %s" % ex.getMessage()

    def createMachine(self, args):
        """ Create a physical machine in abiquo """
        parser = OptionParser(usage="machine create --host <host> <options>")

        # create options
        parser.add_option("-i","--host",
                help="ip or hostname from machine to create in abiquo [required]",action="store",dest="host")
        parser.add_option("-u","--user",help="user to loggin in the machine",action="store",dest="user")
        parser.add_option("-p","--psswd",help="password to loggin in the machine",action="store",dest="psswd")
        # parser.add_option("-c","--port",help="port from machine",action="store",dest="port")
        parser.add_option("-t","--type",help="hypervisor type of the machine",action="store",dest="hypervisor")
        parser.add_option("-r","--rsip",help="ip from remote services",action="store",dest="remoteservicesip")
        parser.add_option("-d","--datastore",
                help="datastore to enable on physical machine",action="store",dest="datastore")
        parser.add_option("-s","--vswitch",
                help="virtual switch to select on physical machine",action="store",dest="vswitch")
        (options, args) = parser.parse_args(args)
        
        # parse options
        host = options.host
        if not host:
            parser.print_help()
            return


        user = self._getConfig(options,host,"user")
        psswd = self._getConfig(options,host,"psswd")
        rsip = self._getConfig(options,host,"remoteservicesip")
        dsname = self._getConfig(options,host,"datastore")
        vswitch =  self._getConfig(options,host,"vswitch")
        hypervisor = options.hypervisor

        context = ContextLoader().load()
        api_context = context.getApiContext()
        try:
            admin = context.getAdministrationService()

            # search or create datacenter
            log.debug("Searching for the datacenter 'kahuna'.")
            dc = admin.findDatacenter(DatacenterPredicates.name('kahuna'))
            if not dc:
                log.debug("No datacenter 'kahuna' found.")
                dc = Datacenter.builder(api_context) \
                        .name('kahuna') \
                        .location('terrassa') \
                        .remoteServices(rsip,AbiquoEdition.ENTERPRISE) \
                        .build()
                try:
                    dc.save()
                except (AbiquoException), ex:
                    if ex.hasError("RS-3"):
                        print "ip %s to create remote services has been used yet, try with another one" % rsip
                        dc.delete()
                        return
                    else:
                        raise ex
                rack = Rack.builder(api_context,dc).name('rack').build()
                rack.save()
                log.debug("New datacenter 'kahuna' created.")
            else:
                rack = dc.findRack(RackPredicates.name('rack'))
                if not rack:
                    rack = Rack.builder(api_context,dc).name('rack').build()
                    rack.save()
                log.debug("Datacenter 'kahuna' found")
        
            # discover machine
            hypTypes = [HypervisorType.valueOf(hypervisor)] if hypervisor else HypervisorType.values()

            machine = None
            for hyp in hypTypes:
                try:
                    log.debug("Trying hypervisor %s" % hyp.name())
                    machine = dc.discoverSingleMachine(host, hyp, user, psswd)
                    break
                except (AbiquoException, HttpResponseException), ex:
                    if ex.hasError("NC-3") or ex.hasError("RS-2"):
                        print ex.getMessage().replace("\n","")
                        return
                    log.debug(ex.getMessage().replace("\n",""))

            if not machine:
                print "Not machine found in %s" % host
                return

            log.debug("Machine %s of type %s found" % (machine.getName(), machine.getType().name()))

            # enabling datastore
            ds = machine.findDatastore(dsname)
            if not ds:
                print "Missing datastore %s in machine" % dsname
                return
            ds.setEnabled(True)

            # setting virtual switch
            vs=machine.findAvailableVirtualSwitch(vswitch)
            if not vs:
                print "Missing virtual switch %s in machine" % vswitch
                return

            # saving machine
            machine.setRack(rack)
            machine.setVirtualSwitch(vs)
            machine.save()
            log.debug("Machine saved")
            pprint_machines([machine])

        except (AbiquoException,AuthorizationException), ex:
            if ex.hasError("HYPERVISOR-1") or ex.hasError("HYPERVISOR-2"):
                print "Error: Machine already exists"
            else:
                print "Error: %s " % ex.getMessage()
        finally:
            context.close()

    def deleteMachine(self, args):
        """ Remove a physical machine from abiquo """
        parser = OptionParser(usage="machine delete <options>")
        parser.add_option("-n","--name",help="the name of the physical machine",action="store",dest="name")
        parser.add_option("-i","--host",help="the ip of the physical machine",action="store",dest="host")
        (options, args) = parser.parse_args(args)
        name = options.name
        host = options.host

        if not name and not host:
            parser.print_help()
            return

        context = ContextLoader().load()
        try:
            admin =  context.getAdministrationService()
            if name:
                machine = admin.findMachine(MachinePredicates.name(name))
            else:
                machine = admin.findMachine(MachinePredicates.ip(host))
            if not machine:
                print "Machine not found"
                return
            name=machine.getName()
            machine.delete()
            log.debug("Machine %s deleted succesfully" % name)

        except (AbiquoException, AuthorizationException), ex:
            print "Error %s" % ex.getMessage()
        finally:
            context.close()
    
    def listMachines(self,args):
        """ List physical machines from abiquo """
        context = ContextLoader().load()
        try:
            admin = context.getAdministrationService()
            machines = admin.listMachines()
            pprint_machines(machines)
        except (AbiquoException, AuthorizationException), ex:
            print "Error %s" % ex.getMessage()
        finally:
            context.close()

    def _getConfig(self, options, host, prop):
        """ Gets a value from config or options """
        p = eval("options.%s" % prop)
        if p:
            return p
        try:
            return self.__config.get(host, prop)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return self.__config.get("global", prop)

def load():
    """ Loads the current plugin """
    return MachinePlugin()

