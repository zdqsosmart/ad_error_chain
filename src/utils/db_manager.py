import os
import logging

class Logger2File:
    _instance = {}

    @classmethod
    def get_logger(cls,logger_name:str,logging_file:Optional[str] = None) -> logging.Logger:
        if logger_name in cls._instances:
            return cls._instances[logger_name]
        if logging_file is None:
            path = "./logs"
        os.makedirs(path,exist_ok=True)

        # 创建日志器
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 可选: 添加文件处理器
        if logging_file:
            file_handler = logging.FileHandler(logging_file,encoding="UTF-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        cls._instance[logger_name] = logger
        return logger



class PostgreManager:
    pass

class Redis:
