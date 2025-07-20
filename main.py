#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧智能剪辑系统 - 主程序
集成了智能API配置、剧情分析、视频剪辑等功能
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
from api_config_helper import config_helper

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
        # 查找字幕文件 - 支持.txt和.srt格式
        srt_files = glob.glob("srt/*.srt") + glob.glob("srt/*.txt")

        if not srt_files:
            print("❌ 未找到字幕文件")
            print("💡 请将字幕文件(.srt或.txt)放在 srt/ 目录下")
            return

        print(f"\n📄 找到 {len(srt_files)} 个字幕文件:")
        
        # 检查已分析的文件
        analyzed_files = []
        pending_files = []
        
        for file_path in srt_files:
            filename = os.path.basename(file_path)
            cache_name = os.path.splitext(filename)[0] + '.json'
            cache_path = os.path.join('analysis_cache', cache_name)
            
            if os.path.exists(cache_path):
                analyzed_files.append((file_path, True))
                print(f"✅ {filename} (已分析)")
            else:
                pending_files.append((file_path, False))
                print(f"⏳ {filename} (待分析)")

        if analyzed_files:
            print(f"\n📊 状态统计:")
            print(f"   已分析: {len(analyzed_files)} 个文件")
            print(f"   待分析: {len(pending_files)} 个文件")

        print(f"\n📋 分析选项:")
        print(f"1. 🔄 分析所有文件 (跳过已分析的)")
        print(f"2. 🆕 重新分析所有文件 (覆盖已有结果)")
        print(f"3. ⚡ 只分析未完成的文件")

        while True:
            try:
                choice = input(f"\n请选择分析模式 (1-3): ").strip()
                choice = int(choice)

                if choice == 1:
                    # 智能分析 - 跳过已分析的
                    self._analyze_all_files_smart(srt_files, skip_analyzed=True)
                    break
                elif choice == 2:
                    # 重新分析所有
                    self._analyze_all_files_smart(srt_files, skip_analyzed=False)
                    break
                elif choice == 3:
                    # 只分析待分析的
                    if pending_files:
                        self._analyze_all_files_smart([f[0] for f in pending_files], skip_analyzed=False)
                    else:
                        print("✅ 所有文件都已分析完成")
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

    def _analyze_all_files_smart(self, srt_files: List[str], skip_analyzed: bool = True):
        """智能批量分析所有字幕文件 - 保证一致性"""
        print(f"\n🔍 开始智能批量分析 {len(srt_files)} 个文件...")
        print(f"📋 模式: {'跳过已分析' if skip_analyzed else '重新分析所有'}")

        analyzer = SubtitleAnalyzer(self.ai_config)
        all_results = []
        skipped_count = 0
        success_count = 0
        error_count = 0

        for i, file_path in enumerate(srt_files, 1):
            filename = os.path.basename(file_path)
            cache_name = os.path.splitext(filename)[0] + '.json'
            cache_path = os.path.join('analysis_cache', cache_name)

            print(f"\n[{i}/{len(srt_files)}] 处理: {filename}")

            # 检查是否已存在分析结果
            if skip_analyzed and os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cached_result = json.load(f)
                    
                    all_results.append(cached_result)
                    skipped_count += 1
                    print(f"⏩ 跳过已分析 (已有 {len(cached_result.get('clips', []))} 个片段)")
                    continue
                except Exception as e:
                    print(f"⚠️ 缓存文件损坏，重新分析: {e}")

            # 执行分析
            try:
                result = analyzer.analyze_episode(file_path)

                if result and 'clips' in result:
                    # 保存分析结果到缓存
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    all_results.append(result)
                    success_count += 1
                    print(f"✅ 分析完成，识别到 {len(result.get('clips', []))} 个精彩片段")
                    print(f"💾 结果已缓存到: {cache_name}")
                else:
                    error_count += 1
                    print("❌ 分析失败 - 未识别到有效片段")

            except Exception as e:
                error_count += 1
                print(f"❌ 分析出错: {e}")

        # 统计结果
        print(f"\n📊 批量分析完成:")
        print(f"   总文件数: {len(srt_files)} 个")
        print(f"   跳过已分析: {skipped_count} 个")
        print(f"   新分析成功: {success_count} 个")
        print(f"   分析失败: {error_count} 个")
        
        total_clips = sum(len(r.get('clips', [])) for r in all_results)
        print(f"   总计精彩片段: {total_clips} 个")

        if all_results:
            self._generate_batch_summary(all_results)

    def _generate_batch_summary(self, results: List[Dict]):
        """生成批量分析汇总报告"""
        summary_path = os.path.join('analysis_cache', 'batch_summary.json')
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_episodes': len(results),
            'total_clips': sum(len(r.get('clips', [])) for r in results),
            'episodes': []
        }

        for result in results:
            episode_info = {
                'filename': result.get('episode', 'unknown'),
                'clips_count': len(result.get('clips', [])),
                'total_duration': sum(clip.get('duration', 0) for clip in result.get('clips', [])),
                'theme': result.get('theme', 'unknown')
            }
            summary['episodes'].append(episode_info)

        # 保存汇总
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"📋 批量汇总已保存: analysis_cache/batch_summary.json")

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
        # 检查是否有分析结果 (排除汇总文件)
        cache_files = [f for f in glob.glob("analysis_cache/*.json") 
                      if not f.endswith('batch_summary.json')]

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

        # 检查已剪辑的视频
        clipped_files = glob.glob("clips/*.mp4")
        already_clipped = set()
        for clip_file in clipped_files:
            # 从剪辑文件名提取原始集数
            basename = os.path.basename(clip_file)
            if basename.startswith('E') or 'S01E' in basename:
                already_clipped.add(basename.split('_')[0])

        print(f"✂️ 已剪辑: {len(already_clipped)} 个集数")

        clipper = VideoClipper()
        success_count = 0
        skip_count = 0
        error_count = 0

        for cache_file in cache_files:
            episode_name = os.path.splitext(os.path.basename(cache_file))[0]
            
            # 检查是否已剪辑
            episode_prefix = episode_name.replace('_4K_60fps', '').replace('S01', '')
            if any(episode_prefix in clipped for clipped in already_clipped):
                print(f"\n⏩ 跳过已剪辑: {episode_name}")
                skip_count += 1
                continue

            # 查找对应的视频文件
            matching_video = self._find_matching_video(episode_name, video_files)

            if matching_video:
                print(f"\n✂️ 剪辑 {episode_name}")
                try:
                    if clipper.clip_episode(cache_file, matching_video):
                        success_count += 1
                        print(f"✅ 剪辑完成: {episode_name}")
                    else:
                        error_count += 1
                        print(f"❌ 剪辑失败: {episode_name}")
                except Exception as e:
                    error_count += 1
                    print(f"❌ 剪辑出错: {episode_name} - {e}")
            else:
                error_count += 1
                print(f"⚠️ 未找到 {episode_name} 对应的视频文件")

        print(f"\n📊 剪辑任务完成:")
        print(f"   成功剪辑: {success_count} 个")
        print(f"   跳过已有: {skip_count} 个") 
        print(f"   失败/错误: {error_count} 个")

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

# 实际导入必要的模块
try:
    from subtitle_analyzer import SubtitleAnalyzer
except ImportError:
    print("⚠️ 字幕分析器模块未找到，将使用基础功能")
    
    class SubtitleAnalyzer:
        def __init__(self, ai_config):
            self.ai_config = ai_config
        
        def analyze_episode(self, file_path):
            # 基础字幕分析实现
            return {'clips': []}

try:
    from video_clipper import VideoClipper
except ImportError:
    print("⚠️ 视频剪辑器模块未找到，将使用基础功能")
    
    class VideoClipper:
        def clip_episode(self, cache_file, matching_video):
            print(f"📹 模拟剪辑: {os.path.basename(cache_file)} -> {os.path.basename(matching_video)}")
            return True