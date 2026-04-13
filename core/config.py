import os
from typing import Dict, Any, Optional
import yaml
from utils.logger import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        """初始化配置管理器"""
        self.config_file: str = config_file
        self.config: Dict[str, Any] = {}
        self.current_env: str = os.environ.get('TEST_ENV', 'dev')
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"成功加载配置文件: {self.config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        else:
            logger.warning(f"配置文件不存在: {self.config_file}")
    
    def set_env(self, env: str) -> None:
        """设置环境"""
        self.current_env = env
        logger.info(f"切换环境到: {env}")
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """获取配置值"""
        # 首先尝试从当前环境获取
        env_config = self.config.get(self.current_env, {})
        if key in env_config:
            return env_config[key]
        
        # 然后尝试从全局配置获取
        global_config = self.config.get('global', {})
        if key in global_config:
            return global_config[key]
        
        # 最后尝试从根配置获取
        if key in self.config:
            return self.config[key]
        
        return default
    
    def get_env_config(self) -> Dict[str, Any]:
        """获取当前环境的配置"""
        return self.config.get(self.current_env, {})