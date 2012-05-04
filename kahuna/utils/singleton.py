#!/usr/bin/env jython

import logging

log = logging.getLogger('kahuna')


def singleton(cls):
    """ Singleton decorator """
    instances = {}

    def instance():
        if cls not in instances:
            instances[cls] = cls()
            log.debug("Loaded singleton instance of %s" % cls)
        return instances[cls]

    return instance
