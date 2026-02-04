import logging
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv("../../.env")


class _Logger2File:
    _instances = {}

    @classmethod
    def get_logger(cls, logger_name: str, logging_file: Optional[str] = None) -> logging.Logger:
        if logger_name in cls._instances:
            return cls._instances[logger_name]
        if logging_file is None:
            logging_file = "./logs"
        # os.makedirs(logging_file, exist_ok=True)

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

            file_handler = logging.FileHandler(logging_file, encoding="UTF-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        cls._instances[logger_name] = logger
        return logger

def getMyLog():
    """返回一个log对象"""
    name = os.getenv("LOG_NAME")
    path = os.getenv("LOG_PATH")
    date_ = datetime.now().strftime("%Y%m%d")
    log_file= f"{path}/{name}_{date_}.log"
    logger = _Logger2File.get_logger(name, log_file)
    return logger



if __name__ == "__main__":
    logger = getMyLog()
    logger.info("正常信息输出")
    logger.debug("DEBUG信息输出")
    logger.error("异常信息输出")


