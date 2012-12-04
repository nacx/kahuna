#!/usr/bin/env jython

from org.jclouds.scriptbuilder.domain import Statements


def reset():
    """ Resets a RabbitMQ instance """
    return [Statements.exec("rabbitmqctl stop_app"),
        Statements.exec("rabbitmqctl reset"),
        Statements.exec("rabbitmqctl start_app")]
