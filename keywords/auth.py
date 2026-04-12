class AuthKeywords:
    def authenticate(self, params, context):
        """进行认证"""
        auth_type = params.get('auth_type')
        credentials = params.get('credentials')
        
        if not auth_type or not credentials:
            raise Exception("缺少必要参数: auth_type 和 credentials")
        
        if auth_type == 'bearer':
            # Bearer Token认证
            token = credentials.get('token')
            if not token:
                raise Exception("缺少Bearer Token")
            # 添加Authorization头
            from keywords.http import HttpKeywords
            http_keywords = HttpKeywords()
            http_keywords.add_header({'name': 'Authorization', 'value': f'Bearer {token}'}, context)
        elif auth_type == 'basic':
            # Basic Auth认证
            username = credentials.get('username')
            password = credentials.get('password')
            if not username or not password:
                raise Exception("缺少用户名或密码")
            # 编码并添加Authorization头
            import base64
            auth_str = f"{username}:{password}"
            auth_bytes = auth_str.encode('utf-8')
            auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
            from keywords.http import HttpKeywords
            http_keywords = HttpKeywords()
            http_keywords.add_header({'name': 'Authorization', 'value': f'Basic {auth_base64}'}, context)
        elif auth_type == 'api_key':
            # API Key认证
            api_key = credentials.get('api_key')
            header_name = credentials.get('header_name', 'X-API-Key')
            if not api_key:
                raise Exception("缺少API Key")
            from keywords.http import HttpKeywords
            http_keywords = HttpKeywords()
            http_keywords.add_header({'name': header_name, 'value': api_key}, context)
        else:
            raise Exception(f"不支持的认证类型: {auth_type}")
