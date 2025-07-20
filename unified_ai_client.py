
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一AI客户端
支持所有AI提供商的统一调用接口
"""

from typing import Optional
from unified_config import unified_config

class UnifiedAIClient:
    """统一AI客户端"""
    
    def __init__(self):
        self.config = unified_config.config
        self.enabled = unified_config.is_enabled()
    
    def call_ai(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """统一AI调用接口"""
        if not self.enabled:
            return None
        
        try:
            provider = self.config.get('provider')
            
            if provider == 'gemini_official':
                return self._call_gemini(prompt, system_prompt)
            else:
                return self._call_openai_compatible(prompt, system_prompt)
        except Exception as e:
            print(f"⚠️ AI调用失败: {e}")
            return None
    
    def _call_gemini(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用Gemini API"""
        try:
            from google import genai
            
            client = genai.Client(api_key=self.config['api_key'])
            
            # 组合提示词
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = client.models.generate_content(
                model=self.config['model'],
                contents=full_prompt
            )
            
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini调用失败: {e}")
            return None
    
    def _call_openai_compatible(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            from openai import OpenAI
            
            client_kwargs = {'api_key': self.config['api_key']}
            if 'base_url' in self.config:
                client_kwargs['base_url'] = self.config['base_url']
            
            client = OpenAI(**client_kwargs)
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            completion = client.chat.completions.create(
                model=self.config['model'],
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                extra_headers=self.config.get('extra_headers', {})
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ OpenAI兼容API调用失败: {e}")
            return None

# 全局AI客户端实例
ai_client = UnifiedAIClient()
