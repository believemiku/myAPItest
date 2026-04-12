from keywords.http import HttpKeywords
from keywords.assertion import AssertionKeywords
from keywords.auth import AuthKeywords

class KeywordManager:
    def __init__(self):
        self.keywords = {}
        self._register_keywords()
    
    def _register_keywords(self):
        """注册内置关键字"""
        # 注册HTTP相关关键字
        http_keywords = HttpKeywords()
        self.register_keyword('send_request', http_keywords.send_request)
        self.register_keyword('add_header', http_keywords.add_header)
        
        # 注册断言相关关键字
        assertion_keywords = AssertionKeywords()
        self.register_keyword('assert_status_code', assertion_keywords.assert_status_code)
        self.register_keyword('assert_json_path', assertion_keywords.assert_json_path)
        self.register_keyword('assert_response_time', assertion_keywords.assert_response_time)
        
        # 注册认证相关关键字
        auth_keywords = AuthKeywords()
        self.register_keyword('authenticate', auth_keywords.authenticate)
        
        # 注册变量相关关键字
        self.register_keyword('set_variable', self.set_variable)
        self.register_keyword('get_variable', self.get_variable)
    
    def register_keyword(self, name, func):
        """注册关键字"""
        self.keywords[name] = func
    
    def execute(self, keyword_name, params, context):
        """执行关键字"""
        if keyword_name not in self.keywords:
            raise Exception(f"未知关键字: {keyword_name}")
        
        func = self.keywords[keyword_name]
        try:
            return func(params, context)
        except Exception as e:
            raise Exception(f"执行关键字 {keyword_name} 失败: {str(e)}")
    
    def set_variable(self, params, context):
        """设置变量"""
        variable_name = params.get('variable_name')
        value = params.get('value')
        if not variable_name:
            raise Exception("缺少变量名")
        context.set_variable(variable_name, value)
    
    def get_variable(self, params, context):
        """获取变量"""
        variable_name = params.get('variable_name')
        if not variable_name:
            raise Exception("缺少变量名")
        return context.get_variable(variable_name)
