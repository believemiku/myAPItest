import json
import time
from datetime import datetime

import yaml

from core.data import DataManager
from core.keyword import KeywordManager
from utils.logger import logger


class TestEngine:
    def __init__(self, config=None):
        self.config = config or {}
        self.keyword_manager = KeywordManager()
        self.data_manager = DataManager()
        self.variables = {}

    def load_test_case(self, test_case_path):
        """加载测试用例文件"""
        if test_case_path.endswith('.yaml') or test_case_path.endswith('.yml'):
            with open(test_case_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        elif test_case_path.endswith('.json'):
            with open(test_case_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise Exception(f"不支持的测试用例文件格式: {test_case_path}")

    def load_test_data(self, data_path):
        """加载测试数据"""
        return self.data_manager.load_data(data_path)

    def run_test_case(self, test_case, test_data=None):
        """运行单个测试用例"""
        self.variables.clear()
        test_name = test_case.get('test_case', {}).get('name', 'Unnamed Test')
        steps = test_case.get('test_case', {}).get('steps', [])

        logger.info(f"开始执行测试用例: {test_name}")
        start_time = time.time()

        # 处理测试数据
        if test_data:
            logger.warning(f"使用测试数据: {test_data}")
            self.variables.update(test_data)

        for step in steps:
            keyword = step.get('keyword')
            params = step.get('params', {})

            # 替换参数中的变量
            processed_params = self._process_params(params)

            logger.info(f"执行步骤: {keyword} 参数:{processed_params}")
            try:
                result = self.keyword_manager.execute(keyword, processed_params, self)
            except Exception as e:
                logger.error(f"步骤执行失败: {keyword}, 错误: {str(e)}")
                raise AssertionError(f"步骤执行失败: {keyword}, 错误: {str(e)}")

        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(f"测试用例执行完成: {test_name}, 结果: PASS, 执行时间: {execution_time:.2f}s")

    def _process_params(self, params):
        """处理参数中的变量"""
        return self._process_value(params)

    def _process_value(self, value):
        """处理单个值中的变量"""
        if isinstance(value, dict):
            logger.info(f"处理参数: {value}")
            return {k: self._process_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            logger.info(f"处理参数列表: {value}")
            return [self._process_value(item) for item in value]
        elif isinstance(value, str) and '${' in value and '}' in value:
            logger.info(f"处理变量引用: {value}")
            # 处理变量引用
            for var_name, var_value in self.variables.items():
                placeholder = f"${{{var_name}}}"
                if placeholder in value:
                    value = value.replace(placeholder, str(var_value))
            # 处理特殊变量
            if '${response' in value:
                # 这里可以扩展处理response相关的变量
                pass
        return value

    def set_variable(self, name, value):
        """设置变量"""
        self.variables[name] = value
        logger.info(f"设置变量: {name} = {value}")

    def get_variable(self, name):
        """获取变量"""
        return self.variables.get(name)
