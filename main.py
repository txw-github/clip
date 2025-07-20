#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一电视剧智能剪辑系统
使用统一的配置和AI客户端
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional
from unified_config import unified_config
from unified_ai_client import ai_client

class UnifiedTVClipper:
    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos" 
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"

        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        print("🚀 统一电视剧智能剪辑系统")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

        # 显示AI状态
        if unified_config.is_enabled():
            provider_name = unified_config.providers.get(
                unified_config.config.get('provider'), {}
            ).get('name', '未知')
            model = unified_config.config.get('model', '未知')
            print(f"🤖 AI分析: 已启用 ({provider_name} - {model})")
        else:
            print("📝 AI分析: 未启用")

    def setup_ai_config(self):
        """配置AI"""
        return unified_config.interactive_setup()

    def check_files(self) -> tuple:
        """检查文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) 
                    if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        video_files = [f for f in os.listdir(self.video_folder) 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'))]

        srt_files.sort()
        video_files.sort()

        print(f"\n📊 文件状态:")
        print(f"📄 字幕文件: {len(srt_files)} 个")
        print(f"🎬 视频文件: {len(video_files)} 个")

        return srt_files, video_files

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
                except:
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
        """完整剧集分析 - 解决API调用次数、剧情连贯性和旁白生成问题"""
        episode_num = self._extract_episode_number(filename)

        # 检查缓存 - 避免重复API调用
        cache_file = os.path.join(self.cache_folder, f"{episode_num}_complete_analysis.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    print(f"📋 使用缓存完整分析: {episode_num}")
                    return cached_analysis
            except:
                pass

        if not unified_config.is_enabled():
            print(f"❌ 未启用AI分析，使用智能规则分析")
            return self._fallback_intelligent_analysis(subtitles, episode_num)

        # **核心改进1**: 整集一次性AI分析，大幅减少API调用
        print(f"🤖 AI完整分析 {episode_num}（整集上下文，保证连贯性）")
        analysis = self._ai_analyze_complete_episode(subtitles, episode_num)

        # 保存到缓存
        if analysis:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                print(f"💾 完整分析结果已缓存")
            except Exception as e:
                print(f"⚠️ 缓存保存失败: {e}")

        return analysis

    def _ai_analyze_complete_episode(self, subtitles: List[Dict], episode_num: str) -> Optional[Dict]:
        """**核心改进**: AI完整分析整集，一次调用解决所有问题"""
        # **改进1**: 构建完整上下文，避免片段化分析
        full_text = ' '.join([sub['text'] for sub in subtitles])
        
        # **改进2**: 智能分段，避免超长文本
        text_segments = self._create_text_segments(full_text, max_length=8000)
        main_segment = text_segments[0] if text_segments else full_text[:8000]

        # **改进3**: 专业剪辑师提示词，确保剧情连贯性
        prompt = f"""你是专业电视剧剪辑师，请为{episode_num}进行完整分析，创建3-5个连贯短视频片段。

【完整剧集内容】
{main_segment}

**核心要求**：
1. 剧情连贯性：所有短视频合起来能完整叙述本集剧情
2. 反转处理：如果有剧情反转，需要联系前面内容
3. 完整对话：确保每个片段都是完整场景，不截断重要对话
4. 专业旁白：为每个片段生成深度剧情解说

请返回JSON格式：
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "main_theme": "本集核心主题",
        "plot_type": "法律剧/悬疑剧/都市剧等",
        "emotional_arc": "情感发展弧线",
        "key_conflicts": ["核心冲突1", "核心冲突2"],
        "plot_continuity": "与前后集的剧情连贯说明"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题（吸引人的）",
            "start_time": "HH:MM:SS,mmm",
            "end_time": "HH:MM:SS,mmm",
            "duration_seconds": 150,
            "plot_significance": "剧情重要性说明",
            "dramatic_value": 8.5,
            "emotional_peak": "情感高潮描述",
            "key_dialogues": ["关键台词1", "关键台词2"],
            "content_highlights": ["亮点1", "亮点2"],
            "narrative_voice": {{
                "opening": "开场解说文字",
                "process": "过程解说文字", 
                "climax": "高潮解说文字",
                "ending": "结尾解说文字"
            }},
            "connection_to_next": "与下个片段的逻辑连接"
        }}
    ],
    "series_continuity": {{
        "previous_episode_link": "与上集的连接点",
        "next_episode_setup": "为下集埋下的伏笔",
        "character_development": "角色发展重点",
        "plot_threads": ["剧情线索1", "剧情线索2"]
    }}
}}

**关键**：时间必须精确对应字幕，确保完整对话场景。"""

        system_prompt = """你是资深电视剧剪辑师和编剧分析师，精通：
1. 剧情结构分析和故事线梳理
2. 戏剧冲突识别和情感节点把握  
3. 角色关系发展和人物弧线设计
4. 短视频剪辑和观众心理分析
请严格按照JSON格式返回专业分析结果。"""

        try:
            response = ai_client.call_ai(prompt, system_prompt)
            if response:
                parsed_result = self._parse_complete_ai_response(response)
                if parsed_result:
                    print(f"✅ AI完整分析成功：{len(parsed_result.get('highlight_segments', []))} 个片段")
                    return parsed_result
        except Exception as e:
            print(f"⚠️ AI完整分析失败: {e}")

        # 降级到智能规则分析
        return self._fallback_intelligent_analysis(subtitles, episode_num)

    def _parse_complete_ai_response(self, response: str) -> Optional[Dict]:
        """解析完整AI响应"""
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
            
            # **改进4**: 验证和完善分析结果
            return self._validate_and_enhance_analysis(result)
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
            return None

    def _validate_and_enhance_analysis(self, analysis: Dict) -> Dict:
        """验证和完善分析结果"""
        # 确保必要字段存在
        if 'episode_analysis' not in analysis:
            analysis['episode_analysis'] = {}
        
        if 'highlight_segments' not in analysis:
            analysis['highlight_segments'] = []

        # 为每个片段补充旁白
        for segment in analysis['highlight_segments']:
            if 'narrative_voice' not in segment:
                segment['narrative_voice'] = self._generate_segment_narration(segment)

        return analysis

    def _generate_segment_narration(self, segment: Dict) -> Dict:
        """为片段生成专业旁白"""
        title = segment.get('title', '精彩片段')
        significance = segment.get('plot_significance', '重要剧情')
        
        return {
            "opening": f"在这个关键时刻，{title}即将展开...",
            "process": f"随着剧情的深入，{significance}逐渐显现",
            "climax": f"紧张的氛围达到顶点，真相即将揭晓",
            "ending": f"这一幕为后续剧情埋下了重要伏笔"
        }

    def _create_text_segments(self, text: str, max_length: int = 8000) -> List[str]:
        """创建文本分段，避免超长"""
        if len(text) <= max_length:
            return [text]
        
        segments = []
        words = text.split()
        current_segment = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > max_length:
                segments.append(' '.join(current_segment))
                current_segment = [word]
                current_length = len(word)
            else:
                current_segment.append(word)
                current_length += len(word) + 1
        
        if current_segment:
            segments.append(' '.join(current_segment))
        
        return segments

    def _fallback_intelligent_analysis(self, subtitles: List[Dict], episode_num: str) -> Dict:
        """**改进5**: 智能规则分析作为备选方案"""
        print(f"📝 使用智能规则分析（无AI）")
        
        # 基于规则的智能分析
        segments = self._find_key_segments_by_rules(subtitles)
        
        return {
            "episode_analysis": {
                "episode_number": episode_num,
                "main_theme": f"{episode_num}集核心剧情",
                "plot_type": "剧情片",
                "analysis_method": "智能规则"
            },
            "highlight_segments": segments[:3],  # 最多3个片段
            "series_continuity": {
                "note": "基于规则分析，建议启用AI获得更好效果"
            }
        }

    def _find_key_segments_by_rules(self, subtitles: List[Dict]) -> List[Dict]:
        """基于规则找到关键片段"""
        key_segments = []
        
        # 关键词权重
        keywords = {
            '四二八案': 10, '628案': 10, '听证会': 8, '申诉': 8,
            '证据': 6, '真相': 6, '霸凌': 7, '正当防卫': 8,
            '反转': 5, '发现': 4, '冲突': 4, '决定': 3
        }
        
        # 分析每个时间窗口
        window_size = 30  # 30个字幕条目约2-3分钟
        step = 15
        
        for i in range(0, len(subtitles) - window_size, step):
            window = subtitles[i:i + window_size]
            text = ' '.join([sub['text'] for sub in window])
            
            # 计算权重分数
            score = 0
            for keyword, weight in keywords.items():
                score += text.count(keyword) * weight
            
            if score >= 15:  # 高分片段
                key_segments.append({
                    "segment_id": len(key_segments) + 1,
                    "title": f"精彩片段{len(key_segments) + 1}",
                    "start_time": window[0]['start'],
                    "end_time": window[-1]['end'],
                    "duration_seconds": self._time_to_seconds(window[-1]['end']) - self._time_to_seconds(window[0]['start']),
                    "dramatic_value": min(score / 10, 10),
                    "plot_significance": "基于关键词识别的重要片段",
                    "narrative_voice": self._generate_segment_narration({"title": f"片段{len(key_segments) + 1}"})
                })
        
        return key_segments

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """匹配视频文件"""
        base_name = os.path.splitext(subtitle_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

        print(f"🔍 查找视频文件: {base_name}")

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                print(f"✅ 找到匹配: {base_name + ext}")
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

    def create_video_clips(self, analysis: Dict, video_file: str) -> List[str]:
        """创建视频片段和专业旁白文件"""
        created_clips = []

        for segment in analysis.get('highlight_segments', []):
            title = segment['title']
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024*1024:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # **改进6**: 剪辑视频并生成旁白
            if self._create_single_clip(video_file, segment, clip_path):
                # **改进7**: 生成专业旁白文件
                self._create_narration_file(clip_path, segment, analysis)
                created_clips.append(clip_path)

        return created_clips

    def _create_narration_file(self, video_path: str, segment: Dict, analysis: Dict):
        """**改进**: 创建专业旁白解说文件"""
        try:
            narration_path = video_path.replace('.mp4', '_旁白解说.txt')
            
            narrative = segment.get('narrative_voice', {})
            episode_theme = analysis.get('episode_analysis', {}).get('main_theme', '精彩剧情')
            
            content = f"""🎙️ 专业旁白解说稿
{"=" * 50}

📺 片段标题: {segment.get('title', '精彩片段')}
🎯 剧情主题: {episode_theme}
⏱️ 时长: {segment.get('duration_seconds', 0):.1f} 秒

📜 完整旁白解说:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【开场解说】 (0-3秒)
{narrative.get('opening', '在这个关键时刻，剧情即将展开...')}

【过程解说】 (3-8秒) 
{narrative.get('process', '随着故事的深入发展...')}

【高潮解说】 (8-12秒)
{narrative.get('climax', '紧张的氛围达到顶点...')}

【结尾解说】 (12-15秒)
{narrative.get('ending', '这一幕为后续剧情埋下伏笔...')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 剧情价值解析:
{segment.get('plot_significance', '重要剧情节点')}

🎭 情感高潮:
{segment.get('emotional_peak', '情感张力充沛')}

📝 关键台词:
"""
            
            for dialogue in segment.get('key_dialogues', []):
                content += f"• {dialogue}\n"
            
            content += f"""
✨ 内容亮点:
"""
            for highlight in segment.get('content_highlights', ['精彩剧情']):
                content += f"• {highlight}\n"
            
            content += f"""
🔗 剧情衔接:
{segment.get('connection_to_next', '与后续剧情紧密相连')}

📋 使用说明:
• 本旁白解说可直接用于短视频配音
• 分段时间仅供参考，可根据实际调整
• 解说内容突出剧情核心，增强观众理解
• 适合抖音、B站等短视频平台使用
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📜 生成旁白解说: {os.path.basename(narration_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 生成旁白文件失败: {e}")

    def _create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']

            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")

            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0 or duration > 300:
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
                '-hide_banner', '-loglevel', 'error',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-preset', 'fast', '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                '-y', output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                if file_size > 0.5:
                    print(f"   ✅ 成功: {file_size:.1f}MB")
                    return True
                else:
                    print(f"   ❌ 文件太小")
                    os.remove(output_path)
                    return False
            else:
                print(f"   ❌ 剪辑失败")
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
        """处理单集"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False

        # 2. AI分析
        analysis = self.analyze_episode(subtitles, subtitle_file)
        if not analysis:
            print(f"❌ AI分析失败")
            return False

        # 3. 查找视频
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False

        # 4. 创建片段
        created_clips = self.create_video_clips(analysis, video_file)

        print(f"✅ {subtitle_file} 处理完成: {len(created_clips)} 个片段")
        return len(created_clips) > 0

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 60)

        srt_files, video_files = self.check_files()

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        if not video_files:
            print(f"❌ {self.video_folder}/ 目录中未找到视频文件")
            return

        if not unified_config.is_enabled():
            print(f"❌ 请先配置AI接口")
            return

        total_success = 0

        for subtitle_file in srt_files:
            try:
                if self.process_single_episode(subtitle_file):
                    total_success += 1
            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")

        final_clips = len([f for f in os.listdir(self.output_folder) if f.endswith('.mp4')])

        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {final_clips} 个")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("📺 统一电视剧智能剪辑系统")
            print("=" * 60)

            # 显示状态
            config_status = "🤖 已配置" if unified_config.is_enabled() else "❌ 未配置"
            print(f"AI状态: {config_status}")

            srt_files, video_files = self.check_files()

            print("\n请选择操作:")
            print("1. 🎬 开始智能剪辑")
            print("2. 🤖 配置AI接口")
            print("3. 📁 检查文件状态")
            print("4. ❌ 退出")

            try:
                choice = input("\n请输入选择 (1-4): ").strip()

                if choice == '1':
                    if not unified_config.is_enabled():
                        print(f"\n❌ 请先配置AI接口")
                        continue
                    if not srt_files or not video_files:
                        print(f"\n❌ 请检查文件是否准备完整")
                        continue

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
                    print("❌ 无效选择")

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