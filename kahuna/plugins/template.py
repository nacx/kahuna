#!/usr/bin/env jython

from __future__ import with_statement
import simplejson as json  # JSON module is available from Python 2.6
from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException
from optparse import OptionParser
from time import sleep
from upload.repository import TransientRepository


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

    def upload(self, args):
        """ Upload a template to a repository """
        parser = OptionParser(usage="template upload <options>")
        parser.add_option('-b', '--bind-address',
                help='The bind address fot the local repository',
                action='store', dest='address', default='localhost')
        parser.add_option('-p', '--port',
                help='The port to open locally for the repository',
                action='store', dest='port', type='int', default=8888)
        parser.add_option('-d', '--disk-file',
                help='The disk file to be uploaded',
                action='store', dest='disk')
        parser.add_option('-c', '--config',
                help='Path to a json configuration file for the template',
                action='store', dest='config')
        (options, args) = parser.parse_args(args)

        if not options.disk or not options.config:
            parser.print_help()
            return

        with open(options.config, "r") as f:
            config = json.loads(f.read())

        repo = TransientRepository(options.address, options.port)
        try:
            repo.create()
            definition = repo.add_definition(self._context, options.disk, config)
            print definition
            repo.start()

            # TODO: Once the server is listening, call the API to download
            # the necessary files.
            sleep(30)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            repo.destroy()


def load():
    """ Loads the current plugin """
    return TemplatePlugin()
