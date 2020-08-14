import datetime
import logging


# Get date and time for logging timestamp.
def get_timestamp():
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.replace(' ', '_')
    timestamp = timestamp.replace(':', '-')
    timestamp = timestamp.replace('.', '-')
    return timestamp


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
