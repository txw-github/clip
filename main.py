
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

        # 加载配置
        self.config = self._load_config()

        print("🚀 统一电视剧智能剪辑系统")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = 'config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"🤖 AI分析: 已启用 ({config.get('provider', '未知')})")
                    return config
            except Exception as e:
                print(f"⚠️ 配置加载失败: {e}")
        
        print("📝 AI分析: 未配置，请先配置API")
        return {}

    def setup_config(self):
        """配置系统"""
        print("\n🤖 系统配置")
        print("=" * 40)
        
        # 第一步：选择API类型
        print("1. 官方API")
        print("2. 中转API")
        
        api_type = input("请选择API类型 (1-2): ").strip()
        
        if api_type == "1":
            config = self._setup_official_api()
        elif api_type == "2":
            config = self._setup_proxy_api()
        else:
            print("❌ 无效选择")
            return
        
        if config:
            self._save_config(config)
            self.config = config
            print("✅ 配置保存成功")

    def _setup_official_api(self) -> Optional[Dict]:
        """配置官方API"""
        print("\n选择官方API提供商:")
        print("1. Google Gemini")
        print("2. OpenAI")
        
        provider = input("请选择 (1-2): ").strip()
        
        if provider == "1":
            api_key = input("请输入Gemini API密钥: ").strip()
            if not api_key:
                print("❌ API密钥不能为空")
                return None
            
            print("选择Gemini模型:")
            print("1. gemini-2.5-flash")
            print("2. gemini-2.5-pro")
            model_choice = input("请选择 (1-2): ").strip()
            model = "gemini-2.5-flash" if model_choice == "1" else "gemini-2.5-pro"
            
            return {
                "api_type": "official",
                "provider": "gemini",
                "api_key": api_key,
                "model": model
            }
            
        elif provider == "2":
            api_key = input("请输入OpenAI API密钥: ").strip()
            if not api_key:
                print("❌ API密钥不能为空")
                return None
                
            print("选择OpenAI模型:")
            print("1. gpt-3.5-turbo")
            print("2. gpt-4")
            print("3. gpt-4o")
            model_choice = input("请选择 (1-3): ").strip()
            
            models = {"1": "gpt-3.5-turbo", "2": "gpt-4", "3": "gpt-4o"}
            model = models.get(model_choice, "gpt-3.5-turbo")
            
            return {
                "api_type": "official", 
                "provider": "openai",
                "api_key": api_key,
                "model": model
            }
        
        return None

    def _setup_proxy_api(self) -> Optional[Dict]:
        """配置中转API"""
        print("\n中转API配置:")
        base_url = input("API地址 (如: https://www.chataiapi.com/v1): ").strip()
        api_key = input("API密钥: ").strip()
        
        if not all([base_url, api_key]):
            print("❌ API地址和密钥都不能为空")
            return None
        
        print("选择模型:")
        print("1. deepseek-r1")
        print("2. claude-3.5-sonnet")
        print("3. gpt-4o")
        print("4. 自定义")
        
        model_choice = input("请选择 (1-4): ").strip()
        
        models = {
            "1": "deepseek-r1",
            "2": "claude-3-5-sonnet-20240620", 
            "3": "gpt-4o"
        }
        
        if model_choice == "4":
            model = input("请输入自定义模型名称: ").strip()
        else:
            model = models.get(model_choice, "deepseek-r1")
        
        return {
            "api_type": "proxy",
            "provider": "custom",
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }

    def _save_config(self, config: Dict):
        """保存配置"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
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
        
        if not self.config:
            print(f"❌ 未配置API，无法进行AI分析")
            return None
        
        # 进行AI分析
        analysis = self._ai_analyze(subtitles, episode_num, filename)
        
        # 保存分析结果到缓存
        if analysis:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                print(f"💾 分析结果已缓存: {episode_num}")
            except Exception as e:
                print(f"⚠️ 缓存保存失败: {e}")
        
        return analysis

    def _ai_analyze(self, subtitles: List[Dict], episode_num: str, filename: str) -> Optional[Dict]:
        """AI智能分析"""
        # 构建上下文 - 使用更合理的取样
        total_subs = len(subtitles)
        sample_size = min(300, total_subs)  # 最多300条字幕
        
        # 均匀取样
        if total_subs > sample_size:
            step = total_subs // sample_size
            sampled_subtitles = [subtitles[i] for i in range(0, total_subs, step)][:sample_size]
        else:
            sampled_subtitles = subtitles
            
        context = ' '.join([sub['text'] for sub in sampled_subtitles])
        
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
            "start_time": "开始时间(格式: HH:MM:SS,mmm)",
            "end_time": "结束时间(格式: HH:MM:SS,mmm)",
            "description": "内容描述",
            "dramatic_value": 8.5
        }}
    ]
}}

注意：时间格式必须是HH:MM:SS,mmm格式，确保时间段合理且存在于字幕中。"""

        try:
            response = self._call_ai_api(prompt)
            if response:
                analysis = self._parse_ai_response(response)
                if analysis:
                    return analysis
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return None

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            if self.config.get('api_type') == 'official':
                return self._call_official_api(prompt)
            else:
                return self._call_proxy_api(prompt)
        except Exception as e:
            print(f"⚠️ API调用异常: {e}")
            return None

    def _call_official_api(self, prompt: str) -> Optional[str]:
        """调用官方API"""
        provider = self.config.get('provider')
        
        if provider == 'gemini':
            try:
                from google import genai
                
                client = genai.Client(api_key=self.config['api_key'])
                response = client.models.generate_content(
                    model=self.config['model'],
                    contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"⚠️ Gemini API调用失败: {e}")
                return None
        
        elif provider == 'openai':
            try:
                from openai import OpenAI
                
                client = OpenAI(api_key=self.config['api_key'])
                
                completion = client.chat.completions.create(
                    model=self.config['model'],
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
                api_key=self.config['api_key'],
                base_url=self.config['base_url']
            )
            
            completion = client.chat.completions.create(
                model=self.config['model'],
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
            title = segment['title']
            
            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)
            
            # 检查是否已存在且大小合理
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024*1024:  # 大于1MB
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue
            
            # 剪辑视频
            if self._create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)
        
        return created_clips

    def _create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")
            
            # 时间转换
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            if duration <= 0 or duration > 300:  # 最多5分钟
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
                '-hide_banner',
                '-loglevel', 'error',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                '-y',
                output_path
            ]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                if file_size > 0.5:  # 至少500KB
                    print(f"   ✅ 成功: {file_size:.1f}MB")
                    return True
                else:
                    print(f"   ❌ 文件太小: {file_size:.1f}MB")
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return False
            else:
                error_msg = result.stderr[:200] if result.stderr else '未知错误'
                print(f"   ❌ 剪辑失败: {error_msg}")
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
        if not analysis:
            print(f"❌ AI分析失败，跳过该集")
            return False
        
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
        
        if not self.config:
            print(f"❌ 未配置API，请先配置")
            return
        
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        print(f"🤖 AI分析: 已启用")
        
        # 处理每一集
        total_success = 0
        total_clips = 0
        
        for subtitle_file in srt_files:
            try:
                success = self.process_single_episode(subtitle_file)
                if success:
                    total_success += 1
                
                # 统计片段数
                clips_count = len([f for f in os.listdir(self.output_folder) if f.endswith('.mp4')])
                
            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")
        
        # 最终统计
        final_clips = len([f for f in os.listdir(self.output_folder) if f.endswith('.mp4')])
        
        print(f"\n📊 最终统计:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {final_clips} 个")

    def show_main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("📺 统一电视剧智能剪辑系统")
            print("=" * 60)
            
            # 显示状态
            config_status = "🤖 已配置" if self.config else "❌ 未配置"
            print(f"API状态: {config_status}")
            
            srt_files, video_files = self.check_files()
            
            print("\n请选择操作:")
            print("1. 🎬 开始智能剪辑")
            print("2. 🤖 配置API接口")
            print("3. 📁 检查文件状态")
            print("4. ❌ 退出")
            
            try:
                choice = input("\n请输入选择 (1-4): ").strip()
                
                if choice == '1':
                    if not self.config:
                        print(f"\n❌ 请先配置API接口")
                        continue
                    if not srt_files:
                        print(f"\n❌ 请先将字幕文件放入 {self.srt_folder}/ 目录")
                        continue
                    if not video_files:
                        print(f"\n❌ 请先将视频文件放入 {self.video_folder}/ 目录")
                        continue
                    
                    print("\n🚀 开始智能剪辑...")
                    self.process_all_episodes()
                
                elif choice == '2':
                    self.setup_config()
                
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
