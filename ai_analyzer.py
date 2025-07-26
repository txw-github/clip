
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI分析器 - 使用固定格式提示词确保返回结果一致性
"""

import json
import re
from typing import Dict, List, Optional
from api_config_helper import config_helper

class AIAnalyzer:
    def __init__(self):
        self.config = config_helper.load_config()
        
    def analyze_episode_with_fixed_format(self, subtitles: List[Dict], episode_context: str = "") -> Dict:
        """使用固定格式提示词分析剧集"""
        
        # 构建固定格式的提示词
        prompt = self._build_fixed_format_prompt(subtitles, episode_context)
        
        try:
            # 调用AI API
            response = config_helper.call_ai_api(prompt, self.config)
            
            if response:
                # 解析AI返回的JSON格式
                analysis = self._parse_ai_response(response)
                
                # 验证和补全必要字段
                analysis = self._validate_and_complete_analysis(analysis)
                
                return analysis
            else:
                return self._get_fallback_analysis()
                
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._get_fallback_analysis()
    
    def _build_fixed_format_prompt(self, subtitles: List[Dict], episode_context: str) -> str:
        """构建固定格式的提示词"""
        
        # 提取部分字幕内容用于分析
        subtitle_text = ""
        for i, sub in enumerate(subtitles[:50]):  # 分析前50条字幕
            subtitle_text += f"[{sub['start']}] {sub['text']}\n"
        
        prompt = f"""你是专业的电视剧内容分析师，请按照严格的JSON格式分析以下剧集片段。

【分析内容】
剧集背景: {episode_context}
字幕内容（前50条）:
{subtitle_text}

【输出要求】
请严格按照以下JSON格式返回分析结果，不要添加任何其他文字：

{{
    "episode_theme": "E01：核心剧情主题（15字以内）",
    "genre_type": "legal/crime/romance/family/medical/business/general中的一种",
    "highlight_segments": [
        {{
            "title": "片段标题（如：关键证据揭露）",
            "start_time": "00:05:30,000",
            "end_time": "00:07:45,000", 
            "duration_seconds": 135,
            "plot_significance": "剧情重要意义（如：首次提及张园涉案，颠覆旧案认知）",
            "professional_narration": {{
                "opening_line": "开场引入（3秒内，如：法庭激辩即将开始）",
                "main_explanation": "核心解说（5-8秒，详细说明正在发生的事情）",
                "highlight_moment": "精彩强调（3秒内，突出最关键的时刻）",
                "closing_line": "结尾总结（2秒内，点题或制造悬念）",
                "full_script": "完整连贯的旁白解说稿（将上述4部分自然连接）"
            }},
            "highlight_tip": "一句话字幕亮点提示（如：💡真相即将大白，不容错过）",
            "emotional_tone": "tense/dramatic/romantic/warm/suspenseful中的一种",
            "content_summary": "片段内容摘要（50字以内）"
        }}
    ],
    "episode_continuity": {{
        "main_storyline": "本集主线剧情发展",
        "character_development": "主要角色发展变化", 
        "plot_progression": "剧情推进关键点",
        "next_episode_hook": "与下集的衔接点"
    }},
    "technical_analysis": {{
        "total_duration": 180,
        "segment_count": 2,
        "genre_confidence": 0.85,
        "analysis_quality": "high/medium/low"
    }}
}}

【特别要求】
1. professional_narration必须包含4个固定字段，每个字段控制在指定时长内
2. 时间格式必须是 HH:MM:SS,mmm 格式
3. highlight_tip必须以表情符号开头，简洁有力
4. 所有字段都必须填写，不能为空
5. 只返回JSON，不要任何解释文字

请开始分析："""

        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """解析AI返回的JSON响应"""
        try:
            # 清理响应文本
            response_text = response_text.strip()
            
            # 提取JSON部分
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            
            # 解析JSON
            analysis = json.loads(response_text)
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response_text[:200]}...")
            return self._get_fallback_analysis()
        except Exception as e:
            print(f"响应解析失败: {e}")
            return self._get_fallback_analysis()
    
    def _validate_and_complete_analysis(self, analysis: Dict) -> Dict:
        """验证和补全分析结果"""
        
        # 确保必要字段存在
        if 'episode_theme' not in analysis:
            analysis['episode_theme'] = "E01：精彩剧情片段"
        
        if 'genre_type' not in analysis:
            analysis['genre_type'] = "general"
        
        if 'highlight_segments' not in analysis:
            analysis['highlight_segments'] = []
        
        # 验证和修正每个片段
        for i, segment in enumerate(analysis['highlight_segments']):
            segment = self._validate_segment(segment, i+1)
            analysis['highlight_segments'][i] = segment
        
        # 确保其他必要字段
        if 'episode_continuity' not in analysis:
            analysis['episode_continuity'] = {
                "main_storyline": "剧情稳步发展",
                "character_development": "角色关系推进",
                "plot_progression": "故事线索展开",
                "next_episode_hook": "期待下集更多精彩"
            }
        
        if 'technical_analysis' not in analysis:
            total_duration = sum(seg.get('duration_seconds', 120) for seg in analysis['highlight_segments'])
            analysis['technical_analysis'] = {
                "total_duration": total_duration,
                "segment_count": len(analysis['highlight_segments']),
                "genre_confidence": 0.75,
                "analysis_quality": "medium"
            }
        
        return analysis
    
    def _validate_segment(self, segment: Dict, segment_num: int) -> Dict:
        """验证和修正单个片段"""
        
        # 基础字段验证
        if 'title' not in segment:
            segment['title'] = f"精彩片段{segment_num}"
        
        if 'start_time' not in segment:
            segment['start_time'] = "00:01:00,000"
        
        if 'end_time' not in segment:
            segment['end_time'] = "00:03:00,000"
        
        if 'duration_seconds' not in segment:
            segment['duration_seconds'] = 120
        
        # 验证professional_narration字段
        if 'professional_narration' not in segment:
            segment['professional_narration'] = {}
        
        narration = segment['professional_narration']
        
        # 确保旁白的4个固定字段
        if 'opening_line' not in narration:
            narration['opening_line'] = "精彩剧情即将上演"
        
        if 'main_explanation' not in narration:
            narration['main_explanation'] = "在这个关键时刻，主要角色面临重要选择，剧情紧张刺激"
        
        if 'highlight_moment' not in narration:
            narration['highlight_moment'] = "最精彩的部分即将到来"
        
        if 'closing_line' not in narration:
            narration['closing_line'] = "令人印象深刻"
        
        if 'full_script' not in narration:
            narration['full_script'] = f"{narration['opening_line']}。{narration['main_explanation']}，{narration['highlight_moment']}，{narration['closing_line']}。"
        
        # 其他必要字段
        if 'plot_significance' not in segment:
            segment['plot_significance'] = "推进剧情发展的重要节点"
        
        if 'highlight_tip' not in segment:
            segment['highlight_tip'] = "💡 精彩内容不容错过"
        
        if 'emotional_tone' not in segment:
            segment['emotional_tone'] = "dramatic"
        
        if 'content_summary' not in segment:
            segment['content_summary'] = "精彩对话和情节发展"
        
        return segment
    
    def _get_fallback_analysis(self) -> Dict:
        """获取备用分析结果"""
        return {
            "episode_theme": "E01：精彩剧情片段",
            "genre_type": "general",
            "highlight_segments": [
                {
                    "title": "精彩对话片段",
                    "start_time": "00:01:00,000",
                    "end_time": "00:03:00,000",
                    "duration_seconds": 120,
                    "plot_significance": "推进剧情发展的重要对话",
                    "professional_narration": {
                        "opening_line": "精彩剧情即将上演",
                        "main_explanation": "在这个重要时刻，角色们的对话揭示了关键信息",
                        "highlight_moment": "最精彩的部分正在进行",
                        "closing_line": "令人期待后续发展"
                    },
                    "highlight_tip": "💡 重要剧情发展，值得关注",
                    "emotional_tone": "dramatic",
                    "content_summary": "角色对话推进故事发展"
                }
            ],
            "episode_continuity": {
                "main_storyline": "剧情稳步推进",
                "character_development": "角色关系发展",
                "plot_progression": "故事线索展开",
                "next_episode_hook": "期待下集精彩内容"
            },
            "technical_analysis": {
                "total_duration": 120,
                "segment_count": 1,
                "genre_confidence": 0.6,
                "analysis_quality": "basic"
            }
        }
    
    def generate_srt_narration(self, professional_narration: Dict, video_duration: float) -> str:
        """将专业旁白转换为SRT字幕格式"""
        
        srt_content = ""
        subtitle_index = 1
        
        try:
            # 开场引入 (0-3秒)
            if professional_narration.get('opening_line'):
                srt_content += f"""{subtitle_index}
00:00:00,000 --> 00:00:03,000
{professional_narration['opening_line']}

"""
                subtitle_index += 1
            
            # 核心解说 (3-8秒)
            if professional_narration.get('main_explanation'):
                srt_content += f"""{subtitle_index}
00:00:03,000 --> 00:00:08,000
{professional_narration['main_explanation']}

"""
                subtitle_index += 1
            
            # 精彩强调 (从结尾倒数3秒开始)
            if professional_narration.get('highlight_moment'):
                end_time = int(video_duration)
                start_time = max(8, end_time - 3)
                
                start_formatted = f"00:00:{start_time:02d},000"
                end_formatted = f"00:00:{end_time:02d},000"
                
                srt_content += f"""{subtitle_index}
{start_formatted} --> {end_formatted}
{professional_narration['highlight_moment']}

"""
                subtitle_index += 1
            
            # 结尾总结 (最后1秒)
            if professional_narration.get('closing_line'):
                end_time = int(video_duration)
                start_time = max(end_time - 1, 0)
                
                start_formatted = f"00:00:{start_time:02d},000"
                end_formatted = f"00:00:{end_time:02d},000"
                
                srt_content += f"""{subtitle_index}
{start_formatted} --> {end_formatted}
{professional_narration['closing_line']}

"""
            
            return srt_content.strip()
            
        except Exception as e:
            print(f"SRT生成失败: {e}")
            return f"""1
00:00:00,000 --> 00:00:05,000
精彩内容正在播放

2
00:00:05,000 --> 00:00:10,000
{professional_narration.get('full_script', '请欣赏精彩剧情')}
"""

# 使用示例
def test_fixed_format_analysis():
    """测试固定格式分析"""
    analyzer = AIAnalyzer()
    
    # 模拟字幕数据
    sample_subtitles = [
        {"start": "00:01:00,000", "end": "00:01:03,000", "text": "这个案件有很多疑点"},
        {"start": "00:01:03,000", "end": "00:01:06,000", "text": "我们需要重新调查"},
        {"start": "00:01:06,000", "end": "00:01:09,000", "text": "真相可能不是我们想的那样"}
    ]
    
    analysis = analyzer.analyze_episode_with_fixed_format(sample_subtitles, "法律剧")
    
    print("固定格式分析结果:")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    # 测试SRT生成
    if analysis['highlight_segments']:
        segment = analysis['highlight_segments'][0]
        narration = segment['professional_narration']
        
        srt_content = analyzer.generate_srt_narration(narration, 120)
        print("\n生成的SRT旁白:")
        print(srt_content)

if __name__ == "__main__":
    test_fixed_format_analysis()
