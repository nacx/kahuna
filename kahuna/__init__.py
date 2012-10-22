import logging
from config import Config
from ch.qos.logback.classic import Level
from org.slf4j import LoggerFactory


# Configure the python logger
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)

# Disable the Java logger
java_logger_context = LoggerFactory.getILoggerFactory()
root_logger = java_logger_context.getLogger("ROOT")
root_logger.setLevel(Level.OFF)

# Load the singleton configuration instance to initialize
# the 'kahuna' logger
Config()
