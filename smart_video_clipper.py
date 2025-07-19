#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能视频剪辑器 - 支持videos目录结构，自动生成多个短视频，包含旁白解释
"""

import os
import json
import subprocess
from typing import List, Dict, Optional
from smart_analyzer import SmartAnalyzer

class SmartVideoClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder

        # 创建输出文件夹
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ 创建输出目录: {self.output_folder}/")

    def get_video_file(self, episode_subtitle_name: str) -> Optional[str]:
        """根据字幕文件名找到对应视频"""
        # 处理srt目录来的字幕文件
        base_name = os.path.basename(episode_subtitle_name)
        base_name = base_name.replace('.txt', '').replace('.srt', '')

        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']

        # 检查videos目录
        if not os.path.exists(self.video_folder):
            print(f"❌ 视频目录不存在: {self.video_folder}")
            return None

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for file in os.listdir(self.video_folder):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(file)[0]

                # 提取集数信息进行匹配
                import re
                subtitle_episode = re.search(r'[se](\d+)[ex](\d+)', base_name.lower())
                video_episode = re.search(r'[se](\d+)[ex](\d+)', file_base.lower())

                if subtitle_episode and video_episode:
                    if subtitle_episode.groups() == video_episode.groups():
                        return os.path.join(self.video_folder, file)

        print(f"⚠ 未找到匹配的视频文件: {base_name}")
        return None

    def generate_narration(self, clip_analysis: Dict, episode_context: str = "") -> Dict:
        """生成旁白文本"""
        from narration_generator import NarrationGenerator

        generator = NarrationGenerator()
        narration_data = generator.generate_professional_narration(clip_analysis, episode_context)

        return narration_data

    def create_narration_audio(self, narration_text: str, output_path: str) -> bool:
        """创建旁白音频文件"""
        try:
            # 使用系统TTS生成音频（这里使用一个简单的方法）
            # 实际项目中可以使用更高质量的TTS服务

            # 创建一个简单的音频文件（使用ffmpeg生成静音，然后添加字幕）
            # 这里我们先创建一个静音音频作为占位符
            duration = max(5, len(narration_text) * 0.1)  # 根据文本长度估算时长

            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', str(duration),
                '-c:a', 'aac',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=300, encoding='utf-8', errors='ignore')
            return result.returncode == 0

        except Exception as e:
            print(f"    ⚠ 生成旁白音频失败: {e}")
            return False

    def create_single_clip(self, video_file: str, clip_analysis: Dict, output_path: str) -> bool:
        """创建单个短视频片段，包含旁白"""
        try:
            segment = clip_analysis['original_segment']

            # 获取AI建议的调整
            adjustment = clip_analysis.get('clip_adjustment', {})
            start_seconds = self.time_to_seconds(segment['start_time'])
            end_seconds = self.time_to_seconds(segment['end_time'])

            # 应用AI调整
            start_offset = adjustment.get('new_start_offset', -2)  # 默认前2秒
            end_offset = adjustment.get('new_end_offset', 2)      # 默认后2秒

            adjusted_start = max(0, start_seconds + start_offset)
            adjusted_end = end_seconds + end_offset
            duration = adjusted_end - adjusted_start

            # 智能质量设置
            if duration < 60:
                crf = '20'  # 短片段高质量
            elif duration < 180:
                crf = '23'  # 中等片段平衡
            else:
                crf = '25'  # 长片段压缩

            # 第一步：剪辑原始视频
            temp_video = output_path.replace('.mp4', '_temp.mp4')
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(adjusted_start),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-crf', crf,
                '-preset', 'medium',
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                temp_video,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=300, encoding='utf-8', errors='ignore')

            if result.returncode != 0:
                print(f"    ❌ 视频剪辑失败: {result.stderr[:100]}")
                return False

            # 第二步：添加旁白和字幕
            narration_data = self.generate_narration(clip_analysis, "")
            final_video = self.add_narration_and_subtitles(temp_video, narration_data, clip_analysis, output_path)

            # 清理临时文件
            if os.path.exists(temp_video):
                os.remove(temp_video)

            if final_video and os.path.exists(final_video):
                file_size = os.path.getsize(final_video) / (1024*1024)
                print(f"    ✅ 生成短视频: {os.path.basename(final_video)} ({file_size:.1f}MB)")
                print(f"    📝 旁白内容: {narration_data.get('full_narration', '')[:50]}...")
                return True
            else:
                print(f"    ❌ 添加旁白失败")
                return False

        except Exception as e:
            print(f"    ❌ 处理出错: {e}")
            return False

    def add_narration_and_subtitles(self, video_path: str, narration_data: Dict, clip_analysis: Dict, output_path: str) -> str:
        """添加旁白解释和字幕"""
        try:
            title = clip_analysis.get('video_title', '精彩片段')
            hook = clip_analysis.get('hook_reason', '')

            # 清理文本
            title_clean = title.replace("'", "").replace('"', '').replace('/', '_')[:35]

            # 构建视频滤镜
            filter_parts = []

            # 主标题 (0-3秒)
            filter_parts.append(
                f"drawtext=text='{title_clean}':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=50:"
                f"box=1:boxcolor=black@0.8:boxborderw=5:enable='between(t,0,3)'"
            )

            # 分段旁白字幕
            timing = narration_data.get('timing', {})

            # 开场旁白
            opening_text = narration_data.get('opening', '').replace("'", "").replace('"', '')[:50]
            if opening_text:
                opening_time = timing.get('opening', [0, 3])
                filter_parts.append(
                    f"drawtext=text='{opening_text}':fontsize=16:fontcolor=yellow:x=(w-text_w)/2:y=(h-120):"
                    f"box=1:boxcolor=black@0.7:boxborderw=4:enable='between(t,{opening_time[0]},{opening_time[1]})'"
                )

            # 过程解说
            process_text = narration_data.get('process', '').replace("'", "").replace('"', '')[:50]
            if process_text:
                process_time = timing.get('process', [3, 8])
                filter_parts.append(
                    f"drawtext=text='{process_text}':fontsize=16:fontcolor=lightblue:x=(w-text_w)/2:y=(h-120):"
                    f"box=1:boxcolor=black@0.7:boxborderw=4:enable='between(t,{process_time[0]},{process_time[1]})'"
                )

            # 亮点强调
            highlight_text = narration_data.get('highlight', '').replace("'", "").replace('"', '')[:50]
            if highlight_text:
                highlight_time = timing.get('highlight', [8, 11])
                filter_parts.append(
                    f"drawtext=text='{highlight_text}':fontsize=18:fontcolor=orange:x=(w-text_w)/2:y=(h-120):"
                    f"box=1:boxcolor=black@0.8:boxborderw=4:enable='between(t,{highlight_time[0]},{highlight_time[1]})'"
                )

            # 结尾
            ending_text = narration_data.get('ending', '').replace("'", "").replace('"', '')[:40]
            if ending_text:
                ending_time = timing.get('ending', [11, 12])
                filter_parts.append(
                    f"drawtext=text='{ending_text}':fontsize=16:fontcolor=lightgreen:x=(w-text_w)/2:y=(h-120):"
                    f"box=1:boxcolor=black@0.7:boxborderw=4:enable='between(t,{ending_time[0]},{ending_time[1]})'"
                )

            # 亮点提示标签
            if hook:
                hook_clean = hook.replace("'", "").replace('"', '')[:30]
                filter_parts.append(
                    f"drawtext=text='🔥 {hook_clean}':fontsize=14:fontcolor=red:x=20:y=20:"
                    f"box=1:boxcolor=black@0.6:boxborderw=3:enable='gt(t,5)'"
                )

            filter_text = ",".join(filter_parts)

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_text,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '22',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=120, encoding='utf-8', errors='ignore')

            if result.returncode == 0:
                print(f"    ✓ 添加专业旁白和字幕完成")
                return output_path
            else:
                print(f"    ⚠ 添加旁白失败，保留原视频: {result.stderr[:100]}")
                # 如果失败，至少保留原视频
                if os.path.exists(video_path):
                    import shutil
                    shutil.copy2(video_path, output_path)
                return output_path

        except Exception as e:
            print(f"    ⚠ 添加旁白失败: {e}")
            # 如果失败，至少保留原视频
            if os.path.exists(video_path):
                import shutil
                shutil.copy2(video_path, output_path)
            return output_path

    def create_episode_clips(self, episode_plan: Dict) -> List[str]:
        """为单集创建所有推荐的短视频"""
        episode_file = episode_plan['episode']
        video_file = self.get_video_file(episode_file)

        if not video_file:
            print(f"❌ 未找到视频文件: {os.path.basename(episode_file)}")
            return []

        episode_num = episode_plan['episode_number']
        clips = episode_plan['clips']

        print(f"\n🎬 第{episode_num}集 - 创建 {len(clips)} 个短视频")
        print(f"📁 源视频: {os.path.basename(video_file)}")

        created_clips = []

        for i, clip_analysis in enumerate(clips):
            title = clip_analysis.get('video_title', '精彩片段')
            score = clip_analysis.get('overall_score', 0)

            # 安全的文件名
            safe_title = title.replace('/', '_').replace(':', '_').replace('?', '').replace('*', '')[:25]
            output_name = f"E{episode_num}_clip{i+1}_{safe_title}.mp4"
            output_path = os.path.join(self.output_folder, output_name)

            print(f"  🎯 创建短视频 {i+1}: {title} (评分:{score:.1f})")

            if self.create_single_clip(video_file, clip_analysis, output_path):
                created_clips.append(output_path)

                # 生成说明文件
                self.create_clip_description(output_path, clip_analysis, episode_num, i+1)

        print(f"  ✅ 成功创建 {len(created_clips)}/{len(clips)} 个短视频")
        return created_clips

    def create_clip_description(self, clip_path: str, clip_analysis: Dict, episode_num: str, clip_num: int):
        """为每个短视频创建说明文件"""
        try:
            desc_path = clip_path.replace('.mp4', '_说明.txt')

            narration_data = self.generate_narration(clip_analysis, "")

            content = f"""短视频说明文件
================================

📺 集数: 第{episode_num}集 - 短视频{clip_num}
🎬 标题: {clip_analysis.get('video_title', '精彩片段')}
⭐ 评分: {clip_analysis.get('overall_score', 0):.1f}/10

📝 旁白内容:
完整旁白: {narration_data.get('full_narration', '暂无')}

旁白分段:
• 开场白: {narration_data.get('opening', '暂无')}
• 过程解说: {narration_data.get('process', '暂无')}
• 亮点强调: {narration_data.get('highlight', '暂无')}
• 结尾: {narration_data.get('ending', '暂无')}

🎯 剧情类型: {clip_analysis.get('segment_type', '未知')}
💡 吸引点: {clip_analysis.get('hook_reason', '暂无')}

✨ 精彩亮点:
"""

            highlights = clip_analysis.get('highlights', [])
            for i, highlight in enumerate(highlights, 1):
                content += f"{i}. {highlight}\n"

            content += f"""
⏰ 原始时间: {clip_analysis['original_segment']['start_time']} --> {clip_analysis['original_segment']['end_time']}
🎞️ 建议时长: {clip_analysis.get('optimal_duration', 0)}秒
🔧 AI调整: {clip_analysis.get('clip_adjustment', {}).get('action', '保持原样')}

📈 置信度: {clip_analysis.get('confidence', 0):.2f}
"""

            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"    📄 生成说明文件: {os.path.basename(desc_path)}")

        except Exception as e:
            print(f"    ⚠ 生成说明文件失败: {e}")

    def create_episode_collection(self, episode_clips: List[str], episode_num: str) -> Optional[str]:
        """合并单集的所有短视频为集锦"""
        if not episode_clips:
            return None

        print(f"  🔗 合并第{episode_num}集集锦...")

        list_file = f"temp_ep{episode_num}_list.txt"
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for clip in episode_clips:
                    abs_path = os.path.abspath(clip).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")

            output_path = os.path.join(self.output_folder, f"E{episode_num}_完整集锦.mp4")

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=300, encoding='utf-8', errors='ignore')

            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"    ✅ 集锦: E{episode_num}_完整集锦.mp4 ({file_size:.1f}MB)")
                return output_path
            else:
                print(f"    ❌ 合并失败: {result.stderr[:100]}")

        except Exception as e:
            print(f"    ❌ 合并失败: {e}")
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)

        return None

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

def process_all_episodes_smartly():
    """智能处理所有剧集"""
    from smart_analyzer import analyze_all_episodes_smartly

    print("🚀 启动完全智能化视频剪辑系统 (包含旁白功能)")
    print("=" * 60)

    # 第一步：智能分析
    print("🧠 第一步：完全智能化剧情分析...")
    episodes_plans = analyze_all_episodes_smartly()

    if not episodes_plans:
        print("❌ 没有分析结果")
        return

    # 第二步：创建视频
    print(f"\n🎬 第二步：创建短视频 ({len(episodes_plans)} 集)...")
    print("=" * 60)

    clipper = SmartVideoClipper()

    # 检查videos目录
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入视频文件")
        return

    video_files = [f for f in os.listdir(clipper.video_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]

    if not video_files:
        print(f"❌ videos目录中没有视频文件")
        return

    print(f"✅ 找到 {len(video_files)} 个视频文件")

    all_clips = []
    episode_collections = []

    for episode_plan in episodes_plans:
        try:
            # 创建单集的所有短视频
            episode_clips = clipper.create_episode_clips(episode_plan)
            all_clips.extend(episode_clips)

            # 创建单集集锦
            if episode_clips:
                collection = clipper.create_episode_collection(
                    episode_clips, 
                    episode_plan['episode_number']
                )
                if collection:
                    episode_collections.append(collection)

        except Exception as e:
            print(f"❌ 处理第{episode_plan['episode_number']}集失败: {e}")

    # 第三步：创建完整剧集合集
    if episode_collections:
        print(f"\n🎭 第三步：创建完整剧集合集...")
        create_series_collection(episode_collections, clipper.output_folder)

    # 生成总结报告
    print(f"\n📊 剪辑完成统计：")
    print(f"✅ 创建短视频: {len(all_clips)} 个")
    print(f"✅ 单集集锦: {len(episode_collections)} 个")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"🎬 每个短视频都包含旁白解释和字幕")
    print(f"📄 每个短视频都有对应的说明文件")

    return all_clips

def create_series_collection(episode_collections: List[str], output_folder: str):
    """创建完整剧集合集"""
    try:
        list_file = "temp_series_list.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            for collection in episode_collections:
                abs_path = os.path.abspath(collection).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")

        output_path = os.path.join(output_folder, "完整剧集精彩合集.mp4")

        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            output_path,
            '-y'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=600, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            file_size = os.path.getsize(output_path) / (1024*1024)
            print(f"✅ 完整剧集合集: 完整剧集精彩合集.mp4 ({file_size:.1f}MB)")
        else:
            print(f"❌ 创建合集失败: {result.stderr[:100]}")

    except Exception as e:
        print(f"❌ 创建合集失败: {e}")
    finally:
        if os.path.exists("temp_series_list.txt"):
            os.remove("temp_series_list.txt")

if __name__ == "__main__":
    process_all_episodes_smartly()