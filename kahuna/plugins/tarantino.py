#!/usr/bin/env python

# Plugin adapted from: https://gist.github.com/2586413
# Original author: Enric Ruiz

from kahuna.abstract import AbsPlugin
from kahuna.utils.prettyprint import pprint_tasks
from optparse import OptionParser
import redis


class TarantinoPlugin(AbsPlugin):
    """ Tarantino plugin """

    def _commands(self):
        """ Get teh lsit of commands of the plugin """
        commands = {}
        commands['vm-tasks'] = self.vm_tasks
        return commands

    def _load_context(self):
        """ This plugin does not require an open context. """
        pass

    def vm_tasks(self, args):
        """ Dumps the Tarantino status from Redis """
        parser = OptionParser(usage="tarantino dump <options>",
                add_help_option=False)
        parser.add_option("-v", "--vm", dest="vm",
                 help="The id of the virtual machine to check")
        parser.add_option("-h", "--host", dest="host", default="localhost",
                help="The Redis host (default: localhost)")
        parser.add_option("-p", "--port", dest="port", type="int",
                default=6379, help="The Redis port (default: 6379)")
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

        tasks = []
        for task_key in task_keys:
            task = r.hgetall(task_key)
            job_keys = r.lrange(task['jobs'], 0, -1)
            jobs = map(lambda k: r.hgetall(k), job_keys)
            tasks.append((task, jobs))
        pprint_tasks(tasks)


def load():
    """ Loads the current plugin """
    return TarantinoPlugin()
