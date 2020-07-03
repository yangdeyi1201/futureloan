import logging
from config import paths


def get_logger(logger_name='own_logger',
               file_path=paths.LOGS_PATH/'log.log',
               logger_level='DEBUG', console_level='DEBUG', file_level='INFO',
               fmt='<%(asctime)s>--<%(filename)s>--line:%(lineno)d--<%(levelname)s>--%(message)s'
               ):

    logger = logging.getLogger(logger_name)  # 从内存取出名为 logger_name 的日志收集器，若无名为 logger_name 的日志收集器则会新建
    logger.handlers.clear()  # 清除日志收集器已有的处理器
    logger.setLevel(logger_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)
    console_handler.setFormatter(logging.Formatter(fmt))

    if file_path:
        file_handler = logging.FileHandler(file_path, 'a', encoding='UTF-8')
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)
        file_handler.setFormatter(logging.Formatter(fmt))

    return logger
