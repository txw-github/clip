#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能电视剧剪辑系统 - 主启动脚本
"""

import os
from intelligent_tv_clipper import IntelligentTVClipper
from ai_config_helper import configure_ai, load_config

def check_directories():
    """检查目录结构"""
    required_dirs = ['srt', 'videos', 'clips', 'cache']

    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/")

def check_files():
    """检查文件状态"""
    srt_count = len([f for f in os.listdir('srt') if f.endswith(('.srt', '.txt'))]) if os.path.exists('srt') else 0
    video_count = len([f for f in os.listdir('videos') if f.endswith(('.mp4', '.mkv', '.avi'))]) if os.path.exists('videos') else 0

    print(f"📝 字幕文件: {srt_count} 个")
    print(f"🎬 视频文件: {video_count} 个")

    if srt_count == 0:
        print("⚠️ 请将字幕文件放入 srt/ 目录")
        return False

    if video_count == 0:
        print("⚠️ 请将视频文件放入 videos/ 目录")
        return False

    return True

def main():
    """主函数"""
    print("🎬 智能电视剧剪辑系统 v3.0")
    print("=" * 60)

    # 1. 检查目录
    check_directories()

    # 2. 检查AI配置
    config = load_config()
    if not config.get('enabled', False):
        print("🤖 需要配置AI接口")
        if input("是否现在配置? (y/n): ").lower() == 'y':
            configure_ai()

    # 3. 检查文件
    if not check_files():
        print("\n📋 使用说明:")
        print("1. 将字幕文件 (*.srt, *.txt) 放入 srt/ 目录")
        print("2. 将对应视频文件放入 videos/ 目录")
        print("3. 重新运行程序")
        return

    # 4. 开始剪辑
    print("\n🚀 开始智能剪辑...")
    clipper = IntelligentTVClipper()
    clipper.process_all_episodes()

if __name__ == "__main__":
    main()