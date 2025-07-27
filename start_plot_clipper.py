#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整智能电视剧剪辑系统启动脚本
"""

import os
import sys

def setup_directories():
    """设置必要目录结构"""
    directories = ['srt', 'videos', 'clips', 'cache', 'reports']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")

def check_files():
    """检查文件准备情况"""
    print("\n📋 文件检查:")

    # 检查字幕文件
    srt_files = [f for f in os.listdir('srt') if f.endswith(('.srt', '.txt'))] if os.path.exists('srt') else []
    if srt_files:
        print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    else:
        print("⚠️ srt/ 目录中未找到字幕文件")
        print("   请将字幕文件放入 srt/ 目录")

    # 检查视频文件
    video_files = [f for f in os.listdir('videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))] if os.path.exists('videos') else []
    if video_files:
        print(f"✅ 找到 {len(video_files)} 个视频文件")
    else:
        print("⚠️ videos/ 目录中未找到视频文件")
        print("   请将视频文件放入 videos/ 目录")

    # 检查FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg 已安装")
        else:
            print("❌ FFmpeg 未正确安装")
    except:
        print("❌ FFmpeg 未安装")
        print("   请安装FFmpeg以支持视频剪辑功能")

    return len(srt_files) > 0 and len(video_files) > 0

def main():
    """主函数"""
    print("🚀 完整智能电视剧剪辑系统启动")
    print("=" * 60)

    # 设置目录
    setup_directories()

    # 检查文件
    if not check_files():
        print("\n❌ 请先准备好字幕文件和视频文件")
        print("\n📋 文件准备指南:")
        print("1. 将字幕文件(.srt/.txt)放入 srt/ 目录")
        print("2. 将视频文件(.mp4/.mkv等)放入 videos/ 目录")
        print("3. 确保文件名对应（如 E01.srt 对应 E01.mp4）")
        return

    print("\n🎬 启动完整剪辑系统...")

    # 导入并运行主程序
    try:
        from clean_main import main as clipper_main
        clipper_main()
    except ImportError:
        print("❌ 找不到 clean_main.py")
        print("请确保 clean_main.py 文件存在")
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    main()