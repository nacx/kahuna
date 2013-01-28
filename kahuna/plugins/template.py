#!/usr/bin/env jython

from __future__ import with_statement
import logging
import re
import simplejson as json  # JSON module is available from Python 2.6
from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_templates
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.abiquo.predicates.infrastructure import DatacenterPredicates
from org.jclouds.rest import AuthorizationException
from optparse import OptionParser
from upload.repository import TransientRepository
from urllib import urlopen

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
                help='The bind address fot the local repository'
                'By default the public IP will be detected and used',
                action='store', dest='address')
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

        # Find the public bind address if not provided
        if not options.address:
            options.address = self._get_public_address()

        repo = TransientRepository(options.address, options.port)
        try:
            log.info("Creating temporal OVF repository")
            repo.create()
            definition = repo.add_definition(self._context,
                options.disk, config)
            repo.start()

            log.info("Loading destination repository: %s" % options.datacenter)
            admin = self._context.getAdministrationService()
            dc = admin.findDatacenter(
                DatacenterPredicates.name(options.datacenter))

            log.info("Uploading template. This may take some time...")
            definition.save()

            monitor = self._context.getMonitoringService() \
                .getAsyncTaskMonitor()
            task = definition.downloadToRepository(dc)
            monitor.awaitCompletion(task)

            pprint_templates([task.getResult()])
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        finally:
            repo.destroy()

    def _get_public_address(self):
        """ Gets the bind address """
        data = str(urlopen('http://checkip.dyndns.com/').read())
        return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)') \
            .search(data).group(1)


def load():
    """ Loads the current plugin """
    return TemplatePlugin()
