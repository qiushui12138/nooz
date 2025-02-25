"""
    Author : RoyHe
    Mail   : habaihua666@gmail.com
    Date   : 16:19 2025/2/14
    Description : 
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import colorama
from colorama import Fore, Style

# 初始化colorama，支持Windows下的彩色输出
colorama.init()


class ColoredFormatter(logging.Formatter):
    """自定义彩色日志格式化器"""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        # 保存原始消息
        original_msg = record.msg

        # 添加颜色到日志级别
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{Style.RESET_ALL}"

        # 格式化日志
        result = super().format(record)

        # 还原原始消息，避免影响文件日志
        record.msg = original_msg
        return result


def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 生成日志文件名
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 清除现有的处理器
    logger.handlers.clear()

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建文件处理器（自动轮转）
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setLevel(logging.DEBUG)

    # 创建格式化器
    console_formatter = ColoredFormatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(message)s", datefmt="%H:%M:%S"
    )

    file_formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 设置格式化器
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    # 添加处理器到根日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
