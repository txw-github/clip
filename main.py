#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 电视剧智能剪辑系统 - 重构版
简洁统一的AI分析和视频剪辑工具
"""

import os
import re
import json
import subprocess
import hashlib
import sys
from typing import List, Dict, Optional
from datetime import datetime

class TVClipperSystem:
    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos" 
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"
        self.config_file = ".ai_config.json"

        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        print("🎬 电视剧智能剪辑系统")
        print("=" * 50)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")

        # 加载AI配置
        self.ai_config = self.load_ai_config()

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled'):
                    print(f"🤖 AI分析: 已启用 ({config.get('model', '未知模型')})")
                    return config
        except:
            pass

        print("❌ AI分析: 未配置")
        return {'enabled': False}

    def save_ai_config(self, config: Dict):
        """保存AI配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✅ AI配置已保存")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")

    def configure_ai_interactive(self) -> bool:
        """交互式AI配置"""
        print("\n🤖 AI配置向导")
        print("=" * 40)

        providers = {
            "1": {
                "name": "DeepSeek 官方",
                "api_type": "official",
                "model": "deepseek-r1"
            },
            "2": {
                "name": "Gemini 官方", 
                "api_type": "official",
                "model": "gemini-2.5-flash"
            },
            "3": {
                "name": "DeepSeek 中转",
                "api_type": "proxy",
                "base_url": "https://www.chataiapi.com/v1",
                "model": "deepseek-r1"
            },
            "4": {
                "name": "Claude 中转",
                "api_type": "proxy", 
                "base_url": "https://www.chataiapi.com/v1",
                "model": "claude-3-5-sonnet-20240620"
            },
            "5": {
                "name": "GPT-4o 中转",
                "api_type": "proxy",
                "base_url": "https://www.chataiapi.com/v1",
                "model": "gpt-4o"
            }
        }

        print("推荐的AI模型:")
        for key, config in providers.items():
            print(f"{key}. {config['name']}")

        print("0. 跳过AI配置")

        choice = input("\n请选择 (0-5): ").strip()

        if choice == '0':
            config = {'enabled': False}
            self.save_ai_config(config)
            self.ai_config = config
            return True

        if choice not in providers:
            print("❌ 无效选择")
            return False

        selected = providers[choice]
        api_key = input(f"\n输入 {selected['name']} 的API密钥: ").strip()

        if not api_key:
            print("❌ API密钥不能为空")
            return False

        # 构建配置
        config = {
            'enabled': True,
            'api_type': selected['api_type'],
            'api_key': api_key,
            'model': selected['model']
        }

        if selected['api_type'] == 'proxy':
            config['base_url'] = selected['base_url']

        # 测试连接
        if self.test_ai_connection(config):
            self.save_ai_config(config)
            self.ai_config = config
            print(f"✅ AI配置成功！")
            return True
        else:
            print("❌ 连接测试失败")
            return False

    def test_ai_connection(self, config: Dict) -> bool:
        """测试AI连接"""
        print("🔍 测试API连接...")

        try:
            if config['api_type'] == 'official':
                if 'gemini' in config['model']:
                    return self.test_gemini_official(config)
                else:
                    return self.test_deepseek_official(config)
            else:
                return self.test_proxy_api(config)
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False

    def test_gemini_official(self, config: Dict) -> bool:
        """测试Gemini官方API"""
        try:
            from google import genai
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents="hello"
            )
            print("✅ Gemini官方API连接成功")
            return True
        except ImportError:
            print("❌ 需要安装: pip install google-genai")
            return False
        except Exception as e:
            print(f"❌ Gemini测试失败: {e}")
            return False

    def test_deepseek_official(self, config: Dict) -> bool:
        """测试DeepSeek官方API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url="https://api.deepseek.com/v1"
            )
            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10
            )
            print("✅ DeepSeek官方API连接成功")
            return True
        except Exception as e:
            print(f"❌ DeepSeek测试失败: {e}")
            return False

    def test_proxy_api(self, config: Dict) -> bool:
        """测试中转API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10
            )
            print("✅ 中转API连接成功")
            return True
        except Exception as e:
            print(f"❌ 中转API测试失败: {e}")
            return False

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用AI API"""
        if not self.ai_config.get('enabled'):
            return None

        try:
            if self.ai_config['api_type'] == 'official':
                if 'gemini' in self.ai_config['model']:
                    return self.call_gemini_official(prompt, system_prompt)
                else:
                    return self.call_deepseek_official(prompt, system_prompt)
            else:
                return self.call_proxy_api(prompt, system_prompt)
        except Exception as e:
            print(f"⚠️ AI API调用失败: {e}")
            return None

    def call_gemini_official(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai
            client = genai.Client(api_key=self.ai_config['api_key'])
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.ai_config['model'],
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini API失败: {e}")
            return None

    def call_deepseek_official(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用DeepSeek官方API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.ai_config['api_key'],
                base_url="https://api.deepseek.com/v1"
            )
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            completion = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ DeepSeek API失败: {e}")
            return None

    def call_proxy_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用中转API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.ai_config['api_key'],
                base_url=self.ai_config['base_url']
            )
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            completion = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ 中转API失败: {e}")
            return None

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 读取文件内容
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

    def analyze_episode_with_ai(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """AI分析单集"""
        if not self.ai_config.get('enabled'):
            print("⏸️ AI未启用，跳过智能分析")
            return None

        # 检查缓存
        cache_key = self.get_analysis_cache_key(subtitles)
        cached_analysis = self.load_analysis_cache(cache_key, filename)
        if cached_analysis:
            return cached_analysis

        episode_num = self.extract_episode_number(filename)

        # 构建分析内容（取前80%避免剧透）
        sample_size = int(len(subtitles) * 0.8)
        context_parts = []
        for i in range(0, sample_size, 50):
            segment = subtitles[i:i+50]
            segment_text = ' '.join([sub['text'] for sub in segment])
            context_parts.append(segment_text)
        full_context = '\n\n'.join(context_parts)

        print(f"🤖 AI分析第{episode_num}集...")

        prompt = f"""# 电视剧智能分析与精彩剪辑

请为 **第{episode_num}集** 进行智能分析。

## 当前集内容
```
{full_context}
```

## 分析要求
1. 智能识别3-5个最精彩的片段
2. 每个片段2-3分钟，包含完整对话
3. 确保片段间逻辑连贯
4. 生成专业旁白解说

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
            "professional_narration": "完整的专业旁白解说稿"
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
                    self.save_analysis_cache(cache_key, filename, parsed_result)
                    return parsed_result
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return None

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
        """从文件名提取集数，使用字符串排序"""
        base_name = os.path.splitext(filename)[0]
        return base_name

    def get_analysis_cache_key(self, subtitles: List[Dict]) -> str:
        """生成分析缓存键"""
        content = json.dumps(subtitles, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def load_analysis_cache(self, cache_key: str, filename: str) -> Optional[Dict]:
        """加载分析缓存"""
        cache_file = os.path.join(self.cache_folder, f"{filename}_{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                    print(f"💾 使用缓存分析: {filename}")
                    return analysis
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
        return None

    def save_analysis_cache(self, cache_key: str, filename: str, analysis: Dict):
        """保存分析缓存"""
        cache_file = os.path.join(self.cache_folder, f"{filename}_{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"💾 保存分析缓存: {filename}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

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
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
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

            # 添加缓冲确保对话完整
            buffer_start = max(0, start_seconds - 3)
            buffer_duration = duration + 6

            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"   ✅ 成功: {file_size:.1f}MB")
                return True
            else:
                print(f"   ❌ 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
                return False

        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def create_narration_file(self, video_path: str, segment: Dict):
        """创建专业旁白解说文件"""
        try:
            narration_path = video_path.replace('.mp4', '_旁白解说.txt')

            content = f"""📺 {segment['title']} - 专业旁白解说
{"=" * 60}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration_seconds', 0)} 秒
• 剧情意义: {segment.get('plot_significance', '关键剧情节点')}

🎙️ 专业旁白解说稿:
{segment.get('professional_narration', '精彩剧情片段')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"   📜 生成旁白解说: {os.path.basename(narration_path)}")

        except Exception as e:
            print(f"   ⚠️ 旁白文件生成失败: {e}")

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
        analysis = self.analyze_episode_with_ai(subtitles, subtitle_file)
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

    def install_dependencies(self):
        """安装必要依赖"""
        print("🔧 检查并安装必要依赖...")

        dependencies = ['openai', 'google-genai']

        for package in dependencies:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} 已安装")
            except ImportError:
                print(f"📦 安装 {package}...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"✅ {package} 安装成功")
                except Exception as e:
                    print(f"❌ {package} 安装失败: {e}")

    def clear_cache(self):
        """清空分析缓存"""
        import shutil
        if os.path.exists(self.cache_folder):
            shutil.rmtree(self.cache_folder)
            os.makedirs(self.cache_folder)
            print(f"✅ 已清空分析缓存")
        else:
            print(f"📝 缓存目录不存在")

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

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 50)
            print("🎬 电视剧智能剪辑系统")
            print("=" * 50)

            # 显示状态
            ai_status = "🤖 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"AI状态: {ai_status}")

            print("\n🎯 主要功能:")
            print("1. 🤖 配置AI接口")
            print("2. 🎬 开始智能剪辑")
            print("3. 📁 查看文件状态")
            print("4. 🔧 安装系统依赖")
            print("5. 🔄 清空分析缓存")
            print("0. ❌ 退出系统")

            try:
                choice = input("\n请选择操作 (0-5): ").strip()

                if choice == '1':
                    self.configure_ai_interactive()
                elif choice == '2':
                    self.process_all_episodes()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '4':
                    self.install_dependencies()
                elif choice == '5':
                    self.clear_cache()
                elif choice == '0':
                    print("\n👋 感谢使用电视剧智能剪辑系统！")
                    break
                else:
                    print("❌ 无效选择，请输入0-5")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")

def main():
    """主函数"""
    try:
        system = TVClipperSystem()

        print("\n🎉 欢迎使用电视剧智能剪辑系统！")
        print("💡 功能特点：")
        print("   • 官方API和中转API支持")
        print("   • 智能分析剧情内容")
        print("   • 自动剪辑精彩片段")
        print("   • 生成专业旁白解说")

        system.show_main_menu()

    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 系统错误: {e}")

if __name__ == "__main__":
    main()