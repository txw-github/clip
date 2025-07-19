#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧智能剪辑系统 - 主程序
专注单集核心剧情，保持跨集连贯性
"""

import os
import sys

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")

    # 检查字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith('.txt') and any(pattern in file.lower() for pattern in ['e', 's01e', '第', '集']):
            subtitle_files.append(file)

    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请确保字幕文件在当前目录，命名包含集数信息 (如: S01E01.txt)")
        return False

    print(f"✅ 找到 {len(subtitle_files)} 个字幕文件")

    # 检查videos目录 (仅在需要剪辑时)
    videos_exist = os.path.exists('videos') and any(
        f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')) 
        for f in os.listdir('videos')
    )

    if videos_exist:
        video_count = len([f for f in os.listdir('videos') 
                          if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))])
        print(f"✅ 找到 {video_count} 个视频文件")
    else:
        print("⚠ videos目录不存在或无视频文件 (仅分析时可忽略)")

    return True

def main_menu():
    """主菜单"""
    print("\n" + "=" * 60)
    print("📺 电视剧智能剪辑系统")
    print("=" * 60)
    print("功能特性:")
    print("• 单集核心聚焦: 每集1个核心剧情点，2-3分钟时长")
    print("• 主线剧情优先: 四二八案、628旧案、听证会等关键线索")
    print("• 跨集连贯性: 保持故事线逻辑一致和明确衔接")
    print("• 自动错别字修正: 防衛→防卫, 正當→正当等")
    print("• 专业字幕: 主题+剧情意义+内容亮点展示")
    print("=" * 60)

    print("\n请选择操作:")
    print("1. 📝 仅字幕分析 (生成剪辑方案)")
    print("2. 🎬 完整剪辑流程 (分析+视频剪辑)")
    print("3. 📊 查看上次分析结果")
    print("4. ❌ 退出")

    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("❌ 请输入有效选项 (1-4)")
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
            return '4'

def subtitle_analysis_only():
    """仅进行字幕分析"""
    print("\n🧠 开始智能字幕分析...")
    print("-" * 40)

    try:
        from smart_analyzer import analyze_all_episodes_smartly

        plans = analyze_all_episodes_smartly()

        if plans:
            print(f"\n✅ 分析完成！")
            print(f"📊 成功分析了 {len(plans)} 集")
            print(f"📄 详细方案已保存到: smart_analysis_report.txt")

            # 显示简要统计
            total_duration = sum(plan['segment']['duration'] for plan in plans)
            print(f"⏱️ 总剪辑时长: {total_duration:.1f}秒 ({total_duration/60:.1f}分钟)")
            print(f"📺 平均每集: {total_duration/len(plans):.1f}秒")

            return True
        else:
            print("❌ 分析失败，请检查字幕文件")
            return False

    except Exception as e:
        print(f"❌ 分析过程出错: {e}")
        return False

def full_clip_process():
    """完整剪辑流程"""
    print("\n🚀 开始完整剪辑流程...")
    print("-" * 40)

    # 检查videos目录
    if not os.path.exists('videos'):
        print("❌ videos目录不存在")
        print("请创建videos目录并放入对应的视频文件")
        return False

    video_files = [f for f in os.listdir('videos') 
                   if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]

    if not video_files:
        print("❌ videos目录中没有视频文件")
        print("请在videos目录中放入视频文件")
        return False

    try:
        from smart_video_clipper import process_all_episodes_smartly

        created_clips = process_all_episodes_smartly()

        if created_clips:
            print(f"\n🎉 剪辑完成！")
            print(f"✅ 成功创建 {len(created_clips)} 个短视频")
            print(f"📁 输出目录: clips/")
            print(f"📄 每个视频都有对应的说明文件")

            return True
        else:
            print("❌ 剪辑失败")
            return False

    except Exception as e:
        print(f"❌ 剪辑过程出错: {e}")
        return False

def view_last_results():
    """查看上次分析结果"""
    if os.path.exists('smart_analysis_report.txt'):
        print("\n📄 上次分析结果:")
        print("-" * 40)

        try:
            with open('smart_analysis_report.txt', 'r', encoding='utf-8') as f:
                content = f.read()

            # 显示前几行摘要
            lines = content.split('\n')
            summary_lines = []

            for line in lines[:30]:  # 显示前30行
                if line.strip():
                    summary_lines.append(line)
                if len(summary_lines) >= 15:  # 最多显示15行有效内容
                    break

            print('\n'.join(summary_lines))

            if len(lines) > 30:
                print("\n... (查看完整内容请打开 smart_analysis_report.txt)")

            return True

        except Exception as e:
            print(f"❌ 读取报告文件失败: {e}")
            return False
    else:
        print("❌ 未找到分析报告文件")
        print("请先执行字幕分析或完整剪辑流程")
        return False

def main():
    """主函数"""
    print("🚀 电视剧智能剪辑系统启动")

    # 检查环境
    if not check_environment():
        input("\n按Enter键退出...")
        return

    while True:
        choice = main_menu()

        if choice == '1':
            subtitle_analysis_only()

        elif choice == '2':
            full_clip_process()

        elif choice == '3':
            view_last_results()

        elif choice == '4':
            print("\n👋 感谢使用！")
            break

        # 询问是否继续
        if choice in ['1', '2', '3']:
            print("\n" + "-" * 40)
            continue_choice = input("是否继续操作？(y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '是']:
                print("\n👋 感谢使用！")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        input("按Enter键退出...")