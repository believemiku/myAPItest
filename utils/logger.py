import logging
import colorlog
import os
import json
from datetime import datetime

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 自动清理旧日志文件
def clean_old_logs(max_files=10):
    """清理旧的日志文件，只保留最近的max_files个文件"""
    try:
        # 获取所有日志文件
        log_files = [f for f in os.listdir(log_dir) if f.startswith('test_') and f.endswith('.log')]
        
        # 按修改时间排序（最新的在前）
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
        
        # 删除超过max_files的旧文件
        for file_to_delete in log_files[max_files:]:
            file_path = os.path.join(log_dir, file_to_delete)
            os.remove(file_path)
            logging.debug(f"已清理旧日志文件: {file_to_delete}")
    except Exception as e:
        logging.error(f"清理旧日志文件时出错: {str(e)}")

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 获取日志级别
def get_log_level():
    """从环境变量或配置文件中获取日志级别"""
    # 从环境变量获取
    env_level = os.environ.get('LOG_LEVEL')
    if env_level and env_level in LOG_LEVELS:
        return LOG_LEVELS[env_level]
    
    # 尝试从配置文件获取
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        if os.path.exists(config_path):
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                log_level = config.get('global', {}).get('log_level', 'INFO')
                if log_level in LOG_LEVELS:
                    return LOG_LEVELS[log_level]
    except Exception:
        pass
    
    # 默认日志级别
    return logging.WARNING

# 日志文件名
log_file = os.path.join(log_dir, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 配置日志
logger = logging.getLogger('api-test-framework')
logger.setLevel(logging.DEBUG)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(get_log_level())

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

# 结构化日志格式
class StructuredFormatter(logging.Formatter):
    """结构化日志格式"""
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
        return json.dumps(log_record)

# 结构化文件日志处理器
structured_file_handler = logging.FileHandler(
    os.path.join(log_dir, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_structured.log"), 
    encoding='utf-8'
)
structured_file_handler.setLevel(logging.DEBUG)
structured_file_handler.setFormatter(StructuredFormatter())

# 设置格式
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# 添加处理器
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(structured_file_handler)

# 清理旧日志
clean_old_logs()
