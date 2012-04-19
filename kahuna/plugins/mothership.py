#!/usr/bin/env jython

import logging
from kahuna.config import ConfigLoader
from com.google.common.collect import Iterables
from org.jclouds import ContextBuilder
from org.jclouds.abiquo import AbiquoApiMetadata
from org.jclouds.abiquo import AbiquoContext
from org.jclouds.compute import RunNodesException
from org.jclouds.domain import LoginCredentials
from org.jclouds.logging.config import NullLoggingModule
from org.jclouds.util import Strings2
from org.jclouds.ssh.jsch.config import JschSshClientModule

log = logging.getLogger('kahuna')


class MothershipPlugin:
    """ Mothership plugin. """
    def __init__(self):
        self.__endpoint = "http://mothership.bcn.abiquo.com/api"
        self.__config = ConfigLoader().load("mothership.conf",
                "config/mothership.conf")
        self.__scriptdir = "kahuna/plugins/mothership"

    def commands(self):
        """ Returns the provided commands, mapped to handler methods. """
        commands = {}
        commands['deploy-chef'] = self.deploy_chef
        return commands

    def deploy_chef(self, args):
        """ Deploys and configures the Chef Server. """
        context = self._create_context()
        compute = context.getComputeService()

        try:
            name = self.__config.get("deploy-chef", "template")
            log.info("Loading template: %s" % name)
            options = self._template_options(compute)
            template = compute.templateBuilder() \
                    .imageNameMatches(name) \
                    .options(options.blockOnPort(4000, 60)) \
                    .build()

            log.info("Deploying node...")
            node = Iterables.getOnlyElement(
                    compute.createNodesInGroup("jclouds-chef", 1, template))

            f = open(self.__scriptdir + "/configure-chef.sh", "r")
            script_contents = f.read()
            f.close()
            cookbooks = self.__config.get("deploy-chef", "cookbooks")
            script = "COOKBOOKS=(%s)\n%s" % (cookbooks, script_contents)

            log.info("Configuring node with cookbooks: %s..." % cookbooks)
            compute.runScriptOnNode(node.getId(), script)

            log.info("Chef Server configured!")
            log.info("You can access the admin console at: http://%s:4040"
                    % Iterables.getOnlyElement(node.getPrivateAddresses()))

            log.info("These are the certificates to access the API:")
            self._print_node_file(context, node, "/etc/chef/validation.pem")
            self._print_node_file(context, node, "/etc/chef/webui.pem")

        except RunNodesException, ex:
            for error in ex.getExecutionErrors().values():
                print "Error %s" % error.getMessage()
            for error in ex.getNodeErrors().values():
                print "Error %s" % error.getMessage()
        finally:
            context.close()

    def _create_context(self):
        user = self.__config.get("mothership", "user")
        password = self.__config.get("mothership", "password")
        return ContextBuilder.newBuilder(AbiquoApiMetadata()) \
                .endpoint(self.__endpoint) \
                .credentials(user, password) \
                .modules([JschSshClientModule(), NullLoggingModule()]) \
                .build(AbiquoContext)

    def _template_options(self, compute):
        login = LoginCredentials.builder() \
                .authenticateSudo(self.__config.getboolean("deploy-chef",
                    "requires_sudo")) \
                .user(self.__config.get("deploy-chef", "template_user")) \
                .password(self.__config.get("deploy-chef", "template_pass")) \
                .build()
        return compute.templateOptions() \
                .overrideLoginCredentials(login) \
                .virtualDatacenter(self.__config.get("mothership", "vdc"))

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


def load():
    """ Loads the current plugin. """
    return MothershipPlugin()
