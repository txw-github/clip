
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
剧情点聚焦剪辑系统启动脚本
"""

import os

def setup_directories():
    """设置目录结构"""
    directories = {
        'srt': 'SRT字幕文件目录',
        'videos': '视频文件目录',
        'plot_clips': '剧情点短视频输出目录',
        'plot_reports': '剧情点分析报告目录'
    }
    
    print("📁 设置剧情点聚焦剪辑目录结构...")
    print("=" * 60)
    
    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/ - {description}")
        else:
            print(f"✓ 目录已存在: {dir_name}/ - {description}")
    
    print()
    
    # 检查文件状态
    srt_files = []
    video_files = []
    
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.lower().endswith('.srt')]
    
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    print("📊 当前状态:")
    print(f"• SRT字幕文件: {len(srt_files)} 个")
    print(f"• 视频文件: {len(video_files)} 个")
    
    if srt_files:
        print("📄 字幕文件列表:")
        for i, file in enumerate(srt_files[:5], 1):
            print(f"  {i}. {file}")
        if len(srt_files) > 5:
            print(f"  ... 等共 {len(srt_files)} 个文件")
    
    if video_files:
        print("🎬 视频文件列表:")
        for i, file in enumerate(video_files[:5], 1):
            print(f"  {i}. {file}")
        if len(video_files) > 5:
            print(f"  ... 等共 {len(video_files)} 个文件")
    
    if not srt_files:
        print("\n⚠️ 请将SRT字幕文件放入 srt/ 目录")
        return False
    
    if not video_files:
        print("\n⚠️ 请将视频文件放入 videos/ 目录")
        return False
    
    return True

def main():
    """主启动函数"""
    print("🎭 剧情点聚焦剪辑系统")
    print("=" * 60)
    print("🎯 系统特点:")
    print("• 按剧情点分析：关键冲突、人物转折、线索揭露")
    print("• 每个剧情点2-3分钟，非连续但剪辑后连贯")
    print("• 智能过渡点识别，确保自然衔接")
    print("• 多剧情点合并成完整短视频")
    print("=" * 60)
    
    # 设置目录
    if not setup_directories():
        print("\n请按照说明放入文件后重新运行")
        return
    
    print("\n🎬 启动剧情点聚焦剪辑分析...")
    
    try:
        from plot_point_clipper import main as run_clipper
        run_clipper()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保 plot_point_clipper.py 文件存在")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()
