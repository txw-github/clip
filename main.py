#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一电视剧智能剪辑系统
支持官方API和中转API两种模式
"""

import os
import re
import json
import subprocess
import requests
from typing import List, Dict, Optional
from datetime import datetime

class UnifiedTVClipper:
    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos"
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"

        # 创建必要目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        # AI配置
        self.ai_config = self._load_ai_config()

        print("🚀 统一电视剧智能剪辑系统")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

    def _load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        print(f"🤖 AI分析: 已启用 ({config.get('provider', '未知')})")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")

        print("📝 AI分析: 未配置，将使用基础分析")
        return {'enabled': False}

    def setup_ai_config(self):
        """配置AI接口"""
        print("\n🤖 AI配置")
        print("=" * 40)
        print("1. 官方API (需要魔法上网)")
        print("2. 中转API (国内可访问)")
        print("0. 跳过AI配置")

        choice = input("请选择 (0-2): ").strip()

        if choice == "1":
            self._setup_official_api()
        elif choice == "2":
            self._setup_proxy_api()
        else:
            self.ai_config = {'enabled': False}

    def _setup_official_api(self):
        """配置官方API"""
        print("\n选择官方API:")
        print("1. Google Gemini")
        print("2. OpenAI")

        choice = input("请选择 (1-2): ").strip()
        api_key = input("请输入API密钥: ").strip()

        if not api_key:
            self.ai_config = {'enabled': False}
            return

        if choice == "1":
            config = {
                'enabled': True,
                'api_type': 'official',
                'provider': 'gemini',
                'api_key': api_key,
                'model': 'gemini-2.5-flash'
            }
        else:
            config = {
                'enabled': True,
                'api_type': 'official',
                'provider': 'openai',
                'api_key': api_key,
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-3.5-turbo'
            }

        self.ai_config = config
        self._save_ai_config()

    def _setup_proxy_api(self):
        """配置中转API"""
        print("\n中转API配置:")
        base_url = input("API地址 (如: https://www.chataiapi.com/v1): ").strip()
        api_key = input("API密钥: ").strip()
        model = input("模型名称 (如: deepseek-r1): ").strip() or "deepseek-r1"

        if not all([base_url, api_key]):
            self.ai_config = {'enabled': False}
            return

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'custom',
            'api_key': api_key,
            'base_url': base_url,
            'model': model
        }

        self.ai_config = config
        self._save_ai_config()

    def _save_ai_config(self):
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.ai_config, f, indent=2, ensure_ascii=False)
            print("✅ AI配置已保存")
        except Exception as e:
            print(f"⚠️ 配置保存失败: {e}")

    def check_files(self) -> tuple:
        """检查文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) 
                    if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        video_files = [f for f in os.listdir(self.video_folder) 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'))]

        # 按字符串排序，这就是电视剧的顺序
        srt_files.sort()

        video_files.sort()

        print(f"\n📊 文件状态:")
        print(f"📄 字幕文件: {len(srt_files)} 个")
        print(f"🎬 视频文件: {len(video_files)} 个")

        return srt_files, video_files

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试不同编码
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
                except (ValueError, IndexError):
                    continue

        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数 - 直接使用SRT文件名"""
        # 直接使用文件名作为集数标识
        base_name = os.path.splitext(filename)[0]

        # 尝试提取数字集数
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']
        for pattern in patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                return match.group(1).zfill(2)

        # 如果没有找到数字，返回文件名本身
        return base_name

    def analyze_episode(self, subtitles: List[Dict], filename: str) -> Dict:
        """分析剧集"""
        episode_num = self._extract_episode_number(filename)

        if self.ai_config.get('enabled', False):
            return self._ai_analyze(subtitles, episode_num, filename)
        else:
            return self._basic_analyze(subtitles, episode_num, filename)

    def _ai_analyze(self, subtitles: List[Dict], episode_num: str, filename: str) -> Dict:
        """AI智能分析"""
        # 构建完整上下文
        context = ' '.join([sub['text'] for sub in subtitles[:200]])  # 前200条字幕

        prompt = f"""你是专业的电视剧剪辑师，需要为{episode_num}创建3个2-3分钟的精彩短视频。

剧情内容：{context}

请以JSON格式返回：
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre": "剧情类型",
        "main_theme": "本集主题"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "description": "内容描述",
            "dramatic_value": 8.5
        }}
    ]
}}"""

        try:
            response = self._call_ai_api(prompt)
            if response:
                analysis = self._parse_ai_response(response)
                if analysis:
                    return analysis
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        # 降级到基础分析
        return self._basic_analyze(subtitles, episode_num, filename)

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            if self.ai_config.get('api_type') == 'official':
                return self._call_official_api(prompt)
            else:
                return self._call_proxy_api(prompt)
        except Exception as e:
            print(f"⚠️ API调用异常: {e}")
            return None

    def _call_official_api(self, prompt: str) -> Optional[str]:
        """调用官方API"""
        provider = self.ai_config.get('provider')

        if provider == 'gemini':
            try:
                from google import genai

                client = genai.Client(api_key=self.ai_config['api_key'])
                response = client.models.generate_content(
                    model=self.ai_config['model'],
                    contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"⚠️ Gemini API调用失败: {e}")
                return None

        elif provider == 'openai':
            try:
                from openai import OpenAI

                client = OpenAI(
                    api_key=self.ai_config['api_key'],
                    base_url=self.ai_config.get('base_url')
                )

                completion = client.chat.completions.create(
                    model=self.ai_config['model'],
                    messages=[
                        {'role': 'system', 'content': '你是专业的电视剧剪辑师。'},
                        {'role': 'user', 'content': prompt}
                    ],
                    max_tokens=2000
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"⚠️ OpenAI API调用失败: {e}")
                return None

    def _call_proxy_api(self, prompt: str) -> Optional[str]:
        """调用中转API"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.ai_config['api_key'],
                base_url=self.ai_config['base_url']
            )

            completion = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=[
                    {'role': 'system', 'content': '你是专业的电视剧剪辑师。'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ 中转API调用失败: {e}")
            return None

    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON内容
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
            print(f"⚠️ JSON解析失败")
            return None

    def _basic_analyze(self, subtitles: List[Dict], episode_num: str, filename: str) -> Dict:
        """基础分析（无AI时）"""
        dramatic_keywords = [
            '突然', '发现', '真相', '秘密', '不可能', '为什么', '杀人', '死了', 
            '救命', '危险', '完了', '震惊', '愤怒', '哭', '崩溃', '听证会', '法庭'
        ]

        high_score_segments = []

        for i, subtitle in enumerate(subtitles):
            score = 0
            text = subtitle['text']

            # 关键词评分
            for keyword in dramatic_keywords:
                if keyword in text:
                    score += 2

            # 标点符号评分
            score += text.count('！') + text.count('？') + text.count('...') * 0.5

            if score >= 3:
                high_score_segments.append({
                    'index': i,
                    'subtitle': subtitle,
                    'score': score
                })

        # 选择最佳片段
        high_score_segments.sort(key=lambda x: x['score'], reverse=True)

        segments = []
        for i, seg in enumerate(high_score_segments[:3], 1):  # 最多3个片段
            start_idx = max(0, seg['index'] - 20)
            end_idx = min(len(subtitles) - 1, seg['index'] + 20)

            segments.append({
                "segment_id": i,
                "title": f"{episode_num}_精彩片段{i}",
                "start_time": subtitles[start_idx]['start'],
                "end_time": subtitles[end_idx]['end'],
                "description": f"精彩片段: {seg['subtitle']['text'][:50]}...",
                "dramatic_value": min(seg['score'] * 1.5, 10)
            })

        return {
            "episode_analysis": {
                "episode_number": episode_num,
                "genre": "通用",
                "main_theme": f"{episode_num}精彩内容"
            },
            "highlight_segments": segments
        }

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        base_name = os.path.splitext(subtitle_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

        print(f"🔍 查找视频文件: {base_name}")

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                print(f"✅ 找到精确匹配: {base_name + ext}")
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

    def create_video_clips(self, analysis: Dict, video_file: str, subtitle_filename: str) -> List[str]:
        """创建视频片段"""
        created_clips = []

        for segment in analysis.get('highlight_segments', []):
            segment_id = segment['segment_id']
            title = segment['title']

            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # 剪辑视频
            if self._create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)

        return created_clips

    def _create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段 - Windows兼容版本"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']

            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")

            # 时间转换
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0:
                print(f"   ❌ 无效时间段")
                return False

            # 添加缓冲确保对话完整
            buffer_start = max(0, start_seconds - 2)
            buffer_duration = duration + 4

            # 检查ffmpeg - Windows兼容
            ffmpeg_cmd = 'ffmpeg'
            try:
                # Windows下可能需要指定.exe
                test_result = subprocess.run([ffmpeg_cmd, '-version'],
                                           capture_output=True, text=True, timeout=10)
                if test_result.returncode != 0:
                    ffmpeg_cmd = 'ffmpeg.exe'
                    test_result = subprocess.run([ffmpeg_cmd, '-version'],
                                               capture_output=True, text=True, timeout=10)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print(f"   ❌ ffmpeg未安装或不可用")
                print(f"   💡 请安装ffmpeg: https://ffmpeg.org/download.html")
                return False

            # Windows路径处理
            video_file = os.path.abspath(video_file)
            output_path = os.path.abspath(output_path)

            # FFmpeg命令 - Windows优化
            cmd = [
                ffmpeg_cmd,
                '-hide_banner',  # 减少输出
                '-loglevel', 'error',  # 只显示错误
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'ultrafast',  # 更快的预设
                '-crf', '28',  # 稍微降低质量以提高速度
                '-avoid_negative_ts', 'make_zero',  # 避免时间戳问题
                output_path,
                '-y'
            ]

            # Windows下使用不同的subprocess调用方式
            import sys
            if sys.platform.startswith('win'):
                # Windows下使用shell=True可以避免一些线程问题
                cmd_str = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in cmd])
                process = subprocess.Popen(
                    cmd_str,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )

                # 设置超时并等待完成
                try:
                    stdout, stderr = process.communicate(timeout=300)
                    returncode = process.returncode
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"   ❌ 超时: 剪辑时间过长")
                    return False
            else:
                # 非Windows系统使用原来的方式
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                returncode = result.returncode
                stderr = result.stderr

            # 检查结果
            if returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"   ✅ 成功: {file_size:.1f}MB")
                return True
            else:
                error_msg = stderr[:200] if stderr else '未知错误'
                print(f"   ❌ 失败: {error_msg}")
                return False

        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def process_single_episode(self, subtitle_file: str) -> bool:
        """处理单集完整流程"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False

        # 2. 分析剧集
        analysis = self.analyze_episode(subtitles, subtitle_file)

        # 3. 找到视频文件
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到匹配的视频文件")
            return False

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 4. 创建视频片段
        created_clips = self.create_video_clips(analysis, video_file, subtitle_file)

        print(f"✅ {subtitle_file} 处理完成: {len(created_clips)} 个片段")
        return len(created_clips) > 0

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 60)

        # 检查文件
        srt_files, video_files = self.check_files()

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        if not video_files:
            print(f"❌ {self.video_folder}/ 目录中未找到视频文件")
            return

        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        print(f"🤖 AI分析: {'启用' if self.ai_config.get('enabled') else '未启用'}")

        # 处理每一集
        total_success = 0
        total_clips = 0

        for subtitle_file in srt_files:
            try:
                success = self.process_single_episode(subtitle_file)
                if success:
                    total_success += 1

                # 统计片段数
                episode_clips = [f for f in os.listdir(self.output_folder)
                               if f.startswith(os.path.splitext(subtitle_file)[0]) and f.endswith('.mp4')]
                total_clips += len(episode_clips)

            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")

        print(f"\n📊 最终统计:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")

    def show_main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("📺 统一电视剧智能剪辑系统")
            print("=" * 60)

            # 显示状态
            ai_status = "🤖 AI增强" if self.ai_config.get('enabled') else "📝 基础分析"
            print(f"当前模式: {ai_status}")

            srt_files, video_files = self.check_files()

            print("\n请选择操作:")
            print("1. 🎬 开始智能剪辑")
            print("2. 🤖 配置AI接口")
            print("3. 📁 检查文件状态")
            print("4. ❌ 退出")

            try:
                choice = input("\n请输入选择 (1-4): ").strip()

                if choice == '1':
                    if not srt_files:
                        print(f"\n❌ 请先将字幕文件放入 {self.srt_folder}/ 目录")
                        continue
                    if not video_files:
                        print(f"\n❌ 请先将视频文件放入 {self.video_folder}/ 目录")
                        continue

                    print("\n🚀 开始智能剪辑...")
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
                    print("❌ 无效选择，请重试")

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