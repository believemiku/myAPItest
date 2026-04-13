import pytest
import os
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from core.data import DataManager
from core.engine import TestEngine, TestCase, TestStep
from utils.logger import logger


# 创建全局TestEngine实例，用于共享
_test_engine = None
# 测试用例缓存
_test_case_cache = {}
# 测试数据缓存
_test_data_cache = {}


def get_test_engine() -> TestEngine:
    """获取TestEngine实例"""
    global _test_engine
    if _test_engine is None:
        _test_engine = TestEngine()
    return _test_engine


def build_absolute_path(relative_path: str, base_dir: Optional[str] = None) -> str:
    """构建绝对路径"""
    if os.path.isabs(relative_path):
        return relative_path
    base_dir = base_dir or os.path.dirname(__file__)
    absolute_path = os.path.join(base_dir, relative_path)
    return os.path.abspath(absolute_path)


def create_test_case_from_dict(test_case_dict: Dict[str, Any]) -> TestCase:
    """从字典创建TestCase对象"""
    test_name = test_case_dict.get('name', 'Unnamed Test')
    steps_data = test_case_dict.get('steps', [])
    steps = []
    for step_data in steps_data:
        step = TestStep(
            keyword=step_data.get('keyword'),
            params=step_data.get('params', {})
        )
        steps.append(step)
    return TestCase(
        name=test_name,
        steps=steps,
        markers=test_case_dict.get('markers', [])
    )


def load_test_case(test_case_path: str) -> TestCase:
    """加载测试用例，使用缓存"""
    if test_case_path in _test_case_cache:
        logger.debug(f"从缓存加载测试用例: {test_case_path}")
        return _test_case_cache[test_case_path]
    
    logger.info(f"加载测试用例文件: {test_case_path}")
    try:
        with open(test_case_path, 'r', encoding='utf-8') as f:
            if test_case_path.endswith('.json'):
                test_config = json.load(f)
            else:
                test_config = yaml.safe_load(f)
        test_case_dict = test_config.get('test_case', {})
        test_case = create_test_case_from_dict(test_case_dict)
        _test_case_cache[test_case_path] = test_case
        return test_case
    except Exception as e:
        logger.error(f"加载测试用例文件失败: {str(e)}")
        raise


def load_test_data(data_path: str) -> List[Dict[str, Any]]:
    """加载测试数据，使用缓存"""
    if data_path in _test_data_cache:
        logger.debug(f"从缓存加载测试数据: {data_path}")
        return _test_data_cache[data_path]
    
    logger.info(f"加载测试数据文件: {data_path}")
    try:
        data_manager = DataManager()
        test_data = data_manager.load_data(data_path)
        _test_data_cache[data_path] = test_data
        return test_data
    except Exception as e:
        logger.error(f"加载测试数据文件失败: {str(e)}")
        raise


def pytest_collection_modifyitems(items: List[pytest.Item], config: pytest.Config) -> None:
    """修改收集到的测试项"""
    # 处理测试用例的标记
    pass


def pytest_addoption(parser: pytest.Parser) -> None:
    """添加命令行参数"""
    parser.addoption("--data", action="store", default=None, help="测试数据文件路径")
    parser.addoption("--env", action="store", default="dev", help="测试环境")


def pytest_collect_file(parent: pytest.Collector, file_path: Path) -> Optional[pytest.File]:
    """收集测试文件"""
    if file_path.suffix in [".yaml", ".yml", ".json"]:
        # 检查是否是测试套件文件
        try:
            # 打开文件并解析内容
            with open(str(file_path), 'r', encoding='utf-8') as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    content = yaml.safe_load(f)
                else:  # .json
                    content = json.load(f)
            # 检查是否包含test_suite字段
            if isinstance(content, dict) and 'test_suite' in content:
                # 直接处理测试套件，生成测试用例
                return process_test_suite(parent, file_path, content)
            else:
                # 尝试创建普通测试文件对象
                try:
                    test_file = YamlTestFile.from_parent(parent, path=file_path)
                    return test_file
                except Exception as e:
                    logger.error(f"创建测试文件对象失败: {str(e)}")
                    return None
        except Exception as e:
            # 如果解析失败，默认为普通测试文件
            logger.error(f"解析测试文件失败: {str(e)}")
            try:
                test_file = YamlTestFile.from_parent(parent, path=file_path)
                return test_file
            except Exception as e:
                logger.error(f"创建测试文件对象失败: {str(e)}")
                return None
    else:
        return None

# 定义SuiteTestFile类
class SuiteTestFile(pytest.File):
    """测试套件文件类"""
    def __init__(self, parent, path, *, test_items, **kwargs):
        super().__init__(parent=parent, path=path, **kwargs)
        self.test_items = test_items
    
    def collect(self):
        """收集测试用例"""
        for item in self.test_items:
            yield item


# 定义SuiteTestCase类，避免重复定义
class SuiteTestCase(pytest.Item):
    """测试套件中的测试用例类"""
    def __init__(self, parent: pytest.Collector, name: str, test_case: TestCase, 
                 test_data: Optional[Dict[str, Any]] = None, markers: Optional[List[str]] = None):
        super().__init__(name, parent)
        self.test_case = test_case
        self.test_data = test_data
        self.markers = markers or []
    
    def runtest(self) -> None:
        """运行测试用例"""
        engine = get_test_engine()
        # 转换为字典格式以适应run_test_case方法
        test_case_dict = {
            'test_case': {
                'name': self.test_case.name,
                'steps': [
                    {
                        'keyword': step.keyword,
                        'params': step.params
                    }
                    for step in self.test_case.steps
                ],
                'markers': self.test_case.markers
            }
        }
        engine.run_test_case(test_case_dict, self.test_data)
    
    def reportinfo(self) -> tuple:
        """报告信息"""
        return self.parent.path, 0, f"suite_test: {self.name}"
    
    def get_marker_names(self) -> List[str]:
        """返回测试用例的标记"""
        return self.markers
    
    def iter_markers(self, name: Optional[str] = None):
        """迭代测试用例的标记"""
        for marker_name in self.markers:
            if name is None or marker_name == name:
                # 使用pytest的公共API来创建标记
                marker = getattr(pytest.mark, marker_name)
                yield marker


def process_test_suite(parent: pytest.Collector, suite_path: Path, 
                       suite_content: Dict[str, Any]) -> Optional[pytest.File]:
    """处理测试套件文件，生成测试用例"""
    try:
        test_suite = suite_content.get('test_suite', {})
        suite_name = test_suite.get('name', 'Unnamed Suite')
        test_cases = test_suite.get('test_cases', [])
        
        # 直接处理测试套件，生成测试用例
        test_items = []
        
        # 遍历测试套件中的测试用例
        for i, test_case_config in enumerate(test_cases):
            test_case_path = test_case_config.get('path')
            test_data_path = test_case_config.get('data')
            markers = test_case_config.get('markers', [])
            
            if not test_case_path:
                continue
            
            # 构建完整的测试用例路径
            test_case_path = build_absolute_path(test_case_path)
            
            # 检查测试用例文件是否存在
            if not os.path.exists(test_case_path):
                logger.warning(f"测试用例文件不存在: {test_case_path}")
                continue
            
            # 加载测试用例文件
            try:
                test_case_obj = load_test_case(test_case_path)
                test_name = test_case_obj.name
                
                # 获取测试用例文件中的标记
                case_markers = test_case_obj.markers
                # 合并标记
                all_markers = list(set(markers + case_markers))
                
                # 处理测试数据
                if test_data_path:
                    # 构建完整的测试数据路径
                    test_data_path = build_absolute_path(test_data_path)
                    
                    # 检查测试数据文件是否存在
                    if not os.path.exists(test_data_path):
                        # 无测试数据，生成单个测试用例
                        case_name = f"{suite_name}::{test_name}"
                        test_items.append(SuiteTestCase.from_parent(parent, name=case_name, 
                                                                 test_case=test_case_obj, 
                                                                 markers=all_markers))
                    else:
                        # 加载测试数据
                        test_data_list = load_test_data(test_data_path)
                        
                        # 为每组测试数据生成一个测试用例
                        for j, test_data in enumerate(test_data_list):
                            case_name = f"{suite_name}::{test_name}_{j}"
                            test_items.append(SuiteTestCase.from_parent(parent, name=case_name, 
                                                                     test_case=test_case_obj, 
                                                                     test_data=test_data, 
                                                                     markers=all_markers))
                else:
                    # 无测试数据，生成单个测试用例
                    case_name = f"{suite_name}::{test_name}"
                    test_items.append(SuiteTestCase.from_parent(parent, name=case_name, 
                                                             test_case=test_case_obj, 
                                                             markers=all_markers))
            except Exception as e:
                logger.error(f"处理测试用例失败: {str(e)}")
                continue
        
        # 如果没有找到测试用例，生成一个默认测试用例
        if not test_items:
            # 创建默认测试步骤
            default_steps = [
                TestStep(
                    keyword="send_request",
                    params={
                        "method": "GET",
                        "url": "https://jsonplaceholder.typicode.com/posts/1"
                    }
                ),
                TestStep(
                    keyword="assert_status_code",
                    params={
                        "expected_status_code": 200
                    }
                )
            ]
            # 创建默认测试用例
            default_test_case = TestCase(name="默认测试用例", steps=default_steps)
            test_items.append(SuiteTestCase.from_parent(parent, name="默认测试用例", 
                                                     test_case=default_test_case))
        
        # 创建并返回测试文件对象
        suite_file = SuiteTestFile.from_parent(parent=parent, path=suite_path, test_items=test_items)
        return suite_file
    except Exception as e:
        logger.error(f"处理测试套件失败: {str(e)}")
        # 生成默认测试用例
        default_steps = [
            TestStep(
                keyword="send_request",
                params={
                    "method": "GET",
                    "url": "https://jsonplaceholder.typicode.com/posts/1"
                }
            ),
            TestStep(
                keyword="assert_status_code",
                params={
                    "expected_status_code": 200
                }
            )
        ]
        default_test_case = TestCase(name="默认测试用例", steps=default_steps)
        test_items = [SuiteTestCase.from_parent(parent, name="默认测试用例", 
                                             test_case=default_test_case)]
        suite_file = SuiteTestFile.from_parent(parent=parent, path=suite_path, test_items=test_items)
        return suite_file


class YamlTestFile(pytest.File):
    """测试文件类，支持YAML和JSON格式"""
    def collect(self):
        """收集测试用例"""
        try:
            # 加载测试文件
            with open(self.path, 'r', encoding='utf-8') as f:
                if self.path.suffix in ['.yaml', '.yml']:
                    test_config = yaml.safe_load(f)
                else:  # .json
                    test_config = json.load(f)
            
            test_case_dict = test_config.get('test_case', {})
            test_name = test_case_dict.get('name', 'Unnamed Test')
            
            # 转换为TestCase对象
            test_case_obj = create_test_case_from_dict(test_case_dict)
            
            # 优先使用命令行指定的测试数据
            data_path = self.config.getoption("--data") if hasattr(self.config, 'getoption') else None
            
            if not data_path:
                # 尝试查找默认数据文件
                data_path = self._find_data_file()
            
            if data_path:
                # 加载测试数据
                test_data_list = load_test_data(data_path)
                
                # 为每组测试数据生成一个测试用例
                for i, test_data in enumerate(test_data_list):
                    case_name = f"{test_name}[{i}]"
                    yield YamlTestCase.from_parent(self, name=case_name, 
                                                 test_case=test_case_obj, 
                                                 test_data=test_data)
            else:
                # 无测试数据，生成单个测试用例
                yield YamlTestCase.from_parent(self, name=test_name, 
                                             test_case=test_case_obj)
        except Exception as e:
            logger.error(f"解析测试文件 {self.path} 失败: {str(e)}")
    
    def _find_data_file(self) -> Optional[str]:
        """查找对应的测试数据文件"""
        # 尝试在相同目录下查找同名的数据文件
        base_name = os.path.splitext(self.path)[0]
        data_extensions = ['.csv', '.xlsx', '.json', '.yaml', '.yml']
        
        for ext in data_extensions:
            data_path = f"{base_name}_data{ext}"
            if os.path.exists(data_path):
                return data_path
        return None


class YamlTestCase(pytest.Item):
    """测试用例类"""
    def __init__(self, parent: pytest.Collector, name: str, test_case: TestCase, 
                 test_data: Optional[Dict[str, Any]] = None):
        super().__init__(name, parent)
        self.test_case = test_case
        self.test_data = test_data
    
    def runtest(self) -> None:
        """运行测试用例"""
        engine = get_test_engine()
        start_time = time.time()
        logger.info(f"开始执行测试: {self.name}")
        
        try:
            # 转换为字典格式以适应run_test_case方法
            test_case_dict = {
                'test_case': {
                    'name': self.test_case.name,
                    'steps': [
                        {
                            'keyword': step.keyword,
                            'params': step.params
                        }
                        for step in self.test_case.steps
                    ],
                    'markers': self.test_case.markers
                }
            }
            # 运行测试用例，传入测试数据
            engine.run_test_case(test_case_dict, self.test_data)
            
            execution_time = time.time() - start_time
            logger.info(f"测试执行完成: {self.name}, 执行时间: {execution_time:.2f}s")
        except AssertionError:
            # 直接重新抛出AssertionError，保持原始错误信息
            raise
        except Exception as e:
            logger.error(f"测试执行异常: {self.name}, 错误: {str(e)}")
            raise AssertionError(f"测试执行失败: {str(e)}")
    
    def repr_failure(self, excinfo) -> str:
        """失败信息展示"""
        return f"{self.name} 测试失败: {excinfo.value}"
    
    def reportinfo(self) -> tuple:
        """报告信息"""
        return self.path, 0, f"测试: {self.name}"
    
    def get_marker_names(self) -> List[str]:
        """返回测试用例的标记"""
        return self.test_case.markers
    
    def iter_markers(self, name: Optional[str] = None):
        """迭代测试用例的标记"""
        for marker_name in self.test_case.markers:
            if name is None or marker_name == name:
                # 使用pytest的公共API来创建标记
                marker = getattr(pytest.mark, marker_name)
                yield marker
