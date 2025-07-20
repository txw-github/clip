#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧智能剪辑系统 - 主程序
集成了智能API配置、剧情分析、视频剪辑等功能
"""

import os
import json
import glob
from typing import Dict, Any, List, Optional
#from api_config_helper import config_helper

class TVClipperMain:
    """电视剧剪辑系统主程序"""

    def __init__(self):
        self.ensure_directories()
        self.ai_config = None

    def ensure_directories(self):
        """确保必要目录存在"""
        directories = ['srt', 'videos', 'clips', 'analysis_cache']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def run(self):
        """主运行流程"""
        print("🎬 电视剧智能剪辑系统")
        print("=" * 60)
        print("基于AI的智能剧情分析和精彩片段剪辑")
        print()

        # 1. 检查并配置AI
        self.setup_ai()

        # 2. 选择操作模式
        while True:
            print("\n📋 选择操作:")
            print("1. 🔍 分析字幕文件")
            print("2. ✂️  开始剪辑视频")
            print("3. ⚙️  重新配置AI")
            print("4. 📊 查看分析报告")
            print("0. 退出")

            choice = input("\n请选择 (0-4): ").strip()

            if choice == "0":
                print("👋 感谢使用！")
                break
            elif choice == "1":
                self.analyze_subtitles()
            elif choice == "2":
                self.clip_videos()
            elif choice == "3":
                self.setup_ai(force_reconfig=True)
            elif choice == "4":
                self.show_analysis_reports()
            else:
                print("❌ 无效选择，请重试")

    def setup_ai(self, force_reconfig: bool = False):
        """设置AI配置"""
        if not force_reconfig:
            # 尝试加载现有配置
            self.ai_config = config_helper.load_config()

            if self.ai_config.get('enabled'):
                print(f"✅ AI配置已加载")
                print(f"   服务商: {self.ai_config.get('provider_name', '未知')}")
                print(f"   模型: {self.ai_config.get('model', '未知')}")
                return

        print("\n🤖 AI配置")
        print("-" * 30)
        print("AI分析可以大幅提升剧情识别准确性")

        use_ai = input("是否启用AI分析？(y/n): ").lower().strip()

        if use_ai != 'y':
            self.ai_config = {'enabled': False}
            print("✅ 已禁用AI，将使用基础规则分析")
            return

        # 启动智能配置向导
        self.ai_config = config_helper.interactive_setup()

        if not self.ai_config.get('enabled'):
            print("⚠️ AI配置失败，将使用基础规则分析")

    def analyze_subtitles(self):
        """分析字幕文件"""
        # 查找字幕文件
        srt_files = glob.glob("srt/*.srt")

        if not srt_files:
            print("❌ 未找到字幕文件")
            print("💡 请将字幕文件(.srt)放在 srt/ 目录下")
            return

        print(f"\n📄 找到 {len(srt_files)} 个字幕文件:")
        for i, file_path in enumerate(srt_files, 1):
            filename = os.path.basename(file_path)
            print(f"{i}. {filename}")

        print(f"{len(srt_files) + 1}. 分析所有文件")

        while True:
            try:
                choice = input(f"\n请选择要分析的文件 (1-{len(srt_files) + 1}): ").strip()
                choice = int(choice)

                if 1 <= choice <= len(srt_files):
                    # 分析单个文件
                    self._analyze_single_file(srt_files[choice - 1])
                    break
                elif choice == len(srt_files) + 1:
                    # 分析所有文件
                    self._analyze_all_files(srt_files)
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")

    def _analyze_single_file(self, file_path: str):
        """分析单个字幕文件"""
        #from subtitle_analyzer import SubtitleAnalyzer

        print(f"\n🔍 分析文件: {os.path.basename(file_path)}")

        analyzer = SubtitleAnalyzer(self.ai_config)
        result = analyzer.analyze_episode(file_path)

        if result and 'clips' in result:
            print(f"✅ 分析完成，识别到 {len(result['clips'])} 个精彩片段")
            self._show_analysis_summary(result)
        else:
            print("❌ 分析失败")

    def _analyze_all_files(self, srt_files: List[str]):
        """分析所有字幕文件"""
        #from subtitle_analyzer import SubtitleAnalyzer

        print(f"\n🔍 开始批量分析 {len(srt_files)} 个文件...")

        analyzer = SubtitleAnalyzer(self.ai_config)
        all_results = []

        for i, file_path in enumerate(srt_files, 1):
            filename = os.path.basename(file_path)
            print(f"\n[{i}/{len(srt_files)}] 分析: {filename}")

            result = analyzer.analyze_episode(file_path)

            if result:
                all_results.append(result)
                print(f"✅ 完成，识别到 {len(result.get('clips', []))} 个片段")
            else:
                print("❌ 分析失败")

        print(f"\n📊 批量分析完成:")
        print(f"   成功分析: {len(all_results)} 个文件")
        total_clips = sum(len(r.get('clips', [])) for r in all_results)
        print(f"   总计识别: {total_clips} 个精彩片段")

    def _show_analysis_summary(self, result: Dict[str, Any]):
        """显示分析摘要"""
        clips = result.get('clips', [])
        if not clips:
            return

        print("\n📋 精彩片段摘要:")
        for i, clip in enumerate(clips[:5], 1):  # 只显示前5个
            print(f"{i}. {clip['start_time']} - {clip['end_time']}")
            print(f"   主题: {clip.get('theme', '未知')}")
            print(f"   评分: {clip.get('score', 0):.1f}")
            if clip.get('description'):
                print(f"   描述: {clip['description'][:50]}...")

        if len(clips) > 5:
            print(f"... 还有 {len(clips) - 5} 个片段")

    def clip_videos(self):
        """剪辑视频"""
        # 检查是否有分析结果
        cache_files = glob.glob("analysis_cache/*.json")

        if not cache_files:
            print("❌ 未找到分析结果")
            print("💡 请先分析字幕文件")
            return

        # 检查视频文件
        video_files = glob.glob("videos/*.*")
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
        video_files = [f for f in video_files if any(f.lower().endswith(ext) for ext in video_extensions)]

        if not video_files:
            print("❌ 未找到视频文件")
            print("💡 请将视频文件放在 videos/ 目录下")
            return

        print(f"\n📹 找到 {len(video_files)} 个视频文件")
        print(f"📄 找到 {len(cache_files)} 个分析结果")

        # 开始剪辑流程
        #from video_clipper import VideoClipper

        clipper = VideoClipper()

        for cache_file in cache_files:
            episode_name = os.path.splitext(os.path.basename(cache_file))[0]

            # 查找对应的视频文件
            matching_video = self._find_matching_video(episode_name, video_files)

            if matching_video:
                print(f"\n✂️ 剪辑 {episode_name}")
                clipper.clip_episode(cache_file, matching_video)
            else:
                print(f"⚠️ 未找到 {episode_name} 对应的视频文件")

    def _find_matching_video(self, episode_name: str, video_files: List[str]) -> Optional[str]:
        """查找匹配的视频文件"""
        episode_name_clean = episode_name.lower()

        for video_file in video_files:
            video_name = os.path.splitext(os.path.basename(video_file))[0].lower()

            # 简单的名称匹配
            if episode_name_clean in video_name or video_name in episode_name_clean:
                return video_file

        return None

    def show_analysis_reports(self):
        """显示分析报告"""
        cache_files = glob.glob("analysis_cache/*.json")

        if not cache_files:
            print("❌ 未找到分析报告")
            return

        print(f"\n📊 分析报告总览 ({len(cache_files)} 个文件):")
        print("=" * 50)

        total_clips = 0
        total_duration = 0

        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)

                episode_name = os.path.splitext(os.path.basename(cache_file))[0]
                clips = result.get('clips', [])

                print(f"\n📺 {episode_name}")
                print(f"   精彩片段: {len(clips)} 个")

                if clips:
                    avg_score = sum(c.get('score', 0) for c in clips) / len(clips)
                    print(f"   平均评分: {avg_score:.1f}")

                    clip_duration = sum(self._parse_duration(c.get('end_time', '0:0:0')) - 
                                      self._parse_duration(c.get('start_time', '0:0:0')) for c in clips)
                    print(f"   总时长: {clip_duration // 60:.0f}分{clip_duration % 60:.0f}秒")

                    total_clips += len(clips)
                    total_duration += clip_duration

            except Exception as e:
                print(f"⚠️ 读取 {cache_file} 失败: {e}")

        print(f"\n📈 总计统计:")
        print(f"   总片段数: {total_clips}")
        print(f"   总时长: {total_duration // 60:.0f}分{total_duration % 60:.0f}秒")

    def _parse_duration(self, time_str: str) -> int:
        """解析时间字符串为秒数"""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = map(int, parts)
                return m * 60 + s
            else:
                return int(parts[0])
        except:
            return 0

def main():
    """主函数"""
    try:
        clipper = TVClipperMain()
        clipper.run()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        print("请检查错误信息并重试")

if __name__ == "__main__":
    main()

# Dummy implementations for the helper modules
class config_helper:
    @staticmethod
    def load_config():
        return {'enabled': False}

    @staticmethod
    def interactive_setup():
        return {'enabled': False}

class SubtitleAnalyzer:
    def __init__(self, ai_config):
        pass

    def analyze_episode(self, file_path):
        return {'clips': []}

class VideoClipper:
    def clip_episode(self, cache_file, matching_video):
        pass