import time
from utils.http_client import HttpClient
from utils.logger import logger

class HttpKeywords:
    def __init__(self):
        self.http_client = HttpClient()
    
    def send_request(self, params, context, retry_count=None, retry_interval=None):
        """发送HTTP请求"""
        method = params.get('method')
        url = params.get('url')
        headers = params.get('headers')
        data = params.get('data')
        params_dict = params.get('params')
        json_data = params.get('json')
        
        if not method or not url:
            raise Exception("缺少必要参数: method 和 url")
        
        # 获取重试配置，优先级：方法参数 > 配置文件 > 默认值
        if retry_count is None:
            retry_count = context.config_manager.get('retry_count', 3)
        if retry_interval is None:
            retry_interval = context.config_manager.get('retry_interval', 1)
        
        # 验证配置有效性
        if not isinstance(retry_count, int) or retry_count < 1:
            logger.warning(f"无效的重试次数: {retry_count}，使用默认值 3")
            retry_count = 3
        if not isinstance(retry_interval, (int, float)) or retry_interval < 0:
            logger.warning(f"无效的重试间隔: {retry_interval}，使用默认值 1")
            retry_interval = 1
        
        # 实现重试机制
        for attempt in range(retry_count):
            try:
                logger.info(f"发送HTTP请求 (尝试 {attempt + 1}/{retry_count}): {method} {url}")
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
            except Exception as e:
                logger.error(f"HTTP请求失败: {str(e)}")
                if attempt < retry_count - 1:
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    raise Exception(f"HTTP请求失败: {str(e)}")
    
    def add_header(self, params, context):
        """添加请求头"""
        name = params.get('name')
        value = params.get('value')
        
        if not name or value is None:
            raise Exception("缺少必要参数: name 和 value")
        
        self.http_client.add_header(name, value)
