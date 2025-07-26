#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API配置助手模块 - 统一的AI配置管理
"""

import json
import os
from typing import Dict, Optional

class ConfigHelper:
    """配置助手类"""

    def interactive_setup(self) -> Dict:
        """交互式AI配置"""
        print("\n🤖 AI接口配置向导")
        print("=" * 40)

        print("选择AI服务提供商:")
        print("1. 🌐 代理API (推荐 - ChatAI, OpenRouter等)")
        print("2. 🔒 官方API (Google Gemini)")
        print("3. 🚫 跳过配置")

        try:
            choice = input("请选择 (1-3): ").strip()

            if choice == '1':
                return self._setup_proxy_api()
            elif choice == '2':
                return self._setup_official_api()
            else:
                print("⚠️ 跳过AI配置，将使用基础分析")
                return {'enabled': False}

        except KeyboardInterrupt:
            print("\n用户取消配置")
            return {'enabled': False}

    def _setup_proxy_api(self) -> Dict:
        """配置代理API"""
        print("\n🌐 代理API配置")
        print("推荐服务商: ChatAI, OpenRouter, DeepSeek等")

        try:
            base_url = input("API地址 (如: https://api.chatai.com/v1): ").strip()
            api_key = input("API密钥: ").strip()
            model = input("模型名称 (如: gpt-4, deepseek-r1): ").strip()

            if not all([base_url, api_key, model]):
                print("❌ 配置信息不完整")
                return {'enabled': False}

            config = {
                'enabled': True,
                'api_type': 'proxy',
                'provider': 'proxy',
                'base_url': base_url,
                'api_key': api_key,
                'model': model
            }

            # 测试连接
            print("🔍 测试连接...")
            if self._test_openai_compatible(config):
                print("✅ 连接测试成功")
                self._save_config(config)
                return config
            else:
                print("❌ 连接测试失败")
                return {'enabled': False}

        except Exception as e:
            print(f"❌ 配置失败: {e}")
            return {'enabled': False}

    def _setup_official_api(self) -> Dict:
        """配置官方API"""
        print("\n🔒 官方API配置")

        try:
            provider = input("服务商 (gemini): ").strip().lower() or 'gemini'
            api_key = input("API密钥: ").strip()

            if not api_key:
                print("❌ API密钥不能为空")
                return {'enabled': False}

            config = {
                'enabled': True,
                'api_type': 'official',
                'provider': provider,
                'api_key': api_key,
                'model': 'gemini-2.5-flash' if provider == 'gemini' else 'gpt-4'
            }

            # 测试连接
            print("🔍 测试连接...")
            if provider == 'gemini' and self._test_gemini_official(config):
                print("✅ 连接测试成功")
                self._save_config(config)
                return config
            else:
                print("❌ 连接测试失败")
                return {'enabled': False}

        except Exception as e:
            print(f"❌ 配置失败: {e}")
            return {'enabled': False}

    def _test_openai_compatible(self, config: Dict) -> bool:
        """测试OpenAI兼容API"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )

            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试连接'}],
                max_tokens=10
            )

            return bool(response.choices[0].message.content)

        except Exception:
            return False

    def _test_gemini_official(self, config: Dict) -> bool:
        """测试Gemini官方API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=config['api_key'])
            model = genai.GenerativeModel(config['model'])
            response = model.generate_content("测试")

            return bool(response.text)

        except Exception:
            return False

    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def call_ai_api(self, prompt: str, config: Dict, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用"""
        if not config.get('enabled'):
            return None

        try:
            api_type = config.get('api_type', 'proxy')

            if api_type == 'official' and config.get('provider') == 'gemini':
                return self._call_gemini_official(prompt, config, system_prompt)
            else:
                return self._call_openai_compatible(prompt, config, system_prompt)

        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=config['api_key'])
            model = genai.GenerativeModel(config['model'])

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(full_prompt)

            return response.text

        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_openai_compatible(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=config['api_key'],
                base_url=config.get('base_url', 'https://api.openai.com/v1')
            )

            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            response = client.chat.completions.create(
                model=config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"API调用失败: {e}")
            return None

# 全局实例
config_helper = ConfigHelper()