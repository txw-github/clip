#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一电视剧智能剪辑系统
使用统一的配置和AI客户端
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional
from unified_config import unified_config
from unified_ai_client import ai_client

class UnifiedTVClipper:
    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos" 
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"

        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        print("🚀 统一电视剧智能剪辑系统")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

        # 显示AI状态
        if unified_config.is_enabled():
            provider_name = unified_config.providers.get(
                unified_config.config.get('provider'), {}
            ).get('name', '未知')
            model = unified_config.config.get('model', '未知')
            print(f"🤖 AI分析: 已启用 ({provider_name} - {model})")
        else:
            print("📝 AI分析: 未启用")

    def setup_ai_config(self):
        """配置AI"""
        return unified_config.interactive_setup()

    def check_files(self) -> tuple:
        """检查文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) 
                    if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        video_files = [f for f in os.listdir(self.video_folder) 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'))]

        srt_files.sort()
        video_files.sort()

        print(f"\n📊 文件状态:")
        print(f"📄 字幕文件: {len(srt_files)} 个")
        print(f"🎬 视频文件: {len(video_files)} 个")

        return srt_files, video_files

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试读取文件
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue

        if not content:
            return []
        
        # 智能错别字修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)

        # 解析字幕条目
        subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1

                    time_pattern = r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})'
                    time_match = re.search(time_pattern, lines[1])

                    if time_match:
                        start_time = time_match.group(1).replace('.', ',')
                        end_time = time_match.group(2).replace('.', ',')
                        text = '\n'.join(lines[2:]).strip()

                        if text:
                            subtitles.append({
                                'index': index,
                                'start': start_time,
                                'end': end_time,
                                'text': text
                            })
                except:
                    continue

        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数 - 直接使用SRT文件名"""
        base_name = os.path.splitext(filename)[0]
        
        # 尝试提取数字集数
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']
        for pattern in patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                return f"E{match.group(1).zfill(2)}"
        
        # 如果没有找到数字，返回文件名本身
        return base_name

    def analyze_episode(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """分析剧集"""
        episode_num = self._extract_episode_number(filename)

        # 检查缓存
        cache_file = os.path.join(self.cache_folder, f"{episode_num}_analysis.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    print(f"📋 使用缓存分析: {episode_num}")
                    return cached_analysis
            except:
                pass

        if not unified_config.is_enabled():
            print(f"❌ 未启用AI分析，无法处理")
            return None

        # AI分析
        analysis = self._ai_analyze(subtitles, episode_num)

        # 保存到缓存
        if analysis:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                print(f"💾 分析结果已缓存")
            except Exception as e:
                print(f"⚠️ 缓存保存失败: {e}")

        return analysis

    def _ai_analyze(self, subtitles: List[Dict], episode_num: str) -> Optional[Dict]:
        """AI智能分析"""
        # 构建上下文
        total_subs = len(subtitles)
        sample_size = min(300, total_subs)

        if total_subs > sample_size:
            step = total_subs // sample_size
            sampled_subtitles = [subtitles[i] for i in range(0, total_subs, step)][:sample_size]
        else:
            sampled_subtitles = subtitles

        context = ' '.join([sub['text'] for sub in sampled_subtitles])

        # 构建提示词
        prompt = f"""分析电视剧剧集内容，为{episode_num}创建3个2-3分钟的精彩短视频。

剧情内容：{context}

请以JSON格式返回：
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "main_theme": "本集主题"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题",
            "start_time": "开始时间(HH:MM:SS,mmm)",
            "end_time": "结束时间(HH:MM:SS,mmm)", 
            "description": "内容描述",
            "dramatic_value": 8.5
        }}
    ]
}}

注意：时间格式必须准确，确保时间段存在于字幕中。"""

        system_prompt = "你是专业的电视剧剪辑师，擅长识别精彩片段。"

        try:
            response = ai_client.call_ai(prompt, system_prompt)
            if response:
                return self._parse_ai_response(response)
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return None

    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_text = response[start:end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]

            return json.loads(json_text)
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
            return None

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """匹配视频文件"""
        base_name = os.path.splitext(subtitle_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

        print(f"🔍 查找视频文件: {base_name}")

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                print(f"✅ 找到匹配: {base_name + ext}")
                return video_path

        # 模糊匹配
        for filename in os.listdir(self.video_folder):
            if any(filename.lower().endswith(ext.lower()) for ext in video_extensions):
                video_base = os.path.splitext(filename)[0]
                if base_name.lower() in video_base.lower() or video_base.lower() in base_name.lower():
                    print(f"📁 找到模糊匹配: {filename}")
                    return os.path.join(self.video_folder, filename)

        print(f"❌ 未找到匹配的视频文件")
        return None

    def create_video_clips(self, analysis: Dict, video_file: str) -> List[str]:
        """创建视频片段"""
        created_clips = []

        for segment in analysis.get('highlight_segments', []):
            title = segment['title']
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024*1024:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # 剪辑视频
            if self._create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)

        return created_clips

    def _create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']

            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")

            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0 or duration > 300:
                print(f"   ❌ 时间段无效: {duration}秒")
                return False
            
            # 检查ffmpeg
            ffmpeg_cmd = 'ffmpeg'
            try:
                result = subprocess.run([ffmpeg_cmd, '-version'], 
                                      capture_output=True, timeout=5)
                if result.returncode != 0:
                    print(f"   ❌ ffmpeg不可用")
                    return False
            except:
                print(f"   ❌ ffmpeg未安装")
                return False

            # FFmpeg命令
            cmd = [
                ffmpeg_cmd,
                '-hide_banner', '-loglevel', 'error',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-preset', 'fast', '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                '-y', output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                if file_size > 0.5:
                    print(f"   ✅ 成功: {file_size:.1f}MB")
                    return True
                else:
                    print(f"   ❌ 文件太小")
                    os.remove(output_path)
                    return False
            else:
                print(f"   ❌ 剪辑失败")
                return False

        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s_ms = parts
                if ',' in s_ms:
                    s, ms = s_ms.split(',')
                    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                else:
                    return int(h) * 3600 + int(m) * 60 + float(s_ms)
            return 0.0
        except:
            return 0.0

    def process_single_episode(self, subtitle_file: str) -> bool:
        """处理单集"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False

        # 2. AI分析
        analysis = self.analyze_episode(subtitles, subtitle_file)
        if not analysis:
            print(f"❌ AI分析失败")
            return False

        # 3. 查找视频
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False

        # 4. 创建片段
        created_clips = self.create_video_clips(analysis, video_file)

        print(f"✅ {subtitle_file} 处理完成: {len(created_clips)} 个片段")
        return len(created_clips) > 0

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 60)

        srt_files, video_files = self.check_files()

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        if not video_files:
            print(f"❌ {self.video_folder}/ 目录中未找到视频文件")
            return

        if not unified_config.is_enabled():
            print(f"❌ 请先配置AI接口")
            return

        total_success = 0

        for subtitle_file in srt_files:
            try:
                if self.process_single_episode(subtitle_file):
                    total_success += 1
            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")

        final_clips = len([f for f in os.listdir(self.output_folder) if f.endswith('.mp4')])

        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {final_clips} 个")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("📺 统一电视剧智能剪辑系统")
            print("=" * 60)

            # 显示状态
            config_status = "🤖 已配置" if unified_config.is_enabled() else "❌ 未配置"
            print(f"AI状态: {config_status}")

            srt_files, video_files = self.check_files()

            print("\n请选择操作:")
            print("1. 🎬 开始智能剪辑")
            print("2. 🤖 配置AI接口")
            print("3. 📁 检查文件状态")
            print("4. ❌ 退出")

            try:
                choice = input("\n请输入选择 (1-4): ").strip()

                if choice == '1':
                    if not unified_config.is_enabled():
                        print(f"\n❌ 请先配置AI接口")
                        continue
                    if not srt_files or not video_files:
                        print(f"\n❌ 请检查文件是否准备完整")
                        continue

                    self.process_all_episodes()

                elif choice == '2':
                    self.setup_ai_config()

                elif choice == '3':
                    self.check_files()
                    print(f"\n💡 提示:")
                    print(f"• 字幕文件请放入: {self.srt_folder}/")
                    print(f"• 视频文件请放入: {self.video_folder}/")
                    print(f"• 输出文件在: {self.output_folder}/")

                elif choice == '4':
                    print("\n👋 感谢使用！")
                    break

                else:
                    print("❌ 无效选择")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")

def main():
    """主函数"""
    try:
        clipper = UnifiedTVClipper()
        clipper.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 系统错误: {e}")

if __name__ == "__main__":
    main()