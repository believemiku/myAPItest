import pytest
import os
import yaml
import time
from core.data import DataManager
from core.engine import TestEngine
from utils.logger import logger



# 创建全局TestEngine实例，用于共享
_test_engine = None

def get_test_engine():
    """获取TestEngine实例"""
    global _test_engine
    if _test_engine is None:
        _test_engine = TestEngine()
    return _test_engine

def pytest_collection_modifyitems(items, config):
    """修改收集到的测试项"""
    # 处理测试用例的标记
    pass

def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption("--data", action="store", default=None, help="测试数据文件路径")

def pytest_collect_file(parent, file_path):
    """收集yaml测试文件"""
    if file_path.suffix in [".yaml", ".yml"]:
        # 检查是否是测试套件文件
        try:
            # 打开文件并解析内容
            with open(str(file_path), 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
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
                    return None
        except Exception as e:
            # 如果解析失败，默认为普通测试文件
            try:
                test_file = YamlTestFile.from_parent(parent, path=file_path)
                return test_file
            except Exception as e:
                return None
    else:
        return None

# 定义SuiteTestCase类，避免重复定义
class SuiteTestCase(pytest.Item):
    """测试套件中的测试用例类"""
    def __init__(self, parent, name, test_case, test_data=None, markers=None):
        super().__init__(name, parent)
        self.test_case = test_case
        self.test_data = test_data
        self.markers = markers or []
    
    def runtest(self):
        engine = get_test_engine()
        engine.run_test_case({'test_case': self.test_case}, self.test_data)
    
    def reportinfo(self):
        """报告信息"""
        return self.parent.path, 0, f"suite_test: {self.name}"
    
    def get_marker_names(self):
        """返回测试用例的标记"""
        return self.markers
    
    def iter_markers(self, name=None):
        """迭代测试用例的标记"""
        for marker_name in self.markers:
            if name is None or marker_name == name:
                # 使用pytest的公共API来创建标记
                marker = getattr(pytest.mark, marker_name)
                yield marker

def process_test_suite(parent, suite_path, suite_content):
    """处理测试套件文件，生成测试用例"""
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
        if not os.path.isabs(test_case_path):
            # 从当前文件所在目录开始构建路径
            current_dir = os.path.dirname(__file__)
            test_case_path = os.path.join(current_dir, test_case_path)
            # 转换为绝对路径
            test_case_path = os.path.abspath(test_case_path)
        
        # 检查测试用例文件是否存在
        if not os.path.exists(test_case_path):
            continue
        
        # 加载测试用例文件
        try:
            with open(test_case_path, 'r', encoding='utf-8') as f:
                test_config = yaml.safe_load(f)
            test_case = test_config.get('test_case', {})
            test_name = test_case.get('name', f'Test {i+1}')
            
            # 获取测试用例文件中的标记
            case_markers = test_case.get('markers', [])
            # 合并标记
            all_markers = list(set(markers + case_markers))
            
            # 处理测试数据
            if test_data_path:
                # 构建完整的测试数据路径
                if not os.path.isabs(test_data_path):
                    # 从当前文件所在目录开始构建路径
                    current_dir = os.path.dirname(__file__)
                    test_data_path = os.path.join(current_dir, test_data_path)
                    # 转换为绝对路径
                    test_data_path = os.path.abspath(test_data_path)
                
                # 检查测试数据文件是否存在
                if not os.path.exists(test_data_path):
                    # 无测试数据，生成单个测试用例
                    case_name = f"{suite_name}::{test_name}"
                    test_items.append(SuiteTestCase.from_parent(parent, name=case_name, test_case=test_case, markers=all_markers))
                else:
                    # 加载测试数据
                    data_manager = DataManager()
                    test_data_list = data_manager.load_data(test_data_path)
                    
                    # 为每组测试数据生成一个测试用例
                    for j, test_data in enumerate(test_data_list):
                        case_name = f"{suite_name}::{test_name}_{j}"
                        test_items.append(SuiteTestCase.from_parent(parent, name=case_name, test_case=test_case, test_data=test_data, markers=all_markers))
            else:
                # 无测试数据，生成单个测试用例
                case_name = f"{suite_name}::{test_name}"
                test_items.append(SuiteTestCase.from_parent(parent, name=case_name, test_case=test_case, markers=all_markers))
        except Exception as e:
            pass
    
    # 如果没有找到测试用例，生成一个默认测试用例
    if not test_items:
        default_test_case = {
            "name": "默认测试用例",
            "steps": [
                {
                    "keyword": "send_request",
                    "params": {
                        "method": "GET",
                        "url": "https://jsonplaceholder.typicode.com/posts/1"
                    }
                },
                {
                    "keyword": "assert_status_code",
                    "params": {
                        "expected_status_code": 200
                    }
                }
            ]
        }
        test_items.append(SuiteTestCase.from_parent(parent, name="默认测试用例", test_case=default_test_case))
    
    # 创建一个测试文件对象来容纳所有测试用例
    class SuiteTestFile(pytest.File):
        def collect(self):
            for item in test_items:
                yield item
    
    # 创建并返回测试文件对象
    suite_file = SuiteTestFile.from_parent(parent, path=suite_path)
    return suite_file


class YamlTestFile(pytest.File):
    """yaml测试文件类"""
    def collect(self):
        """收集测试用例"""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                test_config = yaml.safe_load(f)
            test_case = test_config.get('test_case', {})
            test_name = test_case.get('name', 'Unnamed Test')
            
            # 优先使用命令行指定的测试数据
            data_path = self.config.getoption("--data") if hasattr(self.config, 'getoption') else None
            
            if not data_path:
                # 尝试查找默认数据文件
                data_path = self._find_data_file()
            
            if data_path:
                # 加载测试数据
                data_manager = DataManager()
                test_data_list = data_manager.load_data(data_path)
                
                # 为每组测试数据生成一个测试用例
                for i, test_data in enumerate(test_data_list):
                    case_name = f"{test_name}[{i}]"
                    yield YamlTestCase.from_parent(self, name=case_name, 
                                                 test_case=test_case, 
                                                 test_data=test_data)
            else:
                # 无测试数据，生成单个测试用例
                yield YamlTestCase.from_parent(self, name=test_name, 
                                             test_case=test_case)
        except Exception as e:
            logger.error(f"解析测试文件 {self.path} 失败: {str(e)}")
    
    def _find_data_file(self):
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
    """yaml测试用例类"""
    def __init__(self, parent, name, test_case, test_data=None):
        super().__init__(name, parent)
        self.test_case = test_case
        self.test_data = test_data
    
    def runtest(self):
        """运行测试用例"""
        engine = get_test_engine()
        start_time = time.time()
        logger.info(f"开始执行测试: {self.name}")
        
        try:
            # 运行测试用例，传入测试数据
            engine.run_test_case({'test_case': self.test_case}, self.test_data)
            
            execution_time = time.time() - start_time
            logger.info(f"测试执行完成: {self.name}, 执行时间: {execution_time:.2f}s")
        except AssertionError:
            # 直接重新抛出AssertionError，保持原始错误信息
            raise
        except Exception as e:
            logger.error(f"测试执行异常: {self.name}, 错误: {str(e)}")
            raise AssertionError(f"测试执行失败: {str(e)}")
    
    def repr_failure(self, excinfo):
        """失败信息展示"""
        return f"{self.name} 测试失败: {excinfo.value}"
    
    def reportinfo(self):
        """报告信息"""
        return self.path, 0, f"yaml测试: {self.name}"
    
    def get_marker_names(self):
        """返回测试用例的标记"""
        return self.test_case.get('markers', [])
    
    def iter_markers(self, name=None):
        """迭代测试用例的标记"""
        markers = self.test_case.get('markers', [])
        for marker_name in markers:
            if name is None or marker_name == name:
                # 使用pytest的公共API来创建标记
                marker = getattr(pytest.mark, marker_name)
                yield marker
