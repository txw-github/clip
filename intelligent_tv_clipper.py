#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整智能电视剧剪辑系统
解决所有核心问题：
1. 实际剪辑生成短视频和旁白
2. 全文分析减少API调用
3. 保证剧情连贯性和反转处理
4. 生成专业剧情分析旁白
5. 确保对话完整性
"""

import os
import re
import json
import hashlib
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
from unified_config import unified_config
from unified_ai_client import ai_client

class IntelligentTVClipper:
    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.video_folder = "videos"
        self.output_folder = "clips"
        self.cache_folder = "analysis_cache"
        self.narration_folder = "narrations"

        # 创建必要目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, 
                      self.cache_folder, self.narration_folder]:
            os.makedirs(folder, exist_ok=True)

        print("🎬 完整智能电视剧剪辑系统")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎥 视频目录: {self.video_folder}/")
        print(f"✂️ 输出目录: {self.output_folder}/")
        print(f"🎙️ 旁白目录: {self.narration_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件，智能修正错误"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试多种编码读取
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue

        if not content:
            print("❌ 字幕文件读取失败")
            return []

        # 智能错别字修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            '員': '员', '數': '数', '務': '务', '險': '险', '種': '种'
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
                                'text': text,
                                'start_seconds': self._time_to_seconds(start_time),
                                'end_seconds': self._time_to_seconds(end_time)
                            })
                except:
                    continue

        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析缓存路径"""
        file_hash = self._get_file_hash(srt_file)
        base_name = os.path.splitext(os.path.basename(srt_file))[0]
        return os.path.join(self.cache_folder, f"{base_name}_{file_hash}_analysis.json")

    def _get_file_hash(self, filepath: str) -> str:
        """获取文件内容哈希值"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except:
            return "unknown"

    def load_cached_analysis(self, srt_file: str) -> Optional[Dict]:
        """加载缓存的分析结果"""
        cache_path = self.get_analysis_cache_path(srt_file)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                print(f"📂 使用缓存分析: {os.path.basename(srt_file)}")
                return analysis
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
        return None

    def save_analysis_cache(self, srt_file: str, analysis: Dict):
        """保存分析结果到缓存"""
        cache_path = self.get_analysis_cache_path(srt_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"💾 保存分析缓存: {os.path.basename(srt_file)}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def ai_analyze_full_episode(self, subtitles: List[Dict], episode_name: str) -> Optional[Dict]:
        """AI分析整集内容 - 全文分析减少API调用"""
        if not unified_config.is_enabled():
            print("❌ AI未启用，无法进行分析")
            return None

        episode_num = self._extract_episode_number(episode_name)

        # 构建完整剧情文本 - 全文输入保证连贯性
        full_context = []
        for sub in subtitles:
            timestamp = f"[{sub['start']}]"
            full_context.append(f"{timestamp} {sub['text']}")

        complete_script = '\n'.join(full_context)

        # 专业剧情分析提示词
        prompt = f"""你是专业的电视剧剪辑师和剧情分析专家。请对这一集进行深度分析，识别出3-4个最精彩且连贯的片段用于短视频制作。

【集数】{episode_num}
【完整剧情内容】
{complete_script}

请进行专业分析并返回JSON格式结果：

{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "main_storyline": "主要故事线描述",
        "key_characters": ["主要角色1", "主要角色2"],
        "plot_progression": ["情节发展1", "情节发展2"],
        "dramatic_arc": "整体戏剧弧线",
        "emotional_journey": "情感历程",
        "plot_twists": ["反转点1", "反转点2"],
        "continuity_points": ["与前集联系", "为后集铺垫"]
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题",
            "start_time": "00:05:30,000",
            "end_time": "00:08:45,000",
            "plot_significance": "剧情重要性说明",
            "dramatic_tension": 8.5,
            "emotional_impact": 9.0,
            "dialogue_quality": 8.0,
            "story_progression": "推进主线剧情",
            "character_development": "角色发展描述",
            "visual_elements": ["视觉亮点1", "视觉亮点2"],
            "key_dialogues": [
                {{"speaker": "角色名", "line": "关键台词", "timestamp": "00:06:15,000"}},
                {{"speaker": "角色名", "line": "重要对话", "timestamp": "00:07:20,000"}}
            ],
            "narrative_analysis": {{
                "setup": "情节铺垫",
                "conflict": "核心冲突",
                "climax": "高潮部分",
                "resolution": "解决方案",
                "hook": "悬念设置"
            }},
            "connection_to_series": {{
                "previous_reference": "与前面剧情的联系",
                "future_setup": "为后续情节的铺垫",
                "series_importance": "在整部剧中的重要性"
            }}
        }}
    ],
    "series_continuity": {{
        "previous_episode_connections": ["与前集的联系1", "与前集的联系2"],
        "next_episode_setup": ["为下集的铺垫1", "为下集的铺垫2"],
        "overarching_themes": ["总体主题1", "总体主题2"],
        "character_arcs": {{"角色名": "角色发展轨迹"}}
    }},
    "narrative_coherence": {{
        "story_flow": "故事流畅性评估",
        "logical_consistency": "逻辑一致性",
        "emotional_consistency": "情感一致性",
        "pacing_analysis": "节奏分析"
    }}
}}

分析要求：
1. 确保片段时间在字幕范围内且格式为HH:MM:SS,mmm
2. 每个片段2-3分钟，包含完整的戏剧结构
3. 片段之间要有逻辑联系，能完整叙述剧情
4. 特别关注反转情节与前面剧情的联系
5. 确保对话完整性，不截断句子
6. 分析要深度专业，适合制作旁白解说"""

        try:
            print(f"🤖 AI分析整集内容...")
            response = ai_client.call_ai(prompt, "你是专业的电视剧剪辑师和剧情分析专家。")

            if not response:
                print("❌ AI分析失败")
                return None

            # 解析AI响应
            analysis = self._parse_ai_response(response)
            if not analysis:
                print("❌ AI响应解析失败")
                return None

            # 验证和修正时间段
            validated_segments = []
            for segment in analysis.get('highlight_segments', []):
                if self._validate_and_fix_segment(segment, subtitles):
                    validated_segments.append(segment)

            if not validated_segments:
                print("❌ 没有有效的片段")
                return None

            analysis['highlight_segments'] = validated_segments
            return analysis

        except Exception as e:
            print(f"❌ AI分析出错: {e}")
            return None

    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON内容
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            print(f"原始响应: {response}")
            return None
        except Exception as e:
            print(f"❌ 解析AI响应出错: {e}")
            return None

    def _validate_and_fix_segment(self, segment: Dict, subtitles: List[Dict]) -> bool:
        """验证并修正时间段"""
        start_time = segment['start_time']
        end_time = segment['end_time']

        # 转换为秒数
        start_seconds = self._time_to_seconds(start_time)
        end_seconds = self._time_to_seconds(end_time)

        # 查找最接近的字幕条目
        closest_start = None
        closest_end = None

        for sub in subtitles:
            if abs(sub['start_seconds'] - start_seconds) <= 10:
                closest_start = sub
            if abs(sub['end_seconds'] - end_seconds) <= 10:
                closest_end = sub

        # 如果找到，则更新时间
        if closest_start:
            segment['start_time'] = closest_start['start']
            start_seconds = closest_start['start_seconds']
        if closest_end:
            segment['end_time'] = closest_end['end']
            end_seconds = closest_end['end_seconds']

        # 验证时间顺序
        if start_seconds >= end_seconds:
            print(f"⚠️ 时间段无效: {start_time} --> {end_time}")
            return False

        return True

    def _time_to_seconds(self, time_str: str) -> float:
        """时间字符串转秒数"""
        try:
            time_obj = datetime.strptime(time_str, '%H:%M:%S,%f')
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000.0
        except ValueError:
            time_obj = datetime.strptime(time_str, '%H:%M:%S,%f')
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000.0

    def _safe_filename(self, title: str) -> str:
        """创建安全的文件名"""
        safe_title = re.sub(r'[^\w\s]', '', title)
        safe_title = safe_title.replace(' ', '_')
        return safe_title[:60]  # 限制长度

    def _find_video_file(self, episode_name: str) -> Optional[str]:
        """查找对应的视频文件"""
        for filename in os.listdir(self.video_folder):
            if episode_name in filename and filename.lower().endswith(('.mp4', '.avi', '.mkv')):
                return os.path.join(self.video_folder, filename)
        return None

    def _extract_episode_number(self, episode_name: str) -> str:
        """提取剧集号码"""
        match = re.search(r'第(\d+)集', episode_name)
        if match:
            return match.group(1)
        return "未知集数"

    def _clip_video_segment(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """剪辑视频片段"""
        start_time = segment['start_time'].replace(',', '.')
        end_time = segment['end_time'].replace(',', '.')

        try:
            # 计算持续时间
            start_seconds = self._time_to_seconds(start_time.replace('.', ','))
            end_seconds = self._time_to_seconds(end_time.replace('.', ','))
            duration = end_seconds - start_seconds

            # 构建ffmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', start_time,
                '-t', str(duration),
                '-c', 'copy',  # 使用copy避免重新编码
                output_path
            ]

            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ 剪辑命令: {' '.join(cmd)}")
            print(f"   ✅ 剪辑输出: {result.stderr}")  # ffmpeg输出到stderr

            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 剪辑失败: {e.stderr}")
            return False
        except Exception as e:
            print(f"   ❌ 剪辑出错: {e}")
            return False

    def create_clip_with_narration(self, analysis: Dict, srt_file: str) -> bool:
        """创建剪辑片段并生成旁白 - 一体化流程"""
        print(f"\n🎬 开始剪辑并生成旁白...")

        episode_name = os.path.splitext(os.path.basename(srt_file))[0]
        video_file = self._find_video_file(episode_name)

        if not video_file:
            print(f"❌ 找不到对应视频: {episode_name}")
            return False

        print(f"🎥 源视频: {os.path.basename(video_file)}")

        success_count = 0

        for i, segment in enumerate(analysis['highlight_segments']):
            print(f"\n📹 剪辑片段 {i+1}: {segment['title']}")

            # 生成输出文件名
            safe_title = self._safe_filename(segment['title'])
            clip_filename = f"{episode_name}_{safe_title}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 旁白文件路径
            narration_filename = f"{episode_name}_{safe_title}_旁白.txt"
            narration_path = os.path.join(self.narration_folder, narration_filename)

            # 检查是否已存在完整的剪辑和旁白
            if os.path.exists(clip_path) and os.path.exists(narration_path):
                print(f"✅ 片段和旁白已存在: {clip_filename}")
                success_count += 1
                continue

            # 剪辑视频
            print(f"   ⏱️ 时间: {segment['start_time']} --> {segment['end_time']}")
            if self._clip_video_segment(video_file, segment, clip_path):
                print(f"   ✅ 视频剪辑完成")

                # 立即生成对应的旁白
                print(f"   🎙️ 生成旁白中...")
                narration = self._generate_segment_narration(segment, analysis)

                # 保存旁白文件
                self._save_narration_file(narration_path, segment, narration)

                print(f"   ✅ 旁白生成完成: {narration_filename}")
                success_count += 1
            else:
                print(f"   ❌ 剪辑失败: {segment['title']}")

        print(f"\n📊 剪辑完成: {success_count}/{len(analysis['highlight_segments'])} 个片段成功")
        return success_count > 0

    def _save_narration_file(self, narration_path: str, segment: Dict, narration: Dict):
        """保存旁白文件"""
        with open(narration_path, 'w', encoding='utf-8') as f:
            f.write(f"片段标题: {segment['title']}\n")
            f.write(f"时间段: {segment['start_time']} --> {segment['end_time']}\n")
            f.write(f"剧情重要性: {segment['plot_significance']}\n")
            f.write(f"戏剧张力: {segment.get('dramatic_tension', 'N/A')}\n")
            f.write(f"情感冲击: {segment.get('emotional_impact', 'N/A')}\n\n")

            f.write("=== 旁白内容 ===\n")
            f.write(f"开场白: {narration['opening']}\n")
            f.write(f"过程解说: {narration['process']}\n")
            f.write(f"亮点强调: {narration['highlight']}\n")
            f.write(f"结尾: {narration['ending']}\n\n")

            f.write("=== 完整旁白 ===\n")
            f.write(f"{narration['full_narration']}\n\n")

            if 'timing' in narration:
                f.write("=== 时间安排 ===\n")
                for section, timing in narration['timing'].items():
                    f.write(f"{section}: {timing[0]}-{timing[1]}秒\n")

            if 'key_dialogues' in segment:
                f.write("\n=== 关键台词 ===\n")
                for dialogue in segment['key_dialogues']:
                    f.write(f"[{dialogue['timestamp']}] {dialogue['speaker']}: {dialogue['line']}\n")

    def _generate_segment_narration(self, segment: Dict, analysis: Dict) -> Dict:
        """为片段生成专业旁白"""
        if not unified_config.is_enabled():
            # 使用模板生成基础旁白
            return self._generate_template_narration(segment)

        # 使用AI生成专业旁白
        context = analysis.get('episode_analysis', {})
        episode_theme = context.get('main_storyline', '')

        # 提取关键对话作为参考
        key_dialogues = segment.get('key_dialogues', [])
        dialogue_context = ""
        if key_dialogues:
            dialogue_context = "\n关键对话：\n"
            for d in key_dialogues[:3]:  # 只取前3个
                dialogue_context += f"- {d['speaker']}: {d['line']}\n"

        prompt = f"""你是专业的电视剧短视频旁白解说员。请为这个精彩片段生成专业的解说旁白。

片段信息：
标题：{segment['title']}
时间：{segment['start_time']} --> {segment['end_time']}
剧情重要性：{segment['plot_significance']}
故事发展：{segment.get('story_progression', '')}
角色发展：{segment.get('character_development', '')}
剧集主题：{episode_theme}{dialogue_context}

请生成专业的4段式旁白：
1. 开场白（2-3秒）：抓住观众注意力的开场
2. 过程解说（3-5秒）：解释核心情节和人物动机
3. 亮点强调（2-3秒）：突出最精彩的戏剧冲突
4. 结尾（1-2秒）：制造悬念或情感共鸣

旁白要求：
- 语言简洁有力，节奏感强
- 突出戏剧张力和情感冲突
- 适合短视频快节奏观看
- 避免过度剧透，保持悬念
- 总时长8-12秒

请返回JSON格式：
{{
    "opening": "开场白文本",
    "process": "过程解说文本",
    "highlight": "亮点强调文本", 
    "ending": "结尾文本",
    "full_narration": "完整连贯的旁白文本",
    "timing": {{
        "opening": [0, 3],
        "process": [3, 8], 
        "highlight": [8, 11],
        "ending": [11, 12]
    }}
}}"""

        try:
            response = ai_client.call_ai(prompt, "你是专业的短视频旁白解说员。")
            if response:
                parsed = self._parse_narration_response(response)
                if parsed:
                    return parsed
        except Exception as e:
            print(f"   ⚠️ AI旁白生成失败: {e}")

        # 降级到模板生成
        return self._generate_template_narration(segment)

    def _generate_template_narration(self, segment: Dict) -> Dict:
        """使用模板生成基础旁白"""
        title = segment['title']
        significance = segment.get('plot_significance', '')

        # 根据标题内容智能生成旁白
        if "案件" in title or "法庭" in title:
            opening = f"法律剧情的关键时刻，{title}即将揭晓。"
            process = f"我们看到{significance}，正义与法律的较量正在展开。"
            highlight = "最紧张的是法庭上的激烈辩论，真相即将大白。"
            ending = "这个案件的走向将如何发展？"
        elif "情感" in title or "关系" in title:
            opening = f"感人的情感片段，{title}牵动人心。"
            process = f"我们看到{significance}，人物关系发生重要变化。"
            highlight = "最动人的是角色之间的真情流露，令人动容。"
            ending = "这段情感将如何影响他们的未来？"
        else:
            opening = f"精彩的剧情片段，{title}正在上演。"
            process = f"我们看到{significance}，故事迎来重要转折。"
            highlight = "最精彩的是剧情的意外发展，让人目不转睛。"
            ending = "后续剧情将如何展开？让我们继续关注。"

        full_narration = f"{opening} {process} {highlight} {ending}"

        return {
            "opening": opening,
            "process": process,
            "highlight": highlight,
            "ending": ending,
            "full_narration": full_narration,
            "timing": {
                "opening": [0, 3],
                "process": [3, 8],
                "highlight": [8, 11],
                "ending": [11, 12]
            }
        }