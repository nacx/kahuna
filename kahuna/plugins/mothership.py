#!/usr/bin/env jython

from __future__ import with_statement
import logging
from kahuna.abstract import AbsPlugin
from kahuna.config import ConfigLoader
from kahuna.utils.prettyprint import pprint_templates
from kahuna.utils import ssh
from com.google.common.collect import Iterables
from optparse import OptionParser
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.compute import RunNodesException
from org.jclouds.domain import LoginCredentials
from org.jclouds.rest import AuthorizationException
from org.jclouds.scriptbuilder.domain import StatementList
from org.jclouds.scriptbuilder.domain import Statements

log = logging.getLogger('kahuna')


class MothershipPlugin(AbsPlugin):
    """ Mothership plugin """
    def __init__(self):
        self.__config = ConfigLoader().load("mothership.conf",
                "config/mothership.conf")
        self.__scriptdir = "kahuna/plugins/mothership"

    # Override the endpoint address and credentials to create the
    # context
    def _config_overrides(self):
        overrides = {}
        overrides['address'] = self.__config.get("mothership", "host")
        overrides['user'] = self.__config.get("mothership", "user")
        overrides['password'] = self.__config.get("mothership", "password")
        return overrides

    # Override the commands factory method because the command names we want
    # can not be used as valid python class method names
    def _commands(self):
        """ Returns the provided commands, mapped to handler methods """
        commands = {}
        commands['deploy-abiquo'] = self.deploy_abiquo
        commands['deploy-chef'] = self.deploy_chef
        commands['deploy-kvm'] = self.deploy_kvm
        commands['deploy-vbox'] = self.deploy_vbox
        commands['list-templates'] = self.list_templates
        return commands

    def list_templates(self, args):
        """ List all available templates """
        try:
            admin = self._context.getAdministrationService()
            enterprise = admin.getCurrentEnterprise()
            templates = enterprise.listTemplates()
            pprint_templates(templates)
        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()

    def deploy_chef(self, args):
        """ Deploys and configures a Chef Server """
        compute = self._context.getComputeService()

        try:
            name = self.__config.get("deploy-chef", "template")
            log.info("Loading template...")
            vdc, options = self._template_options(compute, "deploy-chef")
            template = compute.templateBuilder() \
                .imageNameMatches(name) \
                .locationId(vdc.getId()) \
                .options(options) \
                .build()

            log.info("Deploying %s to %s..." % (template.getImage().getName(),
                vdc.getDescription()))
            node = Iterables.getOnlyElement(
                compute.createNodesInGroup("kahuna-chef", 1, template))

            log.info("Created %s at %s" % (node.getName(),
                Iterables.getOnlyElement(node.getPublicAddresses())))

            cookbooks = self.__config.get("deploy-chef", "cookbooks")
            with open("%s/configure-chef.sh" % self.__scriptdir, "r") as f:
                script = f.read() % {'cookbooks': cookbooks}

            log.info("Configuring node with cookbooks: %s..." % cookbooks)
            compute.runScriptOnNode(node.getId(), script)

            log.info("Done! You can access the admin console at: "
                    "http://%s:4040"
                    % Iterables.getOnlyElement(node.getPublicAddresses()))

            log.info("These are the certificates to access the API:")
            webui = ssh.get(self._context, node, "/etc/chef/webui.pem")
            log.info("webui.pem: %s", webui)
            validator = ssh.get(self._context, node,
                "/etc/chef/validation.pem")
            log.info("validation.pem: %s" % validator)

        except RunNodesException, ex:
            self._print_node_errors(ex)

    def deploy_kvm(self, args):
        """ Deploys and configures a KVM hypervisor """
        self._deploy_aim("deploy-kvm", "kahuna-kvm")

    def deploy_vbox(self, args):
        """ Deploys and configures a VirtualBox hypervisor """
        self._deploy_aim("deploy-vbox", "kahuna-vbox")

    def deploy_abiquo(self, args):
        """ Deploys and configures an Abiquo platform """
        parser = OptionParser(usage="mothership deploy-abiquo <options>")
        parser.add_option('-t', '--template-id',
                help='The id of the template to deploy',
                action='store', dest='template')
        parser.add_option('-p', '--properties',
                help='Path to the abiquo.properties file to use',
                action='store', dest='props')
        parser.add_option('-j', '--jenkins-version',
                help='Download the given version of the wars from Jenkins',
                action='store', dest='jenkins')
        (options, args) = parser.parse_args(args)

        if not options.template or not options.props:
            parser.print_help()
            return

        compute = self._context.getComputeService()

        try:
            log.info("Loading template...")
            vdc, template_options = self._template_options(compute,
                    "deploy-abiquo")
            template = compute.templateBuilder() \
                .imageId(options.template) \
                .locationId(vdc.getId()) \
                .options(template_options) \
                .build()

            log.info("Deploying %s to %s..." % (template.getImage().getName(),
                vdc.getDescription()))
            node = Iterables.getOnlyElement(
                compute.createNodesInGroup("kahuna-abiquo", 1, template))

            log.info("Created %s at %s" % (node.getName(),
                Iterables.getOnlyElement(node.getPublicAddresses())))

            # Generate the bootstrap script
            bootstrap = []
            bootstrap.append(Statements.exec("service abiquo-tomcat stop"))

            with open(options.props, "r") as f:
                bootstrap.append(Statements.createOrOverwriteFile(
                    "/opt/abiquo/config/abiquo.properties", [f.read()]))

            with open("%s/configure-abiquo.sh" % self.__scriptdir, "r") as f:
                bootstrap.append(Statements.exec(f.read()))

            if options.jenkins:
                log.info("Configuring node to download the %s version "
                    "from Jenkins..." % options.jenkins)
                with open("%s/configure-from-jenkins.sh" %
                        self.__scriptdir, "r") as f:
                    jenkins_script = f.read() % {'version': options.jenkins}
                bootstrap.append(Statements.exec(jenkins_script))

            bootstrap.append(Statements.exec("service abiquo-tomcat start"))

            log.info("Configuring node with the given properties...")
            compute.runScriptOnNode(node.getId(), StatementList(bootstrap))

            log.info("Done! Abiquo configured at: %s" %
                    Iterables.getOnlyElement(node.getPublicAddresses()))

        except RunNodesException, ex:
            self._print_node_errors(ex)

    # Utility functions
    def _deploy_aim(self, config_section, vapp_name):
        """ Deploys and configures an AIM based hypervisor """
        compute = self._context.getComputeService()

        try:
            name = self.__config.get(config_section, "template")
            log.info("Loading template...")
            vdc, options = self._template_options(compute, config_section)
            template = compute.templateBuilder() \
                .imageNameMatches(name) \
                .locationId(vdc.getId()) \
                .options(options) \
                .build()

            log.info("Deploying %s to %s..." % (template.getImage().getName(),
                vdc.getDescription()))
            node = Iterables.getOnlyElement(
                compute.createNodesInGroup(vapp_name, 1, template))

            log.info("Created %s at %s" % (node.getName(),
                Iterables.getOnlyElement(node.getPublicAddresses())))

            # Configuration values
            redishost = self.__config.get(config_section, "redis_host")
            redisport = self.__config.get(config_section, "redis_port")
            nfsto = self.__config.get(config_section, "nfs_to")
            nfsfrom = self.__config.get(config_section, "nfs_from")

            bootstrap = []

            with open("%s/abiquo-aim.ini" % self.__scriptdir, "r") as f:
                aim_config = f.read() % {'redishost': redishost,
                    'redisport': redisport, 'nfsto': nfsto}
            bootstrap.append(Statements.createOrOverwriteFile(
                "/etc/abiquo-aim.ini", [aim_config]))

            with open("%s/configure-aim-node.sh" % self.__scriptdir, "r") as f:
                script = f.read() % {'nfsfrom': nfsfrom, 'nfsto': nfsto}
            bootstrap.append(Statements.exec(script))

            log.info("Configuring node...")
            compute.runScriptOnNode(node.getId(), StatementList(bootstrap))

            log.info("Done! You can access it at: %s" %
                Iterables.getOnlyElement(node.getPublicAddresses()))

        except RunNodesException, ex:
            self._print_node_errors(ex)

    def _template_options(self, compute, deploycommand):
        locations = compute.listAssignableLocations()
        vdc = self.__config.get("mothership", "vdc")
        location = filter(lambda l: l.getDescription() == vdc, locations)[0]
        log.debug("Found VDC %s %s" % (location.getId(),
            location.getDescription()))
        login = LoginCredentials.builder() \
            .authenticateSudo(self.__config.getboolean(deploycommand,
                    "requires_sudo")) \
            .user(self.__config.get(deploycommand, "template_user")) \
            .password(self.__config.get(deploycommand, "template_pass")) \
            .build()
        return (location, compute.templateOptions()
            .overrideLoginCredentials(login))

    def _print_node_errors(self, ex):
        for error in ex.getExecutionErrors().values():
            print "Error %s" % error.getMessage()
        for error in ex.getNodeErrors().values():
            print "Error %s" % error.getMessage()


def load():
    """ Loads the current plugin """
    return MothershipPlugin()
