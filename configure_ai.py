
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI配置辅助脚本 - 快速配置智能分析API
"""

import json
import os

def configure_ai():
    """配置AI API"""
    print("🤖 AI智能分析配置")
    print("=" * 40)
    print("AI分析可以提升片段识别准确性，但不是必需的")
    
    choice = input("\n是否启用AI增强分析？(y/n): ").lower().strip()
    
    if choice not in ['y', 'yes', '是']:
        # 禁用AI分析
        config = {'enabled': False}
        save_config(config)
        print("✅ 已禁用AI分析，将使用规则分析模式")
        return
    
    print("\n请选择AI服务提供商：")
    print("1. OpenAI (GPT)")
    print("2. 中转API (推荐)")
    print("3. 自定义API")
    
    provider_choice = input("\n请选择 (1-3): ").strip()
    
    if provider_choice == "1":
        configure_openai()
    elif provider_choice == "2":
        configure_proxy_api()
    elif provider_choice == "3":
        configure_custom_api()
    else:
        print("❌ 无效选择")

def configure_openai():
    """配置OpenAI官方API"""
    print("\n📝 配置OpenAI官方API")
    api_key = input("请输入OpenAI API密钥 (sk-开头): ").strip()
    
    if not api_key.startswith('sk-'):
        print("❌ API密钥格式错误")
        return
    
    config = {
        'enabled': True,
        'provider': 'openai',
        'api_key': api_key,
        'base_url': 'https://api.openai.com/v1',
        'model': 'gpt-3.5-turbo'
    }
    
    save_config(config)
    test_api_connection(config)

def configure_proxy_api():
    """配置中转API"""
    print("\n📝 配置中转API")
    print("常见中转API服务：")
    print("• https://api.chatanywhere.tech/v1")
    print("• https://api.chataiapi.com/v1")
    print("• https://api.aigc369.com/v1")
    
    base_url = input("\n请输入API地址: ").strip()
    if not base_url:
        base_url = "https://api.chatanywhere.tech/v1"
    
    api_key = input("请输入API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return
    
    print("\n选择模型：")
    print("1. gpt-3.5-turbo (推荐)")
    print("2. gpt-4")
    print("3. claude-3-sonnet")
    
    model_choice = input("请选择模型 (1-3): ").strip()
    
    models = {
        '1': 'gpt-3.5-turbo',
        '2': 'gpt-4',
        '3': 'claude-3-sonnet-20240229'
    }
    
    model = models.get(model_choice, 'gpt-3.5-turbo')
    
    config = {
        'enabled': True,
        'provider': 'proxy',
        'api_key': api_key,
        'base_url': base_url,
        'model': model
    }
    
    save_config(config)
    test_api_connection(config)

def configure_custom_api():
    """配置自定义API"""
    print("\n📝 配置自定义API")
    
    base_url = input("请输入API地址: ").strip()
    api_key = input("请输入API密钥: ").strip()
    model = input("请输入模型名称: ").strip()
    
    if not all([base_url, api_key, model]):
        print("❌ 所有字段都不能为空")
        return
    
    config = {
        'enabled': True,
        'provider': 'custom',
        'api_key': api_key,
        'base_url': base_url,
        'model': model
    }
    
    save_config(config)
    test_api_connection(config)

def save_config(config):
    """保存配置"""
    try:
        with open('.ai_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ 配置已保存到 .ai_config.json")
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")

def test_api_connection(config):
    """测试API连接"""
    if not config.get('enabled'):
        return
    
    print("\n🔍 测试API连接...")
    
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config['model'],
            'messages': [
                {'role': 'user', 'content': '你好，请回复"测试成功"'}
            ],
            'max_tokens': 10
        }
        
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API连接测试成功！")
        else:
            print(f"❌ API连接失败: {response.status_code} - {response.text[:100]}")
            
    except Exception as e:
        print(f"⚠ API测试出错: {e}")
        print("可能是网络问题，但配置已保存，系统仍可正常使用")

def main():
    print("🤖 智能电视剧剪辑系统 - AI配置")
    configure_ai()

if __name__ == "__main__":
    main()
