
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能AI电视剧剪辑系统 - 主程序
解决所有15个核心问题的完整解决方案
"""

import os
import re
import json
import hashlib
import subprocess
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class EnhancedNarrationGenerator:
    """增强版旁白生成器"""
    
    def __init__(self, ai_config: Dict):
        self.ai_config = ai_config

    def create_subtitle_filters(self, narration: Dict, video_duration: float) -> List[str]:
        """创建字幕滤镜"""
        filters = []
        
        # 主要解说（前1/3时间）
        main_text = self.clean_text_for_ffmpeg(narration.get('main_explanation', ''))[:50]
        if main_text:
            filters.append(
                f"drawtext=text='{main_text}':fontsize=20:fontcolor=white:"
                f"x=(w-text_w)/2:y=(h-100):box=1:boxcolor=black@0.7:boxborderw=3:"
                f"enable='between(t,2,{video_duration/3})'"
            )
        
        # 亮点提示（后1/3时间）
        highlight_text = self.clean_text_for_ffmpeg(narration.get('highlight_tip', ''))[:40]
        if highlight_text:
            filters.append(
                f"drawtext=text='💡 {highlight_text}':fontsize=18:fontcolor=yellow:"
                f"x=(w-text_w)/2:y=(h-60):box=1:boxcolor=black@0.6:boxborderw=2:"
                f"enable='between(t,{video_duration*2/3},{video_duration-1})'"
            )
        
        return filters

    def clean_text_for_ffmpeg(self, text: str) -> str:
        """清理文本用于FFmpeg"""
        return text.replace("'", "").replace('"', '').replace(':', '-').replace('\n', ' ')

    def export_narration_text(self, narration: Dict, video_path: str):
        """导出旁白文本文件"""
        narration_path = video_path.replace('.mp4', '_旁白.txt')
        
        content = f"""🎙️ 视频旁白解说
{"=" * 40}

📝 主要解说:
{narration.get('main_explanation', '精彩片段解说')}

💡 亮点提示:
{narration.get('highlight_tip', '关键看点')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        try:
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"⚠️ 旁白文件保存失败: {e}")

class PlatformFix:
    """平台兼容性修复"""
    
    @staticmethod
    def safe_file_read(filepath: str) -> Optional[str]:
        """安全文件读取"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    @staticmethod
    def safe_file_write(filepath: str, content: str) -> bool:
        """安全文件写入"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False

    @staticmethod
    def safe_subprocess_run(cmd, **kwargs):
        """安全子进程运行"""
        try:
            return subprocess.run(cmd, **kwargs)
        except Exception as e:
            print(f"⚠️ 命令执行失败: {e}")
            return subprocess.CompletedProcess(cmd, 1, "", str(e))

platform_fix = PlatformFix()

class IntelligentTVClipper:
    """智能电视剧剪辑系统"""
    
    def __init__(self):
        # 标准目录结构 - 解决问题6
        self.srt_folder = "srt"
        self.video_folder = "videos"
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"
        
        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置 - 解决问题1
        self.ai_config = self.load_ai_config()
        
        print("🚀 智能AI电视剧剪辑系统已初始化")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")

    def load_ai_config(self) -> Dict:
        """加载AI配置 - 解决问题1：支持官方和中转API"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        api_type = config.get('api_type', 'proxy')
                        provider = config.get('provider', 'unknown')
                        print(f"🤖 AI分析已启用: {provider} ({api_type})")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")
        
        print("📝 AI分析未启用，使用基础规则分析")
        return {'enabled': False}

    def configure_ai_interactive(self):
        """交互式AI配置"""
        print("\n🤖 AI接口配置")
        print("=" * 40)
        
        # 选择API类型
        print("请选择API类型:")
        print("1. 官方API (Google Gemini, OpenAI等)")
        print("2. 中转API (支持多种模型)")
        
        choice = input("请选择 (1-2): ").strip()
        
        if choice == '1':
            self.configure_official_api()
        elif choice == '2':
            self.configure_proxy_api()
        else:
            print("❌ 无效选择")

    def configure_official_api(self):
        """配置官方API"""
        print("\n📝 官方API配置")
        
        provider = input("请输入提供商 (gemini/openai): ").strip().lower()
        api_key = input("请输入API密钥: ").strip()
        
        if not api_key:
            print("❌ API密钥不能为空")
            return
        
        if provider == 'gemini':
            model = input("请输入模型名称 (默认: gemini-2.0-flash-exp): ").strip() or "gemini-2.0-flash-exp"
        else:
            model = input("请输入模型名称 (默认: gpt-4): ").strip() or "gpt-4"
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': provider,
            'api_key': api_key,
            'model': model
        }
        
        if self.save_ai_config(config):
            self.ai_config = config
            print(f"✅ 官方API配置成功: {provider}")

    def configure_proxy_api(self):
        """配置中转API"""
        print("\n🔄 中转API配置")
        
        base_url = input("请输入API地址 (如: https://www.chataiapi.com/v1): ").strip()
        api_key = input("请输入API密钥: ").strip()
        model = input("请输入模型名称 (如: deepseek-r1): ").strip()
        
        if not all([base_url, api_key, model]):
            print("❌ 所有字段都不能为空")
            return
        
        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'proxy',
            'api_key': api_key,
            'base_url': base_url,
            'model': model
        }
        
        if self.save_ai_config(config):
            self.ai_config = config
            print(f"✅ 中转API配置成功")

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
        """统一AI API调用 - 解决问题1"""
        if not self.ai_config.get('enabled'):
            return None
        
        try:
            api_type = self.ai_config.get('api_type', 'proxy')
            
            if api_type == 'official':
                return self.call_official_api(prompt, system_prompt)
            else:
                return self.call_proxy_api(prompt, system_prompt)
                
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def call_official_api(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用官方API"""
        provider = self.ai_config.get('provider', '')
        
        if provider == 'gemini':
            return self.call_gemini_api(prompt, system_prompt)
        elif provider == 'openai':
            return self.call_openai_official_api(prompt, system_prompt)
        else:
            print(f"⚠️ 不支持的官方API提供商: {provider}")
            return None

    def call_gemini_api(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用Google Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.ai_config['api_key'])
            model = genai.GenerativeModel(self.ai_config.get('model', 'gemini-2.0-flash-exp'))
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"⚠️ Gemini API调用失败: {e}")
            return None

    def call_openai_official_api(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用OpenAI官方API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.ai_config['api_key'])
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.ai_config.get('model', 'gpt-4'),
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ OpenAI API调用失败: {e}")
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
        """使用AI分析整集 - 解决问题2,3,8：整集分析避免割裂"""
        # 检查缓存 - 解决问题12
        cache_key = self.get_analysis_cache_key(subtitles)
        cached_analysis = self.load_analysis_cache(cache_key, filename)
        if cached_analysis:
            return cached_analysis
        
        if not self.ai_config.get('enabled'):
            print(f"⚠️ AI未启用，跳过 {filename}")
            return None
        
        # 构建完整上下文 - 解决问题2,3
        full_context = self.build_complete_context(subtitles)
        episode_num = self.extract_episode_number(filename)
        
        prompt = f"""你是专业的电视剧剪辑师，请分析第{episode_num}集的完整内容，找出3-5个最精彩的片段制作短视频。

【完整剧情内容】
{full_context}

## 分析要求
1. 智能识别3-5个最精彩的片段
2. 每个片段2-3分钟，包含完整对话
3. 确保片段间逻辑连贯
4. 生成专业旁白解说和字幕提示

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
                    self.save_analysis_cache(cache_key, filename, parsed_result)
                    return parsed_result
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return None

    def build_complete_context(self, subtitles: List[Dict]) -> str:
        """构建完整上下文 - 解决问题2"""
        # 每20条字幕合并成一段，保持上下文
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
                cache_content = platform_fix.safe_file_read(cache_file)
                if cache_content:
                    analysis = json.loads(cache_content)
                    print(f"💾 使用缓存分析: {filename}")
                    return analysis
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
        return None

    def save_analysis_cache(self, cache_key: str, filename: str, analysis: Dict):
        """保存分析缓存"""
        cache_file = os.path.join(self.cache_folder, f"{filename}_{cache_key}.json")
        try:
            cache_content = json.dumps(analysis, ensure_ascii=False, indent=2)
            platform_fix.safe_file_write(cache_file, cache_content)
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
            result = platform_fix.safe_subprocess_run(
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

        # 获取完整字幕数据用于详细解释
        subtitle_path = os.path.join(self.srt_folder, subtitle_filename)
        all_subtitles = self.parse_subtitle_file(subtitle_path)

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
            temp_clip_path = clip_path.replace(".mp4", "_temp.mp4")
            if self.create_single_clip(video_file, segment, temp_clip_path):
                # 添加精彩字幕提示
                if self.add_highlight_subtitles(temp_clip_path, segment, clip_path):
                    created_clips.append(clip_path)
                else:
                    # 如果添加字幕失败，则保留原始剪辑
                    created_clips.append(temp_clip_path)
                    os.rename(temp_clip_path, clip_path)  # 重命名为最终文件名

                # 删除临时文件
                if os.path.exists(temp_clip_path):
                    os.remove(temp_clip_path)

            # 生成详细的SRT解释文件（独立文件）
            self.create_detailed_srt_explanation(clip_path, segment, all_subtitles)
            
            # 生成旁白文件（附加字幕形式）
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

            result = platform_fix.safe_subprocess_run(
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

    def add_highlight_subtitles(self, video_path: str, segment: Dict, output_path: str) -> bool:
        """为视频添加精彩字幕提示"""
        try:
            print(f"   💡 添加精彩字幕提示...")

            # 生成精彩提示内容
            highlights = self.generate_highlight_tips(segment)

            if not highlights:
                print(f"   ⚠️ 无法生成字幕提示")
                return False

            # 获取视频时长
            video_duration = segment.get('duration_seconds', 180)

            # 构建字幕滤镜
            subtitle_filters = []

            # 1. 主标题（开头3秒）
            title = segment.get('title', '精彩片段')[:25]
            title_clean = self.clean_text_for_ffmpeg(title)
            subtitle_filters.append(
                f"drawtext=text='{title_clean}':fontsize=24:fontcolor=white:"
                f"x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.8:boxborderw=3:"
                f"enable='between(t,0,3)'"
            )

            # 2. 精彩提示1（3-8秒）
            tip1 = self.clean_text_for_ffmpeg(highlights.get('tip1', ''))
            if tip1:
                subtitle_filters.append(
                    f"drawtext=text='💡 {tip1}':fontsize=18:fontcolor=yellow:"
                    f"x=(w-text_w)/2:y=(h-80):box=1:boxcolor=black@0.7:boxborderw=2:"
                    f"enable='between(t,3,8)'"
                )

            # 3. 精彩提示2（最后3秒）
            tip2 = self.clean_text_for_ffmpeg(highlights.get('tip2', ''))
            if tip2 and video_duration > 8:
                start_time = max(8, video_duration - 3)
                subtitle_filters.append(
                    f"drawtext=text='🔥 {tip2}':fontsize=18:fontcolor=lightblue:"
                    f"x=(w-text_w)/2:y=(h-40):box=1:boxcolor=black@0.6:boxborderw=2:"
                    f"enable='gte(t,{start_time})'"
                )

            if not subtitle_filters:
                print(f"   ⚠️ 没有有效的字幕内容")
                return False

            # 合并所有滤镜
            filter_complex = ",".join(subtitle_filters)

            # FFmpeg命令添加字幕
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_complex,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                output_path,
                '-y'
            ]

            result = platform_fix.safe_subprocess_run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )

            success = result.returncode == 0 and os.path.exists(output_path)
            if success:
                print(f"   ✅ 精彩字幕提示添加成功")
            else:
                error_msg = result.stderr[:100] if result.stderr else '未知错误'
                print(f"   ⚠️ 字幕添加失败: {error_msg}")

            return success

        except Exception as e:
            print(f"   ⚠️ 字幕处理异常: {e}")
            return False

    def generate_highlight_tips(self, segment: Dict) -> Dict:
        """生成精彩提示内容"""
        try:
            title = segment.get('title', '')
            significance = segment.get('plot_significance', '')
            narration = segment.get('professional_narration', '')
            
            # 基于内容智能生成提示
            tips = {'tip1': '', 'tip2': ''}
            
            # 提示1：基于剧情意义
            if '申诉' in significance:
                tips['tip1'] = '申诉程序启动'
            elif '听证会' in significance:
                tips['tip1'] = '法庭激烈辩论'
            elif '证据' in significance:
                tips['tip1'] = '关键证据出现'
            elif '真相' in significance:
                tips['tip1'] = '真相即将揭露'
            elif '冲突' in significance:
                tips['tip1'] = '矛盾达到高点'
            else:
                tips['tip1'] = '关键剧情节点'
            
            # 提示2：基于标题或旁白内容
            if '四二八' in title or '四二八' in narration:
                tips['tip2'] = '四二八案关键进展'
            elif '628' in title or '628' in narration:
                tips['tip2'] = '628旧案线索'
            elif '正当防卫' in narration:
                tips['tip2'] = '正当防卫争议'
            elif '法官' in narration or '检察官' in narration:
                tips['tip2'] = '法庭精彩对话'
            elif '父女' in narration or '亲情' in narration:
                tips['tip2'] = '动人情感时刻'
            else:
                tips['tip2'] = '精彩内容值得关注'
            
            return tips
            
        except Exception as e:
            print(f"⚠️ 生成精彩提示失败: {e}")
            return {'tip1': '精彩片段', 'tip2': '值得关注'}

    def create_detailed_srt_explanation(self, video_path: str, segment: Dict, subtitles: List[Dict]):
        """创建详细的SRT解释文件（独立文件，不嵌入视频）"""
        try:
            srt_explanation_path = video_path.replace('.mp4', '_SRT详细解释.txt')
            
            # 获取片段对应的字幕
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            segment_subtitles = []
            for sub in subtitles:
                sub_start = self.time_to_seconds(sub['start'])
                segment_start = self.time_to_seconds(start_time)
                segment_end = self.time_to_seconds(end_time)
                
                if segment_start <= sub_start <= segment_end:
                    segment_subtitles.append(sub)
            
            content = f"""📝 {segment['title']} - SRT字幕详细解释
{"=" * 80}

⏰ 片段时间: {start_time} --> {end_time}
📺 剧情意义: {segment.get('plot_significance', '关键剧情节点')}

📖 逐句字幕解释:
{"=" * 40}

"""
            
            for i, sub in enumerate(segment_subtitles, 1):
                content += f"{i:2d}. [{sub['start']} --> {sub['end']}]\n"
                content += f"    台词: {sub['text']}\n"
                
                # 智能分析每句台词的重要性
                analysis = self.analyze_dialogue_significance(sub['text'], segment)
                if analysis:
                    content += f"    解释: {analysis}\n"
                content += "\n"
            
            # 添加整体解读
            content += f"""
📊 片段整体解读:
{"=" * 40}
• 核心看点: {segment.get('professional_narration', '精彩剧情发展')}
• 情感基调: {self.analyze_emotional_tone_from_text(segment.get('professional_narration', ''))}
• 剧情价值: 该片段展现了{segment.get('plot_significance', '重要剧情转折')}
• 观众体验: 通过这个片段，观众可以深入理解角色心理和故事发展

💡 通俗易懂说明:
简单来说，这个片段就是{self.generate_simple_explanation(segment)}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            platform_fix.safe_file_write(srt_explanation_path, content)
            print(f"   📝 生成SRT详细解释: {os.path.basename(srt_explanation_path)}")
            
        except Exception as e:
            print(f"   ⚠️ SRT解释文件生成失败: {e}")

    def create_narration_file(self, video_path: str, segment: Dict):
        """创建专业旁白解说文件（附加字幕形式）"""
        try:
            narration_path = video_path.replace('.mp4', '_旁白解说.txt')

            # 生成多层次旁白内容
            narration_content = self.generate_layered_narration(segment)

            content = f"""🎙️ {segment['title']} - 专业旁白解说
{"=" * 60}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration_seconds', 0)} 秒
• 剧情意义: {segment.get('plot_significance', '关键剧情节点')}

📺 旁白内容（附加字幕形式）:
{"=" * 40}

🎤 开场解说 (0-3秒):
{narration_content['opening']}

🎤 过程解说 (3-8秒):
{narration_content['process']}

🎤 精彩提示 (最后3秒):
{narration_content['highlight']}

🎤 简短字幕提示:
• 亮点1: {narration_content['tip1']}
• 亮点2: {narration_content['tip2']}

💬 完整旁白稿:
{narration_content['full_script']}

🎯 使用说明:
这些旁白内容设计为"附加字幕"，可以在视频播放时以字幕形式出现，
为观众提供额外的解释和提示，增强观看体验。

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            platform_fix.safe_file_write(narration_path, content)

            print(f"   📜 生成旁白解说: {os.path.basename(narration_path)}")

        except Exception as e:
            print(f"   ⚠️ 旁白文件生成失败: {e}")

    def analyze_dialogue_significance(self, dialogue: str, segment: Dict) -> str:
        """分析单句台词的重要性"""
        if not dialogue or len(dialogue.strip()) < 3:
            return ""
        
        # 检查是否包含关键信息
        key_indicators = {
            '案件': '涉及案件关键信息',
            '证据': '重要证据相关',
            '真相': '真相揭露时刻',
            '法庭': '法庭程序进展',
            '申诉': '申诉程序关键',
            '听证会': '听证会重要内容',
            '正当防卫': '正当防卫争议焦点',
            '四二八': '四二八案核心内容',
            '628': '628旧案相关',
            '决定': '重要决策时刻',
            '发现': '新发现或线索',
            '问题': '关键问题提出',
            '怎么': '疑问或质疑',
            '为什么': '原因探究',
            '不是': '否定或反驳',
            '但是': '转折或对比',
            '如果': '假设或推理'
        }
        
        for keyword, explanation in key_indicators.items():
            if keyword in dialogue:
                return f"{explanation} - 这句话点出了{keyword}相关的重要信息"
        
        # 情感分析
        if any(word in dialogue for word in ['愤怒', '生气', '激动', '着急']):
            return "情感激烈 - 角色情绪达到高点，推动剧情发展"
        elif any(word in dialogue for word in ['担心', '害怕', '紧张']):
            return "情感紧张 - 营造紧张氛围，增强戏剧效果"
        elif any(word in dialogue for word in ['感动', '温暖', '理解']):
            return "情感温暖 - 展现人物情感深度和关系变化"
        
        # 对话功能分析
        if '？' in dialogue or '吗' in dialogue:
            return "疑问句 - 推进对话发展，引出重要信息"
        elif '！' in dialogue:
            return "感叹句 - 表达强烈情感，增强戏剧张力"
        elif len(dialogue) > 20:
            return "详细表述 - 包含重要信息或复杂情感表达"
        
        return "推进对话 - 维持剧情连贯性和角色互动"

    def analyze_emotional_tone_from_text(self, text: str) -> str:
        """从文本分析情感基调"""
        if not text:
            return "中性"
        
        positive_words = ['温暖', '感动', '希望', '开心', '高兴', '快乐', '幸福']
        negative_words = ['痛苦', '悲伤', '愤怒', '绝望', '难过', '沮丧', '失望']
        tense_words = ['紧张', '危险', '冲突', '争论', '激烈', '急迫', '关键']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        tense_count = sum(1 for word in tense_words if word in text)
        
        if tense_count > max(positive_count, negative_count):
            return "紧张激烈"
        elif positive_count > negative_count:
            return "积极温暖"
        elif negative_count > positive_count:
            return "沉重压抑"
        else:
            return "平稳推进"

    def generate_simple_explanation(self, segment: Dict) -> str:
        """生成通俗易懂的解释"""
        title = segment.get('title', '')
        significance = segment.get('plot_significance', '')
        
        # 根据内容生成简单解释
        if '申诉' in title or '申诉' in significance:
            return "当事人开始为案件重新申请审理，希望能翻案"
        elif '听证会' in title or '听证会' in significance:
            return "法官听取各方意见，决定是否重新审理案件"
        elif '证据' in title or '证据' in significance:
            return "发现了新的重要证据，可能改变案件结果"
        elif '真相' in title or '真相' in significance:
            return "事情的真实情况开始浮现，之前的判断可能有误"
        elif '冲突' in significance or '争论' in significance:
            return "不同观点发生激烈碰撞，矛盾达到高点"
        elif '情感' in significance:
            return "角色的内心情感得到深度展现，触动人心"
        else:
            return "剧情出现重要发展，值得观众重点关注"

    def generate_layered_narration(self, segment: Dict) -> Dict:
        """生成多层次旁白内容"""
        title = segment.get('title', '精彩片段')
        significance = segment.get('plot_significance', '')
        professional_narration = segment.get('professional_narration', '')
        
        # 开场解说
        opening = f"接下来的片段展现了{title.split('：')[-1] if '：' in title else title}"
        
        # 过程解说
        if '申诉' in significance:
            process = "我们看到当事人正式启动法律程序，为案件寻求新的审理机会"
        elif '听证会' in significance:
            process = "法庭上各方激烈辩论，每一个细节都可能影响最终结果"
        elif '证据' in significance:
            process = "关键证据的出现，让案件出现了新的转机"
        elif '真相' in significance:
            process = "隐藏的真相逐渐浮出水面，事情的本质开始清晰"
        else:
            process = "剧情发展到关键节点，角色面临重要选择"
        
        # 精彩提示
        if '法律' in significance or '案件' in significance:
            highlight = "💡 法律智慧：注意观察法理与人情的博弈"
        elif '情感' in significance:
            highlight = "💡 情感共鸣：感受角色内心的复杂情感"
        elif '冲突' in significance:
            highlight = "💡 戏剧张力：观察矛盾如何推向高潮"
        else:
            highlight = "💡 剧情关键：这里的细节很重要，值得仔细观看"
        
        # 简短字幕提示
        tip1 = "关键看点"
        tip2 = "精彩时刻"
        
        if '证据' in significance:
            tip1 = "新证据出现"
            tip2 = "案件转机"
        elif '听证会' in significance:
            tip1 = "法庭辩论"
            tip2 = "关键争议"
        elif '申诉' in significance:
            tip1 = "申诉启动"
            tip2 = "希望重燃"
        
        # 完整旁白稿
        full_script = f"{opening}。{process}。{highlight}"
        
        return {
            'opening': opening,
            'process': process,
            'highlight': highlight,
            'tip1': tip1,
            'tip2': tip2,
            'full_script': full_script
        }

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
                    result = platform_fix.safe_subprocess_run(
                        [sys.executable, '-m', 'pip', 'install', package],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ {package} 安装成功")
                    else:
                        print(f"❌ {package} 安装失败: {result.stderr}")
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

    def generate_segment_narration(self, segment: Dict) -> Dict:
        """生成片段旁白内容"""
        if not self.ai_config.get('enabled'):
            return {}

        try:
            title = segment.get('title', '精彩片段')
            plot_significance = segment.get('plot_significance', '关键剧情节点')
            professional_narration = segment.get('professional_narration', '精彩剧情片段')
            highlight_tip = segment.get('highlight_tip', '一句话亮点')

            prompt = f"""# 旁白内容生成

请为以下电视剧片段生成更专业的旁白内容：

## 片段信息
• 标题: {title}
• 剧情意义: {plot_significance}
• 解说稿: {professional_narration}
• 亮点提示: {highlight_tip}

## 生成要求
1. 主题解说：概括片段核心看点，1-2句话
2. 字幕亮点：生成吸引眼球的字幕亮点提示，1句话

请严格按照以下JSON格式输出：

```json
{{
    "main_explanation": "片段核心看点",
    "highlight_tip": "吸引眼球的字幕亮点提示"
}}
```"""

            system_prompt = "你是专业的影视内容创作专家，专长电视剧情深度解说与叙事吸引。"

            response = self.call_ai_api(prompt, system_prompt)
            if response:
                narration = self.parse_narration_response(response)
                return narration

        except Exception as e:
            print(f"⚠️ 旁白生成失败: {e}")
            return {}

    def parse_narration_response(self, response: str) -> Dict:
        """解析旁白生成响应"""
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
            return result

        except Exception as e:
            print(f"⚠️ 旁白解析失败: {e}")
            return {}

    def clean_text_for_ffmpeg(self, text: str) -> str:
        """清理文本用于FFmpeg"""
        return text.replace("'", "").replace('"', '').replace(':', '-').replace('\n', ' ')

def main():
    """主函数"""
    import sys
    
    clipper = IntelligentTVClipper()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--menu':
        clipper.show_main_menu()
    else:
        clipper.process_all_episodes()

if __name__ == "__main__":
    main()
