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
                end = response.find("