
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速API配置脚本 - 支持多种中转服务商
"""

from api_config_helper import config_helper

def quick_setup_chataiapi():
    """快速配置ChatAI API"""
    print("🚀 快速配置 ChatAI API")
    print("=" * 40)
    
    api_key = input("请输入ChatAI API密钥: ").strip()
    if not api_key:
        return False
    
    config = {
        'enabled': True,
        'provider': 'chataiapi',
        'api_key': api_key,
        'model': 'deepseek-r1',
        'base_url': 'https://www.chataiapi.com/v1',
        'api_type': 'openai_compatible',
        'extra_headers': {}
    }
    
    if config_helper._test_api_connection(config):
        config_helper._save_config(config)
        print("✅ ChatAI API配置成功！")
        return True
    else:
        print("❌ 配置失败")
        return False

def quick_setup_suanli():
    """快速配置算力云API"""
    print("🚀 快速配置算力云API")
    print("=" * 40)
    
    api_key = input("请输入算力云API密钥: ").strip()
    if not api_key:
        return False
    
    config = {
        'enabled': True,
        'provider': 'suanli',
        'api_key': api_key,
        'model': 'deepseek-ai/DeepSeek-R1',
        'base_url': 'https://api.suanli.cn/v1',
        'api_type': 'openai_compatible',
        'extra_headers': {}
    }
    
    if config_helper._test_api_connection(config):
        config_helper._save_config(config)
        print("✅ 算力云API配置成功！")
        return True
    else:
        print("❌ 配置失败")
        return False

def quick_setup_custom():
    """快速配置自定义API"""
    print("🚀 快速配置自定义API")
    print("=" * 40)
    print("💡 请按照以下格式配置:")
    print("示例1 (ChatAI型): https://www.chataiapi.com/v1")
    print("示例2 (算力云型): https://api.suanli.cn/v1")
    print("示例3 (OpenRouter型): https://openrouter.ai/api/v1")
    print()
    
    base_url = input("API地址: ").strip()
    api_key = input("API密钥: ").strip()
    model = input("模型名称: ").strip()
    
    if not all([base_url, api_key, model]):
        print("❌ 所有字段都必须填写")
        return False
    
    # 询问是否需要特殊头部
    extra_headers = {}
    if 'openrouter' in base_url.lower():
        extra_headers = {
            'HTTP-Referer': 'https://replit.com',
            'X-Title': 'TV-Clipper-AI'
        }
        print("✓ 自动添加OpenRouter所需头部")
    
    config = {
        'enabled': True,
        'provider': 'custom',
        'api_key': api_key,
        'model': model,
        'base_url': base_url,
        'api_type': 'openai_compatible',
        'extra_headers': extra_headers
    }
    
    if config_helper._test_api_connection(config):
        config_helper._save_config(config)
        print("✅ 自定义API配置成功！")
        return True
    else:
        print("❌ 配置失败")
        return False

def main():
    """主配置菜单"""
    print("🤖 快速API配置助手")
    print("=" * 50)
    print("支持多种中转服务商，一键配置")
    print()
    
    while True:
        print("选择配置方式:")
        print("1. ChatAI API (推荐)")
        print("2. 算力云 API")
        print("3. 自定义API (支持任何OpenAI兼容服务)")
        print("4. 完整交互式配置")
        print("0. 退出")
        
        choice = input("\n请选择 (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            if quick_setup_chataiapi():
                print("\n🎉 配置完成！现在可以运行 python main.py")
                break
        elif choice == "2":
            if quick_setup_suanli():
                print("\n🎉 配置完成！现在可以运行 python main.py")
                break
        elif choice == "3":
            if quick_setup_custom():
                print("\n🎉 配置完成！现在可以运行 python main.py")
                break
        elif choice == "4":
            config = config_helper.interactive_setup()
            if config.get('enabled'):
                print("\n🎉 配置完成！现在可以运行 python main.py")
                break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
