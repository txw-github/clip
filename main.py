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
        from api_config_helper import config_helper
        
        new_config = config_helper.interactive_setup()
        if new_config.get('enabled'):
            self.ai_config = new_config
            print("✅ AI配置已更新")
        else:
            print("⚠️ AI配置未更新")

    

    def save_ai_config(self, config: Dict) -> bool:
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def test_current_connection(self):
        """测试当前AI连接"""
        print("\n🔍 AI连接测试")
        print("=" * 40)
        
        if not self.ai_config.get('enabled'):
            print("❌ 未找到AI配置")
            print("💡 请先配置AI接口")
            input("\n按回车键返回...")
            return
        
        print("📋 当前配置信息:")
        print(f"   🏷️  服务商: {self.ai_config.get('provider', '未知')}")
        print(f"   🤖 模型: {self.ai_config.get('model', '未知')}")
        print(f"   🔗 类型: {self.ai_config.get('api_type', '未知')}")
        if self.ai_config.get('base_url'):
            print(f"   🌐 地址: {self.ai_config['base_url']}")
        print(f"   🔑 密钥: {self.ai_config.get('api_key', '')[:10]}...")
        print()
        
        # 执行连接测试
        print("🔍 正在测试连接...")
        success = self.test_api_connection(self.ai_config)
        
        if success:
            print("\n" + "="*50)
            print("🎉 连接测试成功！AI接口工作正常")
            print("=" * 50)
            
            # 进行功能测试
            print("\n🧪 进行功能测试...")
            test_prompt = "请简单介绍一下电视剧剧情分析的重要性，回复不超过50字"
            
            try:
                response = self.call_ai_api(test_prompt, "你是专业的影视分析师")
                if response:
                    print("✅ AI功能测试成功")
                    print(f"📝 AI回复预览: {response[:100]}...")
                else:
                    print("⚠️  AI功能测试失败，但连接正常")
            except Exception as e:
                print(f"⚠️  AI功能测试异常: {e}")
                
        else:
            print("\n" + "="*50)
            print("❌ 连接测试失败")
            print("=" * 50)
            print("🔧 建议解决方案:")
            print("1. 检查网络连接")
            print("2. 验证API密钥")
            print("3. 确认服务商状态")
            print("4. 重新配置API")
            
            provider = self.ai_config.get('provider', '')
            if provider == 'openai':
                print("\n📞 OpenAI状态页: https://status.openai.com/")
            elif provider == 'deepseek':
                print("\n📞 DeepSeek文档: https://platform.deepseek.com/")
            elif provider == 'gemini':
                print("\n📞 Google AI文档: https://ai.google.dev/")
        
        input("\n按回车键返回...")

    def test_api_connection(self, config: Dict) -> bool:
        """测试API连接"""
        from api_config_helper import config_helper
        
        if config.get('api_type') == 'official' and config.get('provider') == 'gemini':
            return config_helper._test_gemini_official(config)
        else:
            return config_helper._test_openai_compatible(config)

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
        from api_config_helper import config_helper
        return config_helper.call_ai_api(prompt, self.ai_config, system_prompt)

    def analyze_episode_with_ai(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """使用AI分析整集"""
        if not self.ai_config.get('enabled'):
            print(f"⚠️ AI未启用，跳过 {filename}")
            return None

        # 构建完整上下文
        full_context = self.build_complete_context(subtitles)
        episode_num = self.extract_episode_number(filename)

        prompt = f"""你是资深电视剧剪辑师，需要分析第{episode_num}集内容，找出最适合制作短视频的精彩片段。

【剧集字幕内容】
{full_context}

【分析要求】
1. 找出3-5个最精彩的片段，每个片段时长2-3分钟
2. 优先选择戏剧冲突强烈、情感张力大的场景
3. 确保片段有完整的故事起承转合
4. 每个片段都要有吸引观众的亮点

【输出格式】
请严格按照JSON格式输出，不要添加任何解释文字：

{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre_type": "推测的剧情类型（如：悬疑、爱情、家庭、职场等）",
        "main_theme": "本集核心主题（一句话概括）"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "吸引人的片段标题",
            "start_time": "精确的开始时间（格式：00:XX:XX,XXX）",
            "end_time": "精确的结束时间（格式：00:XX:XX,XXX）",
            "duration_seconds": 片段时长秒数,
            "plot_significance": "这个片段在剧情中的重要作用",
            "professional_narration": "为这个片段写的专业解说词，要生动有趣，能吸引观众",
            "highlight_tip": "一句话提示观众关注的精彩点",
            "content_summary": "片段内容简要概括"
        }}
    ]
}}

注意：
- 时间格式必须准确，从字幕中选择真实存在的时间点
- 旁白解说要通俗易懂，避免过于专业的术语
- 每个片段都要有明确的看点和价值"""

        system_prompt = "你是专业的影视剪辑师和内容分析专家，擅长识别电视剧中的精彩片段并制作吸引人的短视频。请严格按照JSON格式输出，确保时间格式正确。"

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
            segment_id = segment.get('segment_id', 1)
            title = segment.get('title', '精彩片段')

            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}_seg{segment_id}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 检查是否已存在且完整
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:  # 至少1KB
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                
                # 检查旁白文件是否存在
                narration_path = clip_path.replace('.mp4', '_旁白解说.txt')
                if not os.path.exists(narration_path):
                    self.create_narration_file(clip_path, segment)
                
                # 检查SRT文件是否存在
                srt_path = clip_path.replace('.mp4', '_旁白字幕.srt')
                if not os.path.exists(srt_path):
                    self.create_srt_narration(clip_path, segment)
                
                continue

            # 验证时间格式
            start_time = segment.get('start_time', '')
            end_time = segment.get('end_time', '')
            
            if not start_time or not end_time:
                print(f"⚠️ 跳过无效时间片段: {title}")
                continue

            # 剪辑视频
            if self.create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)
                # 生成旁白文件
                self.create_narration_file(clip_path, segment)
                # 生成SRT字幕
                self.create_srt_narration(clip_path, segment)
            else:
                print(f"❌ 片段创建失败: {title}")

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

            # 安全获取旁白内容
            professional_narration = segment.get('professional_narration', '')
            if isinstance(professional_narration, str):
                # 如果是字符串，直接使用
                narration_text = professional_narration
            elif isinstance(professional_narration, dict):
                # 如果是字典，提取内容
                narration_text = professional_narration.get('full_script', professional_narration.get('full_narration', '暂无旁白'))
            else:
                narration_text = '暂无旁白'

            content = f"""🎙️ {segment['title']} - 专业旁白解说
{"=" * 60}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration_seconds', 0)} 秒
• 重要性: {segment.get('plot_significance', '重要剧情片段')}

🎙️ 专业旁白解说:
{narration_text}

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

            # 安全获取旁白内容
            professional_narration = segment.get('professional_narration', '')
            duration = segment.get('duration_seconds', 120)

            if self.ai_config.get('enabled') and professional_narration:
                try:
                    from ai_analyzer import AIAnalyzer
                    analyzer = AIAnalyzer()
                    
                    # 确保传递字典格式
                    if isinstance(professional_narration, str):
                        narration_dict = {'full_narration': professional_narration}
                    else:
                        narration_dict = professional_narration
                    
                    srt_content = analyzer.generate_srt_narration(narration_dict, duration)
                except Exception as ai_error:
                    print(f"   ⚠️ AI SRT生成失败: {ai_error}")
                    # 回退到基础生成
                    srt_content = self._generate_basic_srt(segment, duration)
            else:
                # 基础SRT生成
                srt_content = self._generate_basic_srt(segment, duration)

            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)

            print(f"   🎬 SRT字幕: {os.path.basename(srt_path)}")

        except Exception as e:
            print(f"   ⚠️ SRT生成失败: {e}")

    def _generate_basic_srt(self, segment: Dict, duration: int) -> str:
        """生成基础SRT字幕"""
        title = segment.get('title', '精彩片段')
        highlight_tip = segment.get('highlight_tip', '精彩内容正在播放')
        
        # 确保时长不超过99分钟（SRT格式限制）
        end_minutes = min(duration // 60, 99)
        end_seconds = duration % 60
        
        return f"""1
00:00:00,000 --> 00:00:05,000
{title}

2
00:00:05,000 --> 00:{end_minutes:02d}:{end_seconds:02d},000
{highlight_tip}
"""

    def get_analysis_cache_path(self, subtitle_file: str) -> str:
        """获取分析缓存文件路径"""
        # 生成基于文件内容的缓存key
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        try:
            with open(subtitle_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        except:
            content_hash = hashlib.md5(subtitle_file.encode()).hexdigest()[:12]
        
        cache_filename = f"{os.path.splitext(subtitle_file)[0]}_{content_hash}.json"
        return os.path.join(self.cache_folder, cache_filename)

    def load_analysis_cache(self, subtitle_file: str) -> Optional[Dict]:
        """加载分析缓存"""
        cache_path = self.get_analysis_cache_path(subtitle_file)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save_analysis_cache(self, subtitle_file: str, analysis: Dict):
        """保存分析缓存"""
        cache_path = self.get_analysis_cache_path(subtitle_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def process_single_episode(self, subtitle_file: str) -> Optional[bool]:
        """处理单集完整流程"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 检查分析缓存
        cached_analysis = self.load_analysis_cache(subtitle_file)
        if cached_analysis:
            print(f"💾 使用缓存的分析结果")
            analysis = cached_analysis
        else:
            # 2. 解析字幕
            subtitle_path = os.path.join(self.srt_folder, subtitle_file)
            subtitles = self.parse_subtitle_file(subtitle_path)

            if not subtitles:
                print(f"❌ 字幕解析失败")
                return False

            # 3. AI分析
            if self.ai_config.get('enabled'):
                analysis = self.analyze_episode_with_ai(subtitles, subtitle_file)
                if not analysis:
                    print(f"❌ AI分析失败，跳过此集")
                    return False
                
                # 保存到缓存
                self.save_analysis_cache(subtitle_file, analysis)
            else:
                analysis = None
                print(f"⚠️ AI未启用，跳过 {subtitle_file} 的AI分析")

        if analysis is None:
            print(f"⏸️ AI不可用，{subtitle_file} 已跳过")
            return None
        elif not analysis:
            print(f"❌ AI分析失败，跳过此集")
            return False

        # 4. 找到视频文件
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 5. 创建视频片段（检查已存在的片段）
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
            if self.ai_config.get('enabled'):
                provider = self.ai_config.get('provider', '未知')
                model = self.ai_config.get('model', '未知模型')
                ai_status = f"🤖 已配置 ({provider} - {model})"
                
                # 显示连接状态指示
                try:
                    # 快速测试连接状态（不输出详细信息）
                    test_success = self.test_api_connection(self.ai_config)
                    connection_status = "🟢 连接正常" if test_success else "🔴 连接异常"
                except:
                    connection_status = "🟡 状态未知"
                
                print(f"AI状态: {ai_status} {connection_status}")
            else:
                print(f"AI状态: ❌ 未配置")

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
            if self.ai_config.get('enabled'):
                print("5. 🔍 测试AI连接")
                print("0. ❌ 退出系统")
            else:
                print("0. ❌ 退出系统")

            try:
                max_choice = "5" if self.ai_config.get('enabled') else "4"
                choice = input(f"\n请选择操作 (0-{max_choice}): ").strip()

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
                elif choice == '5' and self.ai_config.get('enabled'):
                    self.test_current_connection()
                elif choice == '0':
                    print("\n👋 感谢使用智能电视剧剪辑系统！")
                    break
                else:
                    print(f"❌ 无效选择，请输入0-{max_choice}")

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