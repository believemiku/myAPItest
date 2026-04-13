from typing import Dict, Any, List, Union
from utils.logger import logger


class VariableManager:
    """变量管理器"""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
    
    def clear(self) -> None:
        """清空变量"""
        self.variables.clear()
        logger.info("变量已清空")
    
    def update(self, variables: Dict[str, Any]) -> None:
        """更新变量"""
        if variables:
            self.variables.update(variables)
            logger.info(f"更新变量: {variables}")
    
    def set(self, name: str, value: Any) -> None:
        """设置变量"""
        self.variables[name] = value
        logger.info(f"设置变量: {name} = {value}")
    
    def get(self, name: str) -> Any:
        """获取变量"""
        return self.variables.get(name)
    
    def process_params(self, params: Any) -> Any:
        """处理参数中的变量"""
        return self._process_value(params)
    
    def _process_value(self, value: Any) -> Any:
        """处理单个值中的变量"""
        if isinstance(value, dict):
            logger.debug(f"处理字典参数: {value}")
            return {k: self._process_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            logger.debug(f"处理列表参数: {value}")
            return [self._process_value(item) for item in value]
        elif isinstance(value, str) and '${' in value and '}' in value:
            logger.debug(f"处理变量引用: {value}")
            # 处理变量引用
            processed_value = value
            for var_name, var_value in self.variables.items():
                placeholder = f"${{{var_name}}}"
                if placeholder in processed_value:
                    # 如果变量值是字符串，直接替换
                    if isinstance(var_value, str):
                        processed_value = processed_value.replace(placeholder, var_value)
                    else:
                        # 如果变量值不是字符串，先检查整个字符串是否只包含这个变量
                        if processed_value == placeholder:
                            # 如果整个字符串只包含这个变量，返回变量值本身（保持类型）
                            return var_value
                        else:
                            # 否则，将变量值转换为字符串进行替换
                            processed_value = processed_value.replace(placeholder, str(var_value))
            # 处理特殊变量
            if '${response' in processed_value:
                # 处理response相关的变量
                import jsonpath
                # 提取response变量格式: ${response.属性} 或 ${response.json.路径}
                import re
                response_pattern = r'\$\{response(\.(json|status_code|text|headers)(\..+)?)?\}'
                matches = re.findall(response_pattern, processed_value)
                
                for match in matches:
                    full_match = f"${{response{match[0]}}}"
                    if full_match in processed_value:
                        # 获取响应对象
                        response = self.get('response')
                        if not response:
                            continue
                        
                        # 处理不同类型的response变量
                        if not match[0]:
                            # ${response} - 返回整个响应对象
                            var_value = response
                        elif match[1] == 'status_code':
                            # ${response.status_code} - 返回状态码
                            var_value = response.status_code
                        elif match[1] == 'text':
                            # ${response.text} - 返回响应文本
                            var_value = response.text
                        elif match[1] == 'headers':
                            # ${response.headers.名称} - 返回响应头
                            if match[2]:
                                header_name = match[2][1:]  # 移除开头的点
                                var_value = response.headers.get(header_name)
                            else:
                                var_value = dict(response.headers)
                        elif match[1] == 'json':
                            # ${response.json.路径} - 返回JSON路径对应的值
                            response_json = self.get('response_json')
                            if not response_json:
                                try:
                                    response_json = response.json()
                                except Exception:
                                    continue
                            
                            if match[2]:
                                json_path = match[2][1:]  # 移除开头的点
                                try:
                                    json_result = jsonpath.jsonpath(response_json, json_path)
                                    if json_result and len(json_result) > 0:
                                        var_value = json_result[0]
                                    else:
                                        continue
                                except Exception:
                                    continue
                            else:
                                var_value = response_json
                        else:
                            continue
                        
                        # 替换变量
                        if isinstance(var_value, str):
                            processed_value = processed_value.replace(full_match, var_value)
                        else:
                            # 如果整个字符串只包含这个变量，返回变量值本身（保持类型）
                            if processed_value == full_match:
                                return var_value
                            else:
                                # 否则，将变量值转换为字符串进行替换
                                processed_value = processed_value.replace(full_match, str(var_value))
            return processed_value
        return value