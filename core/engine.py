import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from utils.logger import logger
from core.config import ConfigManager
from core.keyword import KeywordManager
from core.data import DataManager
from core.loader import TestCaseLoader
from core.variables import VariableManager


@dataclass
class TestStep:
    """测试步骤"""
    keyword: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """测试用例"""
    name: str
    steps: List[TestStep] = field(default_factory=list)
    markers: List[str] = field(default_factory=list)


@dataclass
class TestCaseWrapper:
    """测试用例包装器"""
    test_case: TestCase


class TestEngine:
    """测试引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化测试引擎"""
        self.config: Dict[str, Any] = config or {}
        self.config_manager: ConfigManager = ConfigManager()
        self.keyword_manager: KeywordManager = KeywordManager()
        self.data_manager: DataManager = DataManager()
        self.test_case_loader: TestCaseLoader = TestCaseLoader()
        self.variable_manager: VariableManager = VariableManager()
        # 将环境配置添加到变量中
        self._load_env_variables()
    
    def _load_env_variables(self) -> None:
        """加载环境变量到变量管理器"""
        env_config = self.config_manager.get_env_config()
        if env_config:
            self.variable_manager.update({f"env.{k}": v for k, v in env_config.items()})
            logger.info(f"已加载环境变量: {list(env_config.keys())}")
    
    def run_test_case(self, test_case: Dict[str, Any], test_data: Optional[Dict[str, Any]] = None) -> None:
        """运行单个测试用例"""
        # 清空变量
        self.variable_manager.clear()
        # 重新加载环境变量
        self._load_env_variables()
        
        # 获取测试用例信息
        test_case_dict = test_case.get('test_case', {})
        test_name = test_case_dict.get('name', 'Unnamed Test')
        steps_data = test_case_dict.get('steps', [])
        
        # 转换为TestStep对象
        steps = []
        for step_data in steps_data:
            step = TestStep(
                keyword=step_data.get('keyword'),
                params=step_data.get('params', {})
            )
            steps.append(step)
        
        test_case_obj = TestCase(name=test_name, steps=steps)
        
        logger.info(f"开始执行测试用例: {test_case_obj.name}")
        start_time = time.time()
        
        # 处理测试数据
        if test_data:
            logger.info(f"使用测试数据: {test_data}")
            self.variable_manager.update(test_data)
        
        # 执行测试步骤
        for step in test_case_obj.steps:
            # 替换参数中的变量
            processed_params = self.variable_manager.process_params(step.params)
            
            logger.info(f"执行步骤: {step.keyword} 参数:{processed_params}")
            try:
                result = self.keyword_manager.execute(step.keyword, processed_params, self)
            except Exception as e:
                logger.error(f"步骤执行失败: {step.keyword}, 错误: {str(e)}")
                raise AssertionError(f"步骤执行失败: {step.keyword}, 错误: {str(e)}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"测试用例执行完成: {test_case_obj.name}, 结果: PASS, 执行时间: {execution_time:.2f}s")
    
    def set_variable(self, name: str, value: Any) -> None:
        """设置变量"""
        self.variable_manager.set(name, value)
    
    def get_variable(self, name: str) -> Any:
        """获取变量"""
        return self.variable_manager.get(name)
    
    def set_env(self, env: str) -> None:
        """设置环境"""
        self.config_manager.set_env(env)
        # 重新加载环境变量
        self._load_env_variables()
