#!/usr/bin/env jython

from __future__ import with_statement
import git
import hostname
from org.jclouds.scriptbuilder.domain import Statements
from org.jclouds.scriptbuilder.domain.chef import DataBag
from org.jclouds.scriptbuilder.domain.chef import RunList
from org.jclouds.scriptbuilder.statements.chef import ChefSolo


class TomcatScripts:
    """ Generates Tomcat install and configure scripts """
    def __init__(self, boundary_org, boundary_key, newrelic_key):
        self.__templatedir = "kahuna/utils/templates"
        self.__abiquojar = "http://10.60.20.42/2.4/tomcat/abiquo-tomcat.jar"
        self.__mysqljar = "http://repo1.maven.org/maven2/mysql/" + \
            "mysql-connector-java/5.1.10/" + \
            "mysql-connector-java-5.1.10.jar"
        self._boundary_org = boundary_org
        self._boundary_key = boundary_key
        self._newrelic_key = newrelic_key

    def start(self):
        """ Generates the start command """
        return Statements.exec("service tomcat6 start")

    def stop(self):
        """ Generates the stop command """
        return Statements.exec("service tomcat6 stop")

    def configure_context(self, module, dbhost, dbuser="root", dbpass="",
            jndi="jdbc/abiquoDB"):
        """ Configures the context of a given module """
        with open("%s/context.xml" % self.__templatedir, "r") as f:
            context_config = f.read() % {
                'dbhost': dbhost,
                'dbuser': dbuser,
                'dbpass': dbpass,
                'jndi': jndi
            }
        return Statements.createOrOverwriteFile(
            "/etc/tomcat6/Catalina/localhost/%s.xml" % module,
            [context_config])

    def configure_logging(self, module, sysloghost):
        """ Configures the logger of a given module """
        with open("%s/logback.xml" % self.__templatedir, "r") as f:
            log_config = f.read() % {'sysloghost': sysloghost}
        return Statements.createOrOverwriteFile(
            "/var/lib/tomcat6/webapps/%s/WEB-INF/classes/logback.xml" % module,
            [log_config])

    def configure_abiquo_props(self, rabbit, redis, zookeeper):
        """ Configures the abiquo.properties file """
        with open("%s/abiquo.properties" % self.__templatedir, "r") as f:
            abiquo_props = f.read() % {
                'rabbit': rabbit,
                'redis': redis,
                'zookeeper': zookeeper
            }
        script = []
        script.append(Statements.exec("{md} /opt/abiquo/config"))
        script.append(Statements.createOrOverwriteFile(
            "/opt/abiquo/config/abiquo.properties", [abiquo_props]))
        return script

    def upload_libs(self):
        """ Uploads necessary libraries to Tomcat lib dir """
        script = []
        script.append(Statements.exec(
            "wget -O /usr/share/tomcat6/lib/abiquo.jar %s" % self.__abiquojar))
        script.append(Statements.exec(
            "wget -O /usr/share/tomcat6/lib/mysql.jar %s" % self.__mysqljar))
        return script

    def configure_abiquo_listener(self):
        """ Adds the Abiquo listener to server.xml """
        return Statements.exec("sed -i -e "
            "'/GlobalResourcesLifecycleListener/a <Listener className="
            "\"com.abiquo.listeners.AbiquoConfigurationListener\"/>' "
            "/etc/tomcat6/server.xml")

    def install(self, node, ajp_port, java_opts):
        """ Installs Tomcat and the monitoring tools using Chef """
        # Tomcat manager configuration
        with open("%s/tomcat-users.json" % self.__templatedir) as f:
            tomcat_users = DataBag.builder() \
                .name("tomcat_users") \
                .item("abiquo", f.read()) \
                .build()

        # Node configuration
        with open("%s/tomcat-node.json" % self.__templatedir) as f:
            attrs = f.read() % {
                'javaopts': java_opts,
                'ajpport': ajp_port,
                'jvmroute': "node%d" % ajp_port,
                'bprobe_org': self._boundary_org,
                'bprobe_key': self._boundary_key,
                'newrelic_key': self._newrelic_key
            }

        # Recipes to install
        runlist = RunList.builder() \
            .recipe("java") \
            .recipe("tomcat") \
            .recipe("tomcat::users") \
            .recipe("bprobe") \
            .recipe("newrelic") \
            .build()

        chef = ChefSolo.builder() \
            .defineDataBag(tomcat_users) \
            .jsonAttributes(attrs) \
            .runlist(runlist) \
            .build()

        return [git.install()] + self._clone_required_cookbooks() + [chef]

    def install_and_configure(self, data_node, load_balancer, node, module,
            ajp_port, java_opts, install_wars):
        """ Installs and configures a Tomcat and the monitoring tools """
        script = []
        script.extend(hostname.configure(node))
        script.extend(self.install(node, ajp_port, java_opts))
        script.append(self.stop())
        script.extend(install_wars())
        script.append(self.configure_context(module, data_node))
        script.append(self.configure_logging(module, load_balancer))
        script.extend(self.configure_abiquo_props(data_node, data_node,
            data_node))
        script.append(self.configure_abiquo_listener())
        script.extend(self.upload_libs())
        script.append(self.start())
        return script

    def _clone_required_cookbooks(self):
        """ Clone the cookbooks required to install Tomcat """
        script = []
        # Tomcat
        script.append(git.clone_opscode_cookbook("java"))
        script.append(git.clone("git://github.com/abiquo/tomcat.git",
            "/var/chef/cookbooks/tomcat", "ajp"))
        # Monitoring
        script.append(git.clone_opscode_cookbook("build-essential"))
        script.append(git.clone_opscode_cookbook("apt"))
        script.append(git.clone_opscode_cookbook("xml"))
        script.append(git.clone_opscode_cookbook("mysql"))
        script.append(git.clone_opscode_cookbook("php"))
        script.append(git.clone_opscode_cookbook("python"))
        script.append(git.clone_opscode_cookbook("apache2"))
        script.append(
            git.clone("git://github.com/escapestudios/chef-newrelic.git",
            "/var/chef/cookbooks/newrelic"))
        script.append(
            git.clone("git://github.com/boundary/boundary_cookbooks.git",
            "/tmp/boundary"))
        # Use only the bprobe cookbook
        script.append(Statements.exec(
            "mv /tmp/boundary/bprobe /var/chef/cookbooks/"))
        return script
