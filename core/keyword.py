import importlib
import os
import pkgutil
from typing import Any, TYPE_CHECKING, Dict, Callable

from utils.logger import logger

if TYPE_CHECKING:
    from core.engine import TestEngine


class KeywordManager:
    """关键字管理器"""
    
    def __init__(self, keyword_packages: list = None):
        """初始化关键字管理器"""
        self.keywords: Dict[str, Callable] = {}
        self.keyword_packages = keyword_packages or ['keywords']
        self._register_keywords()
    
    def _register_keywords(self):
        """注册关键字"""
        # 注册内置关键字
        self._register_builtin_keywords()
        # 自动发现并注册关键字
        self._discover_keywords()
    
    def _register_builtin_keywords(self):
        """注册内置关键字"""
        # 注册变量相关关键字
        self.register_keyword('set_variable', self.set_variable)
        self.register_keyword('get_variable', self.get_variable)
        logger.info("已注册内置关键字")
    
    def _discover_keywords(self):
        """自动发现关键字"""
        for package_name in self.keyword_packages:
            try:
                package = importlib.import_module(package_name)
                if hasattr(package, '__path__'):
                    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                        if not is_pkg:
                            self._load_keywords_from_module(f"{package_name}.{module_name}")
            except Exception as e:
                logger.error(f"发现关键字时出错: {str(e)}")
    
    def _load_keywords_from_module(self, module_name: str):
        """从模块中加载关键字"""
        try:
            module = importlib.import_module(module_name)
            # 查找模块中的关键字类
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and hasattr(obj, '__name__') and 'Keywords' in obj.__name__:
                    # 实例化关键字类
                    keywords_instance = obj()
                    # 注册类中的所有方法作为关键字
                    for method_name in dir(keywords_instance):
                        if not method_name.startswith('_'):
                            method = getattr(keywords_instance, method_name)
                            if callable(method):
                                # 转换方法名为小写并使用下划线分隔
                                keyword_name = method_name
                                self.register_keyword(keyword_name, method)
                                logger.debug(f"从{module_name}注册关键字: {keyword_name}")
        except Exception as e:
            logger.error(f"加载关键字模块 {module_name} 时出错: {str(e)}")
    
    def register_keyword(self, name: str, func: Callable):
        """注册关键字"""
        self.keywords[name] = func
        logger.debug(f"注册关键字: {name}")
    
    def execute(self, keyword_name: str, params: dict, context: 'TestEngine'):
        """执行关键字"""
        if keyword_name not in self.keywords:
            error_msg = f"未知关键字: {keyword_name}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        func = self.keywords[keyword_name]
        try:
            logger.info(f"执行关键字: {keyword_name}")
            return func(params, context)
        except Exception as e:
            error_msg = f"执行关键字 {keyword_name} 失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def set_variable(self, params: dict, context: 'TestEngine'):
        """设置变量"""
        variable_name = params.get('variable_name')
        value = params.get('value')
        if not variable_name:
            raise Exception("缺少变量名")
        context.set_variable(variable_name, value)
    
    def get_variable(self, params: dict[str, Any], context: 'TestEngine'):
        """获取变量"""
        variable_name = params.get('variable_name')
        if not variable_name:
            raise Exception("缺少变量名")
        return context.get_variable(variable_name)
