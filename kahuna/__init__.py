import logging
from config import Config

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)

# Load the singleton configuration instance to initialize
# the 'kahuna' logger
Config()

