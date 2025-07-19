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
            'chataiapi': {
                'name': 'ChatAI API (推荐 - 支持多模型)',
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
                'rank': 1
            },
            'suanli': {
                'name': '算力云 (Suanli)',
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
                'rank': 2
            },
            'openrouter': {
                'name': 'OpenRouter (多模型支持)',
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
                'rank': 3
            },
            'deepseek_direct': {
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
                'rank': 4
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
        print("🤖 通用AI分析配置 - 支持多种中转服务商")
        print("=" * 60)

        # 显示推荐服务商
        print("🎯 推荐的中转服务商（按推荐程度排序）：")
        sorted_services = sorted(
            self.service_templates.items(),
            key=lambda x: x[1]['rank']
        )

        for i, (key, info) in enumerate(sorted_services, 1):
            if key == 'custom':
                continue
            print(f"{i}. {info['name']}")
            print(f"   • 地址: {info['base_url']}")
            print(f"   • 推荐模型: {info['default_model']}")
            print()

        print(f"{len(sorted_services)}. 手动配置自定义服务商")
        print("0. 跳过AI配置（使用基础分析）")

        while True:
            try:
                choice = input(f"\n请选择服务商 (0-{len(sorted_services)}): ")
                choice = int(choice)

                if choice == 0:
                    return {'enabled': False, 'provider': 'none'}
                elif 1 <= choice <= len(sorted_services) - 1:
                    service_key = list(dict(sorted_services).keys())[choice - 1]
                    return self._configure_service(service_key)
                elif choice == len(sorted_services):
                    return self._configure_custom_service()
                else:
                    print("❌ 无效选择，请重试")
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
            if config.get('api_type') == 'openai_compatible':
                return self._test_openai_compatible_api(config)
            else:
                return self._test_custom_api(config)
        except Exception as e:
            print(f"连接测试错误: {e}")
            return False

    def _test_openai_compatible_api(self, config: Dict[str, Any]) -> bool:
        """测试OpenAI兼容API"""
        try:
            print(f"📡 正在测试连接...")
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