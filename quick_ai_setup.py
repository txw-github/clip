
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速AI配置脚本 - 使用您的中转API
"""

import json
import os
from api_config_helper import config_helper

def quick_setup_chatai_api():
    """快速配置ChatAI API"""
    print("🚀 快速配置您的中转API服务")
    print("=" * 50)
    
    # 您的API信息
    default_config = {
        'enabled': True,
        'provider': 'chataiapi',
        'url': 'https://www.chataiapi.com/v1/chat/completions',
        'models': [
            'claude-3-5-sonnet-20240620',
            'deepseek-r1', 
            'gpt-4',
            'gpt-3.5-turbo'
        ]
    }
    
    print("🔧 请输入您的API配置:")
    print(f"服务商: {default_config['provider']}")
    print(f"API地址: {default_config['url']}")
    
    # 获取API密钥
    api_key = input("请输入您的API密钥 (sk-xxxx): ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 选择模型
    print("\n可用模型:")
    for i, model in enumerate(default_config['models'], 1):
        print(f"{i}. {model}")
    
    while True:
        try:
            choice = input(f"选择模型 (1-{len(default_config['models'])}, 回车使用claude-3-5-sonnet): ").strip()
            if not choice:
                selected_model = 'claude-3-5-sonnet-20240620'
                break
            
            choice = int(choice)
            if 1 <= choice <= len(default_config['models']):
                selected_model = default_config['models'][choice - 1]
                break
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")
    
    # 构建最终配置
    config = {
        'enabled': True,
        'provider': 'chataiapi',
        'api_key': api_key,
        'model': selected_model,
        'url': default_config['url']
    }
    
    # 测试连接
    print(f"\n🔍 测试API连接...")
    print(f"模型: {selected_model}")
    print(f"地址: {default_config['url']}")
    
    if test_api_connection(config):
        print("✅ API连接成功！")
        
        # 保存配置
        save_config(config)
        print("✅ 配置已保存")
        
        return True
    else:
        print("❌ API连接失败，请检查密钥和网络")
        return False

def test_api_connection(config):
    """测试API连接"""
    try:
        import requests
        
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "user",
                    "content": "hello"
                }
            ],
            "max_tokens": 10
        }
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {config["api_key"]}',
            'User-Agent': 'Replit-TV-Clipper/1.0.0',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            config['url'],
            headers=headers,
            json=payload,
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"连接测试错误: {e}")
        return False

def save_config(config):
    """保存配置"""
    try:
        with open('.ai_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"保存配置失败: {e}")

def show_usage_guide():
    """显示使用说明"""
    print("\n📖 使用说明")
    print("=" * 50)
    print("配置完成后，您可以:")
    print("1. 运行 python main.py")
    print("2. 选择 '1. 智能字幕分析' 或 '2. 完整智能剪辑'")
    print("3. 系统会自动使用AI增强分析")
    print("\n🎯 AI增强功能:")
    print("• 深度理解对话内容")
    print("• 识别情感强度和转折点")
    print("• 评估剧情重要性")
    print("• 提供详细分析原因")
    print("\n📊 评分方式:")
    print("• 规则评分权重: 60%")
    print("• AI评分权重: 40%")
    print("• 综合评分更准确")

if __name__ == "__main__":
    print("🤖 智能剪辑系统 - AI配置助手")
    
    if quick_setup_chatai_api():
        show_usage_guide()
        
        print("\n🚀 配置完成！现在可以运行:")
        print("python main.py")
    else:
        print("\n❌ 配置失败，请检查后重试")
