#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能AI电视剧剪辑系统 - 主程序
完整解决方案：智能分析、自动剪辑、旁白生成
"""

import os
import re
import json
import hashlib
import subprocess
import sys
from typing import List, Dict, Optional
from datetime import datetime
from ai_analyzer import AIAnalyzer

class IntelligentTVClipper:
    """智能电视剧剪辑系统"""

    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos"
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"

        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        # 加载AI配置
        self.ai_config = self.load_ai_config()

        print("🚀 智能AI电视剧剪辑系统已初始化")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        provider = config.get('provider', 'unknown')
                        print(f"🤖 AI分析已启用: {provider}")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")

        print("📝 AI分析未启用，使用基础规则分析")
        return {'enabled': False}

    def configure_ai_interactive(self):
        """交互式AI配置"""
        print("\n🤖 AI接口配置")
        print("=" * 50)

        print("📝 推荐的AI模型配置:")
        print("1. OpenAI GPT-4 (中转API)")
        print("2. Claude 3.5 Sonnet (中转API)")
        print("3. DeepSeek R1 (中转API)")
        print("4. Gemini Pro (官方API)")
        print("5. 自定义配置")
        print("0. 返回主菜单")

        choice = input("\n请选择配置 (0-5): ").strip()

        if choice == '0':
            return
        elif choice == '1':
            self.setup_gpt4_config()
        elif choice == '2':
            self.setup_claude_config()
        elif choice == '3':
            self.setup_deepseek_config()
        elif choice == '4':
            self.setup_gemini_config()
        elif choice == '5':
            self.custom_ai_config()
        else:
            print("❌ 无效选择")

    def setup_gpt4_config(self):
        """配置GPT-4"""
        print("\n🚀 配置GPT-4")
        print("推荐使用中转API: https://api.openai-proxy.com/v1")

        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return

        base_url = input("请输入API地址 (默认: https://api.openai-proxy.com/v1): ").strip()
        if not base_url:
            base_url = "https://api.openai-proxy.com/v1"

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'openai',
            'api_key': api_key,
            'base_url': base_url,
            'model': 'gpt-4'
        }

        if self.save_ai_config(config):
            self.ai_config = config
            print("✅ GPT-4配置成功！")

    def setup_claude_config(self):
        """配置Claude 3.5 Sonnet"""
        print("\n🤖 配置Claude 3.5 Sonnet")
        print("推荐使用中转API")

        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return

        base_url = input("请输入API地址: ").strip()
        if not base_url:
            print("❌ API地址不能为空")
            return

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'claude',
            'api_key': api_key,
            'base_url': base_url,
            'model': 'claude-3-5-sonnet-20240620'
        }

        if self.save_ai_config(config):
            self.ai_config = config
            print("✅ Claude 3.5 Sonnet配置成功！")

    def setup_deepseek_config(self):
        """配置DeepSeek R1"""
        print("\n🧠 配置DeepSeek R1")

        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return

        base_url = input("请输入API地址: ").strip()
        if not base_url:
            print("❌ API地址不能为空")
            return

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'deepseek',
            'api_key': api_key,
            'base_url': base_url,
            'model': 'deepseek-r1'
        }

        if self.save_ai_config(config):
            self.ai_config = config
            print("✅ DeepSeek R1配置成功！")

    def setup_gemini_config(self):
        """配置Gemini Pro"""
        print("\n💎 配置Gemini Pro")
        print("使用Google官方API")

        api_key = input("请输入Google API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': 'gemini-pro'
        }

        if self.save_ai_config(config):
            self.ai_config = config
            print("✅ Gemini Pro配置成功！")

    def custom_ai_config(self):
        """自定义AI配置"""
        print("\n⚙️ 自定义AI配置")

        provider = input("请输入提供商名称 (如: openai, claude): ").strip()
        api_key = input("请输入API密钥: ").strip()
        base_url = input("请输入API地址: ").strip()
        model = input("请输入模型名称: ").strip()

        if not all([provider, api_key, base_url, model]):
            print("❌ 所有字段都不能为空")
            return

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': provider,
            'api_key': api_key,
            'base_url': base_url,
            'model': model
        }

        if self.save_ai_config(config):
            self.ai_config = config
            print(f"✅ 自定义配置成功")

    def save_ai_config(self, config: Dict) -> bool:
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

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
            print(f"❌ 无法读取文件: {filepath}")
            return []

        # 解析字幕条目
        subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1

                    # 匹配时间格式
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

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用"""
        if not self.ai_config.get('enabled'):
            return None

        try:
            api_type = self.ai_config.get('api_type', 'proxy')

            if api_type == 'official' and self.ai_config.get('provider') == 'gemini':
                return self.call_gemini_api(prompt, system_prompt)
            else:
                return self.call_proxy_api(prompt, system_prompt)

        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def call_gemini_api(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用Google Gemini API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.ai_config['api_key'])
            model = genai.GenerativeModel(self.ai_config.get('model', 'gemini-pro'))

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(full_prompt)

            return response.text

        except Exception as e:
            print(f"⚠️ Gemini API调用失败: {e}")
            return None

    def call_proxy_api(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用中转API"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.ai_config['api_key'],
                base_url=self.ai_config['base_url']
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ 中转API调用失败: {e}")
            return None

    def analyze_episode_with_ai(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """使用AI分析整集"""
        if not self.ai_config.get('enabled'):
            print(f"⚠️ AI未启用，跳过 {filename}")
            return None

        # 构建完整上下文
        full_context = self.build_complete_context(subtitles)
        episode_num = self.extract_episode_number(filename)

        prompt = f"""你是专业的电视剧剪辑师，请分析第{episode_num}集的完整内容。

【完整剧情内容】
{full_context}

请找出3-5个最精彩的片段制作短视频，每个片段2-3分钟。

请严格按照以下JSON格式输出：

```json
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre_type": "剧情类型",
        "main_theme": "本集核心主题"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "精彩标题",
            "start_time": "00:XX:XX,XXX",
            "end_time": "00:XX:XX,XXX",
            "duration_seconds": 180,
            "plot_significance": "剧情重要意义",
            "professional_narration": "完整的专业旁白解说稿",
            "highlight_tip": "一句话字幕亮点提示"
        }}
    ]
}}
```"""

        system_prompt = "你是专业的影视内容分析专家，专长电视剧情深度解构与叙事分析。"

        try:
            response = self.call_ai_api(prompt, system_prompt)
            if response:
                parsed_result = self.parse_ai_response(response)
                if parsed_result:
                    print(f"✅ AI分析成功：{len(parsed_result.get('highlight_segments', []))} 个片段")
                    return parsed_result
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return None

    def build_complete_context(self, subtitles: List[Dict]) -> str:
        """构建完整上下文"""
        context_segments = []
        for i in range(0, len(subtitles), 20):
            segment = subtitles[i:i+20]
            segment_text = ' '.join([f"[{sub['start']}] {sub['text']}" for sub in segment])
            context_segments.append(segment_text)

        return '\n\n'.join(context_segments)

    def parse_ai_response(self, response: str) -> Optional[Dict]:
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

            result = json.loads(json_text)

            if 'highlight_segments' in result and 'episode_analysis' in result:
                return result
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
        return None

    def extract_episode_number(self, filename: str) -> str:
        """从文件名提取集数"""
        base_name = os.path.splitext(filename)[0]
        return base_name

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        base_name = os.path.splitext(subtitle_filename)[0]

        # 精确匹配
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for filename in os.listdir(self.video_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if base_name.lower() in filename.lower():
                    return os.path.join(self.video_folder, filename)

        return None

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def create_video_clips(self, analysis: Dict, video_file: str, subtitle_filename: str) -> List[str]:
        """创建视频片段"""
        created_clips = []

        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []

        for segment in analysis.get('highlight_segments', []):
            segment_id = segment['segment_id']
            title = segment['title']

            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}_seg{segment_id}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # 剪辑视频
            if self.create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)
                # 生成旁白文件
                self.create_narration_file(clip_path, segment)
                # 生成SRT字幕
                self.create_srt_narration(clip_path, segment)

        return created_clips

    def create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']

            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")

            # 时间转换
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0:
                print(f"   ❌ 无效时间段")
                return False

            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path,
                '-y'
            ]

            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300
            )

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"   ✅ 成功: {file_size:.1f}MB")
                return True
            else:
                error_msg = result.stderr[:100] if result.stderr else '未知错误'
                print(f"   ❌ 失败: {error_msg}")
                return False

        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def create_narration_file(self, video_path: str, segment: Dict):
        """创建旁白文件"""
        try:
            narration_path = video_path.replace('.mp4', '_旁白解说.txt')

            content = f"""🎙️ {segment['title']} - 专业旁白解说
{"=" * 60}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration_seconds', 0)} 秒
• 重要性: {segment.get('plot_significance', '重要剧情片段')}

🎙️ 专业旁白解说:
{segment.get('professional_narration', {}).get('full_script', '暂无旁白')}

💡 观看提示:
{segment.get('highlight_tip', '精彩内容值得关注')}

📝 内容摘要:
{segment.get('content_summary', '精彩剧情片段')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"   📝 旁白文件: {os.path.basename(narration_path)}")

        except Exception as e:
            print(f"   ⚠️ 旁白生成失败: {e}")

    def create_srt_narration(self, video_path: str, segment: Dict):
        """创建SRT格式旁白字幕"""
        try:
            srt_path = video_path.replace('.mp4', '_旁白字幕.srt')

            professional_narration = segment.get('professional_narration', {})
            duration = segment.get('duration_seconds', 120)

            if self.ai_config.get('enabled'):
                analyzer = AIAnalyzer()
                srt_content = analyzer.generate_srt_narration(professional_narration, duration)
            else:
                # 基础SRT生成
                srt_content = f"""1
00:00:00,000 --> 00:00:05,000
{segment.get('title', '精彩片段')}

2
00:00:05,000 --> 00:00:{min(duration, 99):02d},000
{segment.get('highlight_tip', '精彩内容正在播放')}
"""

            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)

            print(f"   🎬 SRT字幕: {os.path.basename(srt_path)}")

        except Exception as e:
            print(f"   ⚠️ SRT生成失败: {e}")

    def process_single_episode(self, subtitle_file: str) -> Optional[bool]:
        """处理单集完整流程"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False

        # 2. AI分析
        if self.ai_config.get('enabled'):
            analyzer = AIAnalyzer()
            analysis = analyzer.analyze_episode_with_fixed_format(
                subtitles,
                episode_context=f"第{self.extract_episode_number(subtitle_file)}集",
                ai_config=self.ai_config
            )
            if not analysis:
                print(f"❌ AI分析失败，跳过此集")
                return False
        else:
            analysis = None
            print(f"⚠️ AI未启用，跳过 {subtitle_file} 的AI分析")

        if analysis is None:
            print(f"⏸️ AI不可用，{subtitle_file} 已跳过")
            return None
        elif not analysis:
            print(f"❌ AI分析失败，跳过此集")
            return False

        # 3. 找到视频文件
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 4. 创建视频片段
        created_clips = self.create_video_clips(analysis, video_file, subtitle_file)

        clips_count = len(created_clips)
        print(f"✅ {subtitle_file} 处理完成: {clips_count} 个短视频")

        return clips_count > 0

    def process_all_episodes(self):
        """处理所有集数 - 主流程"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 50)

        # 检查字幕文件
        subtitle_files = [f for f in os.listdir(self.srt_folder) 
                         if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        if not subtitle_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        # 按字符串排序（即按文件名排序）
        subtitle_files.sort()

        print(f"📝 找到 {len(subtitle_files)} 个字幕文件")

        # 处理每一集
        total_success = 0
        total_clips = 0
        total_skipped = 0

        for subtitle_file in subtitle_files:
            try:
                success = self.process_single_episode(subtitle_file)
                if success:
                    total_success += 1
                elif success is None:
                    total_skipped += 1

                # 统计片段数
                episode_clips = [f for f in os.listdir(self.output_folder) 
                               if f.endswith('.mp4')]
                total_clips = len(episode_clips)

            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")

        # 最终报告
        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(subtitle_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")
        print(f"⏸️ 跳过集数: {total_skipped} 集")

    def show_file_status(self):
        """显示文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        video_files = [f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
        output_files = [f for f in os.listdir(self.output_folder) if f.endswith('.mp4')]

        print(f"\n📊 文件状态:")
        print(f"📝 字幕文件: {len(srt_files)} 个")
        if srt_files:
            for f in srt_files[:5]:
                print(f"   • {f}")
            if len(srt_files) > 5:
                print(f"   • ... 还有 {len(srt_files)-5} 个文件")

        print(f"🎬 视频文件: {len(video_files)} 个")
        if video_files:
            for f in video_files[:5]:
                print(f"   • {f}")
            if len(video_files) > 5:
                print(f"   • ... 还有 {len(video_files)-5} 个文件")

        print(f"📤 输出视频: {len(output_files)} 个")

    def show_usage_guide(self):
        """显示使用教程"""
        print("\n📖 使用教程")
        print("=" * 50)
        print("""
🎯 快速开始:
1. 将字幕文件(.srt/.txt)放在 srt/ 目录
2. 将对应视频文件(.mp4/.mkv/.avi)放在 videos/ 目录
3. 配置AI接口 (推荐GPT-4或Claude)
4. 运行智能剪辑

📁 目录结构:
项目根目录/
├── srt/              # 字幕目录
│   ├── EP01.srt
│   └── EP02.srt
├── videos/           # 视频目录
│   ├── EP01.mp4
│   └── EP02.mp4
└── clips/            # 输出目录 (自动创建)

💡 使用技巧:
• 字幕文件名决定集数顺序 (按字符串排序)
• 确保视频和字幕文件名对应
• 每集生成3-5个2-3分钟的精彩片段
        """)
        input("\n按回车键返回主菜单...")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 智能电视剧剪辑系统")
            print("=" * 60)

            # 显示当前状态
            ai_status = "🤖 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            if self.ai_config.get('enabled'):
                model = self.ai_config.get('model', '未知模型')
                provider = self.ai_config.get('provider', '未知')
                print(f"AI状态: {ai_status} ({provider} - {model})")
            else:
                print(f"AI状态: {ai_status}")

            # 检查文件状态
            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.mkv', '.avi'))])
            clips_count = len([f for f in os.listdir(self.output_folder) if f.endswith('.mp4')])

            print(f"文件状态: 📝{srt_count}个字幕 🎬{video_count}个视频 📤{clips_count}个片段")

            print("\n🎯 主要功能:")
            print("1. 🤖 配置AI接口")
            print("2. 🎬 开始智能剪辑")
            print("3. 📁 查看详细文件状态")
            print("4. 📖 查看使用教程")
            print("0. ❌ 退出系统")

            try:
                choice = input("\n请选择操作 (0-4): ").strip()

                if choice == '1':
                    self.configure_ai_interactive()
                elif choice == '2':
                    if not self.ai_config.get('enabled'):
                        print("\n⚠️ 建议先配置AI接口以获得更好的分析效果")
                        confirm = input("是否继续使用基础分析？(y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    self.process_all_episodes()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '4':
                    self.show_usage_guide()
                elif choice == '0':
                    print("\n👋 感谢使用智能电视剧剪辑系统！")
                    break
                else:
                    print("❌ 无效选择，请输入0-4")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断，程序退出")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    # 安装必要依赖
    print("🔧 检查依赖...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai'], check=False, capture_output=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-generativeai'], check=False, capture_output=True)
    except:
        pass

    clipper = IntelligentTVClipper()

    # 显示菜单
    clipper.show_main_menu()

if __name__ == "__main__":
    main()