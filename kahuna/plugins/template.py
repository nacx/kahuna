#!/usr/bin/env jython

from optparse import OptionParser
from kahuna.session import ContextLoader
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.predicates.cloud import VirtualMachineTemplatePredicates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException


class TemplatePlugin:
    """ Template plugin. """
    def __init__(self):
        pass

    def commands(self):
        """ Returns the provided commands, mapped to handler methods. """
        commands = {}
        commands['list'] = self.list
        commands['find'] = self.find
        return commands

    def list(self, args):
        """ List all available templates. """
        context = ContextLoader().load()
        try:
            admin = context.getAdministrationService()
            enterprise = admin.getCurrentEnterprise()
            templates = enterprise.listTemplates()
            pprint_templates(templates)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()

    def find(self, args):
        """ Find a template given its name. """
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
        context = ContextLoader().load()
        try:
            admin = context.getAdministrationService()
            enterprise = admin.getCurrentEnterprise()
            template = enterprise.findTemplate(
                    VirtualMachineTemplatePredicates.name(name))
            if template:
                pprint_templates([template])
            else:
                print "No template found with name: %s" % name
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            context.close()


def load():
    """ Loads the current plugin. """
    return TemplatePlugin()
