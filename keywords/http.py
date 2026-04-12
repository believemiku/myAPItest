from utils.http_client import HttpClient

class HttpKeywords:
    def __init__(self):
        self.http_client = HttpClient()
    
    def send_request(self, params, context):
        """发送HTTP请求"""
        method = params.get('method')
        url = params.get('url')
        headers = params.get('headers')
        data = params.get('data')
        params_dict = params.get('params')
        json_data = params.get('json')
        
        if not method or not url:
            raise Exception("缺少必要参数: method 和 url")
        
        response = self.http_client.send_request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params_dict,
            json=json_data
        )
        
        # 将响应保存到上下文中
        context.set_variable('response', response)
        context.set_variable('response_status_code', response.status_code)
        
        try:
            response_json = response.json()
            context.set_variable('response_json', response_json)
        except Exception:
            pass
        
        return response
    
    def add_header(self, params, context):
        """添加请求头"""
        name = params.get('name')
        value = params.get('value')
        
        if not name or value is None:
            raise Exception("缺少必要参数: name 和 value")
        
        self.http_client.add_header(name, value)
