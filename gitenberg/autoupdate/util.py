import logging
import logging.handlers

FORMAT = '%(asctime)-15s %(message)s'

def setup_logging(arguments):
    """ creates a logger with our hard-coded configuration
    takes: a docopt arguments object instance
    """
    logger = logging.getLogger('')
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    if '--logging' in arguments:
      log_level = arguments['--logging']
      if log_level == 'debug':
        logger.setLevel(logging.DEBUG)
      elif log_level == 'info':
        logger.setLevel(logging.INFO)
      elif log_level == 'error':
        logger.setLevel(logging.ERROR)
    if '--log_file' in arguments:
      handler = logging.handlers.WatchedFileHandler(arguments['--log_file'])
      logger.addHandler(handler)
