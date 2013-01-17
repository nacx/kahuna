#!/usr/bin/env jython

from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.rest import AuthorizationException
from optparse import OptionParser
from threading import Thread
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
        parser.add_option('-p', '--port',
                help='The port to open locally for the repository',
                action='store', dest='port', type='int', default=8888)
        (options, args) = parser.parse_args(args)

        repo = TransientRepository()
        try:
            repo.create()
            thread = Thread(target=repo.start, args=[options.port])
            thread.start()

            # TODO: Once the server is listening, call the API to download
            # the necessary files.
            sleep(5)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            repo.destroy()


def load():
    """ Loads the current plugin """
    return TemplatePlugin()
