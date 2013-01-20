#!/usr/bin/env jython

from __future__ import with_statement
from org.jclouds.abiquo.domain.cloud import TemplateDefinition
from com.abiquo.model.enumerator import DiskControllerType
from com.abiquo.model.enumerator import DiskFormatType
from com.abiquo.model.enumerator import EthernetDriverType
from com.abiquo.model.enumerator import OSType
import simplejson as json  # JSON module is available from Python 2.6


class DefinitionGenerator:
    """ Generates a template definition given a configuration """
    def __init__(self, config):
        self.__templatedir = "kahuna/plugins/upload"
        self.__values = self._read_defaults()
        self.__values.update(config)
        try:
            self._parse_template_values()
        except KeyError, ex:
            print "Missing configuration value: %s" % ex
            raise ex

    def generate_ovf(self):
        """ Generates a template definition given a configuration """
        with open("%s/ovf.xml" % self.__templatedir, "r") as f:
            ovf = f.read() % self.__values
        return ovf

    def generate_definition(self, context, address, port):
        """ Generates the tempalte definition object """
        try:
            definition = TemplateDefinition.builder(context.getApiContext()) \
                .name(self.__values['name']) \
                .description(self.__values['description']) \
                .url("http://%s:%s/ovf.xml" % (address, port)) \
                .loginUser(self.__values['user']) \
                .loginPassword(self.__values['password']) \
                .osType(OSType.valueOf(self.__values['ostype'])) \
                .diskFormatType(DiskFormatType.fromURI(
                    self.__values['diskformaturl']).name()) \
                .ethernetDriverType(EthernetDriverType.valueOf(
                    self.__values['ethernetdriver'])) \
                .diskFileSize(self.__values['diskfilesize']) \
                .osVersion(self.__values['osversion']) \
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
        # TODO: Extract disk info from http://diskid.frameos.org/
        diskcontroller = self.__values['diskcontroller']
        self.__values['diskcontroller'] = 5 if diskcontroller == 'IDE' else 6
