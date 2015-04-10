import os
from logging.handlers import RotatingFileHandler

__author__ = 'Alexander Pikovsky'


class RotatingFileHandlerExt(RotatingFileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=0):

        #ensure logging directory exists
        log_dir = os.path.dirname(filename)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        super(RotatingFileHandlerExt, self).__init__(filename, mode, encoding, delay)