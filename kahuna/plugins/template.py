#!/usr/bin/env jython

from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException


class TemplatePlugin(AbsPlugin):
    """ Template plugin """

    def list(self, args):
        """ List all available templates """
        try:
            admin = self._context.getAdministrationService()
            enterprise = admin.getCurrentEnterprise()
            templates = enterprise.listTemplates()
            pprint_templates(templates)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the current plugin """
    return TemplatePlugin()
