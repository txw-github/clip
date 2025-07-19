
"""
配置管理 - 支持多种分析模式
"""

class AnalysisConfig:
    """分析配置类"""
    
    # 分析模式
    RULE_BASED = "rule_based"      # 纯规则分析（当前方案）
    AI_ENHANCED = "ai_enhanced"    # AI增强分析
    HYBRID = "hybrid"              # 混合模式
    
    def __init__(self):
        # 默认配置
        self.analysis_mode = self.RULE_BASED
        self.ai_api_key = None
        self.ai_model = "gpt-3.5-turbo"
        self.ai_timeout = 10
        
        # 评分权重配置
        self.rule_weight = 0.7      # 规则评分权重
        self.ai_weight = 0.3        # AI评分权重
        
        # 质量阈值
        self.min_score_threshold = 5.0
        self.duration_range = (120, 180)  # 2-3分钟
        
        # 加载保存的配置
        self._load_config()
        
        # API配置选项
        self.supported_apis = {
            'openai': {
                'url': 'https://api.openai.com/v1/chat/completions',
                'models': ['gpt-3.5-turbo', 'gpt-4'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            },
            'deepseek': {
                'url': 'https://api.deepseek.com/v1/chat/completions',
                'models': ['deepseek-chat', 'deepseek-coder'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            },
            'kimi': {
                'url': 'https://api.moonshot.cn/v1/chat/completions',
                'models': ['moonshot-v1-8k', 'moonshot-v1-32k'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            },
            'qwen': {
                'url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                'models': ['qwen-turbo', 'qwen-plus', 'qwen-max'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            },
            'zhipu': {
                'url': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                'models': ['glm-4', 'glm-3-turbo'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            },
            'baichuan': {
                'url': 'https://api.baichuan-ai.com/v1/chat/completions',
                'models': ['Baichuan2-Turbo', 'Baichuan2-Turbo-192k'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            },
            'custom': {
                'url': '',  # 用户自定义
                'models': ['custom-model'],
                'headers': {'Authorization': 'Bearer {api_key}', 'Content-Type': 'application/json'}
            }
        }
    
    def set_ai_mode(self, api_provider: str = "openai", api_key: str = None, model: str = None, custom_url: str = None):
        """设置AI分析模式"""
        if api_provider in self.supported_apis:
            self.analysis_mode = self.AI_ENHANCED
            self.ai_api_key = api_key
            self.ai_model = model or self.supported_apis[api_provider]['models'][0]
            self.api_url = custom_url or self.supported_apis[api_provider]['url']
            self.api_provider = api_provider
            self.api_headers = self.supported_apis[api_provider]['headers']
            
            # 保存配置到文件
            self._save_config()
            return True
        return False
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                'analysis_mode': self.analysis_mode,
                'api_provider': getattr(self, 'api_provider', None),
                'ai_model': self.ai_model,
                'rule_weight': self.rule_weight,
                'ai_weight': self.ai_weight
            }
            
            with open('.config.json', 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ 保存配置失败: {e}")
    
    def _load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists('.config.json'):
                with open('.config.json', 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                self.analysis_mode = config_data.get('analysis_mode', self.RULE_BASED)
                self.ai_model = config_data.get('ai_model', 'gpt-3.5-turbo')
                self.rule_weight = config_data.get('rule_weight', 0.7)
                self.ai_weight = config_data.get('ai_weight', 0.3)
                
                api_provider = config_data.get('api_provider')
                if api_provider and api_provider in self.supported_apis:
                    self.api_provider = api_provider
                    self.api_url = self.supported_apis[api_provider]['url']
                    self.api_headers = self.supported_apis[api_provider]['headers']
                
                return True
        except Exception as e:
            print(f"⚠ 加载配置失败: {e}")
        return False
    
    def validate_api_connection(self):
        """验证API连接"""
        if not self.ai_api_key or not hasattr(self, 'api_url'):
            return False, "API密钥或URL未配置"
        
        try:
            import requests
            test_data = {
                'model': self.ai_model,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 5
            }
            
            headers = {}
            for key, value in self.api_headers.items():
                headers[key] = value.format(api_key=self.ai_api_key)
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=test_data, 
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "API连接正常"
            else:
                return False, f"API返回错误: {response.status_code}"
                
        except Exception as e:
            return False, f"连接测试失败: {e}"
    
    def set_custom_api(self, api_url: str, api_key: str, model: str = "custom-model"):
        """设置自定义API"""
        self.analysis_mode = self.AI_ENHANCED
        self.ai_api_key = api_key
        self.ai_model = model
        self.api_url = api_url
        self.api_provider = "custom"
        self.api_headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        return True
    
    def set_hybrid_mode(self, rule_weight: float = 0.7):
        """设置混合分析模式"""
        self.analysis_mode = self.HYBRID
        self.rule_weight = rule_weight
        self.ai_weight = 1.0 - rule_weight
    
    def get_prompt_template(self) -> str:
        """获取AI分析提示词模板"""
        return """
你是专业的电视剧剪辑师，专注于法律悬疑剧的精彩片段识别。

请评估以下对话片段：
"{text}"

评估维度：
1. 主线剧情推进度（法案调查、证据揭露、法庭辩论）
2. 戏剧冲突强度（情感爆发、观点对立、真相反转）  
3. 角色关系发展（父女情、法律职业操守、正义追求）
4. 信息密度（关键线索、重要证词、案件突破）
5. 观众吸引力（悬念制造、情感共鸣、剧情张力）

请给出0-10分的综合评分，只返回数字：
"""

# 全局配置实例
config = AnalysisConfig()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI配置管理模块 - 支持多种大模型接口
"""

import os
from typing import Optional, Dict, Any

class AIConfig:
    def __init__(self):
        # 默认配置
        self.analysis_mode = "hybrid"  # hybrid, rule_based, ai_only
        self.ai_timeout = 10
        
        # AI接口配置
        self.api_provider = None
        self.ai_api_key = None
        self.ai_model = None
        self.api_url = None
        self.api_headers = {}
        
        # 支持的AI服务商配置
        self.supported_apis = {
            'openai': {
                'name': 'OpenAI',
                'base_url': 'https://api.openai.com/v1/chat/completions',
                'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview'],
                'headers': {
                    'Authorization': 'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'deepseek': {
                'name': 'DeepSeek',
                'base_url': 'https://api.deepseek.com/v1/chat/completions',
                'models': ['deepseek-chat', 'deepseek-coder'],
                'headers': {
                    'Authorization': 'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'kimi': {
                'name': 'Moonshot',
                'base_url': 'https://api.moonshot.cn/v1/chat/completions',
                'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
                'headers': {
                    'Authorization': 'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'qwen': {
                'name': '通义千问',
                'base_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                'models': ['qwen-turbo', 'qwen-plus', 'qwen-max'],
                'headers': {
                    'Authorization': 'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'zhipu': {
                'name': '智谱清言',
                'base_url': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                'models': ['glm-4', 'glm-3-turbo'],
                'headers': {
                    'Authorization': 'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'baichuan': {
                'name': '百川大模型',
                'base_url': 'https://api.baichuan-ai.com/v1/chat/completions',
                'models': ['Baichuan2-Turbo', 'Baichuan2-Turbo-192k'],
                'headers': {
                    'Authorization': 'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            }
        }
        
        # 尝试从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量或Replit Secrets加载配置"""
        # 检查Replit Secrets
        self.ai_api_key = os.getenv('AI_API_KEY')
        provider = os.getenv('AI_API_PROVIDER')
        model = os.getenv('AI_MODEL')
        
        if self.ai_api_key and provider:
            self.set_ai_mode(provider, self.ai_api_key, model)
    
    def set_ai_mode(self, provider: str, api_key: str, model: str = None) -> bool:
        """配置AI模式"""
        if provider not in self.supported_apis:
            return False
        
        self.api_provider = provider
        self.ai_api_key = api_key
        
        provider_config = self.supported_apis[provider]
        self.api_url = provider_config['base_url']
        
        # 设置模型
        if model and model in provider_config['models']:
            self.ai_model = model
        else:
            self.ai_model = provider_config['models'][0]
        
        # 设置请求头
        self.api_headers = {}
        for key, value in provider_config['headers'].items():
            self.api_headers[key] = value.format(api_key=api_key)
        
        return True
    
    def set_custom_api(self, api_url: str, api_key: str, model: str) -> bool:
        """设置自定义API"""
        self.api_provider = 'custom'
        self.ai_api_key = api_key
        self.api_url = api_url
        self.ai_model = model
        self.api_headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        return True
    
    def is_ai_enabled(self) -> bool:
        """检查是否启用AI"""
        return bool(self.ai_api_key and self.api_url)
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            'analysis_mode': self.analysis_mode,
            'ai_enabled': self.is_ai_enabled(),
            'api_provider': self.api_provider,
            'ai_model': self.ai_model,
            'supported_providers': list(self.supported_apis.keys())
        }

# 全局配置实例
config = AIConfig()
