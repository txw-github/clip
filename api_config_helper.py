
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能API配置助手 - 支持官方API和中转API的灵活选择
"""

import os
import json
import time
import requests
from openai import OpenAI
from typing import Dict, Any, Optional, List, Tuple

class IntelligentAPIHelper:
    """智能API配置助手"""

    def __init__(self):
        self.config_file = '.ai_config.json'
        
        # 模型数据库 - 按模型分类，每个模型可以有多个提供商
        self.model_database = {
            'gpt-4o': {
                'name': 'GPT-4o',
                'description': 'OpenAI最新多模态模型，处理文本和图像',
                'providers': {
                    'openai_official': {
                        'name': 'OpenAI 官方',
                        'type': 'official',
                        'base_url': 'https://api.openai.com/v1',
                        'requires_vpn': True,
                        'cost': 'high',
                        'stability': 'excellent'
                    },
                    'chataiapi': {
                        'name': 'ChatAI API',
                        'type': 'proxy',
                        'base_url': 'https://www.chataiapi.com/v1',
                        'requires_vpn': False,
                        'cost': 'medium',
                        'stability': 'good'
                    },
                    'openrouter': {
                        'name': 'OpenRouter',
                        'type': 'proxy',
                        'base_url': 'https://openrouter.ai/api/v1',
                        'requires_vpn': False,
                        'cost': 'medium',
                        'stability': 'good',
                        'extra_headers': {
                            'HTTP-Referer': 'https://replit.com',
                            'X-Title': 'TV-Clipper-AI'
                        }
                    }
                }
            },
            'gpt-4o-mini': {
                'name': 'GPT-4o Mini',
                'description': 'GPT-4o的轻量版本，速度快成本低',
                'providers': {
                    'openai_official': {
                        'name': 'OpenAI 官方',
                        'type': 'official',
                        'base_url': 'https://api.openai.com/v1',
                        'requires_vpn': True,
                        'cost': 'low',
                        'stability': 'excellent'
                    },
                    'chataiapi': {
                        'name': 'ChatAI API',
                        'type': 'proxy',
                        'base_url': 'https://www.chataiapi.com/v1',
                        'requires_vpn': False,
                        'cost': 'low',
                        'stability': 'good'
                    }
                }
            },
            'claude-3-5-sonnet-20240620': {
                'name': 'Claude 3.5 Sonnet',
                'description': 'Anthropic最强模型，擅长文本分析和推理',
                'providers': {
                    'anthropic_official': {
                        'name': 'Anthropic 官方',
                        'type': 'official',
                        'base_url': 'https://api.anthropic.com',
                        'requires_vpn': True,
                        'cost': 'medium',
                        'stability': 'excellent',
                        'api_format': 'anthropic'  # 特殊API格式
                    },
                    'chataiapi': {
                        'name': 'ChatAI API',
                        'type': 'proxy',
                        'base_url': 'https://www.chataiapi.com/v1',
                        'requires_vpn': False,
                        'cost': 'medium',
                        'stability': 'good'
                    },
                    'openrouter': {
                        'name': 'OpenRouter',
                        'type': 'proxy',
                        'base_url': 'https://openrouter.ai/api/v1',
                        'requires_vpn': False,
                        'cost': 'medium',
                        'stability': 'good',
                        'extra_headers': {
                            'HTTP-Referer': 'https://replit.com',
                            'X-Title': 'TV-Clipper-AI'
                        }
                    }
                }
            },
            'deepseek-r1': {
                'name': 'DeepSeek R1',
                'description': '深度推理模型，支持思考过程展示',
                'providers': {
                    'deepseek_official': {
                        'name': 'DeepSeek 官方',
                        'type': 'official',
                        'base_url': 'https://api.deepseek.com/v1',
                        'requires_vpn': True,
                        'cost': 'low',
                        'stability': 'excellent',
                        'special_features': ['reasoning_content']
                    },
                    'chataiapi': {
                        'name': 'ChatAI API',
                        'type': 'proxy',
                        'base_url': 'https://www.chataiapi.com/v1',
                        'requires_vpn': False,
                        'cost': 'low',
                        'stability': 'good',
                        'special_features': ['reasoning_content']
                    },
                    'suanli': {
                        'name': '算力云',
                        'type': 'proxy',
                        'base_url': 'https://api.suanli.cn/v1',
                        'requires_vpn': False,
                        'cost': 'very_low',
                        'stability': 'fair',
                        'model_path': 'deepseek-ai/DeepSeek-R1'  # 完整模型路径
                    }
                }
            },
            'gemini-2.5-pro': {
                'name': 'Gemini 2.5 Pro',
                'description': 'Google最新大模型，多模态能力强',
                'providers': {
                    'google_official': {
                        'name': 'Google 官方',
                        'type': 'official',
                        'base_url': None,  # 官方API不需要base_url
                        'requires_vpn': True,
                        'cost': 'medium',
                        'stability': 'excellent',
                        'api_format': 'gemini'  # 特殊API格式
                    },
                    'chataiapi': {
                        'name': 'ChatAI API',
                        'type': 'proxy',
                        'base_url': 'https://www.chataiapi.com/v1',
                        'requires_vpn': False,
                        'cost': 'medium',
                        'stability': 'good'
                    }
                }
            },
            'gemini-2.5-flash': {
                'name': 'Gemini 2.5 Flash',
                'description': 'Google快速响应模型',
                'providers': {
                    'google_official': {
                        'name': 'Google 官方',
                        'type': 'official',
                        'base_url': None,
                        'requires_vpn': True,
                        'cost': 'low',
                        'stability': 'excellent',
                        'api_format': 'gemini'
                    },
                    'chataiapi': {
                        'name': 'ChatAI API',
                        'type': 'proxy',
                        'base_url': 'https://www.chataiapi.com/v1',
                        'requires_vpn': False,
                        'cost': 'low',
                        'stability': 'good'
                    }
                }
            }
        }
    
    def interactive_setup(self) -> Dict[str, Any]:
        """智能交互式配置"""
        print("🤖 智能AI配置向导")
        print("=" * 60)
        print("支持官方API和中转API，同一模型可选择不同服务商")
        print()
        
        # 1. 询问网络环境
        print("1️⃣ 网络环境检测")
        has_vpn = input("您是否可以访问国外网站（有魔法上网）？(y/n): ").lower().strip() == 'y'
        print()
        
        # 2. 推荐合适的模型
        print("2️⃣ 为您推荐合适的模型:")
        suitable_models = self._get_suitable_models(has_vpn)
        
        for i, (model_key, model_info) in enumerate(suitable_models, 1):
            print(f"{i}. {model_info['name']}")
            print(f"   📝 {model_info['description']}")
            print(f"   🌐 可用服务商数量: {len(self._get_available_providers(model_key, has_vpn))}")
            print()
        
        # 选择模型
        while True:
            try:
                choice = input(f"请选择模型 (1-{len(suitable_models)}): ").strip()
                choice = int(choice)
                if 1 <= choice <= len(suitable_models):
                    selected_model = list(suitable_models)[choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")
        
        # 3. 选择服务商
        return self._configure_model_provider(selected_model, has_vpn)
    
    def _get_suitable_models(self, has_vpn: bool) -> List[Tuple[str, Dict[str, Any]]]:
        """获取适合的模型列表"""
        suitable = []
        for model_key, model_info in self.model_database.items():
            available_providers = self._get_available_providers(model_key, has_vpn)
            if available_providers:
                suitable.append((model_key, model_info))
        return suitable
    
    def _get_available_providers(self, model_key: str, has_vpn: bool) -> List[Tuple[str, Dict[str, Any]]]:
        """获取可用的服务商"""
        model_info = self.model_database[model_key]
        available = []
        
        for provider_key, provider_info in model_info['providers'].items():
            # 如果没有VPN，跳过需要VPN的官方API
            if not has_vpn and provider_info.get('requires_vpn', False):
                continue
            available.append((provider_key, provider_info))
        
        # 按优先级排序：官方API优先（如果有VPN），然后按稳定性
        def sort_key(item):
            provider_info = item[1]
            priority = 0
            if provider_info['type'] == 'official' and has_vpn:
                priority += 100
            
            stability_scores = {
                'excellent': 50,
                'good': 30,
                'fair': 10
            }
            priority += stability_scores.get(provider_info.get('stability', 'fair'), 0)
            
            return priority
        
        available.sort(key=sort_key, reverse=True)
        return available
    
    def _configure_model_provider(self, model_key: str, has_vpn: bool) -> Dict[str, Any]:
        """配置特定模型的服务商"""
        model_info = self.model_database[model_key]
        available_providers = self._get_available_providers(model_key, has_vpn)
        
        print(f"\n3️⃣ 配置 {model_info['name']}")
        print("=" * 40)
        print("可用服务商:")
        
        for i, (provider_key, provider_info) in enumerate(available_providers, 1):
            print(f"\n{i}. {provider_info['name']}")
            print(f"   🏷️  类型: {'官方API' if provider_info['type'] == 'official' else '中转API'}")
            if provider_info['base_url']:
                print(f"   🌐 地址: {provider_info['base_url']}")
            else:
                print(f"   🌐 地址: 官方SDK直连")
            print(f"   💰 成本: {provider_info['cost']}")
            print(f"   📊 稳定性: {provider_info['stability']}")
            
            if provider_info.get('special_features'):
                print(f"   ⭐ 特色: {', '.join(provider_info['special_features'])}")
            
            if provider_info.get('requires_vpn'):
                print(f"   🔒 需要魔法上网")
            else:
                print(f"   🌏 国内可访问")
        
        # 选择服务商
        while True:
            try:
                choice = input(f"\n请选择服务商 (1-{len(available_providers)}): ").strip()
                choice = int(choice)
                if 1 <= choice <= len(available_providers):
                    selected_provider_key, selected_provider = available_providers[choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")
        
        # 配置API密钥
        print(f"\n4️⃣ 配置API密钥")
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}
        
        # 构建配置
        config = self._build_config(model_key, selected_provider_key, selected_provider, api_key)
        
        # 测试连接
        print(f"\n🔍 测试API连接...")
        if self._test_api_connection(config):
            print("✅ API连接成功！")
            self._save_config(config)
            return config
        else:
            print("❌ API连接失败，请检查密钥和网络")
            return {'enabled': False}
    
    def _build_config(self, model_key: str, provider_key: str, provider_info: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """构建配置对象"""
        # 获取实际使用的模型名称
        actual_model = provider_info.get('model_path', model_key)
        
        config = {
            'enabled': True,
            'model_key': model_key,
            'provider_key': provider_key,
            'provider_name': provider_info['name'],
            'provider_type': provider_info['type'],
            'api_key': api_key,
            'model': actual_model,
            'base_url': provider_info.get('base_url'),
            'api_format': provider_info.get('api_format', 'openai'),
            'extra_headers': provider_info.get('extra_headers', {}),
            'special_features': provider_info.get('special_features', [])
        }
        
        return config
    
    def _test_api_connection(self, config: Dict[str, Any]) -> bool:
        """测试API连接"""
        try:
            api_format = config.get('api_format', 'openai')
            
            if api_format == 'gemini':
                return self._test_gemini_api(config)
            elif api_format == 'anthropic':
                return self._test_anthropic_api(config)
            else:
                return self._test_openai_compatible_api(config)
                
        except Exception as e:
            print(f"连接测试错误: {e}")
            return False
    
    def _test_openai_compatible_api(self, config: Dict[str, Any]) -> bool:
        """测试OpenAI兼容API"""
        try:
            print(f"📡 正在测试OpenAI兼容API...")
            print(f"   服务商: {config['provider_name']}")
            print(f"   模型: {config['model']}")
            
            client = OpenAI(
                base_url=config['base_url'],
                api_key=config['api_key']
            )

            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10,
                extra_headers=config.get('extra_headers', {})
            )
            
            # 处理特殊功能
            message = completion.choices[0].message
            if 'reasoning_content' in config.get('special_features', []):
                if hasattr(message, 'reasoning_content') and message.reasoning_content:
                    print(f"✅ 检测到推理功能")
            
            print(f"✅ API响应成功: {message.content[:20]}...")
            return True
            
        except Exception as e:
            self._handle_api_error(e)
            return False
    
    def _test_gemini_api(self, config: Dict[str, Any]) -> bool:
        """测试Gemini官方API"""
        try:
            print(f"📡 正在测试Gemini官方API...")
            
            try:
                from google import genai
            except ImportError:
                print("❌ 缺少google-genai库，请安装: pip install google-genai")
                return False
            
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'], 
                contents="hello"
            )
            
            print(f"✅ Gemini API响应成功: {response.text[:20]}...")
            return True
            
        except Exception as e:
            print(f"❌ Gemini API测试失败: {e}")
            return False
    
    def _test_anthropic_api(self, config: Dict[str, Any]) -> bool:
        """测试Anthropic官方API"""
        try:
            print(f"📡 正在测试Anthropic官方API...")
            
            try:
                import anthropic
            except ImportError:
                print("❌ 缺少anthropic库，请安装: pip install anthropic")
                return False
            
            client = anthropic.Anthropic(api_key=config['api_key'])
            response = client.messages.create(
                model=config['model'],
                max_tokens=10,
                messages=[{"role": "user", "content": "hello"}]
            )
            
            print(f"✅ Anthropic API响应成功")
            return True
            
        except Exception as e:
            print(f"❌ Anthropic API测试失败: {e}")
            return False
    
    def _handle_api_error(self, error: Exception):
        """处理API错误"""
        error_msg = str(error)
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            print(f"❌ API密钥无效或已过期")
        elif "403" in error_msg or "Forbidden" in error_msg:
            print(f"❌ 访问被拒绝，可能是余额不足或权限问题")
        elif "404" in error_msg or "Not Found" in error_msg:
            print(f"❌ API地址或模型不存在")
        elif "timeout" in error_msg.lower():
            print(f"❌ 连接超时，请检查网络")
        else:
            print(f"❌ 连接错误: {error_msg}")
    
    def call_ai_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """智能API调用"""
        try:
            api_format = config.get('api_format', 'openai')
            
            if api_format == 'gemini':
                return self._call_gemini_api(prompt, config)
            elif api_format == 'anthropic':
                return self._call_anthropic_api(prompt, config)
            else:
                return self._call_openai_compatible_api(prompt, config)
                
        except Exception as e:
            print(f"AI API调用异常: {e}")
            return None
    
    def _call_openai_compatible_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用OpenAI兼容API"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                client = OpenAI(
                    base_url=config['base_url'],
                    api_key=config['api_key'],
                    timeout=30.0
                )

                completion = client.chat.completions.create(
                    model=config['model'],
                    messages=[
                        {'role': 'system', 'content': '你是专业的电视剧剧情分析师。'},
                        {'role': 'user', 'content': prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                    extra_headers=config.get('extra_headers', {})
                )

                message = completion.choices[0].message
                
                # 处理推理内容
                if 'reasoning_content' in config.get('special_features', []):
                    if hasattr(message, 'reasoning_content') and message.reasoning_content:
                        print(f"🤔 AI思考过程预览:")
                        reasoning_lines = message.reasoning_content.split('\n')[:3]
                        for line in reasoning_lines:
                            if line.strip():
                                print(f"   {line.strip()}")
                        print()
                
                return message.content

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⏰ API调用失败，{wait_time}秒后重试... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"❌ API调用最终失败: {e}")
                    return None
        
        return None
    
    def _call_gemini_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai
            
            client = genai.Client(api_key=config['api_key'])
            
            full_prompt = f"你是专业的电视剧剧情分析师。\n\n{prompt}"
            
            response = client.models.generate_content(
                model=config['model'],
                contents=full_prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None
    
    def _call_anthropic_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用Anthropic官方API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=config['api_key'])
            
            response = client.messages.create(
                model=config['model'],
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": f"你是专业的电视剧剧情分析师。\n\n{prompt}"}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Anthropic API调用失败: {e}")
            return None
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ 加载配置失败: {e}")
        return {'enabled': False}
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存")
        except Exception as e:
            print(f"⚠ 保存配置失败: {e}")
    
    def add_custom_model(self, model_key: str, model_name: str, description: str,
                        provider_key: str, provider_name: str, base_url: str = None,
                        api_format: str = 'openai', **kwargs) -> bool:
        """添加自定义模型配置"""
        try:
            if model_key not in self.model_database:
                self.model_database[model_key] = {
                    'name': model_name,
                    'description': description,
                    'providers': {}
                }
            
            self.model_database[model_key]['providers'][provider_key] = {
                'name': provider_name,
                'type': 'custom',
                'base_url': base_url,
                'requires_vpn': kwargs.get('requires_vpn', False),
                'cost': kwargs.get('cost', 'unknown'),
                'stability': kwargs.get('stability', 'unknown'),
                'api_format': api_format,
                **kwargs
            }
            
            print(f"✅ 已添加自定义模型配置: {model_name} @ {provider_name}")
            return True
            
        except Exception as e:
            print(f"❌ 添加自定义模型失败: {e}")
            return False

# 全局配置助手实例
config_helper = IntelligentAPIHelper()

# 向后兼容函数
def call_openai_api(prompt: str, config: Dict[str, Any]) -> Optional[str]:
    """向后兼容的API调用函数"""
    return config_helper.call_ai_api(prompt, config)
