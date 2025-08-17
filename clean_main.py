
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影字幕AI分析剪辑系统 - 完全重构版
简化结构，明确区分官方API和中转API
"""

import os
import re
import json
import hashlib
import subprocess
import time
from typing import List, Dict, Optional
from datetime import datetime

class MovieClipperSystem:
    """电影剪辑系统 - 重构版"""
    
    def __init__(self):
        # 目录结构
        self.srt_folder = "movie_srt"
        self.videos_folder = "movie_videos"
        self.clips_folder = "movie_clips"
        self.cache_folder = "ai_cache"
        
        # 创建目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self._load_ai_config()
        
        print("🎬 电影剪辑系统 - 重构版")
        print("=" * 50)

    def _load_ai_config(self) -> Dict:
        """加载AI配置"""
        config_file = '.ai_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled'):
                        return config
            except Exception as e:
                print(f"⚠️ 配置加载失败: {e}")
        return {'enabled': False}

    def setup_ai_config(self) -> bool:
        """设置AI配置"""
        print("\n🤖 AI配置向导")
        print("=" * 30)
        
        # 检查现有配置
        if self.ai_config.get('enabled'):
            print("✅ 发现现有配置:")
            print(f"   类型: {self.ai_config.get('api_type')}")
            print(f"   提供商: {self.ai_config.get('provider')}")
            
            use_existing = input("\n是否使用现有配置？(Y/n): ").strip().lower()
            if use_existing not in ['n', 'no', '否']:
                return True
        
        print("\n选择API类型:")
        print("1. 🔒 官方API (Gemini官方)")
        print("2. 🌐 中转API (OpenAI兼容)")
        print("0. ❌ 跳过配置")
        
        while True:
            choice = input("\n请选择 (0-2): ").strip()
            
            if choice == '0':
                print("⚠️ 跳过AI配置")
                return False
            elif choice == '1':
                return self._setup_official_api()
            elif choice == '2':
                return self._setup_proxy_api()
            else:
                print("❌ 无效选择")

    def _setup_official_api(self) -> bool:
        """设置官方API - 仅支持Gemini"""
        print("\n🔒 Gemini官方API配置")
        print("获取API密钥: https://aistudio.google.com/apikey")
        
        api_key = input("\nGemini API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False
        
        # 可用模型
        models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
        print(f"\n选择模型:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        
        model_choice = input(f"选择 (1-{len(models)}): ").strip()
        try:
            model = models[int(model_choice) - 1]
        except:
            model = models[0]
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }
        
        # 测试连接
        print("🔍 测试连接...")
        if self._test_gemini_api(config):
            print("✅ 连接成功")
            return self._save_config(config)
        else:
            print("❌ 连接失败")
            return False

    def _setup_proxy_api(self) -> bool:
        """设置中转API"""
        print("\n🌐 中转API配置")
        
        # 预设选项
        presets = {
            "1": {
                "name": "ChatAI API",
                "base_url": "https://www.chataiapi.com/v1",
                "models": ["deepseek-r1", "claude-3-5-sonnet-20240620", "gpt-4o"]
            },
            "2": {
                "name": "OpenRouter",
                "base_url": "https://openrouter.ai/api/v1",
                "models": ["anthropic/claude-3.5-sonnet", "deepseek/deepseek-r1"]
            },
            "3": {
                "name": "自定义中转",
                "base_url": "",
                "models": []
            }
        }
        
        print("选择中转服务:")
        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")
        
        choice = input("请选择 (1-3): ").strip()
        if choice not in presets:
            return False
        
        selected = presets[choice]
        
        if choice == "3":
            base_url = input("API地址: ").strip()
            if not base_url:
                return False
            model = input("模型名称: ").strip()
            if not model:
                return False
        else:
            base_url = selected["base_url"]
            print(f"\n推荐模型:")
            for i, m in enumerate(selected["models"], 1):
                print(f"{i}. {m}")
            
            model_choice = input(f"选择模型 (1-{len(selected['models'])}): ").strip()
            try:
                model = selected["models"][int(model_choice) - 1]
            except:
                model = selected["models"][0]
        
        api_key = input("API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False
        
        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': selected['name'],
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }
        
        # 测试连接
        print("🔍 测试连接...")
        if self._test_proxy_api(config):
            print("✅ 连接成功")
            return self._save_config(config)
        else:
            print("❌ 连接失败")
            return False

    def _test_gemini_api(self, config: Dict) -> bool:
        """测试Gemini官方API"""
        try:
            import google.generativeai as genai
            
            # 官方推荐的配置方式
            genai.configure(api_key=config['api_key'])
            
            # 创建模型实例并测试
            model = genai.GenerativeModel(config['model'])
            response = model.generate_content("测试")
            return bool(response.text)
        except ImportError:
            print("需要安装: pip install google-generativeai")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _test_proxy_api(self, config: Dict) -> bool:
        """测试中转API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试'}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except ImportError:
            print("需要安装: pip install openai")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.ai_config = config
            print(f"✅ 配置保存成功")
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数，使用SRT文件名作为集数标识"""
        # 移除扩展名，直接使用文件名作为集数
        return os.path.splitext(filename)[0]

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")
        
        # 尝试不同编码
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                    if content.strip():
                        break
            except:
                continue
        
        if not content:
            print(f"❌ 无法读取文件")
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
                                'text': text,
                                'start_seconds': self._time_to_seconds(start_time),
                                'end_seconds': self._time_to_seconds(end_time)
                            })
                except (ValueError, IndexError):
                    continue
        
        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def ai_analyze_movie(self, subtitles: List[Dict], episode_name: str) -> Optional[Dict]:
        """AI分析电影（支持缓存）"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置")
            return None
        
        # 缓存机制
        content_hash = hashlib.md5(f"{episode_name}_{len(subtitles)}".encode()).hexdigest()[:16]
        cache_file = os.path.join(self.cache_folder, f"analysis_{episode_name}_{content_hash}.json")
        
        # 检查缓存
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached.get('highlight_clips'):
                        print("💾 使用缓存结果")
                        return cached
            except:
                pass
        
        print(f"🤖 AI分析中: {episode_name}")
        
        # 构建分析内容
        sample_content = self._build_sample_content(subtitles)
        
        prompt = f"""分析电影《{episode_name}》，识别3-5个最精彩的片段用于剪辑。

【字幕内容样本】
{sample_content}

请返回JSON格式：
{{
    "movie_title": "{episode_name}",
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
                    # 保存缓存
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print("✅ AI分析完成")
                    return result
            
            print("❌ AI分析失败")
            return None
        except Exception as e:
            print(f"❌ AI分析异常: {e}")
            return None

    def _build_sample_content(self, subtitles: List[Dict]) -> str:
        """构建分析样本内容"""
        total = len(subtitles)
        
        # 取开头、中间、结尾各20%
        start_end = int(total * 0.2)
        middle_start = int(total * 0.4)
        middle_end = int(total * 0.6)
        end_start = int(total * 0.8)
        
        start_text = ' '.join([sub['text'] for sub in subtitles[:start_end]])
        middle_text = ' '.join([sub['text'] for sub in subtitles[middle_start:middle_end]])
        end_text = ' '.join([sub['text'] for sub in subtitles[end_start:]])
        
        return f"【开头】{start_text}\n\n【中间】{middle_text}\n\n【结尾】{end_text}"

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        config = self.ai_config
        
        try:
            if config.get('api_type') == 'official':
                return self._call_gemini_official(prompt, config)
            else:
                return self._call_proxy_api(prompt, config)
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            import google.generativeai as genai
            
            # 配置API密钥
            genai.configure(api_key=config['api_key'])
            
            # 创建模型实例
            model = genai.GenerativeModel(config['model'])
            
            # 生成内容
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_proxy_api(self, prompt: str, config: Dict) -> Optional[str]:
        """调用中转API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {'role': 'system', 'content': '你是专业的电影分析师，擅长识别精彩片段。'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"中转API调用失败: {e}")
            return None

    def _parse_ai_response(self, response_text: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON部分
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
        except Exception as e:
            print(f"⚠️ 响应解析失败: {e}")
            return None

    def create_video_clips(self, analysis: Dict, video_file: str, episode_name: str) -> List[str]:
        """创建视频片段"""
        if not analysis or not analysis.get('highlight_clips'):
            print("❌ 无分析结果")
            return []
        
        clips = analysis['highlight_clips']
        created_files = []
        
        for i, clip in enumerate(clips, 1):
            clip_title = self._safe_filename(clip.get('title', f'片段{i}'))
            clip_filename = f"{episode_name}_{clip_title}_seg{i}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)
            
            print(f"\n🎬 剪辑片段 {i}: {clip.get('title', '未知')}")
            
            if self._create_single_clip(video_file, clip, clip_path):
                created_files.append(clip_path)
            else:
                print(f"   ❌ 剪辑失败")
        
        return created_files

    def _create_single_clip(self, video_file: str, clip: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = clip.get('start_time')
            end_time = clip.get('end_time')
            
            if not start_time or not end_time:
                return False
            
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            if duration <= 0:
                return False
            
            # FFmpeg命令
            cmd = [
                'ffmpeg', '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-preset', 'medium', '-crf', '23',
                output_path, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"    ✅ 成功: {size_mb:.1f}MB")
                return True
            else:
                print(f"    ❌ FFmpeg失败")
                return False
                
        except Exception as e:
            print(f"    ❌ 异常: {e}")
            return False

    def find_video_file(self, episode_name: str) -> Optional[str]:
        """查找对应视频文件"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, episode_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if episode_name.lower() in filename.lower():
                    return os.path.join(self.videos_folder, filename)
        
        return None

    def process_single_movie(self, srt_file: str) -> bool:
        """处理单部电影"""
        print(f"\n{'='*20} 处理电影 {'='*20}")
        print(f"文件: {srt_file}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_file)
        subtitles = self.parse_srt_file(srt_path)
        
        if not subtitles:
            return False
        
        # 2. 提取集数（使用文件名）
        episode_name = self._extract_episode_number(srt_file)
        
        # 3. AI分析
        analysis = self.ai_analyze_movie(subtitles, episode_name)
        if not analysis:
            return False
        
        # 4. 查找视频文件
        video_file = self.find_video_file(episode_name)
        if not video_file:
            print("❌ 未找到视频文件")
            return False
        
        print(f"📁 视频: {os.path.basename(video_file)}")
        
        # 5. 创建视频片段
        created_clips = self.create_video_clips(analysis, video_file, episode_name)
        
        print(f"✅ 完成！生成 {len(created_clips)} 个片段")
        return True

    def process_all_movies(self):
        """批量处理所有电影"""
        print("\n🚀 批量处理所有电影")
        print("=" * 40)
        
        # 检查AI配置
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置")
            return
        
        # 获取所有SRT文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 中无字幕文件")
            return
        
        # 按字符串排序（电影顺序）
        srt_files.sort()
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        
        success_count = 0
        for i, srt_file in enumerate(srt_files, 1):
            print(f"\n{'🎬'*3} 第 {i}/{len(srt_files)} 部 {'🎬'*3}")
            
            try:
                if self.process_single_movie(srt_file):
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理异常: {e}")
        
        print(f"\n🎉 批量处理完成")
        print(f"✅ 成功: {success_count}/{len(srt_files)} 部")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 50)
            print("🎬 电影剪辑系统")
            print("=" * 50)
            
            # 状态显示
            ai_status = "✅ 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"🤖 AI状态: {ai_status}")
            
            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]) if os.path.exists(self.videos_folder) else 0
            
            print(f"📝 字幕文件: {srt_count} 个")
            print(f"🎬 视频文件: {video_count} 个")
            
            print(f"\n🎯 功能菜单:")
            print("1. 🤖 配置AI接口")
            print("2. 🚀 一键智能剪辑")
            print("3. 📊 查看状态")
            print("0. ❌ 退出")
            
            try:
                choice = input("\n请选择 (0-3): ").strip()
                
                if choice == '0':
                    print("\n👋 谢谢使用！")
                    break
                elif choice == '1':
                    self.setup_ai_config()
                elif choice == '2':
                    if not self.ai_config.get('enabled'):
                        print("❌ 请先配置AI")
                        continue
                    self.process_all_movies()
                elif choice == '3':
                    self._show_status()
                else:
                    print("❌ 无效选择")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break

    def _show_status(self):
        """显示系统状态"""
        print(f"\n📊 系统状态")
        print("=" * 30)
        
        # AI配置
        if self.ai_config.get('enabled'):
            print(f"🤖 AI配置:")
            print(f"   类型: {self.ai_config.get('api_type')}")
            print(f"   提供商: {self.ai_config.get('provider')}")
            print(f"   模型: {self.ai_config.get('model')}")
        else:
            print("🤖 AI: 未配置")
        
        # 文件统计
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        print(f"\n📁 文件统计:")
        print(f"   字幕文件: {len(srt_files)} 个")
        
        if os.path.exists(self.videos_folder):
            video_files = [f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
            print(f"   视频文件: {len(video_files)} 个")
        
        if os.path.exists(self.clips_folder):
            clip_files = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
            print(f"   输出片段: {len(clip_files)} 个")

    def _safe_filename(self, name: str) -> str:
        """安全文件名"""
        return re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', name)[:20]

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

def main():
    """主函数"""
    try:
        system = MovieClipperSystem()
        system.show_main_menu()
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")

if __name__ == "__main__":
    main()
