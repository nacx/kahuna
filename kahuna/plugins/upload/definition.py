#!/usr/bin/env jython

from __future__ import with_statement
import simplejson as json  # JSON module is available from Python 2.6


class DefinitionGenerator:
    """ Generates a template definition given a configuration """
    def __init__(self):
        self.__templatedir = "kahuna/plugins/upload"

    def generate(self, config):
        """ Generates a template definition given a configuration """
        values = self.read_defaults()
        values.update(config)
        with open("%s/ovf.xml" % self.__templatedir, "r") as f:
            ovf = f.read() % values
        print ovf
        return ovf

    def read_defaults(self):
        """ Read the default values for the definition """
        with open("%s/ovf-defaults.json" % self.__templatedir, "r") as f:
            defaults = f.read()
        return json.loads(defaults)
