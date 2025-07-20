
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI API配置助手 - 重构版本
"""

import os
import json
import re
from typing import Dict, Any, Optional, List

class SimpleAPIHelper:
    """简化的API配置助手"""

    def __init__(self):
        self.config_file = '.ai_config.json'

        # 支持的AI模型配置
        self.ai_models = {
            'openai': {
                'name': 'OpenAI GPT',
                'official': {
                    'base_url': 'https://api.openai.com/v1',
                    'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
                    'default_model': 'gpt-4o-mini'
                },
                'proxy': {
                    'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
                    'default_model': 'gpt-4o-mini'
                }
            },
            'gemini': {
                'name': 'Google Gemini',
                'official': {
                    'type': 'gemini_official',
                    'models': ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro'],
                    'default_model': 'gemini-2.5-flash'
                },
                'proxy': {
                    'models': ['gemini-2.5-pro', 'gemini-2.0-flash-thinking-exp'],
                    'default_model': 'gemini-2.5-pro'
                }
            },
            'deepseek': {
                'name': 'DeepSeek',
                'official': {
                    'base_url': 'https://api.deepseek.com/v1',
                    'models': ['deepseek-r1', 'deepseek-v3', 'deepseek-chat'],
                    'default_model': 'deepseek-r1'
                },
                'proxy': {
                    'models': ['deepseek-r1', 'deepseek-v3', 'deepseek-chat'],
                    'default_model': 'deepseek-r1'
                }
            },
            'claude': {
                'name': 'Anthropic Claude',
                'official': None,  # 不支持官方
                'proxy': {
                    'models': ['claude-3.5-sonnet', 'claude-3-opus'],
                    'default_model': 'claude-3.5-sonnet'
                }
            }
        }

        # 中转服务商配置
        self.proxy_providers = {
            'chataiapi': {
                'name': 'ChatAI API (推荐)',
                'base_url': 'https://www.chataiapi.com/v1'
            },
            'openrouter': {
                'name': 'OpenRouter',
                'base_url': 'https://openrouter.ai/api/v1',
                'extra_headers': {
                    'HTTP-Referer': 'https://replit.com',
                    'X-Title': 'TV-Clipper-AI'
                }
            },
            'suanli': {
                'name': '算力云',
                'base_url': 'https://api.suanli.cn/v1'
            },
            'custom': {
                'name': '自定义中转商',
                'base_url': ''
            }
        }

    def interactive_setup(self) -> Dict[str, Any]:
        """交互式配置AI API"""
        print("🤖 AI分析配置")
        print("=" * 40)

        # 第一步：选择模型类型
        print("第一步：选择AI模型类型")
        model_keys = list(self.ai_models.keys())
        for i, (key, info) in enumerate(self.ai_models.items(), 1):
            print(f"{i}. {info['name']}")
        print("0. 跳过AI配置")

        while True:
            try:
                choice = input(f"\n请选择模型类型 (0-{len(model_keys)}): ").strip()
                if choice == "0":
                    return {'enabled': False, 'provider': 'none'}

                choice = int(choice)
                if 1 <= choice <= len(model_keys):
                    selected_model_type = model_keys[choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

        # 第二步：选择官方或中转
        model_info = self.ai_models[selected_model_type]
        print(f"\n第二步：选择 {model_info['name']} 的接口类型")

        api_type_options = []
        if model_info['official']:
            api_type_options.append(('official', '官方API'))
        api_type_options.append(('proxy', '中转API'))

        for i, (key, name) in enumerate(api_type_options, 1):
            print(f"{i}. {name}")

        while True:
            try:
                choice = input(f"请选择接口类型 (1-{len(api_type_options)}): ").strip()
                choice = int(choice)
                if 1 <= choice <= len(api_type_options):
                    api_type = api_type_options[choice - 1][0]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

        # 第三步：具体配置
        if api_type == 'official':
            return self._configure_official_api(selected_model_type)
        else:
            return self._configure_proxy_api(selected_model_type)

    def _configure_official_api(self, model_type: str) -> Dict[str, Any]:
        """配置官方API"""
        model_config = self.ai_models[model_type]['official']
        
        print(f"\n第三步：配置 {self.ai_models[model_type]['name']} 官方API")
        
        # 获取API密钥
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}

        # 选择具体模型
        models = model_config['models']
        print(f"\n第四步：选择具体模型")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == model_config['default_model'] else ""
            print(f"{i}. {model}{mark}")

        while True:
            try:
                model_choice = input(f"选择模型 (1-{len(models)}，回车使用推荐): ").strip()
                if not model_choice:
                    selected_model = model_config['default_model']
                    break

                model_choice = int(model_choice)
                if 1 <= model_choice <= len(models):
                    selected_model = models[model_choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

        # 构建配置
        config = {
            'enabled': True,
            'api_type': 'official',
            'model_provider': model_type,
            'api_key': api_key,
            'model': selected_model
        }

        # 添加特定配置
        if model_type == 'gemini':
            config['api_type'] = 'gemini_official'
        else:
            config['base_url'] = model_config['base_url']

        # 测试连接
        if self._test_api_connection(config):
            print("✅ API连接成功！")
            self._save_config(config)
            return config
        else:
            print("❌ API连接失败")
            return {'enabled': False}

    def _configure_proxy_api(self, model_type: str) -> Dict[str, Any]:
        """配置中转API"""
        model_config = self.ai_models[model_type]['proxy']
        
        print(f"\n第三步：配置 {self.ai_models[model_type]['name']} 中转API")

        # 选择中转服务商
        print("选择中转服务商:")
        providers = list(self.proxy_providers.keys())
        for i, (key, info) in enumerate(self.proxy_providers.items(), 1):
            print(f"{i}. {info['name']}")

        while True:
            try:
                choice = input(f"请选择中转商 (1-{len(providers)}): ").strip()
                choice = int(choice)
                if 1 <= choice <= len(providers):
                    provider_key = providers[choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

        provider_info = self.proxy_providers[provider_key]

        # 获取URL（如果是自定义）
        if provider_key == 'custom':
            base_url = input("请输入API地址 (如: https://api.example.com/v1): ").strip()
            if not base_url:
                print("❌ API地址不能为空")
                return {'enabled': False}
        else:
            base_url = provider_info['base_url']
            print(f"API地址: {base_url}")

        # 获取API密钥
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}

        # 选择具体模型
        models = model_config['models']
        print(f"\n第四步：选择具体模型")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == model_config['default_model'] else ""
            print(f"{i}. {model}{mark}")

        while True:
            try:
                model_choice = input(f"选择模型 (1-{len(models)}，回车使用推荐): ").strip()
                if not model_choice:
                    selected_model = model_config['default_model']
                    break

                model_choice = int(model_choice)
                if 1 <= model_choice <= len(models):
                    selected_model = models[model_choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

        # 构建配置
        config = {
            'enabled': True,
            'api_type': 'proxy',
            'model_provider': model_type,
            'proxy_provider': provider_key,
            'api_key': api_key,
            'base_url': base_url,
            'model': selected_model,
            'extra_headers': provider_info.get('extra_headers', {})
        }

        # 测试连接
        if self._test_api_connection(config):
            print("✅ API连接成功！")
            self._save_config(config)
            return config
        else:
            print("❌ API连接失败")
            return {'enabled': False}

    def _test_api_connection(self, config: Dict[str, Any]) -> bool:
        """测试API连接"""
        try:
            api_type = config.get('api_type')

            if api_type == 'gemini_official':
                return self._test_gemini_official(config)
            elif api_type in ['official', 'proxy']:
                return self._test_openai_compatible(config)
            else:
                return False
        except Exception as e:
            print(f"连接测试错误: {e}")
            return False

    def _test_gemini_official(self, config: Dict[str, Any]) -> bool:
        """测试Gemini官方API"""
        try:
            print("🔍 测试Gemini官方API连接...")

            try:
                from google import genai
            except ImportError:
                print("❌ 缺少google-genai库，请运行: pip install google-genai")
                return False

            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'], 
                contents="hello"
            )

            print(f"✅ Gemini API响应: {response.text[:20]}...")
            return True

        except Exception as e:
            print(f"❌ Gemini API测试失败: {e}")
            return False

    def _test_openai_compatible(self, config: Dict[str, Any]) -> bool:
        """测试OpenAI兼容API"""
        try:
            print("🔍 测试OpenAI兼容API连接...")

            from openai import OpenAI

            client_kwargs = {'api_key': config['api_key']}
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']

            client = OpenAI(**client_kwargs)

            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10,
                extra_headers=config.get('extra_headers', {})
            )

            content = completion.choices[0].message.content
            print(f"✅ API响应: {content[:20]}...")
            return True

        except Exception as e:
            print(f"❌ API测试失败: {e}")
            return False

    def call_ai_api(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用AI API"""
        try:
            api_type = config.get('api_type')

            if api_type == 'gemini_official':
                return self._call_gemini_official(prompt, config)
            elif api_type in ['official', 'proxy']:
                return self._call_openai_compatible(prompt, config)
            else:
                return None
        except Exception as e:
            print(f"AI API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai

            client = genai.Client(api_key=config['api_key'])

            full_prompt = f"你是专业的电视剧剧情分析师，专注于识别精彩片段。\n\n{prompt}"

            response = client.models.generate_content(
                model=config['model'],
                contents=full_prompt
            )

            return response.text

        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_openai_compatible(self, prompt: str, config: Dict[str, Any]) -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            from openai import OpenAI

            client_kwargs = {'api_key': config['api_key']}
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']

            client = OpenAI(**client_kwargs)

            completion = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {'role': 'system', 'content': '你是专业的电视剧剧情分析师，专注于识别精彩片段。'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                extra_headers=config.get('extra_headers', {})
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"OpenAI兼容API调用失败: {e}")
            return None

    def _extract_episode_number(self, filename: str) -> str:
        """从SRT文件名提取集数，使用字符串排序"""
        # 直接使用文件名（去掉扩展名）作为集数标识
        base_name = os.path.splitext(filename)[0]
        return base_name

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

# 全局配置助手实例
config_helper = SimpleAPIHelper()

# 向后兼容的API
def call_openai_api(prompt: str, config: Dict[str, Any]) -> Optional[str]:
    """向后兼容的API调用函数"""
    return config_helper.call_ai_api(prompt, config)
