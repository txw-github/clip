#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完全智能化电视剧精彩片段分析剪辑系统 - 主控制程序
支持srt和videos目录结构，完全AI驱动的剧情分析
"""

import os
import sys
import json
from typing import List, Dict, Optional
from api_config_helper import config_helper

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")

    # 检查Python版本
    python_version = sys.version.split()[0]
    print(f"✓ Python版本: {python_version}")

    # 检查和创建目录结构
    directories = {
        'srt': '字幕文件目录',
        'videos': '视频文件目录',
        'clips': '输出视频目录'
    }

    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建{description}: {dir_name}/")
        else:
            print(f"✓ 找到{description}: {dir_name}/")

    # 检查字幕文件
    subtitle_files = []

    # 检查srt目录
    srt_files = [f for f in os.listdir('srt') if f.endswith(('.txt', '.srt'))]
    if srt_files:
        print(f"✓ srt目录中找到 {len(srt_files)} 个字幕文件")
        subtitle_files.extend(srt_files)

    # 检查根目录（兼容旧结构）
    root_srt_files = [f for f in os.listdir('.') if f.endswith(('.txt', '.srt')) and any(pattern in f.lower() for pattern in ['s01e', 'ep', 'e0', 'e1'])]
    if root_srt_files:
        print(f"✓ 根目录中找到 {len(root_srt_files)} 个字幕文件")
        subtitle_files.extend(root_srt_files)

    if not subtitle_files:
        print("⚠ 未找到字幕文件，请将字幕文件放入srt目录")
        return False

    # 检查视频文件
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
        if video_files:
            print(f"✓ videos目录中找到 {len(video_files)} 个视频文件")
        else:
            print("⚠ videos目录中没有视频文件")

    # 检查FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg已安装")
        else:
            print("⚠ 警告: 未检测到FFmpeg")
    except FileNotFoundError:
        print("⚠ 警告: 未检测到FFmpeg")
        print("请安装FFmpeg以使用视频剪辑功能")
        print("• 在Shell中运行: nix-env -iA nixpkgs.ffmpeg")
        if not video_files:
            print("⚠ 没有视频文件，只能进行字幕分析")

    return len(subtitle_files) > 0

def configure_ai_analysis():
    """配置AI增强分析"""
    print("\n🤖 配置完全智能化AI分析")
    print("=" * 50)

    # 显示推荐模型
    print("🎯 针对电视剧剪辑的推荐模型：")
    print("1. DeepSeek-R1 (推荐) - 推理能力极强，最适合剧情分析")
    print("2. Gemini-2.5-Pro - 上下文理解优秀，适合长片段分析")
    print("3. 通过中转API使用 - 配置简单，支持多模型")
    print()

    # 检查当前配置
    current_config = config_helper.load_config()
    if current_config.get('enabled'):
        print(f"📍 当前配置: {current_config.get('provider', 'unknown')} - {current_config.get('model', 'unknown')}")

        choice = input("是否重新配置? (y/N): ").lower()
        if choice != 'y':
            return current_config

    # 开始配置
    config = config_helper.interactive_setup()

    if config.get('enabled'):
        print("\n✅ 完全智能化AI分析已启用")
        print("🎯 AI将协助:")
        print("• 动态识别剧情类型（无限制）")
        print("• 分析完整上下文片段")
        print("• 判断最佳剪辑时长和内容")
        print("• 生成吸引人的短视频标题")
        print("• 智能调整剪辑时间点")
    else:
        print("\n📝 使用基础规则分析模式")
        print("🎯 基于关键词和规则评分")

    return config

def smart_analysis_only():
    """仅进行智能分析"""
    print("\n🧠 启动完全智能化剧情分析...")
    print("=" * 50)

    try:
        from smart_analyzer import analyze_all_episodes_smartly

        episodes_plans = analyze_all_episodes_smartly()

        if episodes_plans:
            print(f"\n✅ 智能分析完成！")
            print(f"📊 成功分析了 {len(episodes_plans)} 集")

            total_clips = sum(ep.get('total_clips', 0) for ep in episodes_plans)
            total_duration = sum(ep.get('total_duration', 0) for ep in episodes_plans)

            print(f"🎬 推荐短视频: {total_clips} 个")
            print(f"⏱️ 总时长: {total_duration/60:.1f} 分钟")
            print(f"📄 详细报告: smart_analysis_report.txt")

            return episodes_plans
        else:
            print("❌ 分析失败，未找到有效内容")
            return None

    except Exception as e:
        print(f"❌ 分析过程出错: {e}")
        return None

def complete_smart_workflow():
    """完整的智能化工作流程"""
    print("\n🎬 启动完整智能化剪辑工作流程...")
    print("=" * 50)

    # 检查视频文件
    if not os.path.exists('videos'):
        print("❌ videos目录不存在")
        print("请创建videos目录并放入视频文件")
        return False

    video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]

    if not video_files:
        print("❌ videos目录中没有视频文件")
        print("请将视频文件放入videos目录")
        return False

    print(f"✓ 找到 {len(video_files)} 个视频文件")

    try:
        from smart_video_clipper import process_all_episodes_smartly

        all_clips = process_all_episodes_smartly()

        if all_clips:
            print(f"\n🎉 完整智能化剪辑完成！")
            print(f"📊 总计创建: {len(all_clips)} 个短视频")
            print(f"📁 输出目录: clips/")
            print(f"🎬 每集结束后自动生成对应的短视频文件")
            print(f"💡 特色功能:")
            print(f"   • 每集多个精彩短视频")
            print(f"   • AI判断最佳剪辑内容")
            print(f"   • 自动添加智能标题")
            print(f"   • 完整上下文分析")
            print(f"   • 单集精彩集锦")
            print(f"   • 完整剧集合集")
            return True
        else:
            print("❌ 剪辑失败")
            return False

    except Exception as e:
        print(f"❌ 剪辑过程出错: {e}")
        return False

def show_system_status():
    """显示系统状态"""
    print("\n📊 系统状态检查")
    print("=" * 50)

    print("🔧 环境状态:")
    print(f"   • Python: {sys.version.split()[0]}")

    # 目录检查
    for dir_name in ['srt', 'videos', 'clips']:
        if os.path.exists(dir_name):
            files = os.listdir(dir_name)
            print(f"   • {dir_name}目录: ✅ ({len(files)} 个文件)")
        else:
            print(f"   • {dir_name}目录: ❌ 不存在")

    # 文件检查
    srt_files = []
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.endswith(('.txt', '.srt'))]
    print(f"   • 字幕文件: {len(srt_files)} 个")

    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    print(f"   • 视频文件: {len(video_files)} 个")

    # AI配置检查
    ai_config = config_helper.load_config()
    if ai_config.get('enabled'):
        print(f"   • AI分析: ✅ 已启用 ({ai_config.get('provider')}/{ai_config.get('model')})")
    else:
        print(f"   • AI分析: ❌ 未启用")

    # 依赖检查
    try:
        import requests
        print(f"   • requests: ✅ 已安装")
    except ImportError:
        print(f"   • requests: ❌ 未安装")

    # FFmpeg检查
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   • FFmpeg: ✅ 已安装")
        else:
            print(f"   • FFmpeg: ❌ 未检测到")
    except FileNotFoundError:
        print(f"   • FFmpeg: ❌ 未安装")

    print("\n🎯 功能状态:")
    print(f"   • 智能分析: {'✅ 可用' if len(srt_files) > 0 else '❌ 无字幕文件'}")
    print(f"   • 视频剪辑: {'✅ 可用' if len(video_files) > 0 else '❌ 无视频文件'}")
    print(f"   • AI增强: {'✅ 已启用' if ai_config.get('enabled') else '📝 基础模式'}")

def show_usage_guide():
    """显示使用说明"""
    print("\n📖 完全智能化剪辑系统使用说明")
    print("=" * 50)

    print("🎯 核心特点:")
    print("• 完全AI驱动，无任何硬编码限制")
    print("• 自动识别剧情类型和情节转折")
    print("• 每集生成多个精彩短视频")
    print("• 支持srt和videos目录结构")
    print("• AI判断最佳剪辑时长和内容")

    print("\n📁 目录结构:")
    print("srt/          - 字幕文件目录")
    print("videos/       - 视频文件目录")
    print("clips/        - 输出视频目录")

    print("\n🤖 AI模型推荐:")
    print("1. DeepSeek-R1 - 推理能力极强，最适合剧情分析")
    print("2. Gemini-2.5-Pro - 上下文理解优秀，适合长片段")
    print("3. 中转API服务 - 配置简单，支持多模型")

    print("\n📝 使用流程:")
    print("1. 将字幕文件放入srt目录")
    print("2. 将视频文件放入videos目录")
    print("3. 配置AI分析（可选但推荐）")
    print("4. 选择分析模式或完整剪辑")
    print("5. 等待处理完成，查看clips目录")

    print("\n🎬 输出内容:")
    print("• 每集多个精彩短视频（含旁白）")
    print("• 单集完整精彩集锦")
    print("• 完整剧集合集")
    print("• 智能分析报告")
    print("• 每个短视频的详细说明文件")

def main():
    """主函数"""
    print("🚀 启动完全智能化电视剧精彩片段分析剪辑系统...")

    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，无法继续")
        return

    # 显示主菜单
    while True:
        print("\n" + "=" * 70)
        print("🤖 完全智能化电视剧精彩片段分析剪辑系统")
        print("=" * 70)
        print("🎯 核心特点：")
        print("• 完全AI驱动，无硬编码限制")
        print("• 每集生成多个精彩短视频")
        print("• 支持srt和videos目录结构")
        print("• AI判断最佳剪辑内容和时长")
        print("• 自动生成专业旁白解释")
        print("• 智能字幕分段显示")
        print("-" * 70)
        print("请选择操作：")
        print("1. 🧠 仅进行智能分析 (生成剪辑方案)")
        print("2. 🎬 完整智能剪辑 (分析 + 视频生成)")
        print("3. 🤖 配置AI增强分析")
        print("4. 📊 查看系统状态")
        print("5. 📖 查看使用说明")
        print("0. ❌ 退出")
        print("=" * 70)

        choice = input("请输入选项 (0-5): ").strip()

        if choice == "0":
            print("👋 感谢使用完全智能化剪辑系统！")
            break
        elif choice == "1":
            smart_analysis_only()
        elif choice == "2":
            complete_smart_workflow()
        elif choice == "3":
            configure_ai_analysis()
        elif choice == "4":
            show_system_status()
        elif choice == "5":
            show_usage_guide()
        else:
            print("❌ 无效选项，请重试")

if __name__ == "__main__":
    main()