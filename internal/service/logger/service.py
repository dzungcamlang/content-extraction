import logging

logger = None

class Logger():
    def __init__(self):
        global logger
        if logger is None:
            self.logger = logging.getLogger('crawler')
            hdlr = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(module)s:%(filename)s:%(lineno)s] - %(message)s')
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
            self.logger.setLevel(logging.DEBUG)

            logger = self.logger
        else:
            self.logger = logger
