
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影字幕AI分析剪辑系统 - 完整集成版
满足需求12-17：
12. 剪辑一致性保证
13. 已剪辑片段跳过机制
14. 多次执行结果一致性
15. 批量处理所有SRT文件
16. 纯后端，引导式配置
17. 引导式用户选择配置
"""

import os
import re
import json
import hashlib
import subprocess
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime

class StableMovieClipperSystem:
    """稳定的电影剪辑系统 - 满足需求12-17"""
    
    def __init__(self):
        # 目录结构
        self.srt_folder = "movie_srt"
        self.videos_folder = "movie_videos" 
        self.clips_folder = "movie_clips"
        self.analysis_folder = "movie_analysis"
        self.cache_folder = "ai_cache"
        
        # 需求12,13,14: 一致性和状态管理目录
        self.clip_status_folder = "clip_status"
        self.consistency_folder = "consistency_logs"
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, 
                      self.analysis_folder, self.cache_folder, self.clip_status_folder,
                      self.consistency_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 错别字修正词典
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '聽證會': '听证会',
            '問題': '问题', '機會': '机会', '開始': '开始', '結束': '结束'
        }
        
        # 加载AI配置
        self.ai_config = self._load_ai_config()
        
        print("🎬 稳定电影剪辑系统 - 后端服务")
        print("=" * 80)
        print("✨ 核心特性（满足需求12-17）:")
        print("• 需求12: 剪辑结果一致性保证")
        print("• 需求13: 已剪辑片段智能跳过")
        print("• 需求14: 多次执行结果完全一致")
        print("• 需求15: 批量处理所有SRT文件")
        print("• 需求16: 纯后端引导式操作")
        print("• 需求17: 引导式用户配置")

    def _load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")
        return {'enabled': False}

    def guided_ai_setup(self) -> bool:
        """需求16,17: 引导式AI配置"""
        print("\n🤖 AI接口配置向导")
        print("=" * 50)
        
        # 检查现有配置
        if self.ai_config.get('enabled'):
            print("✅ 发现现有AI配置:")
            print(f"   提供商: {self.ai_config.get('provider', '未知')}")
            print(f"   模型: {self.ai_config.get('model', '未知')}")
            
            use_existing = input("\n是否使用现有配置？(Y/n): ").strip().lower()
            if use_existing not in ['n', 'no', '否']:
                print("✅ 使用现有配置")
                return True
        
        print("\n🚀 选择AI服务类型:")
        print("1. 🌐 中转API (推荐 - 稳定便宜)")
        print("2. 🔒 官方API (OpenAI/Claude/Gemini)")
        print("3. 📋 快速预设配置")
        print("0. ❌ 跳过配置")
        
        while True:
            choice = input("\n请选择 (0-3): ").strip()
            
            if choice == '0':
                print("⚠️ 跳过AI配置，将无法进行智能分析")
                return False
            elif choice == '1':
                return self._setup_proxy_api()
            elif choice == '2':
                return self._setup_official_api()
            elif choice == '3':
                return self._setup_preset_config()
            else:
                print("❌ 无效选择，请输入0-3")

    def _setup_proxy_api(self) -> bool:
        """设置中转API"""
        print("\n🌐 中转API配置")
        print("推荐服务商:")
        print("• https://api.chatanywhere.tech/")
        print("• https://api.openai-proxy.org/")
        print("• https://api.openrouter.ai/")
        
        base_url = input("\nAPI地址: ").strip()
        if not base_url:
            print("❌ API地址不能为空")
            return False
        
        api_key = input("API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False
        
        model = input("模型名称 (如: gpt-3.5-turbo): ").strip()
        if not model:
            model = "gpt-3.5-turbo"
        
        config = {
            'enabled': True,
            'provider': 'proxy',
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }
        
        return self._save_config(config)

    def _setup_official_api(self) -> bool:
        """设置官方API"""
        print("\n🔒 官方API配置")
        print("1. OpenAI GPT")
        print("2. Anthropic Claude")
        print("3. Google Gemini")
        
        while True:
            choice = input("请选择 (1-3): ").strip()
            if choice == '1':
                return self._setup_openai()
            elif choice == '2':
                return self._setup_claude()
            elif choice == '3':
                return self._setup_gemini()
            else:
                print("❌ 无效选择，请输入1-3")

    def _setup_openai(self) -> bool:
        """设置OpenAI"""
        api_key = input("请输入OpenAI API密钥: ").strip()
        if not api_key:
            return False
        
        config = {
            'enabled': True,
            'provider': 'openai',
            'base_url': 'https://api.openai.com/v1',
            'api_key': api_key,
            'model': 'gpt-3.5-turbo'
        }
        return self._save_config(config)

    def _setup_claude(self) -> bool:
        """设置Claude"""
        api_key = input("请输入Anthropic API密钥: ").strip()
        if not api_key:
            return False
        
        config = {
            'enabled': True,
            'provider': 'claude',
            'base_url': 'https://api.anthropic.com',
            'api_key': api_key,
            'model': 'claude-3-haiku-20240307'
        }
        return self._save_config(config)

    def _setup_gemini(self) -> bool:
        """设置Gemini"""
        api_key = input("请输入Google API密钥: ").strip()
        if not api_key:
            return False
        
        config = {
            'enabled': True,
            'provider': 'gemini',
            'api_key': api_key,
            'model': 'gemini-pro'
        }
        return self._save_config(config)

    def _setup_preset_config(self) -> bool:
        """快速预设配置"""
        print("\n📋 快速预设配置")
        presets = {
            '1': {
                'name': 'ChatAnywhere',
                'base_url': 'https://api.chatanywhere.tech/v1',
                'model': 'gpt-3.5-turbo'
            },
            '2': {
                'name': 'OpenRouter',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'anthropic/claude-3-haiku'
            }
        }
        
        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")
        
        choice = input("\n请选择预设 (1-2): ").strip()
        if choice in presets:
            preset = presets[choice]
            api_key = input("请输入API密钥: ").strip()
            if not api_key:
                return False
            
            config = {
                'enabled': True,
                'provider': 'preset',
                'base_url': preset['base_url'],
                'api_key': api_key,
                'model': preset['model']
            }
            return self._save_config(config)
        
        print("❌ 无效选择")
        return False

    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.ai_config = config
            print(f"✅ AI配置保存成功: {config.get('provider')}")
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def get_file_hash(self, filepath: str) -> str:
        """需求14: 计算文件内容哈希，确保一致性"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except:
            return hashlib.md5(filepath.encode()).hexdigest()[:16]

    def get_clip_status_path(self, movie_title: str, clip_id: int) -> str:
        """需求13: 获取剪辑状态文件路径"""
        return os.path.join(self.clip_status_folder, f"{movie_title}_clip_{clip_id}_status.json")

    def is_clip_completed(self, movie_title: str, clip_id: int, analysis_hash: str) -> bool:
        """需求13: 检查片段是否已完成剪辑"""
        status_path = self.get_clip_status_path(movie_title, clip_id)
        
        if not os.path.exists(status_path):
            return False
        
        try:
            with open(status_path, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            # 检查分析哈希是否匹配，确保一致性
            if status.get('analysis_hash') != analysis_hash:
                return False
            
            # 检查视频文件是否存在且有效
            clip_path = status.get('clip_path')
            if clip_path and os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:
                return True
            
        except Exception as e:
            print(f"⚠️ 读取剪辑状态失败: {e}")
        
        return False

    def mark_clip_completed(self, movie_title: str, clip_id: int, analysis_hash: str, clip_path: str):
        """需求13: 标记片段已完成"""
        status_path = self.get_clip_status_path(movie_title, clip_id)
        
        status = {
            'movie_title': movie_title,
            'clip_id': clip_id,
            'analysis_hash': analysis_hash,
            'clip_path': clip_path,
            'completed_time': datetime.now().isoformat(),
            'file_size': os.path.getsize(clip_path) if os.path.exists(clip_path) else 0
        }
        
        try:
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存剪辑状态失败: {e}")

    def parse_srt_with_correction(self, filepath: str) -> List[Dict]:
        """解析SRT文件并修正错误"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")
        
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                    if content.strip():
                        break
            except:
                continue
        
        if not content:
            print(f"❌ 无法读取文件: {filepath}")
            return []
        
        # 错别字修正
        corrected_count = 0
        for old, new in self.corrections.items():
            if old in content:
                content = content.replace(old, new)
                corrected_count += 1
        
        if corrected_count > 0:
            print(f"🔧 修正错别字: {corrected_count} 处")
        
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
                                'text': text,
                                'start_seconds': self._time_to_seconds(start_time),
                                'end_seconds': self._time_to_seconds(end_time)
                            })
                except (ValueError, IndexError):
                    continue
        
        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def ai_analyze_movie_with_cache(self, subtitles: List[Dict], movie_title: str) -> Optional[Dict]:
        """AI分析 + 缓存机制"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置，无法进行分析")
            return None
        
        # 需求14: 基于内容生成缓存key
        content_hash = hashlib.md5(f"{movie_title}_{len(subtitles)}".encode()).hexdigest()[:16]
        cache_file = os.path.join(self.cache_folder, f"analysis_{movie_title}_{content_hash}.json")
        
        # 检查缓存
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    if cached_analysis.get('highlight_clips'):
                        print(f"💾 使用缓存的分析结果")
                        return cached_analysis
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
        
        print(f"🤖 AI分析中: {movie_title}")
        
        # 构建分析提示词
        full_content = self._build_movie_context(subtitles)
        prompt = f"""分析电影《{movie_title}》，识别3-5个最精彩的片段用于剪辑。

【字幕内容】
{full_content}

请返回JSON格式：
{{
    "movie_title": "{movie_title}",
    "highlight_clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "start_time": "00:10:30,000",
            "end_time": "00:13:45,000",
            "reason": "选择原因",
            "content": "片段内容描述"
        }}
    ]
}}"""

        try:
            response = self._call_ai_api(prompt)
            if response:
                result = self._parse_ai_response(response)
                if result and result.get('highlight_clips'):
                    # 保存到缓存
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"✅ AI分析完成，已缓存")
                    return result
            
            print("❌ AI分析失败")
            return None
        except Exception as e:
            print(f"❌ AI分析异常: {e}")
            return None

    def _build_movie_context(self, subtitles: List[Dict]) -> str:
        """构建电影上下文"""
        total_subs = len(subtitles)
        
        # 取开头20%、中间20%、结尾20%
        start_end = int(total_subs * 0.2)
        middle_start = int(total_subs * 0.4)
        middle_end = int(total_subs * 0.6)
        end_start = int(total_subs * 0.8)
        
        start_content = ' '.join([sub['text'] for sub in subtitles[:start_end]])
        middle_content = ' '.join([sub['text'] for sub in subtitles[middle_start:middle_end]])
        end_content = ' '.join([sub['text'] for sub in subtitles[end_start:]])
        
        return f"【开头】{start_content}\n\n【中间】{middle_content}\n\n【结尾】{end_content}"

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            config = self.ai_config
            
            if config.get('provider') == 'gemini':
                return self._call_gemini_api(prompt)
            else:
                return self._call_standard_api(prompt)
        except Exception as e:
            print(f"⚠️ API调用异常: {e}")
            return None

    def _call_standard_api(self, prompt: str) -> Optional[str]:
        """调用标准API"""
        try:
            config = self.ai_config
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {'role': 'system', 'content': '你是专业的电影分析师，擅长识别精彩片段。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            url = f"{config.get('base_url', 'https://api.openai.com/v1')}/chat/completions"
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                print(f"⚠️ API调用失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ 标准API调用失败: {e}")
            return None

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """调用Gemini API（简化版）"""
        print("⚠️ Gemini API需要特殊SDK，建议使用中转API")
        return None

    def _parse_ai_response(self, response_text: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end]
            else:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_text = response_text[start:end]
            
            result = json.loads(json_text)
            return result if 'highlight_clips' in result else None
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")
            return None

    def create_stable_video_clips(self, analysis: Dict, video_file: str, movie_title: str) -> List[str]:
        """需求12,13: 稳定的视频剪辑（支持跳过已完成）"""
        if not analysis or not analysis.get('highlight_clips'):
            print("❌ 无有效分析结果")
            return []
        
        clips = analysis['highlight_clips']
        created_files = []
        
        # 需求12: 生成分析哈希确保一致性
        analysis_hash = hashlib.md5(json.dumps(analysis, sort_keys=True).encode()).hexdigest()[:16]
        
        for i, clip in enumerate(clips, 1):
            clip_id = clip.get('clip_id', i)
            
            # 需求13: 检查是否已完成
            if self.is_clip_completed(movie_title, clip_id, analysis_hash):
                status_path = self.get_clip_status_path(movie_title, clip_id)
                with open(status_path, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                clip_path = status['clip_path']
                print(f"  ✅ 片段{clip_id}已存在，跳过: {os.path.basename(clip_path)}")
                created_files.append(clip_path)
                continue
            
            # 执行剪辑
            clip_title = self._generate_safe_filename(clip.get('title', f'片段{clip_id}'))
            clip_filename = f"{movie_title}_{clip_title}_seg{clip_id}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)
            
            print(f"\n🎬 剪辑片段 {clip_id}: {clip.get('title', '未知')}")
            
            if self._create_single_clip(video_file, clip, clip_path):
                # 需求13: 标记完成
                self.mark_clip_completed(movie_title, clip_id, analysis_hash, clip_path)
                created_files.append(clip_path)
                
                # 需求12: 记录一致性日志
                self._log_consistency(movie_title, clip_id, analysis_hash, clip_path)
            else:
                print(f"   ❌ 剪辑失败")
        
        return created_files

    def _create_single_clip(self, video_file: str, clip: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = clip.get('start_time')
            end_time = clip.get('end_time')
            
            if not start_time or not end_time:
                print(f"    ❌ 时间信息不完整")
                return False
            
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            if duration <= 0:
                print(f"    ❌ 无效时间段")
                return False
            
            # 添加缓冲确保完整性
            buffer_start = max(0, start_seconds - 1)
            buffer_duration = duration + 2
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"    ✅ 剪辑成功: {size_mb:.1f}MB")
                return True
            else:
                print(f"    ❌ FFmpeg失败: {result.stderr[:50]}")
                return False
                
        except Exception as e:
            print(f"    ❌ 剪辑异常: {e}")
            return False

    def _log_consistency(self, movie_title: str, clip_id: int, analysis_hash: str, clip_path: str):
        """需求12,14: 记录一致性日志"""
        log_file = os.path.join(self.consistency_folder, f"{movie_title}_consistency.log")
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'movie_title': movie_title,
            'clip_id': clip_id,
            'analysis_hash': analysis_hash,
            'clip_path': clip_path,
            'file_size': os.path.getsize(clip_path) if os.path.exists(clip_path) else 0
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 一致性日志记录失败: {e}")

    def find_movie_video_file(self, movie_title: str) -> Optional[str]:
        """查找对应的视频文件"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, movie_title + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        if os.path.exists(self.videos_folder):
            for filename in os.listdir(self.videos_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    if movie_title.lower() in filename.lower():
                        return os.path.join(self.videos_folder, filename)
        
        return None

    def process_single_movie(self, srt_file: str) -> bool:
        """处理单部电影"""
        print(f"\n{'='*20} 处理电影 {'='*20}")
        print(f"文件: {srt_file}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_file)
        subtitles = self.parse_srt_with_correction(srt_path)
        
        if not subtitles:
            print("❌ 字幕解析失败")
            return False
        
        # 2. 提取电影标题
        movie_title = os.path.splitext(srt_file)[0]
        
        # 3. AI分析（支持缓存）
        analysis = self.ai_analyze_movie_with_cache(subtitles, movie_title)
        
        if not analysis:
            print("❌ AI分析失败")
            return False
        
        # 4. 查找视频文件
        video_file = self.find_movie_video_file(movie_title)
        if not video_file:
            print("❌ 未找到对应视频文件")
            return False
        
        print(f"📁 视频文件: {os.path.basename(video_file)}")
        
        # 5. 创建视频片段（支持跳过已完成）
        created_clips = self.create_stable_video_clips(analysis, video_file, movie_title)
        
        print(f"✅ 处理完成！生成 {len(created_clips)} 个片段")
        return True

    def process_all_movies_batch(self):
        """需求15: 批量处理所有SRT文件"""
        print("\n🚀 批量处理所有电影")
        print("=" * 60)
        
        # 检查AI配置
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置，无法进行智能分析")
            print("💡 请先配置AI接口")
            return
        
        # 需求15: 获取所有SRT文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        srt_files.sort()
        print(f"📝 找到 {len(srt_files)} 个电影字幕文件")
        
        # 检查已处理的文件
        processed_count = 0
        skipped_count = 0
        
        for cache_file in os.listdir(self.cache_folder):
            if cache_file.startswith('analysis_') and cache_file.endswith('.json'):
                processed_count += 1
        
        if processed_count > 0:
            print(f"💾 发现 {processed_count} 个已分析的电影")
        
        print(f"\n开始处理...")
        
        success_count = 0
        
        for i, srt_file in enumerate(srt_files, 1):
            print(f"\n{'🎬'*3} 第 {i}/{len(srt_files)} 部电影 {'🎬'*3}")
            
            try:
                if self.process_single_movie(srt_file):
                    success_count += 1
                else:
                    print(f"❌ 处理失败: {srt_file}")
            except Exception as e:
                print(f"❌ 处理异常 {srt_file}: {e}")
        
        print(f"\n{'🎉'*3} 批量处理完成 {'🎉'*3}")
        print(f"✅ 成功处理: {success_count}/{len(srt_files)} 部电影")
        print(f"📁 输出目录: {self.clips_folder}/")

    def show_main_menu(self):
        """需求16: 纯后端主菜单"""
        while True:
            print("\n" + "=" * 80)
            print("🎬 稳定电影剪辑系统 - 后端控制台")
            print("=" * 80)
            
            # 显示状态
            ai_status = "✅ 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"🤖 AI状态: {ai_status}")
            
            srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
            video_files = [f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))] if os.path.exists(self.videos_folder) else []
            
            print(f"📝 字幕文件: {len(srt_files)} 个")
            print(f"🎬 视频文件: {len(video_files)} 个")
            
            print(f"\n🎯 主要功能:")
            print("1. 🤖 配置AI接口（必需）")
            print("2. 🚀 一键智能剪辑（批量处理所有文件）")
            print("3. 📊 查看处理状态")
            print("4. 🔧 系统环境检查")
            print("0. ❌ 退出系统")
            
            try:
                choice = input("\n请选择操作 (0-4): ").strip()
                
                if choice == '0':
                    print("\n👋 感谢使用稳定电影剪辑系统！")
                    break
                elif choice == '1':
                    self.guided_ai_setup()
                elif choice == '2':
                    if not self.ai_config.get('enabled'):
                        print("❌ 请先配置AI接口")
                        continue
                    self.process_all_movies_batch()
                elif choice == '3':
                    self._show_processing_status()
                elif choice == '4':
                    self._check_system_environment()
                else:
                    print("❌ 无效选择，请输入0-4")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")

    def _show_processing_status(self):
        """显示处理状态"""
        print(f"\n📊 处理状态详情")
        print("=" * 50)
        
        # 分析缓存状态
        cached_analyses = [f for f in os.listdir(self.cache_folder) if f.startswith('analysis_')]
        print(f"💾 已缓存分析: {len(cached_analyses)} 个")
        
        # 剪辑状态
        completed_clips = [f for f in os.listdir(self.clip_status_folder) if f.endswith('_status.json')]
        print(f"✂️ 已完成剪辑: {len(completed_clips)} 个片段")
        
        # 输出文件
        output_clips = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
        print(f"📁 输出视频: {len(output_clips)} 个")
        
        if output_clips:
            total_size = sum(os.path.getsize(os.path.join(self.clips_folder, f)) for f in output_clips)
            print(f"💾 总文件大小: {total_size/(1024*1024*1024):.2f} GB")

    def _check_system_environment(self):
        """检查系统环境"""
        print(f"\n🔧 系统环境检查")
        print("=" * 50)
        
        # 目录检查
        directories = [
            (self.srt_folder, "字幕目录"),
            (self.videos_folder, "视频目录"),
            (self.clips_folder, "输出目录"),
            (self.cache_folder, "分析缓存"),
            (self.clip_status_folder, "剪辑状态"),
            (self.consistency_folder, "一致性日志")
        ]
        
        for directory, name in directories:
            status = "✅ 存在" if os.path.exists(directory) else "❌ 不存在"
            print(f"📁 {name}: {status}")
        
        # AI配置检查
        ai_status = "✅ 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
        print(f"🤖 AI配置: {ai_status}")
        
        if self.ai_config.get('enabled'):
            print(f"   提供商: {self.ai_config.get('provider')}")
            print(f"   模型: {self.ai_config.get('model')}")
        
        # FFmpeg检查
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            ffmpeg_status = "✅ 已安装" if result.returncode == 0 else "❌ 未安装"
        except:
            ffmpeg_status = "❌ 未安装或不可用"
        
        print(f"🎬 FFmpeg: {ffmpeg_status}")

    def _generate_safe_filename(self, title: str) -> str:
        """生成安全的文件名"""
        safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
        return safe_title[:30]

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

def main():
    """主函数 - 需求16: 纯后端启动"""
    try:
        system = StableMovieClipperSystem()
        system.show_main_menu()
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")

if __name__ == "__main__":
    main()
