
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能电视剧剪辑系统 - 全新重构版本
完全AI驱动的智能分析和剪辑系统
"""

import os
import re
import json
import hashlib
import subprocess
import sys
from typing import List, Dict, Optional
from datetime import datetime

class IntelligentTVClipper:
    """智能电视剧剪辑系统"""

    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.clips_folder = "clips"
        self.cache_folder = "cache"
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        print("🚀 智能电视剧剪辑系统已启动")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.videos_folder}/")
        print(f"📤 输出目录: {self.clips_folder}/")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        print(f"🤖 AI已配置: {config.get('provider', 'unknown')}")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")
        
        print("📝 AI未配置，将使用基础分析")
        return {'enabled': False}

    def configure_ai(self):
        """配置AI接口"""
        print("\n🤖 AI配置向导")
        print("=" * 40)
        
        print("选择AI服务类型:")
        print("1. 官方API (Gemini)")
        print("2. 中转API (ChatAI, OpenRouter等)")
        print("0. 跳过配置")
        
        choice = input("请选择 (0-2): ").strip()
        
        if choice == '1':
            self.configure_official_api()
        elif choice == '2':
            self.configure_proxy_api()
        else:
            print("⚠️ 跳过AI配置")

    def configure_official_api(self):
        """配置官方API"""
        print("\n🔒 官方API配置")
        print("目前支持: Google Gemini")
        
        api_key = input("请输入Gemini API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return
        
        model = input("模型名称 (默认: gemini-2.5-flash): ").strip() or 'gemini-2.5-flash'
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }
        
        # 测试连接
        if self.test_gemini_connection(config):
            self.save_ai_config(config)
            self.ai_config = config
            print("✅ Gemini配置成功")
        else:
            print("❌ 连接测试失败")

    def configure_proxy_api(self):
        """配置中转API"""
        print("\n🌐 中转API配置")
        
        base_url = input("API地址 (如: https://www.chataiapi.com/v1): ").strip()
        api_key = input("API密钥: ").strip()
        model = input("模型名称 (如: deepseek-r1): ").strip()
        
        if not all([base_url, api_key, model]):
            print("❌ 所有字段都必须填写")
            return
        
        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'proxy',
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }
        
        # 测试连接
        if self.test_proxy_connection(config):
            self.save_ai_config(config)
            self.ai_config = config
            print("✅ 中转API配置成功")
        else:
            print("❌ 连接测试失败")

    def test_gemini_connection(self, config: Dict) -> bool:
        """测试Gemini连接"""
        try:
            from google import genai
            
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents="测试连接"
            )
            return bool(response.text)
        except ImportError:
            print("❌ 需要安装: pip install google-genai")
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def test_proxy_connection(self, config: Dict) -> bool:
        """测试中转API连接"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试连接'}],
                max_tokens=10
            )
            
            return bool(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def save_ai_config(self, config: Dict):
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ 配置已保存")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用"""
        if not self.ai_config.get('enabled'):
            return None
        
        try:
            if self.ai_config.get('api_type') == 'official':
                return self.call_official_api(prompt, system_prompt)
            else:
                return self.call_proxy_api(prompt, system_prompt)
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None

    def call_official_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用官方API"""
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
            print(f"❌ Gemini API调用失败: {e}")
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
            
            response = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ 中转API调用失败: {e}")
            return None

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")
        
        # 尝试多种编码
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

    def get_cache_key(self, filename: str) -> str:
        """生成缓存键"""
        return hashlib.md5(filename.encode()).hexdigest()[:12]

    def load_analysis_cache(self, filename: str) -> Optional[Dict]:
        """加载分析缓存"""
        cache_key = self.get_cache_key(filename)
        cache_file = os.path.join(self.cache_folder, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save_analysis_cache(self, filename: str, analysis: Dict):
        """保存分析缓存"""
        cache_key = self.get_cache_key(filename)
        cache_file = os.path.join(self.cache_folder, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def extract_episode_number(self, filename: str) -> str:
        """从文件名提取集数"""
        # 直接使用SRT文件名作为集数标识
        return os.path.splitext(filename)[0]

    def ai_analyze_episode(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """AI分析整集"""
        if not self.ai_config.get('enabled'):
            print(f"⚠️ AI未启用，跳过分析: {filename}")
            return None
        
        # 检查缓存
        cached_analysis = self.load_analysis_cache(filename)
        if cached_analysis:
            print(f"💾 使用缓存分析: {filename}")
            return cached_analysis
        
        # 构建完整上下文
        episode_num = self.extract_episode_number(filename)
        full_context = self.build_context(subtitles)
        
        prompt = f"""你是专业的电视剧剪辑师，分析第{episode_num}集内容，找出3-5个最精彩的2-3分钟片段。

【字幕内容】
{full_context}

请严格按JSON格式输出：
{{
    "episode_info": {{
        "episode_number": "{episode_num}",
        "genre": "剧情类型",
        "theme": "核心主题"
    }},
    "segments": [
        {{
            "id": 1,
            "title": "片段标题",
            "start_time": "00:XX:XX,XXX",
            "end_time": "00:XX:XX,XXX",
            "duration": 120,
            "description": "内容描述",
            "narration": "专业解说词",
            "highlight": "观看提示"
        }}
    ]
}}

要求：
- 时间必须从字幕中选择真实存在的时间点
- 每个片段2-3分钟
- 解说词要生动有趣"""

        system_prompt = "你是专业的影视剪辑师，擅长识别精彩片段。请严格按JSON格式输出。"
        
        try:
            response = self.call_ai_api(prompt, system_prompt)
            if response:
                analysis = self.parse_ai_response(response)
                if analysis:
                    # 保存缓存
                    self.save_analysis_cache(filename, analysis)
                    print(f"✅ AI分析成功: {len(analysis.get('segments', []))} 个片段")
                    return analysis
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")
        
        return None

    def build_context(self, subtitles: List[Dict]) -> str:
        """构建上下文"""
        context_parts = []
        for i in range(0, len(subtitles), 30):
            segment = subtitles[i:i+30]
            segment_text = '\n'.join([f"[{sub['start']}] {sub['text']}" for sub in segment])
            context_parts.append(segment_text)
        
        return '\n\n=== 场景分割 ===\n\n'.join(context_parts)

    def parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_text = response[start:end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]
            
            result = json.loads(json_text)
            
            if 'segments' in result and 'episode_info' in result:
                return result
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
        
        return None

    def find_video_file(self, srt_filename: str) -> Optional[str]:
        """查找对应的视频文件"""
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if base_name.lower() in filename.lower():
                    return os.path.join(self.videos_folder, filename)
        
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
        """检查FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def create_video_clips(self, analysis: Dict, video_file: str, srt_filename: str) -> List[str]:
        """创建视频片段"""
        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []
        
        created_clips = []
        
        for segment in analysis.get('segments', []):
            segment_id = segment.get('id', 1)
            title = segment.get('title', '精彩片段')
            episode_name = self.extract_episode_number(srt_filename)
            
            # 生成更安全的文件名，避免特殊字符
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', title)
            safe_title = safe_title.replace('__', '_').strip('_')
            
            # 限制文件名长度
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            clip_filename = f"{episode_name}_{safe_title}_seg{segment_id}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)
            
            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                
                # 创建缺失的旁白文件
                self.create_narration_files(clip_path, segment)
                continue
            
            # 剪辑视频
            if self.create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)
                self.create_narration_files(clip_path, segment)
        
        return created_clips

    def create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")
            
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
            
            # 修复Windows编码问题
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 使用适当的编码参数
            if sys.platform.startswith('win'):
                # Windows特殊处理
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300,
                    encoding='utf-8',
                    errors='ignore',
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                # Unix/Linux系统
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300,
                    encoding='utf-8',
                    errors='ignore',
                    env=env
                )
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"   ✅ 成功: {file_size:.1f}MB")
                return True
            else:
                error_msg = result.stderr[:100] if result.stderr else '未知错误'
                print(f"   ❌ 失败: {error_msg}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"   ❌ 剪辑超时")
            return False
        except UnicodeDecodeError as e:
            print(f"   ❌ 编码错误: {e}")
            return False
        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def create_narration_files(self, video_path: str, segment: Dict):
        """创建旁白文件"""
        try:
            # 旁白文本文件
            narration_path = video_path.replace('.mp4', '_旁白.txt')
            if not os.path.exists(narration_path):
                content = f"""🎙️ {segment['title']} - 专业旁白解说
{"=" * 50}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration', 0)} 秒
• 描述: {segment.get('description', '精彩剧情片段')}

🎙️ 专业解说:
{segment.get('narration', '暂无解说')}

💡 观看提示:
{segment.get('highlight', '精彩内容值得关注')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                with open(narration_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   📝 旁白文件: {os.path.basename(narration_path)}")
            
            # SRT字幕文件
            srt_path = video_path.replace('.mp4', '_字幕.srt')
            if not os.path.exists(srt_path):
                duration = segment.get('duration', 120)
                title = segment.get('title', '精彩片段')
                highlight = segment.get('highlight', '精彩内容正在播放')
                
                srt_content = f"""1
00:00:00,000 --> 00:00:05,000
{title}

2
00:00:05,000 --> 00:{duration//60:02d}:{duration%60:02d},000
{highlight}
"""
                
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                print(f"   🎬 字幕文件: {os.path.basename(srt_path)}")
        
        except Exception as e:
            print(f"   ⚠️ 旁白文件生成失败: {e}")

    def process_episode(self, srt_filename: str) -> bool:
        """处理单集"""
        print(f"\n📺 处理集数: {srt_filename}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_filename)
        subtitles = self.parse_srt_file(srt_path)
        
        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False
        
        # 2. AI分析
        analysis = self.ai_analyze_episode(subtitles, srt_filename)
        if not analysis:
            print(f"❌ AI分析失败，跳过此集")
            return False
        
        # 3. 查找视频文件
        video_file = self.find_video_file(srt_filename)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False
        
        print(f"📁 视频文件: {os.path.basename(video_file)}")
        
        # 4. 创建视频片段
        created_clips = self.create_video_clips(analysis, video_file, srt_filename)
        
        print(f"✅ {srt_filename} 处理完成: {len(created_clips)} 个片段")
        return len(created_clips) > 0

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 50)
        
        # 获取所有SRT文件，按文件名排序
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        # 按文件名排序（电视剧顺序）
        srt_files.sort()
        
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        print(f"🤖 AI状态: {'启用' if self.ai_config.get('enabled') else '未启用'}")
        
        # 处理每一集
        total_success = 0
        total_clips = 0
        
        for srt_file in srt_files:
            try:
                success = self.process_episode(srt_file)
                if success:
                    total_success += 1
                
                # 统计片段数
                clips = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
                total_clips = len(clips)
                
            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")
        
        # 最终报告
        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")

    def show_file_status(self):
        """显示文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        video_files = [f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
        clip_files = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
        
        print(f"\n📊 文件状态:")
        print(f"📝 字幕文件: {len(srt_files)} 个")
        print(f"🎬 视频文件: {len(video_files)} 个")
        print(f"📤 输出片段: {len(clip_files)} 个")
        
        if srt_files:
            print(f"\n字幕文件列表:")
            for i, f in enumerate(srt_files[:10], 1):
                print(f"  {i}. {f}")
            if len(srt_files) > 10:
                print(f"  ... 还有 {len(srt_files)-10} 个文件")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 智能电视剧剪辑系统")
            print("=" * 60)
            
            # 显示状态
            ai_status = "🤖 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"AI状态: {ai_status}")
            
            # 文件统计
            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))])
            clip_count = len([f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')])
            
            print(f"文件状态: 📝{srt_count}个字幕 🎬{video_count}个视频 📤{clip_count}个片段")
            
            print("\n🎯 功能菜单:")
            print("1. 🤖 配置AI接口")
            print("2. 🎬 开始智能剪辑")
            print("3. 📁 查看文件状态")
            print("0. ❌ 退出系统")
            
            try:
                choice = input("\n请选择操作 (0-3): ").strip()
                
                if choice == '1':
                    self.configure_ai()
                elif choice == '2':
                    if not self.ai_config.get('enabled'):
                        print("\n⚠️ 建议先配置AI接口")
                        confirm = input("是否继续？(y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    self.process_all_episodes()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '0':
                    print("\n👋 感谢使用智能电视剧剪辑系统！")
                    break
                else:
                    print(f"❌ 无效选择")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，程序退出")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    # 修复Windows编码问题
    if sys.platform.startswith('win'):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        try:
            import locale
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass
    
    # 检查并安装依赖
    print("🔧 检查依赖...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai', 'google-genai'], 
                      check=False, capture_output=True)
    except:
        pass
    
    clipper = IntelligentTVClipper()
    clipper.show_main_menu()

if __name__ == "__main__":
    main()
