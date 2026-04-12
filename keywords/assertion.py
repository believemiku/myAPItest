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