import logging
import os

FORMAT = "%(levelname)s:ABE: 🎩 %(message)s"
logging.basicConfig(format=FORMAT)

if 'LOG_LEVEL' in os.environ:
    LOG_LEVEL = os.environ.get('LOG_LEVEL').upper()
    level = getattr(logging, LOG_LEVEL.upper(), None)
    if level:
        logging.basicConfig(level=level)
    else:
        logging.warning('Unknown LOG_LEVEL %s', LOG_LEVEL)
