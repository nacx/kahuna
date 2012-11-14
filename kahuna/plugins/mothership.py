#!/usr/bin/env jython

from __future__ import with_statement  # jython 2.5.2 issue
import logging
import os
from java.io import File
from java.net import URI
from kahuna.abstract import AbsPlugin
from kahuna.config import ConfigLoader
from kahuna.utils.prettyprint import pprint_templates
from com.google.common.collect import Iterables
from optparse import OptionParser
from org.jclouds.abiquo.domain.cloud import VirtualAppliance
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.abiquo.predicates.cloud import VirtualAppliancePredicates
from org.jclouds.compute import RunNodesException
from org.jclouds.compute.predicates import NodePredicates
from org.jclouds.domain import LoginCredentials
from org.jclouds.io import Payloads
from org.jclouds.rest import AuthorizationException
from org.jclouds.scriptbuilder.domain import StatementList
from org.jclouds.scriptbuilder.domain import Statements
from org.jclouds.util import Strings2

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
        commands['deploy-wars'] = self.deploy_wars
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

            cookbooks = self.__config.get("deploy-chef", "cookbooks")
            with open(self.__scriptdir + "/configure-chef.sh", "r") as f:
                script = f.read() % {'cookbooks': cookbooks}

            log.info("Configuring node with cookbooks: %s..." % cookbooks)
            compute.runScriptOnNode(node.getId(), script)

            log.info("Done! You can access the admin console at: "
                    "http://%s:4040"
                    % Iterables.getOnlyElement(node.getPublicAddresses()))

            log.info("These are the certificates to access the API:")
            self._print_node_file(self._context, node,
                    "/etc/chef/validation.pem")
            self._print_node_file(self._context, node, "/etc/chef/webui.pem")

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

            self._upload_file_node(self._context, node, "/opt/abiquo/config",
                    options.props, True)

            log.info("Restarting Abiquo Tomcat...")
            compute.runScriptOnNode(node.getId(),
                    "service abiquo-tomcat restart")

            log.info("Done! Abiquo configured at: %s" %
                    Iterables.getOnlyElement(node.getPublicAddresses()))

        except RunNodesException, ex:
            self._print_node_errors(ex)

    def deploy_wars(self, args):
        """ Deploys and configures custom wars of the Abiquo platform """
        parser = OptionParser(usage="mothership deploy-wars <options>")
        parser.add_option('-l', '--local',
                help='Path to a local war file to deploy',
                action='store', dest='local')
        parser.add_option('-r', '--remote',
                help='Path to a remote file to deploy',
                action='store', dest='remote')
        parser.add_option('-n', '--number', type="int", default=1,
                help='Number of nodes to deploy (default 1)',
                action='store', dest='number')
        (options, args) = parser.parse_args(args)

        if not options.local and not options.remote:
            parser.print_help()
            return
        options.number = 1  # FIXME Remove when the multiple deploy is fixed

        compute = self._context.getComputeService()

        try:
            name = self.__config.get("deploy-wars", "template")
            log.info("Loading template...")
            vdc, template_options = self._template_options(compute,
                "deploy-wars")
            template = compute.templateBuilder() \
                .imageNameMatches(name) \
                .locationId(vdc.getId()) \
                .options(template_options) \
                .build()

            # Manually create the vapp to bypass the race condition in
            # AbiquoComputeSericeAdapter when creating multiple nodes
            self._create_vapp(vdc.getId(), "kahuna-wars")

            log.info("Deploying %s %s nodes to %s..." % (options.number,
                template.getImage().getName(), vdc.getDescription()))
            compute.createNodesInGroup("kahuna-wars",
                    options.number, template)

            log.info("Configuring nodes...")
            tomcat_uri = URI.create(self.__config.get("deploy-wars", "tomcat"))
            install_tomcat = Statements.extractTargzAndFlattenIntoDirectory(
                tomcat_uri, "/opt/abiquo/tomcat")

            bootstrap = StatementList(install_tomcat)
            responses = compute.runScriptOnNodesMatching(
                NodePredicates.inGroup("kahuna-wars"), bootstrap)

            log.info("Done!")
            for response in responses.entrySet():
                log.info("Node configured at: %s" %
                    Iterables.getOnlyElement(
                        response.getKey().getPublicAddresses()))

        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
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

            # Configuration values
            redishost = self.__config.get(config_section, "redis_host")
            redisport = self.__config.get(config_section, "redis_port")
            nfsto = self.__config.get(config_section, "nfs_to")
            nfsfrom = self.__config.get(config_section, "nfs_from")

            # abiquo-aim.ini
            self._complete_file("abiquo-aim.ini", {'redishost': redishost,
                'redisport': redisport, 'nfsto': nfsto})
            self._upload_file_node(self._context, node, "/etc/",
                "abiquo-aim.ini")

            # configure-aim-node.sh
            with open(self.__scriptdir + "/configure-aim-node.sh", "r") as f:
                script = f.read() % {'nfsfrom': nfsfrom, 'nfsto': nfsto}

            log.info("Configuring node...")
            compute.runScriptOnNode(node.getId(), script)

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

    def _print_node_file(self, context, node, file):
        ssh = context.getUtils().sshForNode().apply(node)
        try:
            ssh.connect()
            payload = ssh.get(file)
            log.info(file)
            log.info(Strings2.toStringAndClose(payload.getInput()))
        finally:
            if payload:
                payload.release()
            if ssh:
                ssh.disconnect()

    def _upload_file_node(self, context, node, destination, filename,
            abs_path=False):
        log.info("Waiting for ssh access on node...")
        ssh = context.getUtils().sshForNode().apply(node)
        path = filename if abs_path else self.__scriptdir + "/" + filename
        tmpfile = os.path.exists(path + ".tmp")
        file = File(path + ".tmp" if tmpfile else path)

        if abs_path:
            filename = os.path.basename(path)

        try:
            log.info("Uploading %s..." % filename)
            ssh.connect()
            ssh.put(destination + "/" + filename,
                    Payloads.newFilePayload(file))
        finally:
            if ssh:
                ssh.disconnect()
            if tmpfile:
                os.remove(file.getPath())

    def _complete_file(self, filename, dictionary):
        with open(self.__scriptdir + "/" + filename, "r") as f:
            content = f.read()
        content = content % dictionary
        with open(self.__scriptdir + "/" + filename + ".tmp", "w") as f:
            f.write(content)
        log.info("Configuration applied to %s" % filename)

    def _print_node_errors(self, ex):
        for error in ex.getExecutionErrors().values():
            print "Error %s" % error.getMessage()
        for error in ex.getNodeErrors().values():
            print "Error %s" % error.getMessage()

    def _create_vapp(self, vdc_id, vapp_name):
        vdc = self._context.getCloudService().getVirtualDatacenter(int(vdc_id))
        vapp = vdc.findVirtualAppliance(
            VirtualAppliancePredicates.name(vapp_name))
        if not vapp:
            log.debug("Creating virtual appliance %s in %s..." % (vapp_name,
                vdc.getName()))
            vapp = VirtualAppliance.builder(self._context.getApiContext(),
                vdc).name(vapp_name).build()
            vapp.save()


def load():
    """ Loads the current plugin """
    return MothershipPlugin()
