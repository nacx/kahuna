#!/usr/bin/env jython

from optparse import OptionParser
from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.predicates.cloud import VirtualMachineTemplatePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException


class TemplatePlugin(AbsPlugin):
    """ Template plugin. """
    def __init__(self):
        pass

    def list(self, args):
        """ List all available templates. """
        try:
            admin = self._context.getAdministrationService()
            user = admin.getCurrentUser()
            enterprise = user.getEnterprise()
            templates = enterprise.listTemplates()
            pprint_templates(templates)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def find(self, args):
        """ Find a template given its name """
        # Parse user input to get the name of the template
        parser = OptionParser(usage="template find <options>")
        parser.add_option("-n", "--name", deswt="name",
                help="The name of the template to find")
        (options, args) = parser.parse_args(args)
        name = options.name
        if not name:
            parser.print_help()
            return

        # Once user input has been read, find the template
        try:
            admin = self._context.getAdministrationService()
            user = admin.getCurrentUser()
            enterprise = user.getEnterprise()
            template = enterprise.findTemplate(
                    VirtualMachineTemplatePredicates.name(name))
            if template:
                pprint_templates([template])
            else:
                print "No template found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()


def load():
    """ Loads the current plugin """
    return TemplatePlugin()
