#!/usr/bin/env jython

from __future__ import with_statement
import logging
from kahuna.abstract import AbsPlugin
from kahuna.config import ConfigLoader
from kahuna.utils.prettyprint import pprint_templates
from kahuna.utils import hostname
from kahuna.utils import jenkins
from kahuna.utils import ntp
from kahuna.utils import rabbitmq
from kahuna.utils import redis
from kahuna.utils import ssh
from kahuna.utils.tomcat import TomcatScripts
from com.google.common.base import Predicate
from com.google.common.collect import Iterables
from optparse import OptionParser
from org.jclouds.abiquo.domain.exception import AbiquoException
from org.jclouds.compute import RunNodesException
from org.jclouds.compute.options import RunScriptOptions
from org.jclouds.domain import LoginCredentials
from org.jclouds.rest import AuthorizationException
from org.jclouds.scriptbuilder.domain import StatementList
from org.jclouds.scriptbuilder.domain import Statements

log = logging.getLogger('kahuna')


class ScalabilityPlugin(AbsPlugin):
    """ Scalability plugin """
    def __init__(self):
        self.__config = ConfigLoader().load("scalability.conf",
                "config/scalability.conf")

    # Override the endpoint address and credentials to create the
    # context
    def _config_overrides(self):
        overrides = {}
        overrides['address'] = self.__config.get("scalability", "host")
        overrides['user'] = self.__config.get("scalability", "user")
        overrides['password'] = self.__config.get("scalability", "password")
        return overrides

    # Override the commands factory method because the command names we want
    # can not be used as valid python class method names
    def _commands(self):
        """ Returns the provided commands, mapped to handler methods """
        commands = {}
        commands['reset-datanode'] = self.reset_datanode
        commands['deploy-api'] = self.deploy_api
        commands['deploy-rs'] = self.deploy_rs
        return commands

    def reset_datanode(self, args):
        """ Resets the datanode (database, redis and rabbitmq) """
        parser = OptionParser(usage="scalability reset-datanode <options>")
        parser.add_option('-j', '--jenkins-version',
                help='Download the database from the given version '
                'from Jenkins', action='store', dest='jenkins')
        parser.add_option('-d', '--datanode',
                help='Ip address of the data node (with rabbit, '
                'redis and zookeper)', action='store', dest='datanode')
        parser.add_option('-u', '--login-user',
                help='Username used to access the datanode',
                action='store', dest='user')
        parser.add_option('-p', '--login-password',
                help='Password used to access the datanode',
                action='store', dest='password')

        (options, args) = parser.parse_args(args)

        if not options.datanode or not options.jenkins \
                or not options.user or not options.password:
            parser.print_help()
            return

        compute = self._context.getComputeService()
        license = self.__config.get("reset-datanode", "license")
        predicate = NodeHasIp(options.datanode)

        try:
            script = []
            script.append(jenkins._download_database(options.jenkins))
            script.append(Statements.exec(
                "mysql -u %s kinton </tmp/kinton-schema-%s.sql" %
                (options.user, options.jenkins)))
            script.append(Statements.exec(
                'mysql -u %s kinton -e "'
                'insert into license (data, version_c) values (\'%s\', 1)"' %
                (options.user, license)))
            script.append(redis.run("flushall"))
            script.extend(rabbitmq.reset())
            print "Resetting datanode at: %s" % options.datanode
            options = RunScriptOptions.Builder \
                .overrideLoginUser(options.user) \
                .overrideLoginPassword(options.password)
            compute.runScriptOnNodesMatching(predicate,
                StatementList(script), options)
        except RunNodesException, ex:
            self._print_node_errors(ex)

    def deploy_api(self, args):
        """ Deploys and configures custom Abiquo APIs """
        parser = OptionParser(usage="scalability deploy-api <options>")
        parser.add_option('-f', '--file',
                help='Path to a local api file to deploy',
                action='store', dest='file')
        parser.add_option('-j', '--jenkins-version',
                help='Download the api from the given version from Jenkins',
                action='store', dest='jenkins')
        parser.add_option('-d', '--datanode',
                help='Ip address of the data node (with rabbit, '
                'redis and zookeper)',
                action='store', dest='datanode')
        parser.add_option('-b', '--balancer',
                help='Ip address of the load balancer node',
                action='store', dest='balancer')
        parser.add_option('-c', '--count', type="int", default=1,
                help='Number of nodes to deploy (default 1)',
                action='store', dest='count')
        (options, args) = parser.parse_args(args)

        if options.file and options.jenkins:
            print "Cannot use -f and -j together"
            parser.print_help()
            return

        if not options.file and not options.jenkins \
                or not options.datanode or not options.balancer:
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

            java_opts = self.__config.get("deploy-api", "tomcat_opts")
            boundary_org = self.__config.get("deploy-api", "boundary_org")
            boundary_key = self.__config.get("deploy-api", "boundary_key")
            newrelic_key = self.__config.get("deploy-api", "newrelic_key")
            tomcat = TomcatScripts(boundary_org, boundary_key, newrelic_key)

            log.info("Deploying %s %s nodes to %s..." % (options.count,
                template.getImage().getName(), vdc.getDescription()))

            # Due to the IpPoolManagement concurrency issue, we need to deploy
            # the nodes one by one
            nodes = []
            responses = []
            for i in xrange(options.count):
                node = Iterables.getOnlyElement(
                    compute.createNodesInGroup("kahuna-api", 1, template))
                log.info("Created node %s at %s" % (node.getName(),
                    Iterables.getOnlyElement(node.getPublicAddresses())))
                if options.file:
                    ssh.upload(self._context, node, "/tmp", options.file)
                nodes.append(node)

                log.info("Cooking %s with Chef in the background..." %
                    node.getName())
                tomcat_config = {
                    "rabbit": options.datanode,
                    "redis": options.datanode,
                    "zookeeper": options.datanode,
                    "module": "api",
                    "db-host": options.datanode,
                    #"syslog": options.balancer,
                    "ajp_port": 10000 + i,
                    "java-opts": java_opts
                }
                bootstrap = []
                bootstrap.extend(hostname.configure(node))
                bootstrap.append(ntp.install())
                if options.jenkins:
                    bootstrap.extend(jenkins._download_war(
                        options.jenkins, "api"))
                bootstrap.extend(tomcat.install_and_configure(node,
                    tomcat_config, self._install_local_wars))
                responses.append(compute.submitScriptOnNode(node.getId(),
                    StatementList(bootstrap), RunScriptOptions.NONE))

            log.info("Waiting until all nodes are configured...")
            for i, future in enumerate(responses):
                result = future.get()
                log.info("%s node at %s -> %s" % (nodes[i].getName(),
                    Iterables.getOnlyElement(nodes[i].getPublicAddresses()),
                    "OK" if result.getExitStatus() == 0 else "FAILED"))
            log.info("Done!")

        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        except RunNodesException, ex:
            self._print_node_errors(ex)

    def deploy_rs(self, args):
        """ Deploys and configures custom Abiquo Remote Services """
        parser = OptionParser(usage="scalability deploy-rs <options>")
        parser.add_option('-j', '--jenkins-version',
                help='Download the given version of the wars from Jenkins',
                action='store', dest='jenkins')
        parser.add_option('-r', '--rabbit', help='The RabbitMQ host',
                action='store', dest='rabbit')
        parser.add_option('-n', '--nfs', help='The NFS to mount',
                action='store', dest='nfs')
        parser.add_option('-c', '--count', type="int", default=1,
                help='Number of nodes to deploy (default 1)',
                action='store', dest='count')
        parser.add_option('-s', '--hypervisor-sessions', type="int", default=2,
                help='Number of concurrent hypervisor sessions (default 2)',
                action='store', dest='hypervisorsessions')
        parser.add_option('-l', '--war-list',
                help='Upload only those wars (default all rs)',
                default='rs', action='store', dest='wars')
        (options, args) = parser.parse_args(args)

        if not options.jenkins or not options.nfs or not options.rabbit:
            parser.print_help()
            return

        compute = self._context.getComputeService()

        try:
            name = self.__config.get("deploy-rs", "template")
            log.info("Loading template...")
            vdc, template_options = self._template_options(compute,
                "deploy-rs")
            template_options.overrideCores(
                self.__config.getint("deploy-rs", "template_cores"))
            template_options.overrideRam(
                self.__config.getint("deploy-rs", "template_ram"))
            template = compute.templateBuilder() \
                .imageNameMatches(name) \
                .locationId(vdc.getId()) \
                .options(template_options) \
                .build()

            java_opts = self.__config.get("deploy-rs", "tomcat_opts")
            boundary_org = self.__config.get("deploy-rs", "boundary_org")
            boundary_key = self.__config.get("deploy-rs", "boundary_key")
            newrelic_key = self.__config.get("deploy-rs", "newrelic_key")
            tomcat = TomcatScripts(boundary_org, boundary_key, newrelic_key)

            log.info("Deploying %s %s nodes to %s..." % (options.count,
                template.getImage().getName(), vdc.getDescription()))

            # Due to the IpPoolManagement concurrency issue, we need to deploy
            # the nodes one by one
            nodes = []
            responses = []
            for i in xrange(options.count):
                node = Iterables.getOnlyElement(
                    compute.createNodesInGroup("kahuna-rs", 1, template))
                log.info("Created node %s at %s" % (node.getName(),
                    Iterables.getOnlyElement(node.getPublicAddresses())))
                nodes.append(node)

                log.info("Cooking %s with Chef in the background..." %
                    node.getName())
                tomcat_config = {
                    "rabbit": options.rabbit,
                    "datacenter": node.getName(),
                    "nfs": options.nfs,
                    "nfs-mount": True,
                    "java-opts": java_opts,
                    "hypervisor-sessions": options.hypervisorsessions
                }
                install_tomcat = tomcat.install_and_configure(node,
                    tomcat_config, self._install_jenkins_wars(options.jenkins,
                        options.wars))
                bootstrap = hostname.configure(node) + \
                    [ntp.install()] + redis.install("2.6.4") + install_tomcat
                responses.append(compute.submitScriptOnNode(node.getId(),
                    StatementList(bootstrap), RunScriptOptions.NONE))

            log.info("Waiting until all nodes are configured...")
            for i, future in enumerate(responses):
                result = future.get()
                log.info("%s node at %s -> %s" % (nodes[i].getName(),
                    Iterables.getOnlyElement(nodes[i].getPublicAddresses()),
                    "OK" if result.getExitStatus() == 0 else "FAILED"))
            log.info("Done!")

        except (AbiquoException, AuthorizationException), ex:
            print "Error: %s" % ex.getMessage()
        except RunNodesException, ex:
            self._print_node_errors(ex)

    def _template_options(self, compute, deploycommand):
        locations = compute.listAssignableLocations()
        vdc = self.__config.get("scalability", "vdc")
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

    def _install_local_wars(self):
        """ Copies uploaded wars in the tomcat webapps directory """
        script = []
        script.append(Statements.exec(
            "ensure_cmd_or_install_package_apt unzip unzip"))
        script.append(Statements.exec(
            "mv /tmp/*.war /var/lib/tomcat6/webapps"))
        script.append(Statements.exec(
            "for f in /var/lib/tomcat6/webapps/*.war; "
            "do unzip -d ${f%.war} $f; done"))
        return script

    def _install_jenkins_wars(self, version, wars="rs"):
        """ Downloads the Remote Services wars from Jenkins """
        def jenkins_download():
            script = []
            for war in wars.split(","):
                script.extend(jenkins._download_war(version, war))
            script.extend(self._install_local_wars())
            return script
        return jenkins_download

    def _print_node_errors(self, ex):
        for error in ex.getExecutionErrors().values():
            print "Error %s" % error.getMessage()
        for error in ex.getNodeErrors().values():
            print "Error %s" % error.getMessage()


class NodeHasIp(Predicate):
    """ Implements a NodeMetadata predicate to find nodes by Ip """
    def __init__(self, ip):
        self.__ip = ip

    def apply(self, node_metadata):
        return node_metadata.getPublicAddresses().contains(self.__ip)


def load():
    """ Loads the current plugin """
    return ScalabilityPlugin()
