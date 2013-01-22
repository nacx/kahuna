#!/usr/bin/env jython

from __future__ import with_statement
import logging
import simplejson as json  # JSON module is available from Python 2.6
from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.domain import DomainWrapper
from org.jclouds.abiquo.domain.cloud import TemplateDefinition
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.abiquo.predicates.infrastructure import DatacenterPredicates
from org.jclouds.rest import AuthorizationException
from optparse import OptionParser
from upload.repository import TransientRepository
from time import sleep

log = logging.getLogger('kahuna')


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
        parser.add_option('-a', '--bind-address',
                help='The bind address fot the local repository',
                action='store', dest='address', default='localhost')
        parser.add_option('-p', '--port',
                help='The port to open locally for the repository',
                action='store', dest='port', type='int', default=8888)
        parser.add_option('-f', '--disk-file',
                help='The disk file to be uploaded',
                action='store', dest='disk')
        parser.add_option('-c', '--config',
                help='Path to a json configuration file for the template',
                action='store', dest='config')
        parser.add_option('-d', '--datacenter',
                help='The name of the datacenter where the template '
                'will be downloaded', action='store', dest='datacenter')
        (options, args) = parser.parse_args(args)

        if not options.disk or not options.datacenter:
            parser.print_help()
            return

        # Read OVF values from json file
        if options.config:
            with open(options.config, "r") as f:
                config = json.loads(f.read())
        else:
            config = {}

        repo = TransientRepository(options.address, options.port)
        try:
            log.info("Creating temporal OVF repository")
            repo.create()
            definition = repo.add_definition(self._context,
                options.disk, config)
            repo.start()

            log.info("Loading destination repository: %s" % options.datacenter)
            #admin = self._context.getAdministrationService()
            #dc = admin.findDatacenter(
            #    DatacenterPredicates.name(options.datacenter))

            log.info("Uploading template. This may take some time...")
            #definition.save()

            # FIXME Add enterprise to TemplateDefinition builder in jclouds
            # in order to be able to call definition.save()
            #api = self._context.getApiContext().getApi()
            #enterprise = admin.getCurrentEnterprise()
            #dto = api.getEnterpriseApi().createTemplateDefinition(
            #    enterprise.unwrap(), definition.unwrap())
            #definition = DomainWrapper.wrap(self._context.getApiContext(),
            #    TemplateDefinition, dto)

            #definition.downloadToRepository(dc)
            sleep(60)
            log.info("Done!")
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            repo.destroy()


def load():
    """ Loads the current plugin """
    return TemplatePlugin()
