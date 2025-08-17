
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API配置助手模块 - 统一的AI配置管理
支持官方API和中转API，简化用户配置流程
"""

import json
import os
import requests
from typing import Dict, Optional

class ConfigHelper:
    """配置助手类"""

    def interactive_setup(self) -> Dict:
        """交互式AI配置 - 简化版本"""
        print("\n🤖 AI接口配置")
        print("=" * 40)
        print("选择API类型:")
        print("1. 🌐 中转API (推荐) - ChatAI, OpenRouter等")
        print("2. 🔒 官方API - OpenAI, Google Gemini等")
        print("3. ⏭️ 跳过配置")

        try:
            choice = input("请选择 (1-3): ").strip()
            
            if choice == '1':
                return self._setup_proxy_api()
            elif choice == '2':
                return self._setup_official_api()
            else:
                return {'enabled': False}
        except KeyboardInterrupt:
            return {'enabled': False}

    def _setup_proxy_api(self) -> Dict:
        """配置中转API - 简化流程"""
        print("\n🌐 中转API配置")
        
        # 预设选项
        presets = {
            "1": {
                "name": "ChatAI API (推荐)",
                "base_url": "https://www.chataiapi.com/v1",
                "models": ["deepseek-r1", "claude-3-5-sonnet-20240620", "gpt-4o", "gemini-2.5-flash"]
            },
            "2": {
                "name": "OpenRouter",
                "base_url": "https://openrouter.ai/api/v1", 
                "models": ["deepseek/deepseek-r1", "anthropic/claude-3.5-sonnet", "google/gemini-2.0-flash-exp"]
            },
            "3": {
                "name": "自定义中转",
                "base_url": "",
                "models": []
            }
        }

        print("选择中转服务:")
        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")

        choice = input("请选择 (1-3): ").strip()
        
        if choice not in presets:
            return {'enabled': False}

        selected = presets[choice]
        
        if choice == "3":
            # 自定义配置
            base_url = input("API地址 (如: https://api.example.com/v1): ").strip()
            if not base_url:
                return {'enabled': False}
        else:
            base_url = selected["base_url"]

        api_key = input("API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}

        # 选择模型
        if choice == "3":
            model = input("模型名称: ").strip()
            if not model:
                return {'enabled': False}
        else:
            print(f"\n推荐模型:")
            for i, m in enumerate(selected["models"], 1):
                print(f"{i}. {m}")
            
            model_choice = input(f"选择模型 (1-{len(selected['models'])}): ").strip()
            try:
                model = selected["models"][int(model_choice) - 1]
            except:
                model = selected["models"][0]

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': selected['name'],
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_proxy_api(config):
            print("✅ 连接成功")
            self._save_config(config)
            return config
        else:
            print("❌ 连接失败")
            return {'enabled': False}

    def _setup_official_api(self) -> Dict:
        """配置官方API - 简化流程"""
        print("\n🔒 官方API配置")
        
        apis = {
            "1": {
                "name": "Google Gemini",
                "provider": "gemini",
                "models": ["gemini-2.5-flash", "gemini-2.5-pro"]
            },
            "2": {
                "name": "OpenAI",
                "provider": "openai",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
            },
            "3": {
                "name": "DeepSeek",
                "provider": "deepseek",
                "models": ["deepseek-r1", "deepseek-v3"]
            }
        }

        print("选择官方API:")
        for key, api in apis.items():
            print(f"{key}. {api['name']}")

        choice = input("请选择 (1-3): ").strip()
        
        if choice not in apis:
            return {'enabled': False}

        selected = apis[choice]
        api_key = input("API密钥: ").strip()

        if not api_key:
            return {'enabled': False}

        # 选择模型
        print(f"\n可用模型:")
        for i, model in enumerate(selected["models"], 1):
            print(f"{i}. {model}")
        
        model_choice = input(f"选择模型 (1-{len(selected['models'])}): ").strip()
        try:
            model = selected["models"][int(model_choice) - 1]
        except:
            model = selected["models"][0]

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': selected['provider'],
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_official_api(config):
            print("✅ 连接成功")
            self._save_config(config)
            return config
        else:
            print("❌ 连接失败")
            return {'enabled': False}

    def _test_proxy_api(self, config: Dict) -> bool:
        """测试中转API连接"""
        try:
            url = f"{config['base_url']}/chat/completions"
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            payload = {
                "model": config['model'],
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return bool(result.get('choices', [{}])[0].get('message', {}).get('content'))
            else:
                print(f"API错误: {response.status_code}")
                return False

        except Exception as e:
            print(f"连接错误: {e}")
            return False

    def _test_official_api(self, config: Dict) -> bool:
        """测试官方API连接"""
        provider = config.get('provider')
        
        try:
            if provider == 'gemini':
                return self._test_gemini_official(config)
            elif provider == 'openai':
                return self._test_openai_official(config)
            elif provider == 'deepseek':
                return self._test_deepseek_official(config)
            else:
                return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _test_gemini_official(self, config: Dict) -> bool:
        """测试Gemini官方API"""
        try:
            from google import genai
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'], 
                contents="测试"
            )
            return bool(response.text)
        except ImportError:
            print("需要安装: pip install google-genai")
            return False
        except Exception:
            return False

    def _test_openai_official(self, config: Dict) -> bool:
        """测试OpenAI官方API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config['api_key'])
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试'}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except ImportError:
            print("需要安装: pip install openai")
            return False
        except Exception:
            return False

    def _test_deepseek_official(self, config: Dict) -> bool:
        """测试DeepSeek官方API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url='https://api.deepseek.com/v1'
            )
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试'}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except ImportError:
            print("需要安装: pip install openai")
            return False
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
            
            if api_type == 'proxy':
                return self._call_proxy_api(prompt, config, system_prompt)
            else:
                return self._call_official_api(prompt, config, system_prompt)

        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def _call_proxy_api(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用中转API - 使用您提供的代码格式"""
        try:
            # 使用您提供的中转API调用方式
            url = f"{config['base_url']}/chat/completions"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": config['model'],
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('choices', [{}])[0].get('message', {}).get('content')
            else:
                print(f"API调用失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"中转API调用失败: {e}")
            return None

    def _call_official_api(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用官方API"""
        provider = config.get('provider')
        
        if provider == 'gemini':
            return self._call_gemini_official(prompt, config, system_prompt)
        elif provider == 'openai':
            return self._call_openai_official(prompt, config, system_prompt)
        elif provider == 'deepseek':
            return self._call_deepseek_official(prompt, config, system_prompt)
        else:
            return None

    def _call_gemini_official(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用Gemini官方API - 使用您提供的代码格式"""
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
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_openai_official(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用OpenAI官方API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config['api_key'])
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return None

    def _call_deepseek_official(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用DeepSeek官方API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url='https://api.deepseek.com/v1'
            )
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return None

# 全局实例
config_helper = ConfigHelper()
