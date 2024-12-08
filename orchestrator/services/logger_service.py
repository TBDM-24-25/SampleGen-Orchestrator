import logging


class GlobalLogger:
    '''
    The class provides a global logger instance.

        Attributes:
            logger (logging.logger): The global logger instance   
    '''

    def __init__(self, filename: str, level: int = logging.INFO):
        '''
        The function initializes the global logger instance whilst providing some
        level of customization.

            Parameters:
                filename (str): Path to the logfile
                level: (int): Log level (e.g. logging.INFO, logging.DEBUG) (default: logging.INFO)
            Returns:
                None
        '''
        logging.basicConfig(filename=filename,
                            level=level,
                            filemode='w',
                            encoding='utf-8',
                            format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger()

    def get_logger(self) -> logging.Logger:
        '''
        The function returns the global logger instance.
            Returns:
                logger (logging.Logger): The global logger instance
        '''
        return self.logger
