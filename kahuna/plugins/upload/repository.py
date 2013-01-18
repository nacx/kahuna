#!/usr/bin/env jython

from __future__ import with_statement
from definition import DefinitionGenerator
import logging
import os
import random
import select
import shutil
import string
import SimpleHTTPServer
import SocketServer
from threading import Thread

log = logging.getLogger("kahuna")


class TransientRepository:
    """ A transient tempalte repository """
    def __init__(self, basedir="/tmp"):
        """ Sets the base directory to serve """
        rnd = ''.join(random.choice(string.letters) for i in xrange(5))
        self._repodir = basedir + '/repo-' + rnd
        self.__server = None

    def create(self, disk, config):
        """ Creates the repository structure """
        if not os.path.exists(self._repodir):
            os.makedirs(self._repodir)
        shutil.copy(disk, self._repodir)
        ovf = DefinitionGenerator().generate(config)
        with open("%s/ovf.xml" % self._repodir, "w") as f:
            f.write(ovf)

    def destroy(self):
        """ Destroys the repository and its contents """
        if self.__server:
            self.stop()
        shutil.rmtree(self._repodir)

    def start(self, address="localhost", port=8888):
        """ Start serving the contents of the repository """
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.__server = RepositoryServer((address, port), handler)
        log.debug("Serving repository at %s in port %s" %
            (self._repodir, port))
        os.chdir(self._repodir)
        # Start in a new thread to avoid blocking
        thread = Thread(target=self.__server.serve_until_stopped, args=[])
        thread.start()

    def stop(self):
        """ Stop serving the contents of the repository """
        if self.__server:
            log.debug("Shutting down repository server")
            self.__server.shutdown()
            self.__server = None


class RepositoryServer(SocketServer.TCPServer):
    """ Extends the TCP server to add the shutdown missing in Python 2.5 """
    def serve_until_stopped(self):
        """ Starts listening for requests """
        self.socket.setblocking(0)
        self.serving = True
        while self.serving:
            read, write, exception = select.select([self], [], [], 0.5)
            if read:
                self.handle_request()

    def shutdown(self):
        """ Stops listening for requests """
        self.serving = False
