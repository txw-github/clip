
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI分析器 - 使用大模型进行剧情分析
"""

import json
import requests
from typing import Dict, Any, Optional, List
from api_config_helper import config_helper

class AIAnalyzer:
    """AI分析器类"""
    
    def __init__(self):
        self.config = config_helper.load_config()
        self.enabled = self.config.get('enabled', False)
        
        if self.enabled:
            self.api_key = self.config.get('api_key')
            # 统一使用 base_url 字段
            self.base_url = self.config.get('base_url') or self.config.get('url', 'https://www.chataiapi.com/v1')
            self.model = self.config.get('model', 'claude-3-5-sonnet-20240620')
            self.api_type = self.config.get('api_type', 'openai_compatible')
            print(f"✅ AI分析器已启用: {self.config.get('provider', '未知')} / {self.model}")
            print(f"  📡 API类型: {self.api_type}")
            print(f"  🔗 API地址: {self.base_url}")
        else:
            print("📝 AI分析器未启用，使用纯规则分析")
    
    def analyze_dialogue_segment(self, dialogue_text: str, context: str = "") -> Dict[str, Any]:
        """分析对话片段的剧情价值"""
        if not self.enabled:
            return {"score": 5.0, "reasoning": "AI分析未启用"}
        
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(dialogue_text, context)
            
            # 调用AI API
            response = self._call_ai_api(prompt)
            
            if response:
                return self._parse_ai_response(response)
            else:
                return {"score": 5.0, "reasoning": "API调用失败"}
                
        except Exception as e:
            print(f"AI分析出错: {e}")
            return {"score": 5.0, "reasoning": f"分析错误: {str(e)}"}
    
    def _build_analysis_prompt(self, dialogue_text: str, context: str) -> str:
        """构建分析提示词"""
        return f"""
你是专业的影视剧情分析师，请分析以下对话片段的剧情价值。

【对话内容】
{dialogue_text}

【剧情背景】
{context}

请从以下维度评估（0-10分）：
1. 主线剧情推进度（核心案件、关键证据、重要决定）
2. 戏剧冲突强度（观点对立、情感爆发、真相反转）
3. 角色关系发展（情感变化、关系突破、成长转折）
4. 信息密度（关键线索、重要证词、案件突破）
5. 观众吸引力（悬念制造、情感共鸣、剧情张力）

请以JSON格式返回分析结果：
{{
    "score": 综合评分(0-10),
    "dimensions": {{
        "plot_progression": 主线推进分数,
        "conflict_intensity": 冲突强度分数,
        "character_development": 角色发展分数,
        "information_density": 信息密度分数,
        "audience_appeal": 观众吸引力分数
    }},
    "reasoning": "详细分析原因",
    "key_elements": ["关键要素1", "关键要素2", "关键要素3"],
    "emotional_arc": "情感弧线描述",
    "plot_significance": "剧情重要性说明"
}}
"""
    
    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API - 使用统一配置助手"""
        try:
            from api_config_helper import config_helper
            
            # 构建完整的提示
            full_prompt = f"""你是专业的影视剧情分析师，擅长识别电视剧中的精彩片段和剧情价值。

{prompt}"""
            
            # 使用统一的API调用方法
            response = config_helper.call_ai_api(full_prompt, self.config)
            
            if response:
                return response
            else:
                print(f"API调用失败: 返回空结果")
                return None
                
        except Exception as e:
            print(f"API调用出错: {e}")
            return None
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试解析JSON
            if "```json" in response_text:
                # 提取JSON部分
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # 寻找JSON对象
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start != -1 and end > start:
                    json_text = response_text[start:end]
                else:
                    json_text = response_text
            
            result = json.loads(json_text)
            
            # 确保必要字段存在
            if "score" not in result:
                result["score"] = 5.0
            
            return result
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试提取数字评分
            import re
            score_match = re.search(r'评分[：:]\s*(\d+(?:\.\d+)?)', response_text)
            if score_match:
                score = float(score_match.group(1))
            else:
                score = 5.0
            
            return {
                "score": score,
                "reasoning": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "key_elements": ["AI分析内容"],
                "emotional_arc": "情感分析",
                "plot_significance": "剧情重要性"
            }
    
    def analyze_episode_theme(self, episode_content: str, episode_num: int) -> Dict[str, Any]:
        """分析整集的主题和核心冲突"""
        if not self.enabled:
            return {"theme": f"第{episode_num}集", "core_conflict": "剧情发展"}
        
        try:
            prompt = f"""
分析第{episode_num}集的核心主题和主要冲突点。

【剧集内容概要】
{episode_content[:2000]}...

请分析：
1. 这一集的核心主题是什么？
2. 主要的戏剧冲突点在哪里？
3. 推荐的剪辑主题名称

以JSON格式返回：
{{
    "theme": "剪辑主题名称",
    "core_conflict": "核心冲突描述",
    "key_scenes": ["关键场景1", "关键场景2"],
    "emotional_peak": "情感高潮点",
    "next_episode_hook": "与下集的衔接点"
}}
"""
            
            response = self._call_ai_api(prompt)
            if response:
                return self._parse_ai_response(response)
            else:
                return {"theme": f"第{episode_num}集", "core_conflict": "剧情发展"}
                
        except Exception as e:
            print(f"主题分析出错: {e}")
            return {"theme": f"第{episode_num}集", "core_conflict": "剧情发展"}

# 全局AI分析器实例
ai_analyzer = AIAnalyzer()
