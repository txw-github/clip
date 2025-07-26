#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清晰的API配置助手
官方API：无base_url，使用各自的SDK
中转API：有base_url，使用OpenAI兼容格式
"""

import os
import json
from typing import Dict, Any, Optional

class SimpleAPIConfig:
    """简化的API配置管理"""

    def __init__(self):
        self.config_file = '.ai_config.json'

    def interactive_setup(self) -> Dict[str, Any]:
        """交互式配置"""
        print("🤖 AI接口配置")
        print("=" * 40)

        print("选择AI提供商:")
        print("1. Gemini 官方API (推荐)")
        print("2. OpenAI 官方API")
        print("3. DeepSeek 官方API")
        print("4. 中转API (支持所有模型)")
        print("0. 跳过配置")

        choice = input("请选择 (0-4): ").strip()

        if choice == "0":
            return {'enabled': False}
        elif choice == "1":
            return self._setup_gemini_official()
        elif choice == "2":
            return self._setup_openai_official()
        elif choice == "3":
            return self._setup_deepseek_official()
        elif choice == "4":
            return self._setup_proxy_api()
        else:
            print("❌ 无效选择")
            return {'enabled': False}

    def _setup_gemini_official(self) -> Dict[str, Any]:
        """配置Gemini官方API"""
        print("\n💎 配置Gemini官方API")

        api_key = input("请输入Gemini API Key: ").strip()
        if not api_key:
            print("❌ API Key不能为空")
            return {'enabled': False}

        models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro']
        print("\n选择模型:")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == 'gemini-2.5-flash' else ""
            print(f"{i}. {model}{mark}")

        model_choice = input("选择模型 (1-3，回车默认): ").strip()
        if not model_choice:
            model = 'gemini-2.5-flash'
        else:
            try:
                model = models[int(model_choice) - 1]
            except (ValueError, IndexError):
                model = 'gemini-2.5-flash'

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        if self._test_gemini_official(config):
            self._save_config(config)
            print("✅ Gemini官方API配置成功！")
            return config
        else:
            print("❌ Gemini连接测试失败")
            return {'enabled': False}

    def _setup_openai_official(self) -> Dict[str, Any]:
        """配置OpenAI官方API"""
        print("\n🚀 配置OpenAI官方API")

        api_key = input("请输入OpenAI API Key: ").strip()
        if not api_key:
            print("❌ API Key不能为空")
            return {'enabled': False}

        models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']
        print("\n选择模型:")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == 'gpt-4o-mini' else ""
            print(f"{i}. {model}{mark}")

        model_choice = input("选择模型 (1-3，回车默认): ").strip()
        if not model_choice:
            model = 'gpt-4o-mini'
        else:
            try:
                model = models[int(model_choice) - 1]
            except (ValueError, IndexError):
                model = 'gpt-4o-mini'

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'openai',
            'api_key': api_key,
            'model': model,
            'base_url': 'https://api.openai.com/v1'
        }

        # 测试连接
        if self._test_openai_compatible(config):
            self._save_config(config)
            print("✅ OpenAI官方API配置成功！")
            return config
        else:
            print("❌ OpenAI连接测试失败")
            return {'enabled': False}

    def _setup_deepseek_official(self) -> Dict[str, Any]:
        """配置DeepSeek官方API"""
        print("\n🧠 配置DeepSeek官方API")

        api_key = input("请输入DeepSeek API Key: ").strip()
        if not api_key:
            print("❌ API Key不能为空")
            return {'enabled': False}

        models = ['deepseek-r1', 'deepseek-v3', 'deepseek-chat']
        print("\n选择模型:")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == 'deepseek-r1' else ""
            print(f"{i}. {model}{mark}")

        model_choice = input("选择模型 (1-3，回车默认): ").strip()
        if not model_choice:
            model = 'deepseek-r1'
        else:
            try:
                model = models[int(model_choice) - 1]
            except (ValueError, IndexError):
                model = 'deepseek-r1'

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'deepseek',
            'api_key': api_key,
            'model': model,
            'base_url': 'https://api.deepseek.com/v1'
        }

        # 测试连接
        if self._test_openai_compatible(config):
            self._save_config(config)
            print("✅ DeepSeek官方API配置成功！")
            return config
        else:
            print("❌ DeepSeek连接测试失败")
            return {'enabled': False}

    def _setup_proxy_api(self) -> Dict[str, Any]:
        """配置中转API"""
        print("\n🔄 配置中转API")

        # 推荐的中转商
        proxies = [
            ('chataiapi', 'ChatAI API (推荐)', 'https://www.chataiapi.com/v1'),
            ('openrouter', 'OpenRouter', 'https://openrouter.ai/api/v1'),
            ('custom', '自定义中转', '')
        ]

        print("选择中转商:")
        for i, (key, name, url) in enumerate(proxies, 1):
            print(f"{i}. {name}")

        proxy_choice = input("选择中转商 (1-3): ").strip()
        try:
            proxy_key, proxy_name, base_url = proxies[int(proxy_choice) - 1]
        except (ValueError, IndexError):
            proxy_key, proxy_name, base_url = proxies[0]

        if proxy_key == 'custom':
            base_url = input("请输入API地址: ").strip()
            if not base_url:
                print("❌ API地址不能为空")
                return {'enabled': False}

        api_key = input("请输入API Key: ").strip()
        if not api_key:
            print("❌ API Key不能为空")
            return {'enabled': False}

        # 常用模型
        models = ['gpt-4o', 'claude-3.5-sonnet', 'deepseek-r1', 'gemini-2.5-pro']
        print("\n选择模型:")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == 'deepseek-r1' else ""
            print(f"{i}. {model}{mark}")

        model_choice = input("选择模型 (1-4，回车默认): ").strip()
        if not model_choice:
            model = 'deepseek-r1'
        else:
            try:
                model = models[int(model_choice) - 1]
            except (ValueError, IndexError):
                model = 'deepseek-r1'

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': proxy_key,
            'api_key': api_key,
            'model': model,
            'base_url': base_url
        }

        # OpenRouter需要额外headers
        if proxy_key == 'openrouter':
            config['extra_headers'] = {
                'HTTP-Referer': 'https://replit.com',
                'X-Title': 'TV-Clipper-AI'
            }

        # 测试连接
        if self._test_openai_compatible(config):
            self._save_config(config)
            print(f"✅ {proxy_name}配置成功！")
            return config
        else:
            print(f"❌ {proxy_name}连接测试失败")
            return {'enabled': False}

    def _test_gemini_official(self, config: Dict[str, Any]) -> bool:
        """测试Gemini官方API"""
        try:
            print("🔍 测试Gemini连接...")

            try:
                from google import genai
            except ImportError:
                print("❌ 需要安装: pip install google-genai")
                return False

            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents="hello"
            )

            print(f"✅ 连接成功: {response.text[:20]}...")
            return True

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def _test_openai_compatible(self, config: Dict[str, Any]) -> bool:
        """测试OpenAI兼容API"""
        try:
            print("🔍 测试API连接...")

            from openai import OpenAI

            client_kwargs = {'api_key': config['api_key']}
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']

            client = OpenAI(**client_kwargs)

            request_params = {
                'model': config['model'],
                'messages': [{'role': 'user', 'content': 'hello'}],
                'max_tokens': 10
            }

            if 'extra_headers' in config:
                request_params['extra_headers'] = config['extra_headers']

            response = client.chat.completions.create(**request_params)
            content = response.choices[0].message.content

            print(f"✅ 连接成功: {content[:20]}...")
            return True

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def call_ai_api(self, prompt: str, config: Dict[str, Any], system_prompt: str = "") -> Optional[str]:
        """统一API调用"""
        if not config.get('enabled'):
            return None

        try:
            if config.get('api_type') == 'official' and config.get('provider') == 'gemini':
                return self._call_gemini_official(prompt, config, system_prompt)
            else:
                return self._call_openai_compatible(prompt, config, system_prompt)
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict[str, Any], system_prompt: str) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai

            client = genai.Client(api_key=config['api_key'])

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = client.models.generate_content(
                model=config['model'],
                contents=full_prompt
            )

            return response.text

        except Exception as e:
            print(f"⚠️ Gemini调用失败: {e}")
            return None

    def _call_openai_compatible(self, prompt: str, config: Dict[str, Any], system_prompt: str) -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            from openai import OpenAI

            client_kwargs = {'api_key': config['api_key']}
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']

            client = OpenAI(**client_kwargs)

            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            request_params = {
                'model': config['model'],
                'messages': messages,
                'max_tokens': 4000,
                'temperature': 0.7
            }

            if 'extra_headers' in config:
                request_params['extra_headers'] = config['extra_headers']

            response = client.chat.completions.create(**request_params)
            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
        return {'enabled': False}

    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 配置保存失败: {e}")

# 全局实例
api_config = SimpleAPIConfig()

# 向后兼容
def call_ai_api(prompt: str, config: Dict[str, Any], system_prompt: str = "") -> Optional[str]:
    return api_config.call_ai_api(prompt, config, system_prompt)