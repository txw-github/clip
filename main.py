
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 智能电视剧剪辑系统 - 统一主程序
集成一键配置、一键启动、智能分析、视频剪辑等全部功能
"""

import os
import re
import json
import subprocess
import hashlib
import sys
from typing import List, Dict, Optional
from datetime import datetime

class UnifiedTVClipperSystem:
    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos" 
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"
        self.config_file = ".ai_config.json"
        self.series_context_file = os.path.join(self.cache_folder, "series_context.json")

        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        print("🚀 智能电视剧剪辑系统 - 统一版本")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

        # AI配置
        self.ai_config = self.load_ai_config()

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled'):
                    provider_name = config.get('provider', '未知')
                    model = config.get('model', '未知')
                    print(f"🤖 AI分析: 已启用 ({provider_name} - {model})")
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
        print("=" * 50)
        
        # 推荐配置
        providers = {
            "1": {
                "name": "DeepSeek R1 (推荐)",
                "provider": "deepseek_official",
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-r1"
            },
            "2": {
                "name": "Claude 3.5 Sonnet (中转)",
                "provider": "proxy_chataiapi", 
                "base_url": "https://www.chataiapi.com/v1",
                "model": "claude-3-5-sonnet-20240620"
            },
            "3": {
                "name": "GPT-4o (中转)",
                "provider": "proxy_chataiapi",
                "base_url": "https://www.chataiapi.com/v1", 
                "model": "gpt-4o"
            },
            "4": {
                "name": "Gemini 2.5 Pro (官方)",
                "provider": "gemini_official",
                "model": "gemini-2.5-flash"
            }
        }
        
        print("推荐的AI模型:")
        for key, config in providers.items():
            print(f"{key}. {config['name']}")
        
        print("0. 跳过AI配置，使用基础模式")
        
        choice = input("\n请选择 (0-4): ").strip()
        
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
            'provider': selected['provider'],
            'api_key': api_key,
            'model': selected['model']
        }
        
        if 'base_url' in selected:
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
            if config['provider'] == 'gemini_official':
                return self.test_gemini(config)
            else:
                return self.test_openai_compatible(config)
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False

    def test_gemini(self, config: Dict) -> bool:
        """测试Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config['api_key'])
            model = genai.GenerativeModel(config['model'])
            response = model.generate_content("hello")
            print("✅ Gemini连接成功")
            return True
        except ImportError:
            print("❌ 需要安装: pip install google-generativeai")
            return False
        except Exception as e:
            print(f"❌ Gemini测试失败: {e}")
            return False

    def test_openai_compatible(self, config: Dict) -> bool:
        """测试OpenAI兼容API"""
        try:
            import openai
            
            client_kwargs = {'api_key': config['api_key']}
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']
            
            client = openai.OpenAI(**client_kwargs)
            
            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10
            )
            
            print("✅ API连接成功")
            return True
        except Exception as e:
            print(f"❌ API测试失败: {e}")
            return False

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用AI API"""
        if not self.ai_config.get('enabled'):
            return None
        
        try:
            if self.ai_config['provider'] == 'gemini_official':
                return self.call_gemini_api(prompt, system_prompt)
            else:
                return self.call_openai_compatible_api(prompt, system_prompt)
        except Exception as e:
            print(f"⚠️ AI API调用失败: {e}")
            return None

    def call_gemini_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.ai_config['api_key'])
            
            model = genai.GenerativeModel(
                self.ai_config['model'],
                system_instruction=system_prompt if system_prompt else None
            )
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini API失败: {e}")
            return None

    def call_openai_compatible_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            import openai
            
            client_kwargs = {'api_key': self.ai_config['api_key']}
            if 'base_url' in self.ai_config:
                client_kwargs['base_url'] = self.ai_config['base_url']
            
            client = openai.OpenAI(**client_kwargs)
            
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
            print(f"⚠️ OpenAI兼容API失败: {e}")
            return None

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
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            '調查': '调查', '審判': '审判', '辯護': '辩护', '起訴': '起诉'
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
        
        # 构建完整上下文
        full_context = self.build_complete_context(subtitles)
        
        print(f"🤖 AI分析第{episode_num}集...")
        
        prompt = f"""# 电视剧智能分析与精彩剪辑

请为 **第{episode_num}集** 进行完整智能分析。

## 当前集完整内容
```
{full_context}
```

## 分析要求

### 1. 智能识别剧情特点
- 自动识别剧情类型（法律/爱情/悬疑/古装/现代/犯罪/家庭/职场等）
- 智能判断剧情风格和叙事特点

### 2. 精彩片段识别（3-5个短视频）
- 智能识别最具戏剧价值的片段
- 每个片段2-3分钟，包含完整剧情单元
- 确保片段间逻辑连贯
- 片段必须包含完整对话，不截断句子

### 3. 专业解说内容
- 深度剧情理解和分析
- 制造悬念和吸引力
- 强调冲突和转折的精彩之处

请严格按照以下JSON格式输出：

```json
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre_type": "智能识别的剧情类型",
        "main_theme": "本集核心主题",
        "emotional_tone": "整体情感基调"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "精彩标题",
            "start_time": "00:XX:XX,XXX",
            "end_time": "00:XX:XX,XXX",
            "duration_seconds": 180,
            "plot_significance": "剧情重要意义",
            "hook_reason": "吸引观众的核心卖点",
            "professional_narration": {{
                "full_script": "完整的专业旁白解说稿"
            }},
            "key_dialogues": [
                {{"speaker": "角色名", "line": "关键台词", "impact": "台词重要性"}}
            ]
        }}
    ],
    "episode_summary": {{
        "core_conflicts": ["本集核心冲突点"],
        "key_clues": ["重要线索"],
        "character_development": "角色发展"
    }}
}}
```"""

        system_prompt = """你是顶级影视内容分析专家，专长：
- 影视剧情深度解构与叙事分析
- 多类型剧情的自适应分析策略
- 专业旁白解说和深度剧情理解

请运用专业知识进行深度分析，确保输出内容的智能化和连贯性。"""

        try:
            response = self.call_ai_api(prompt, system_prompt)
            if response:
                parsed_result = self.parse_ai_response(response)
                if parsed_result:
                    print(f"✅ AI分析成功：{len(parsed_result.get('highlight_segments', []))} 个片段")
                    # 保存到缓存
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
            
            # 验证必要字段
            if 'highlight_segments' in result and 'episode_analysis' in result:
                return result
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
        return None

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

    def build_complete_context(self, subtitles: List[Dict]) -> str:
        """构建完整上下文"""
        # 取前80%内容作为分析样本
        sample_size = int(len(subtitles) * 0.8)
        context_parts = []
        
        # 每50句分一段，保持上下文连贯
        for i in range(0, sample_size, 50):
            segment = subtitles[i:i+50]
            segment_text = ' '.join([sub['text'] for sub in segment])
            context_parts.append(segment_text)
        
        return '\n\n'.join(context_parts)

    def extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)
        return "00"

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

    def create_video_clips(self, analysis: Dict, video_file: str, subtitle_filename: str) -> List[str]:
        """创建视频片段"""
        created_clips = []
        
        # 检查FFmpeg
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
                self.create_narration_file(clip_path, segment, analysis)

        return created_clips

    def check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

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

    def create_narration_file(self, video_path: str, segment: Dict, analysis: Dict):
        """创建专业旁白解说文件"""
        try:
            narration_path = video_path.replace('.mp4', '_专业旁白解说.txt')
            
            narration = segment.get('professional_narration', {})
            episode_info = analysis.get('episode_analysis', {})
            
            content = f"""📺 {segment['title']} - 专业剧情解说与旁白稿
{"=" * 80}

🎬 短视频信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 集数: 第{episode_info.get('episode_number', '?')}集
🎭 剧情类型: {episode_info.get('genre_type', 'AI智能识别')}
⏱️ 视频时长: {segment.get('duration_seconds', 0)} 秒
🎯 剧情核心: {segment.get('plot_significance', '关键剧情节点')}
🔥 观众吸引力: {segment.get('hook_reason', '高潮剧情')}

🎙️ 完整旁白解说稿:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{narration.get('full_script', f'在第{episode_info.get("episode_number", "?")}集的这个精彩片段中，{segment.get("hook_reason", "关键剧情即将揭晓")}。')}

💬 关键台词解析:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            
            # 添加关键对话分析
            key_dialogues = segment.get('key_dialogues', [])
            if key_dialogues:
                for i, dialogue in enumerate(key_dialogues[:5], 1):
                    speaker = dialogue.get('speaker', '角色')
                    line = dialogue.get('line', '重要台词')
                    impact = dialogue.get('impact', '推进剧情发展')
                    content += f"""
{i}. {speaker}: "{line}"
   → 剧情作用: {impact}"""
            else:
                content += "\n本片段以画面表现为主，通过视觉冲击展现剧情张力"
            
            content += f"""

📊 短视频制作说明:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 视频时长: {segment.get('duration_seconds', 0)} 秒（适合短视频平台）
✅ 内容完整性: 包含完整剧情单元，逻辑连贯
✅ 剧情价值: {segment.get('plot_significance', '核心剧情推进')}

📝 制作信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
分析方式: AI智能分析
系统版本: 统一智能剪辑系统
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   📜 生成专业旁白解说: {os.path.basename(narration_path)}")
            
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
        
        # 5. 生成集数总结
        self.create_episode_summary(subtitle_file, analysis, created_clips)
        
        clips_count = len(created_clips)
        print(f"✅ {subtitle_file} 处理完成: {clips_count} 个短视频")
        
        return clips_count > 0

    def create_episode_summary(self, subtitle_file: str, analysis: Dict, clips: List[str]):
        """创建集数总结"""
        try:
            summary_path = os.path.join(self.output_folder, f"{os.path.splitext(subtitle_file)[0]}_智能分析总结.txt")
            
            episode_analysis = analysis.get('episode_analysis', {})
            episode_summary = analysis.get('episode_summary', {})
            
            content = f"""📺 {subtitle_file} - 智能剪辑总结
{"=" * 80}

🤖 智能分析信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 集数: 第{episode_analysis.get('episode_number', '?')}集
• 智能识别类型: {episode_analysis.get('genre_type', '自动识别')}
• 核心主题: {episode_analysis.get('main_theme', '剧情发展')}
• 情感基调: {episode_analysis.get('emotional_tone', '情感推进')}

🎬 剪辑成果:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 成功片段: {len(clips)} 个
• 总时长: {sum(seg.get('duration_seconds', 0) for seg in analysis.get('highlight_segments', []))} 秒

📝 剧情要点:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 核心冲突: {', '.join(episode_summary.get('core_conflicts', ['主要冲突']))}
• 关键线索: {', '.join(episode_summary.get('key_clues', ['重要线索']))}
• 角色发展: {episode_summary.get('character_development', '角色发展轨迹')}

🎬 片段详情:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            for i, segment in enumerate(analysis.get('highlight_segments', []), 1):
                content += f"""
{i}. {segment['title']}
   时间: {segment['start_time']} - {segment['end_time']} ({segment.get('duration_seconds', 0)}秒)
   剧情意义: {segment.get('plot_significance', '剧情推进')}
   观众吸引点: {segment.get('hook_reason', '精彩内容')}
"""
            
            content += f"""

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析方式: 统一智能剪辑系统
"""
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📄 总结文件: {os.path.basename(summary_path)}")
            
        except Exception as e:
            print(f"⚠️ 总结生成失败: {e}")

    def process_all_episodes(self):
        """处理所有集数 - 主流程"""
        print("🚀 开始智能剪辑处理")
        print("=" * 60)
        
        # 检查目录和文件
        subtitle_files = [f for f in os.listdir(self.srt_folder) 
                         if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not subtitle_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
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
                    print(f"⏸️ {subtitle_file} 已跳过，等待AI可用")
                
                # 统计片段数
                episode_clips = [f for f in os.listdir(self.output_folder) 
                               if f.startswith(os.path.splitext(subtitle_file)[0]) and f.endswith('.mp4')]
                total_clips += len(episode_clips)
                
            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")
        
        # 最终报告
        self.create_final_report(total_success, len(subtitle_files), total_clips, total_skipped)

    def create_final_report(self, success_count: int, total_episodes: int, total_clips: int, skipped_count: int = 0):
        """创建最终报告"""
        report_content = f"""🎬 统一智能剪辑系统 - 最终报告
{"=" * 80}

📊 处理统计:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 总集数: {total_episodes} 集
• 成功处理: {success_count} 集
• AI不可用跳过: {skipped_count} 集
• 失败: {total_episodes - success_count - skipped_count} 集
• 成功率: {(success_count/total_episodes*100):.1f}%
• 生成短视频: {total_clips} 个

📁 输出文件:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 视频片段: {self.output_folder}/*.mp4
• 专业旁白: {self.output_folder}/*_专业旁白解说.txt
• 智能总结: {self.output_folder}/*_智能分析总结.txt

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report_path = os.path.join(self.output_folder, "统一智能剪辑系统报告.txt")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"\n📊 最终统计:")
            print(f"✅ 成功处理: {success_count}/{total_episodes} 集")
            print(f"🎬 生成片段: {total_clips} 个")
            print(f"📄 详细报告: {report_path}")
            
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")

    def install_dependencies(self):
        """安装必要依赖"""
        print("🔧 检查并安装必要依赖...")
        
        dependencies = ['openai', 'google-generativeai']
        
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

    def check_system_requirements(self):
        """检查系统要求"""
        print("🔍 检查系统环境...")
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            print("❌ 需要Python 3.7或更高版本")
            return False
        
        print("✅ Python版本检查通过")
        
        # 检查FFmpeg
        if self.check_ffmpeg():
            print("✅ FFmpeg已安装")
        else:
            print("⚠️ 未找到FFmpeg，将无法进行视频剪辑")
            print("💡 如需视频剪辑功能，请安装FFmpeg")
        
        return True

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 统一智能电视剧剪辑系统")
            print("=" * 60)

            # 显示状态
            ai_status = "🤖 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"AI状态: {ai_status}")

            srt_files = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_files = len([f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.mkv', '.avi'))])
            print(f"字幕文件: {srt_files} 个")
            print(f"视频文件: {video_files} 个")

            print("\n🎯 主要功能:")
            print("1. 🤖 一键配置AI接口")
            print("2. 🎬 一键开始智能剪辑")
            print("3. 📁 检查文件状态")
            print("4. 🔧 安装系统依赖")
            print("5. 🔄 清空分析缓存")
            print("0. ❌ 退出系统")

            try:
                choice = input("\n请选择操作 (0-5): ").strip()

                if choice == '1':
                    self.configure_ai_interactive()

                elif choice == '2':
                    if srt_files == 0:
                        print(f"\n❌ 请先将字幕文件放入 {self.srt_folder}/ 目录")
                        continue
                    
                    if video_files == 0:
                        print(f"\n⚠️ 未找到视频文件，将只进行分析不进行剪辑")
                        print(f"💡 如需视频剪辑，请将视频文件放入 {self.video_folder}/ 目录")
                    
                    self.process_all_episodes()

                elif choice == '3':
                    print(f"\n📊 文件状态检查:")
                    print(f"📁 字幕目录: {self.srt_folder}/ ({srt_files} 个文件)")
                    if srt_files > 0:
                        srt_list = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))][:5]
                        for f in srt_list:
                            print(f"   • {f}")
                        if srt_files > 5:
                            print(f"   • ... 还有 {srt_files-5} 个文件")
                    
                    print(f"🎬 视频目录: {self.video_folder}/ ({video_files} 个文件)")
                    if video_files > 0:
                        video_list = [f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.mkv', '.avi'))][:5]
                        for f in video_list:
                            print(f"   • {f}")
                        if video_files > 5:
                            print(f"   • ... 还有 {video_files-5} 个文件")
                    
                    print(f"📤 输出目录: {self.output_folder}/")
                    output_files = len([f for f in os.listdir(self.output_folder) if f.endswith('.mp4')])
                    print(f"   已生成视频: {output_files} 个")

                elif choice == '4':
                    self.install_dependencies()

                elif choice == '5':
                    import shutil
                    if os.path.exists(self.cache_folder):
                        shutil.rmtree(self.cache_folder)
                        os.makedirs(self.cache_folder)
                        print(f"✅ 已清空分析缓存")
                    else:
                        print(f"📝 缓存目录不存在")

                elif choice == '0':
                    print("\n👋 感谢使用统一智能剪辑系统！")
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
        system = UnifiedTVClipperSystem()
        
        # 检查系统要求
        if not system.check_system_requirements():
            print("❌ 系统要求不满足")
            return
        
        # 显示欢迎信息
        print("\n🎉 欢迎使用统一智能电视剧剪辑系统！")
        print("💡 功能特点：")
        print("   • 一键配置AI接口")
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
