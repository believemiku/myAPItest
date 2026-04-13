import os
import json
import yaml
from typing import Dict, Any, Optional
from utils.logger import logger


class TestCaseLoader:
    """测试用例加载器"""
    
    def __init__(self):
        self.test_case_cache = {}  # 测试用例缓存，键为文件路径，值为加载的测试用例
    
    def load_test_case(self, test_case_path: str) -> Dict[str, Any]:
        """加载测试用例文件"""
        # 转换为绝对路径，确保缓存键的唯一性
        test_case_path = os.path.abspath(test_case_path)
        
        # 检查缓存
        if test_case_path in self.test_case_cache:
            test_case = self.test_case_cache[test_case_path]
            logger.info(f"从缓存加载测试用例: {test_case.get('test_case', {}).get('name', 'Unnamed Test')}")
            return test_case
        
        logger.info(f"加载测试用例文件: {test_case_path}")
        if test_case_path.endswith('.yaml') or test_case_path.endswith('.yml'):
            with open(test_case_path, 'r', encoding='utf-8') as f:
                test_case = yaml.safe_load(f) or {}
                logger.info(f"成功加载测试用例: {test_case.get('test_case', {}).get('name', 'Unnamed Test')}")
        elif test_case_path.endswith('.json'):
            with open(test_case_path, 'r', encoding='utf-8') as f:
                test_case = json.load(f)
                logger.info(f"成功加载测试用例: {test_case.get('test_case', {}).get('name', 'Unnamed Test')}")
        else:
            error_msg = f"不支持的测试用例文件格式: {test_case_path}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # 缓存测试用例
        self.test_case_cache[test_case_path] = test_case
        return test_case
    
    def clear_cache(self) -> None:
        """清空测试用例缓存"""
        self.test_case_cache.clear()