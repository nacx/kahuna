#!/usr/bin/env jython

from __future__ import with_statement
from org.jclouds.abiquo.domain.cloud import TemplateDefinition
from com.abiquo.model.enumerator import DiskControllerType
from com.abiquo.model.enumerator import DiskFormatType
from com.abiquo.model.enumerator import EthernetDriverType
from com.abiquo.model.enumerator import OSType
from subprocess import PIPE
from subprocess import Popen
import simplejson as json  # JSON module is available from Python 2.6


class DefinitionGenerator:
    """ Generates a template definition given a configuration """
    def __init__(self, disk, config):
        self.__diskid = "http://diskid.frameos.org/?format=json"
        self.__templatedir = "kahuna/plugins/upload"
        self.__disk = disk
        self.__values = self._read_defaults()
        self.__values.update(config)
        try:
            self._parse_template_values()
        except KeyError, ex:
            print "Missing configuration value: %s" % ex
            raise ex

    def generate_ovf(self):
        """ Generates a template definition given a configuration """
        with open("%s/ovf.ovf" % self.__templatedir, "r") as f:
            ovf = f.read() % self.__values
        return ovf

    def generate_definition(self, context, address, port):
        """ Generates the tempalte definition object """
        try:
            definition = TemplateDefinition.builder(context.getApiContext()) \
                .name(self.__values['name']) \
                .description(self.__values['description']) \
                .url("http://%s:%s/ovf.ovf" % (address, port)) \
                .loginUser(self.__values['user']) \
                .loginPassword(self.__values['password']) \
                .osType(OSType.valueOf(self.__values['ostype'])) \
                .diskFormatType(DiskFormatType.fromURI(
                    self.__values['diskformaturl']).name()) \
                .ethernetDriverType(EthernetDriverType.valueOf(
                    self.__values['ethernetdriver'])) \
                .diskFileSize(self.__values['diskfilesize']) \
                .osVersion(self.__values['osversion']) \
                .productName(self.__values['name']) \
                .productUrl("") \
                .productVersion("") \
                .productVendor("") \
                .build()
            if self.__values['diskcontroller'] == 5:
                definition.setDiskControllerType(DiskControllerType.IDE)
            else:
                definition.setDiskControllerType(DiskControllerType.SCSI)
        except KeyError, ex:
            print "Missing configuration value: %s" % ex
            raise ex

        return definition

    def _read_defaults(self):
        """ Read the default values for the definition """
        with open("%s/ovf-defaults.json" % self.__templatedir, "r") as f:
            defaults = f.read()
        return json.loads(defaults)

    def _parse_template_values(self):
        """ Parses the special template values """
        diskcontroller = self.__values['diskcontroller']
        self.__values['diskcontroller'] = 5 if diskcontroller == 'IDE' else 6
        disk_info = self._read_disk_file()
        # TODO Parse disk info and fill the values with the appropriate values
        print disk_info

    def _read_disk_file(self):
        """ Reads the information from the given disk file """
        with open(self.__disk, "r") as f:
            head = ''.join([f.next() for i in xrange(20)])
        with open("/tmp/chunk", "w") as chunk:
            chunk.write(head)
        # Use local curl, because pycurl can not be installed in Jython
        # and regular http modules don't support well the multipart upload
        # curl -X POST -F chunk=@/tmp/chunk <target url>
        with open('/dev/null', 'w') as devnull:
            out = Popen(["/usr/bin/curl", "-X", "POST", "-F",
                "chunk=@/tmp/chunk", self.__diskid], stdout=PIPE,
                stderr=devnull).communicate()[0]
        return json.loads(out)
