#!/usr/bin/env jython

def singleton(cls):
    """ Singleton decorator. """
    instances = {}
    def instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return instance

