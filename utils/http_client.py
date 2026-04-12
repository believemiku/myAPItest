import requests
import time

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        self.last_response = None
        self.last_request_time = None
    
    def send_request(self, method, url, headers=None, data=None, params=None, json=None):
        """发送HTTP请求"""
        method = method.upper()
        headers = headers or {}
        
        # 记录请求开始时间
        self.last_request_time = time.time()
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, data=data, json=json, params=params, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, headers=headers, data=data, json=json, params=params, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params, timeout=30)
            elif method == 'PATCH':
                response = self.session.patch(url, headers=headers, data=data, json=json, params=params, timeout=30)
            else:
                raise Exception(f"不支持的HTTP方法: {method}")
            
            self.last_response = response
            return response
        except Exception as e:
            raise Exception(f"发送请求失败: {str(e)}")
    
    def get_last_response(self):
        """获取最后一次响应"""
        return self.last_response
    
    def get_response_time(self):
        """获取响应时间"""
        if self.last_request_time:
            return time.time() - self.last_request_time
        return 0
    
    def add_header(self, name, value):
        """添加请求头"""
        self.session.headers.update({name: value})
    
    def clear_headers(self):
        """清空请求头"""
        self.session.headers.clear()
