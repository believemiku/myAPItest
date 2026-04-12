import logging
import colorlog
import os
from datetime import datetime

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 日志文件名
log_file = os.path.join(log_dir, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 配置日志
logger = logging.getLogger('api-test-framework')
logger.setLevel(logging.DEBUG)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 文件日志处理器
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 控制台日志格式（带颜色）
console_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    }
)

# 文件日志格式
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置格式
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# 添加处理器
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
