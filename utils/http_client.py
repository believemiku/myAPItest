import requests
import time
import hashlib
from typing import Dict, Any, Optional

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        # 配置连接池
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.last_response = None
        self.last_request_time = None
        self.response_cache = {}  # 请求结果缓存
    
    def _generate_cache_key(self, method: str, url: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> str:
        """生成缓存键"""
        key = f"{method}:{url}"
        if params:
            key += f":{str(sorted(params.items()))}"
        if json:
            key += f":{str(sorted(json.items()))}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def send_request(self, method: str, url: str, headers: Optional[Dict[str, Any]] = None, 
                     data: Optional[Any] = None, params: Optional[Dict[str, Any]] = None, 
                     json: Optional[Dict[str, Any]] = None, use_cache: bool = False) -> requests.Response:
        """发送HTTP请求"""
        method = method.upper()
        headers = headers or {}
        
        # 生成缓存键
        cache_key = self._generate_cache_key(method, url, params, json)
        
        # 检查缓存
        if use_cache and cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            self.last_response = cached_response
            return cached_response
        
        # 记录请求开始时间
        self.last_request_time = time.time()
        
        try:
            # 优化超时设置
            timeout = (5, 15)  # 连接超时5秒，读取超时15秒
            
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, data=data, json=json, params=params, timeout=timeout)
            elif method == 'PUT':
                response = self.session.put(url, headers=headers, data=data, json=json, params=params, timeout=timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params, timeout=timeout)
            elif method == 'PATCH':
                response = self.session.patch(url, headers=headers, data=data, json=json, params=params, timeout=timeout)
            else:
                raise Exception(f"不支持的HTTP方法: {method}")
            
            # 缓存响应
            if use_cache:
                self.response_cache[cache_key] = response
            
            self.last_response = response
            return response
        except Exception as e:
            raise Exception(f"发送请求失败: {str(e)}")
    
    def get_last_response(self) -> Optional[requests.Response]:
        """获取最后一次响应"""
        return self.last_response
    
    def get_response_time(self) -> float:
        """获取响应时间"""
        if self.last_request_time:
            return time.time() - self.last_request_time
        return 0
    
    def add_header(self, name: str, value: str) -> None:
        """添加请求头"""
        self.session.headers.update({name: value})
    
    def clear_headers(self) -> None:
        """清空请求头"""
        self.session.headers.clear()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.response_cache.clear()
