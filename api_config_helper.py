#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用API配置助手 - 支持多种中转服务商，灵活配置
"""

import os
import json
import requests
from openai import OpenAI
from typing import Dict, Any, Optional, List

class UniversalAPIHelper:
    """通用API配置助手"""

    def __init__(self):
        self.config_file = '.ai_config.json'

        # 预定义的服务商配置模板
        self.service_templates = {
            # 官方API
            'gemini_official': {
                'name': 'Google Gemini 官方API',
                'base_url': None,  # 官方API不需要base_url
                'api_type': 'gemini_official',
                'models': [
                    'gemini-2.5-flash',
                    'gemini-2.5-pro',
                    'gemini-1.5-pro',
                    'gemini-1.5-flash'
                ],
                'default_model': 'gemini-2.5-flash',
                'headers': {},
                'rank': 1,
                'is_official': True
            },
            'openai_official': {
                'name': 'OpenAI 官方API',
                'base_url': 'https://api.openai.com/v1',
                'api_type': 'openai_official',
                'models': [
                    'gpt-4o',
                    'gpt-4o-mini',
                    'gpt-4-turbo',
                    'gpt-3.5-turbo'
                ],
                'default_model': 'gpt-4o-mini',
                'headers': {},
                'rank': 2,
                'is_official': True
            },
            'deepseek_official': {
                'name': 'DeepSeek 官方API',
                'base_url': 'https://api.deepseek.com/v1',
                'api_type': 'openai_compatible',
                'models': [
                    'deepseek-r1',
                    'deepseek-v3',
                    'deepseek-chat',
                    'deepseek-reasoner'
                ],
                'default_model': 'deepseek-r1',
                'headers': {},
                'rank': 3,
                'is_official': True
            },
            # 中转API
            'chataiapi': {
                'name': 'ChatAI API (中转 - 推荐)',
                'base_url': 'https://www.chataiapi.com/v1',
                'api_type': 'openai_compatible',
                'models': [
                    'deepseek-r1',
                    'deepseek-v3',
                    'gemini-2.5-pro-preview-05-06',
                    'gpt-4o',
                    'claude-3.5-sonnet'
                ],
                'default_model': 'deepseek-r1',
                'headers': {},
                'rank': 4,
                'is_official': False
            },
            'suanli': {
                'name': '算力云 (中转)',
                'base_url': 'https://api.suanli.cn/v1',
                'api_type': 'openai_compatible', 
                'models': [
                    'QwQ-32B',
                    'deepseek-ai/DeepSeek-R1',
                    'deepseek-ai/DeepSeek-V3',
                    'meta-llama/Llama-3.2-90B-Vision-Instruct',
                    'Qwen/Qwen2.5-72B-Instruct'
                ],
                'default_model': 'deepseek-ai/DeepSeek-R1',
                'headers': {},
                'rank': 5,
                'is_official': False
            },
            'openrouter': {
                'name': 'OpenRouter (中转)',
                'base_url': 'https://openrouter.ai/api/v1',
                'api_type': 'openai_compatible',
                'models': [
                    'deepseek/deepseek-r1',
                    'deepseek/deepseek-chat-v3-0324:free',
                    'google/gemini-2.0-flash-thinking-exp',
                    'openai/gpt-4o',
                    'anthropic/claude-3-5-sonnet'
                ],
                'default_model': 'deepseek/deepseek-chat-v3-0324:free',
                'headers': {
                    'HTTP-Referer': 'https://replit.com',
                    'X-Title': 'TV-Clipper-AI'
                },
                'rank': 6,
                'is_official': False
            },
            'custom': {
                'name': '自定义API服务商',
                'base_url': '',
                'api_type': 'openai_compatible',
                'models': ['custom-model'],
                'default_model': 'custom-model',
                'headers': {},
                'rank': 99
            }
        }

    def interactive_setup(self) -> Dict[str, Any]:
        """交互式配置API"""
        print("🤖 AI分析配置 - 支持官方API和中转服务商")
        print("=" * 60)

        # 先让用户选择官方还是中转
        print("请选择API类型:")
        print("1. 🏢 官方API (直连，需要魔法上网)")
        print("2. 🌐 中转API (国内可访问，推荐)")
        print("3. 🔧 自定义配置")
        print("0. 跳过AI配置（使用基础分析）")

        choice = input("\n请选择 (0-3): ").strip()
        
        if choice == "0":
            return {'enabled': False, 'provider': 'none'}
        elif choice == "1":
            return self._setup_official_apis()
        elif choice == "2":
            return self._setup_proxy_apis()
        elif choice == "3":
            return self._configure_custom_service()
        else:
            print("❌ 无效选择，请重试")
            return self.interactive_setup()

    def _setup_official_apis(self) -> Dict[str, Any]:
        """配置官方API"""
        print("\n🏢 官方API配置")
        print("=" * 40)
        print("注意：官方API需要魔法上网，但响应速度快、稳定性高")
        print()

        # 显示官方API服务商
        official_services = {k: v for k, v in self.service_templates.items() 
                           if v.get('is_official', False)}
        
        sorted_services = sorted(official_services.items(), key=lambda x: x[1]['rank'])
        
        for i, (key, info) in enumerate(sorted_services, 1):
            print(f"{i}. {info['name']}")
            print(f"   • 推荐模型: {info['default_model']}")
            if info['api_type'] == 'gemini_official':
                print(f"   • 特点: 无需base_url，直接使用官方SDK")
            print()
        
        while True:
            try:
                choice = input(f"选择服务商 (1-{len(sorted_services)}): ").strip()
                choice = int(choice)
                if 1 <= choice <= len(sorted_services):
                    service_key = sorted_services[choice - 1][0]  # 修复这里的错误
                    return self._configure_service(service_key)
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

    def _setup_proxy_apis(self) -> Dict[str, Any]:
        """配置中转API"""
        print("\n🌐 中转API配置")
        print("=" * 40)
        print("中转API优势：国内可访问，无需魔法上网，支持多种模型")
        print()

        # 显示中转API服务商
        proxy_services = {k: v for k, v in self.service_templates.items() 
                         if not v.get('is_official', True)}
        
        sorted_services = sorted(proxy_services.items(), key=lambda x: x[1]['rank'])
        
        for i, (key, info) in enumerate(sorted_services, 1):
            print(f"{i}. {info['name']}")
            print(f"   • 地址: {info['base_url']}")
            print(f"   • 推荐模型: {info['default_model']}")
            print()
        
        while True:
            try:
                choice = input(f"选择服务商 (1-{len(sorted_services)}): ").strip()
                choice = int(choice)
                if 1 <= choice <= len(sorted_services):
                    service_key = sorted_services[choice - 1][0]  # 修复这里的错误
                    return self._configure_service(service_key)
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

    def _configure_service(self, service_key: str) -> Dict[str, Any]:
        """配置预定义服务商"""
        service = self.service_templates[service_key]

        print(f"\n🔧 配置 {service['name']}")
        print("-" * 40)
        print(f"API地址: {service['base_url']}")

        # 获取API密钥
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}

        # 选择模型
        print(f"\n可用模型:")
        for i, model in enumerate(service['models'], 1):
            mark = " ⭐ 推荐" if model == service['default_model'] else ""
            print(f"{i}. {model}{mark}")

        while True:
            try:
                model_choice = input(f"选择模型 (1-{len(service['models'])}，回车使用推荐): ").strip()
                if not model_choice:
                    selected_model = service['default_model']
                    break

                model_choice = int(model_choice)
                if 1 <= model_choice <= len(service['models']):
                    selected_model = service['models'][model_choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

        # 构建配置
        config = {
            'enabled': True,
            'provider': service_key,
            'api_key': api_key,
            'model': selected_model,
            'base_url': service['base_url'],
            'api_type': service['api_type'],
            'extra_headers': service.get('headers', {})
        }

        # 测试连接
        print(f"\n🔍 测试API连接...")
        print(f"模型: {selected_model}")
        if self._test_api_connection(config):
            print("✅ API连接成功！")
            self._save_config(config)
            return config
        else:
            print("❌ API连接失败，请检查密钥和网络")
            return {'enabled': False}

    def _configure_custom_service(self) -> Dict[str, Any]:
        """配置自定义服务商"""
        print("\n🔧 配置自定义API服务商")
        print("-" * 40)
        print("💡 支持的配置示例:")
        print("1. OpenAI兼容格式 (推荐)")
        print("2. 自定义请求格式")
        print()

        # 基本信息
        name = input("服务商名称 (例: My API): ").strip() or "Custom API"
        base_url = input("API地址 (例: https://api.example.com/v1): ").strip()
        api_key = input("API密钥: ").strip()
        model = input("模型名称 (例: deepseek-r1): ").strip()

        if not all([base_url, api_key, model]):
            print("❌ 所有字段都必须填写")
            return {'enabled': False}

        # API类型选择
        print("\nAPI类型:")
        print("1. OpenAI兼容 (推荐)")
        print("2. 自定义格式")

        api_type_choice = input("选择API类型 (1-2，回车默认1): ").strip() or "1"
        api_type = 'openai_compatible' if api_type_choice == "1" else 'custom'

        # 额外头部配置
        extra_headers = {}
        print("\n是否需要额外的HTTP头部? (如HTTP-Referer, X-Title等)")
        add_headers = input("添加额外头部? (y/N): ").lower() == 'y'

        if add_headers:
            while True:
                header_name = input("头部名称 (回车结束): ").strip()
                if not header_name:
                    break
                header_value = input(f"{header_name}的值: ").strip()
                if header_value:
                    extra_headers[header_name] = header_value

        # 构建配置
        config = {
            'enabled': True,
            'provider': 'custom',
            'provider_name': name,
            'api_key': api_key,
            'model': model,
            'base_url': base_url,
            'api_type': api_type,
            'extra_headers': extra_headers
        }

        # 测试连接
        print(f"\n🔍 测试自定义API连接...")
        if self._test_api_connection(config):
            print("✅ 自定义API连接成功！")
            self._save_config(config)
            return config
        else:
            print("❌ 自定义API连接失败")
            return {'enabled': False}

    def _test_api_connection(self, config: Dict[str, Any]) -> bool:
        """测试API连接"""
        try:
            api_type = config.get('api_type', 'openai_compatible')
            
            if api_type == 'gemini_official':
                return self._test_gemini_official_api(config)
            elif api_type == 'openai_compatible':
                return self._test_openai_compatible_api(config)
            else:
                return self._test_custom_api(config)
        except Exception as e:
            print(f"连接测试错误: {e}")
            return False

    def _test_openai_compatible_api(self, config: Dict[str, Any]) -> bool:
        """测试OpenAI兼容API"""
        try:
            # Gemini官方API需要特殊处理
            if config.get('api_type') == 'gemini_official':
                return self._test_gemini_official_api(config)
            
            print(f"📡 正在测试OpenAI兼容API连接...")
            print(f"   API地址: {config['base_url']}")
            print(f"   模型: {config['model']}")
            print(f"   密钥前缀: {config['api_key'][:10]}...")
            
            client = OpenAI(
                base_url=config['base_url'],
                api_key=config['api_key']
            )

            extra_headers = config.get('extra_headers', {})

            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10,
                extra_headers=extra_headers
            )
            print(f"✅ API响应成功: {completion.choices[0].message.content[:20]}...")
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"❌ API连接详细错误:")
            
            if "401" in error_msg or "Unauthorized" in error_msg:
                print(f"   🔑 API密钥无效或已过期")
                print(f"   💡 请检查您的API密钥是否正确")
            elif "403" in error_msg or "Forbidden" in error_msg:
                print(f"   🚫 访问被拒绝")
                print(f"   💡 可能是账户余额不足或模型权限问题")
            elif "404" in error_msg or "Not Found" in error_msg:
                print(f"   🔍 API地址或模型不存在")
                print(f"   💡 请检查API地址和模型名称是否正确")
            elif "timeout" in error_msg.lower():
                print(f"   ⏰ 连接超时")
                print(f"   💡 请检查网络连接或稍后重试")
            elif "connection" in error_msg.lower():
                print(f"   🌐 网络连接问题")
                print(f"   💡 请检查网络连接或防火墙设置")
            else:
                print(f"   ❓ 未知错误: {error_msg}")
            
            return False

    def _test_custom_api(self, config: Dict[str, Any]) -> bool:
        """测试自定义格式API"""
        try:
            print(f"📡 正在测试自定义API连接...")
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            headers.update(config.get('extra_headers', {}))

            data = {
                'model': config['model'],
                'messages': [{'role': 'user', 'content': 'hello'}],
                'max_tokens': 10
            }

            url = config['base_url'].rstrip('/') + '/chat/completions'
            print(f"   请求URL: {url}")
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            print(f"   HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"✅ API响应成功: {content[:20]}...")
                    return True
                except:
                    print(f"⚠️ 响应格式异常，但连接成功")
                    return True
            else:
                print(f"❌ API返回错误: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   错误详情: {error_detail}")
                except:
                    print(f"   错误内容: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ 自定义API测试失败: {e}")
            return False

    def call_ai_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """通用AI API调用"""
        try:
            if config.get('api_type') == 'openai_compatible':
                return self._call_openai_compatible_api(prompt, config)
            else:
                return self._call_custom_api(prompt, config)
        except Exception as e:
            print(f"AI API调用异常: {e}")
            return None

    def _call_openai_compatible_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            # Gemini官方API特殊处理
            if config.get('api_type') == 'gemini_official':
                return self._call_gemini_official_api(prompt, config)
            
            client = OpenAI(
                base_url=config['base_url'],
                api_key=config['api_key']
            )

            extra_headers = config.get('extra_headers', {})

            completion = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {'role': 'system', 'content': '你是专业的电视剧剧情分析师，专注于识别精彩片段并制定最佳剪辑方案。'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                extra_headers=extra_headers
            )

            # 处理DeepSeek-R1的特殊输出格式
            message = completion.choices[0].message
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                # 如果有推理内容，可以选择是否包含
                return message.content
            else:
                return message.content

        except Exception as e:
            print(f"OpenAI兼容API调用失败: {e}")
            return None

    def _test_gemini_official_api(self, config: Dict[str, Any]) -> bool:
        """测试Gemini官方API"""
        try:
            print(f"   使用Gemini官方API")
            print(f"   模型: {config['model']}")
            print(f"   密钥前缀: {config['api_key'][:10]}...")
            
            # 使用官方google-genai库
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
            print(f"❌ Gemini官方API测试失败: {e}")
            return False

    def _call_gemini_official_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai
            
            client = genai.Client(api_key=config['api_key'])
            
            # 构建完整的提示
            full_prompt = f"""你是专业的电视剧剧情分析师，专注于识别精彩片段并制定最佳剪辑方案。

{prompt}"""
            
            response = client.models.generate_content(
                model=config['model'],
                contents=full_prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"Gemini官方API调用失败: {e}")
            return None

    def _call_custom_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用自定义格式API"""
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            headers.update(config.get('extra_headers', {}))

            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剧情分析师。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }

            url = config['base_url'].rstrip('/') + '/chat/completions'
            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                print(f"自定义API错误: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"自定义API调用失败: {e}")
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
            print(f"✅ 配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"⚠ 保存配置失败: {e}")

    def add_custom_service(self, name: str, base_url: str, models: List[str], 
                          api_type: str = 'openai_compatible', 
                          extra_headers: Dict[str, str] = None) -> bool:
        """程序化添加自定义服务商"""
        try:
            service_key = name.lower().replace(' ', '_')
            self.service_templates[service_key] = {
                'name': name,
                'base_url': base_url,
                'api_type': api_type,
                'models': models,
                'default_model': models[0] if models else 'default',
                'headers': extra_headers or {},
                'rank': 50
            }
            print(f"✅ 已添加自定义服务商: {name}")
            return True
        except Exception as e:
            print(f"❌ 添加自定义服务商失败: {e}")
            return False

# 全局配置助手实例
config_helper = UniversalAPIHelper()

# 向后兼容的API
def call_openai_api(prompt: str, config: Dict[str, Any]) -> Optional[str]:
    """向后兼容的API调用函数"""
    return config_helper.call_ai_api(prompt, config)