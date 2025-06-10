import logging

class Logger:
    def __init__(self, name='MyLogger'):
        # Set up the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create a formatter and set it for the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(ch)

    @property
    def log(self):
        return self.logger
logger = Logger() 