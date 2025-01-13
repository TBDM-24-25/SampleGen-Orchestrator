import logging
import os

class GlobalLogger:
    '''
    The class provides a global logger instance.
    '''

    # classattribute
    _logger = None

    @staticmethod
    def get_logger(filename='logs/app.log', level=logging.INFO, filemode='a') -> logging.Logger:
        if GlobalLogger._logger is None:
            # Ensure the directory exists
            log_dir = os.path.dirname(filename)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            logging.basicConfig(filename=filename,
                                level=level,
                                filemode=filemode,
                                encoding='utf-8',
                                format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')

            GlobalLogger._logger = logging.getLogger('global_logger')

        return GlobalLogger._logger
