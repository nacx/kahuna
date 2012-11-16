#!/usr/bin/env jython

from __future__ import with_statement  # jython 2.5.2 issue
import logging
import os
from java.io import File
from kahuna.abstract import AbsPlugin
from kahuna.config import ConfigLoader
from kahuna.utils.prettyprint import pprint_templates
from com.google.common.collect import Iterables
from optparse import OptionParser
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.compute import RunNodesException
from org.jclouds.compute.options import RunScriptOptions
from org.jclouds.domain import LoginCredentials
from org.jclouds.io import Payloads
from org.jclouds.rest import AuthorizationException
from org.jclouds.scriptbuilder.domain import StatementList
from org.jclouds.scriptbuilder.domain import Statements
from org.jclouds.scriptbuilder.domain.chef import RunList
from org.jclouds.scriptbuilder.statements.chef import ChefSolo
from org.jclouds.scriptbuilder.statements.git import CloneGitRepo
from org.jclouds.scriptbuilder.statements.git import InstallGit
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
        commands['deploy-api'] = self.deploy_api
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

            # Generate the bootstrap script
            bootstrap = []
            with open(options.props, "r") as f:
                bootstrap.append(Statements.createOrOverwriteFile(
                    "/opt/abiquo/config/abiquo.properties", [f.read()]))

            bootstrap.append(Statements.exec("service abiquo-tomcat restart"))

            log.info("Restarting Abiquo Tomcat...")
            compute.runScriptOnNode(node.getId(), StatementList(bootstrap))

            log.info("Done! Abiquo configured at: %s" %
                    Iterables.getOnlyElement(node.getPublicAddresses()))

        except RunNodesException, ex:
            self._print_node_errors(ex)

    def deploy_api(self, args):
        """ Deploys and configures custom Abiquo APIs """
        parser = OptionParser(usage="mothership deploy-apis <options>")
        parser.add_option('-l', '--local',
                help='Path to a local api file to deploy',
                action='store', dest='local')
        parser.add_option('-d', '--datanode',
                help='Ip address of the data node (with rabbit, '
                'redis and zookeper)',
                action='store', dest='datanode')
        parser.add_option('-c', '--count', type="int", default=1,
                help='Number of nodes to deploy (default 1)',
                action='store', dest='count')
        (options, args) = parser.parse_args(args)

        if not options.local or not options.datanode:
            parser.print_help()
            return

        compute = self._context.getComputeService()

        try:
            name = self.__config.get("deploy-api", "template")
            log.info("Loading template...")
            vdc, template_options = self._template_options(compute,
                "deploy-api")
            template_options.overrideCores(
                self.__config.getint("deploy-api", "template_cores"))
            template_options.overrideRam(
                self.__config.getint("deploy-api", "template_ram"))
            template = compute.templateBuilder() \
                .imageNameMatches(name) \
                .locationId(vdc.getId()) \
                .options(template_options) \
                .build()

            log.info("Deploying %s %s nodes to %s..." % (options.count,
                template.getImage().getName(), vdc.getDescription()))

            # Due to the IpPoolManagement concurrency issue, we need to deploy
            # the nodes one by one
            nodes = []
            for i in xrange(options.count):
                node = Iterables.getOnlyElement(
                    compute.createNodesInGroup("kahuna-apis", 1, template))
                log.info("Created node %s at %s" % (node.getName(),
                    Iterables.getOnlyElement(node.getPublicAddresses())))
                self._upload_binary_file(self._context, node, "/tmp",
                    options.local)
                nodes.append(node)

            # Build the bootstrap scripts
            log.info("Cooking nodes with Chef to join the cluster at %s..."
                    % options.datanode)

            bootstrap = []
            bootstrap.append(Statements.exec("service tomcat6 stop"))

            # Copy wars to webapps directory
            bootstrap.append(Statements.exec(
                "ensure_cmd_or_install_package_apt unzip unzip"))
            bootstrap.append(Statements.exec(
                "mv /tmp/*.war /var/lib/tomcat6/webapps"))
            bootstrap.append(Statements.exec(
                "for f in /var/lib/tomcat6/webapps/*.war; "
                "do unzip -d ${f%.war} $f; done"))

            # Configure the context
            with open("%s/context.xml" % self.__scriptdir, "r") as f:
                context_config = f.read() % {'dbhost': options.datanode}
            bootstrap.append(Statements.createOrOverwriteFile(
                "/etc/tomcat6/Catalina/localhost/api.xml", [context_config]))

            # Upload abiquo.properties
            with open("%s/abiquo.properties" % self.__scriptdir, "r") as f:
                abiquo_props = f.read() % {
                    'rabbit': options.datanode,
                    'redis': options.datanode,
                    'zookeeper': options.datanode
                }
            bootstrap.append(Statements.exec("{md} /opt/abiquo/config"))
            bootstrap.append(Statements.createOrOverwriteFile(
                "/opt/abiquo/config/abiquo.properties", [abiquo_props]))

            # Upload tomcat libraries
            bootstrap.append(Statements.exec(
                "wget -O /usr/share/tomcat6/lib/abiquo.jar "
                "http://10.60.20.42/2.4/tomcat/abiquo-tomcat.jar"))
            bootstrap.append(Statements.exec(
                "wget -O /usr/share/tomcat6/lib/mysql.jar "
                "http://repo1.maven.org/maven2/mysql/mysql-connector-java/"
                "5.1.10/mysql-connector-java-5.1.10.jar"))

            # Configure the Abiquo Listener
            bootstrap.append(Statements.exec("sed -i -e "
                "'/GlobalResourcesLifecycleListener/a <Listener className="
                "\"com.abiquo.listeners.AbiquoConfigurationListener\"/>' "
                "/etc/tomcat6/server.xml"))

            bootstrap.append(Statements.exec("service tomcat6 start"))

            # Prepare the Chef cookbooks in the node
            cloneJava = CloneGitRepo.builder() \
                .repository("git://github.com/opscode-cookbooks/java.git") \
                .directory("/var/chef/cookbooks/java") \
                .build()
            cloneTomcat = CloneGitRepo.builder() \
                .repository("git://github.com/abiquo/tomcat.git") \
                .branch("ajp") \
                .directory("/var/chef/cookbooks/tomcat") \
                .build()

            runlist = RunList.builder().recipe("java").recipe("tomcat").build()

            javaopts = self.__config.get("deploy-api", "tomcat_opts")
            with open("%s/api-node.json" % self.__scriptdir) as f:
                node_config = f.read()

            responses = []
            for i, node in enumerate(nodes):
                attrs = node_config % {
                    "javaopts": javaopts,
                    "ajpport": 10000 + i,
                    "jvmroute": "node%s" % i,
                    "dbhost": options.datanode
                }
                chef = ChefSolo.builder() \
                    .jsonAttributes(attrs) \
                    .runlist(runlist) \
                    .build()
                # Bootstrap all nodes concurrently
                boot = [InstallGit(), cloneJava, cloneTomcat, chef] + bootstrap
                responses.append(compute.submitScriptOnNode(node.getId(),
                    StatementList(boot), RunScriptOptions.NONE))

            # Wait until all the bootstrao scripts finish
            for i, future in enumerate(responses):
                result = future.get()
                log.info("%s node at %s -> %s" % (node.getName(),
                    Iterables.getOnlyElement(nodes[i].getPublicAddresses()),
                    "OK" if result.getExitStatus() == 0 else "FAILED"))
            log.info("Done!")

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

            bootstrap = []

            with open(self.__scriptdir + "/abiquo-aim.ini", "r") as f:
                aim_config = f.read() % {'redishost': redishost,
                    'redisport': redisport, 'nfsto': nfsto}
            bootstrap.append(Statements.createOrOverwriteFile(
                "/etc/abiquo-adim.ini", [aim_config]))

            with open(self.__scriptdir + "/configure-aim-node.sh", "r") as f:
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

    def _upload_binary_file(self, context, node, destination, filepath):
        log.info("Waiting for ssh access on node %s..." % node.getName())
        ssh = context.getUtils().sshForNode().apply(node)
        filename = os.path.basename(filepath)
        file = File(filepath)
        try:
            log.info("Uploading %s to %s..." % (filename, node.getName()))
            ssh.connect()
            ssh.put(destination + "/" + filename,
                    Payloads.newFilePayload(file))
        finally:
            if ssh:
                ssh.disconnect()

    def _print_node_errors(self, ex):
        for error in ex.getExecutionErrors().values():
            print "Error %s" % error.getMessage()
        for error in ex.getNodeErrors().values():
            print "Error %s" % error.getMessage()


def load():
    """ Loads the current plugin """
    return MothershipPlugin()
