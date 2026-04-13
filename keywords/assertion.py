import allure
import jsonpath

class AssertionKeywords:
    @allure.step("状态码断言")
    def assert_status_code(self, params, context):
        """验证状态码"""
        expected_status_code = params.get('expected_status_code')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        assert response.status_code == expected_status_code, f"状态码验证失败: 期望 {expected_status_code}, 实际 {response.status_code}"
    
    def assert_status_code_in(self, params, context):
        """验证状态码是否在指定列表中"""
        expected_status_codes = params.get('expected_status_codes')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        assert response.status_code in expected_status_codes, f"状态码验证失败: 期望在 {expected_status_codes} 中, 实际 {response.status_code}"
    
    def assert_contains(self, params, context):
        """验证响应内容是否包含指定字符串"""
        expected_text = params.get('expected_text')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        response_text = response.text
        assert expected_text in response_text, f"响应内容验证失败: 期望包含 '{expected_text}', 实际响应: '{response_text}'"
    
    def assert_not_contains(self, params, context):
        """验证响应内容是否不包含指定字符串"""
        unexpected_text = params.get('unexpected_text')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        response_text = response.text
        assert unexpected_text not in response_text, f"响应内容验证失败: 期望不包含 '{unexpected_text}', 实际响应: '{response_text}'"
    
    def assert_header(self, params, context):
        """验证响应头是否包含指定值"""
        header_name = params.get('header_name')
        expected_value = params.get('expected_value')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        assert header_name in response.headers, f"响应头中不存在 {header_name}"
        actual_value = response.headers.get(header_name)
        assert actual_value == expected_value, f"响应头验证失败: 期望 {header_name} = {expected_value}, 实际 {header_name} = {actual_value}"
    
    def assert_header_exists(self, params, context):
        """验证响应头是否存在"""
        header_name = params.get('header_name')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        assert header_name in response.headers, f"响应头中不存在 {header_name}"
    
    def assert_response_body(self, params, context):
        """验证响应体是否等于指定值"""
        expected_body = params.get('expected_body')
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        response_text = response.text
        assert response_text == expected_body, f"响应体验证失败: 期望 '{expected_body}', 实际 '{response_text}'"
    
    def assert_json_path(self, params, context):
        """验证JSON路径值"""
        json_path = params.get('json_path')
        expected_value = params.get('expected_value')
        response_json = context.get_variable('response_json')
        
        assert response_json is not None, "没有找到响应JSON，请先发送请求并确保响应是JSON格式"
        
        try:
            actual_value = jsonpath.jsonpath(response_json, json_path)
            assert actual_value is not None and len(actual_value) > 0, f"JSON路径 {json_path} 不存在"
            
            actual_value = actual_value[0]  # jsonpath返回列表
            
            if expected_value == 'not_empty':
                assert actual_value, f"JSON路径 {json_path} 的值为空"
            else:
                assert actual_value == expected_value, f"JSON路径验证失败: 期望 {expected_value}, 实际 {actual_value}"
        except AssertionError:
            raise
        except Exception as e:
            assert False, f"验证JSON路径失败: {str(e)}"
    
    def assert_json_path_exists(self, params, context):
        """验证JSON路径是否存在"""
        json_path = params.get('json_path')
        response_json = context.get_variable('response_json')
        
        assert response_json is not None, "没有找到响应JSON，请先发送请求并确保响应是JSON格式"
        
        try:
            actual_value = jsonpath.jsonpath(response_json, json_path)
            assert actual_value is not None and len(actual_value) > 0, f"JSON路径 {json_path} 不存在"
        except AssertionError:
            raise
        except Exception as e:
            assert False, f"验证JSON路径失败: {str(e)}"
    
    def assert_json_path_not_exists(self, params, context):
        """验证JSON路径是否不存在"""
        json_path = params.get('json_path')
        response_json = context.get_variable('response_json')
        
        assert response_json is not None, "没有找到响应JSON，请先发送请求并确保响应是JSON格式"
        
        try:
            actual_value = jsonpath.jsonpath(response_json, json_path)
            assert actual_value is None or len(actual_value) == 0, f"JSON路径 {json_path} 不应该存在"
        except AssertionError:
            raise
        except Exception as e:
            assert False, f"验证JSON路径失败: {str(e)}"
    
    def assert_json_path_length(self, params, context):
        """验证JSON路径数组长度"""
        json_path = params.get('json_path')
        expected_length = params.get('expected_length')
        response_json = context.get_variable('response_json')
        
        assert response_json is not None, "没有找到响应JSON，请先发送请求并确保响应是JSON格式"
        
        try:
            actual_value = jsonpath.jsonpath(response_json, json_path)
            assert actual_value is not None and len(actual_value) > 0, f"JSON路径 {json_path} 不存在"
            
            actual_length = len(actual_value[0]) if isinstance(actual_value[0], list) else len(actual_value)
            assert actual_length == expected_length, f"JSON路径长度验证失败: 期望 {expected_length}, 实际 {actual_length}"
        except AssertionError:
            raise
        except Exception as e:
            assert False, f"验证JSON路径长度失败: {str(e)}"
    
    def assert_response_time(self, params, context):
        """验证响应时间"""
        max_time_ms = params.get('max_time_ms')
        response_time = context.get_variable('response_time')
        
        if response_time is None:
            # 尝试从HTTP客户端获取
            from utils.http_client import HttpClient
            http_client = HttpClient()
            response_time = http_client.get_response_time()
        
        assert response_time * 1000 <= max_time_ms, f"响应时间验证失败: 期望 < {max_time_ms}ms, 实际 {response_time * 1000:.2f}ms"
    
    def assert_response_length(self, params, context):
        """验证响应体长度是否在指定范围内"""
        min_length = params.get('min_length', 0)
        max_length = params.get('max_length', float('inf'))
        response = context.get_variable('response')
        
        assert response is not None, "没有找到响应对象，请先发送请求"
        response_length = len(response.content)
        assert min_length <= response_length <= max_length, f"响应长度验证失败: 期望在 [{min_length}, {max_length}] 范围内, 实际 {response_length}"
    
    def assert_true(self, params, context):
        """验证表达式是否为True"""
        expression = params.get('expression')
        assert expression, f"表达式验证失败: 期望为True, 实际为 {expression}"
    
    def assert_false(self, params, context):
        """验证表达式是否为False"""
        expression = params.get('expression')
        assert not expression, f"表达式验证失败: 期望为False, 实际为 {expression}"
    
    def assert_equal(self, params, context):
        """验证两个值是否相等"""
        actual_value = params.get('actual_value')
        expected_value = params.get('expected_value')
        assert actual_value == expected_value, f"相等性验证失败: 期望 {expected_value}, 实际 {actual_value}"
    
    def assert_not_equal(self, params, context):
        """验证两个值是否不相等"""
        actual_value = params.get('actual_value')
        expected_value = params.get('expected_value')
        assert actual_value != expected_value, f"不等性验证失败: 期望不等于 {expected_value}, 实际 {actual_value}"
    
    def assert_greater_than(self, params, context):
        """验证实际值是否大于期望值"""
        actual_value = params.get('actual_value')
        expected_value = params.get('expected_value')
        assert actual_value > expected_value, f"比较验证失败: 期望 {actual_value} > {expected_value}"
    
    def assert_greater_than_or_equal(self, params, context):
        """验证实际值是否大于或等于期望值"""
        actual_value = params.get('actual_value')
        expected_value = params.get('expected_value')
        assert actual_value >= expected_value, f"比较验证失败: 期望 {actual_value} >= {expected_value}"
    
    def assert_less_than(self, params, context):
        """验证实际值是否小于期望值"""
        actual_value = params.get('actual_value')
        expected_value = params.get('expected_value')
        assert actual_value < expected_value, f"比较验证失败: 期望 {actual_value} < {expected_value}"
    
    def assert_less_than_or_equal(self, params, context):
        """验证实际值是否小于或等于期望值"""
        actual_value = params.get('actual_value')
        expected_value = params.get('expected_value')
        assert actual_value <= expected_value, f"比较验证失败: 期望 {actual_value} <= {expected_value}"