#!/usr/bin/env python

from kahuna.abstract import AbsPlugin
from optparse import OptionParser
import redis


class TarantinoPlugin(AbsPlugin):
    """ Tarantino plugin """
    def __init__(self):
        pass

    def dump(self, args):
        """ Dumps the Tarantino status from Redis """
        parser = OptionParser(usage="tarantino dump <options>",
                add_help_option=False)
        parser.add_option("-v", "--vm", dest="vm",
                 help="The id of the virtual machine to check")
        parser.add_option("-h", "--host", dest="host", default="localhost",
                help="The Redis host")
        parser.add_option("-p", "--port", dest="port", type="int",
                default=6379, help="The Redis port")
        parser.add_option("-a", "--all", dest="all",
                action="store_true",
                help="Show all tasks")

        (options, args) = parser.parse_args(args)
        if not options.vm:
            parser.print_help()
            return

        r = redis.Redis(options.host, options.port)
        range = -1 if options.all else 0
        task_keys = r.lrange("Owner:VirtualMachine:%s" % options.vm, 0, range)

        for task_key in task_keys:
            task = r.hgetall(task_key)
            print "Task: %s" % task['taskId']
            print "Type: %s" % task['type']
            print "State: %s" % task['state']
            print "Jobs:"

            job_keys = r.lrange(task['jobs'], 0, -1)
            for job_key in job_keys:
                job = r.hgetall(job_key)
                print "%s %s %s %s" % (job['id'], job['type'],
                        job['state'], job['rollbackState'])


def load():
    """ Loads the current plugin. """
    return TarantinoPlugin()
