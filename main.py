
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一电视剧智能剪辑系统
解决剪辑时长控制、跨集连贯性、专业旁白优化问题
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
        self.series_context_file = os.path.join(self.cache_folder, "series_context.json")

        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)

        # **更新**: 移除剪辑时长限制，允许灵活剪辑
        self.clip_duration_standards = {
            'min_duration': 30,   # 最短30秒（避免过短片段）
            'max_duration': 600,  # 最长10分钟（允许长片段）
            'target_duration': None,  # 不设固定目标时长
            'buffer_seconds': 5   # 前后缓冲5秒
        }

        print("🚀 统一电视剧智能剪辑系统 v2.0")
        print("=" * 60)
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.video_folder}/")
        print(f"📤 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")
        print(f"⏱️ 片段时长: 根据剧情需要自由确定")

        # 显示AI状态
        if unified_config.is_enabled():
            provider_name = unified_config.providers.get(
                unified_config.config.get('provider'), {}
            ).get('name', '未知')
            model = unified_config.config.get('model', '未知')
            print(f"🤖 AI分析: 已启用 ({provider_name} - {model})")
        else:
            print("📝 AI分析: 未启用")

    def load_series_context(self) -> Dict:
        """**新增**: 加载全剧上下文，支持跨集连贯性"""
        if os.path.exists(self.series_context_file):
            try:
                with open(self.series_context_file, 'r', encoding='utf-8') as f:
                    context = json.load(f)
                    print(f"📚 加载全剧上下文: {len(context.get('episodes', {}))} 集")
                    return context
            except:
                pass
        
        # 默认上下文结构
        return {
            "series_info": {
                "title": "电视剧系列",
                "genre": "法律剧情",
                "main_themes": ["正义与法律", "家庭伦理", "社会问题"],
                "main_characters": {}
            },
            "episodes": {},
            "story_arcs": {
                "main_storyline": [],
                "character_development": {},
                "recurring_themes": []
            },
            "continuity_elements": {
                "unresolved_mysteries": [],
                "character_relationships": {},
                "plot_foreshadowing": []
            }
        }

    def save_series_context(self, context: Dict):
        """**新增**: 保存全剧上下文"""
        try:
            with open(self.series_context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
            print(f"💾 更新全剧上下文")
        except Exception as e:
            print(f"⚠️ 保存上下文失败: {e}")

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
        """提取集数"""
        base_name = os.path.splitext(filename)[0]
        
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']
        for pattern in patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                return f"E{match.group(1).zfill(2)}"
        
        return base_name

    def analyze_episode(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """**重大改进**: 带跨集连贯性的完整剧集分析"""
        episode_num = self._extract_episode_number(filename)

        # 检查缓存
        cache_file = os.path.join(self.cache_folder, f"{episode_num}_enhanced_analysis.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    print(f"📋 使用缓存分析: {episode_num}")
                    return cached_analysis
            except:
                pass

        if not unified_config.is_enabled():
            print(f"❌ 未启用AI分析，使用智能规则分析")
            return self._fallback_intelligent_analysis(subtitles, episode_num)

        # **核心改进**: 加载全剧上下文，实现跨集连贯
        series_context = self.load_series_context()
        
        print(f"🤖 AI完整分析 {episode_num}（含跨集连贯性分析）")
        analysis = self._ai_analyze_with_series_context(subtitles, episode_num, series_context)

        if analysis:
            # **更新全剧上下文**
            self._update_series_context(series_context, episode_num, analysis)
            self.save_series_context(series_context)
            
            # 保存到缓存
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                print(f"💾 分析结果已缓存")
            except Exception as e:
                print(f"⚠️ 缓存保存失败: {e}")

        return analysis

    def _ai_analyze_with_series_context(self, subtitles: List[Dict], episode_num: str, series_context: Dict) -> Optional[Dict]:
        """**核心升级**: 带全剧上下文的AI分析"""
        
        # 构建当前集内容
        full_text = ' '.join([sub['text'] for sub in subtitles])
        main_content = full_text[:10000] if len(full_text) > 10000 else full_text

        # **构建跨集上下文信息**
        previous_episodes = list(series_context.get('episodes', {}).keys())
        story_continuity = ""
        
        if previous_episodes:
            # 获取前一集的关键信息
            prev_ep = previous_episodes[-1] if previous_episodes else None
            if prev_ep and prev_ep in series_context['episodes']:
                prev_info = series_context['episodes'][prev_ep]
                story_continuity = f"""
【前集回顾 - {prev_ep}】:
主要剧情: {prev_info.get('main_theme', '剧情发展')}
关键线索: {', '.join(prev_info.get('key_clues', []))}
悬念伏笔: {', '.join(prev_info.get('cliffhangers', []))}
角色发展: {prev_info.get('character_development', '角色关系变化')}
"""

        # **高级AI分析提示词 - 无时长限制版本**
        prompt = f"""# 电视剧剧情深度分析与专业短视频制作

你是顶级影视剧情分析师和短视频制作专家，请为 **{episode_num}** 进行专业分析。

## 全剧上下文信息
{story_continuity}

主要故事线: {', '.join(series_context.get('story_arcs', {}).get('main_storyline', ['剧情发展']))}
核心主题: {', '.join(series_context.get('series_info', {}).get('main_themes', ['人物关系', '社会话题']))}
未解之谜: {', '.join(series_context.get('continuity_elements', {}).get('unresolved_mysteries', []))}

## 当前集内容
```
{main_content}
```

## 专业分析要求

### 1. 剧情连贯性分析
- 与前集的剧情呼应和发展
- 本集新引入的故事线索
- 为后续剧集埋下的伏笔
- 角色关系的演进轨迹

### 2. 精彩片段识别（不限制数量和时长）
- 根据剧情自然节奏识别所有精彩片段
- 每个片段必须有完整的戏剧结构
- 确保片段间的逻辑连贯性
- 时长完全根据剧情需要确定，可以是几十秒到几分钟

### 3. 专业旁白解说（参考示例风格）
- 开场: 制造悬念和吸引力的开场白
- 背景: 简要说明情境和背景
- 高潮: 强调最精彩和冲突最激烈的部分  
- 结论: 升华意义或引发思考的总结

### 4. 跨集连贯保证
- 确保本集片段与整体故事线的一致性
- 处理剧情反转与前情的关联
- 维护角色发展的连续性

请严格按照以下JSON格式输出：

```json
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "main_theme": "本集核心主题",
        "genre_type": "剧情类型(法律/家庭/悬疑等)",
        "emotional_tone": "整体情感基调",
        "continuity_analysis": {{
            "connections_to_previous": ["与前集的关联点1", "关联点2"],
            "new_story_elements": ["新引入的故事元素1", "元素2"],
            "character_development": "角色在本集中的发展变化",
            "foreshadowing_for_future": ["为后续剧集的铺垫1", "铺垫2"]
        }}
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "【精彩标题】具体描述片段亮点",
            "start_time": "00:XX:XX,XXX",
            "end_time": "00:XX:XX,XXX",
            "duration_seconds": {self.clip_duration_standards['target_duration']},
            "plot_significance": "这个片段在整体剧情中的重要意义",
            "dramatic_elements": ["戏剧元素1", "元素2", "元素3"],
            "character_development": "角色在此片段中的发展或变化",
            "hook_reason": "吸引观众的核心卖点",
            "professional_narration": {{
                "opening": "制造悬念的开场解说（15秒内）",
                "background": "简要说明背景和情境（20-30秒）",
                "climax": "强调高潮和冲突的解说（30-60秒）",
                "conclusion": "升华意义或引发思考（10-15秒）",
                "full_script": "完整的专业旁白解说稿"
            }},
            "key_dialogues": [
                {{"speaker": "角色名", "line": "关键台词", "impact": "台词的重要性"}},
                {{"speaker": "角色名", "line": "重要对话", "impact": "对剧情的推进作用"}}
            ],
            "visual_highlights": ["视觉亮点1", "亮点2"],
            "continuity_bridge": "与下个片段或下集的连接说明"
        }}
    ],
    "episode_summary": {{
        "core_conflicts": ["本集的核心冲突点"],
        "key_clues": ["重要线索或发现"],
        "cliffhangers": ["悬念和伏笔"],
        "character_arcs": "主要角色的发展轨迹",
        "thematic_elements": ["主题元素"]
    }},
    "technical_notes": {{
        "editing_suggestions": ["剪辑建议"],
        "duration_control": "时长控制要点",
        "pacing_notes": "节奏控制建议"
    }}
}}
```

请确保：
1. **时长精确控制**: 每个片段严格控制在{self.clip_duration_standards['min_duration']}-{self.clip_duration_standards['max_duration']}秒
2. **跨集连贯性**: 充分考虑与前后集的关联
3. **专业旁白**: 参考示例，生成引人入胜的专业解说
4. **完整性**: 片段组合能完整讲述本集核心故事"""

        system_prompt = """你是顶级影视内容分析专家，具备以下专业能力：

**核心专长**：
- 影视剧情深度解构与叙事分析
- 短视频爆款内容制作策略  
- 跨集连贯性和故事线索管理
- 专业旁白解说和情感引导
- 观众心理和传播规律研究

**分析标准**：
- 以故事完整性为前提，确保跨集连贯
- 严格控制片段时长，保证观看体验
- 生成专业级旁白解说，引发共鸣
- 平衡艺术价值与传播效果
- 注重细节但不失整体观

请运用专业知识进行深度分析，确保输出内容的专业性和实用性。"""

        try:
            response = ai_client.call_ai(prompt, system_prompt)
            if response:
                parsed_result = self._parse_enhanced_ai_response(response)
                if parsed_result:
                    print(f"✅ AI增强分析成功：{len(parsed_result.get('highlight_segments', []))} 个片段")
                    return parsed_result
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return self._fallback_intelligent_analysis(subtitles, episode_num)

    def _parse_enhanced_ai_response(self, response: str) -> Optional[Dict]:
        """解析增强版AI响应"""
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
            
            # **验证和调整片段时长**
            return self._validate_and_adjust_segments(result)
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
            return None

    def _validate_and_adjust_segments(self, analysis: Dict) -> Dict:
        """**更新**: 基础验证，不强制调整时长"""
        segments = analysis.get('highlight_segments', [])
        
        for segment in segments:
            # 计算实际时长
            start_time = segment.get('start_time', '00:00:00,000')
            end_time = segment.get('end_time', '00:02:30,000')
            
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            actual_duration = end_seconds - start_seconds
            
            # **仅基础验证，不强制调整**
            if actual_duration < 5:  # 仅过滤过短片段（小于5秒）
                print(f"    ⚠️ 片段过短，跳过: {actual_duration:.1f}s")
                continue
                
            # 保持原始时长
            segment['duration_seconds'] = actual_duration
            print(f"    ✅ 片段时长: {actual_duration:.1f}s（保持原始长度）")

            # **确保旁白完整性**
            if 'professional_narration' not in segment:
                segment['professional_narration'] = self._generate_professional_narration(segment)

        # 过滤掉过短的片段
        analysis['highlight_segments'] = [seg for seg in segments if seg.get('duration_seconds', 0) >= 5]
        return analysis

    def _generate_professional_narration(self, segment: Dict) -> Dict:
        """**新增**: 生成专业旁白（参考用户示例风格）"""
        title = segment.get('title', '精彩片段')
        hook_reason = segment.get('hook_reason', '剧情精彩')
        plot_significance = segment.get('plot_significance', '重要剧情')
        
        return {
            "opening": f"在这个关键时刻，{title.replace('【', '').replace('】', '').split('】')[0] if '】' in title else title}即将上演！",
            "background": f"面对复杂的情况，{hook_reason}让所有人都紧张起来。",
            "climax": f"最精彩的是，{plot_significance}在这一刻达到了顶点！",
            "conclusion": f"这一幕，为后续剧情埋下了重要的伏笔。",
            "full_script": f"在这个关键时刻，{title.replace('【', '').replace('】', '').split('】')[0] if '】' in title else title}即将上演！面对复杂的情况，{hook_reason}让所有人都紧张起来。最精彩的是，{plot_significance}在这一刻达到了顶点！这一幕，为后续剧情埋下了重要的伏笔。"
        }

    def _update_series_context(self, context: Dict, episode_num: str, analysis: Dict):
        """**新增**: 更新全剧上下文信息"""
        episode_info = analysis.get('episode_analysis', {})
        episode_summary = analysis.get('episode_summary', {})
        
        # 添加本集信息到全剧上下文
        context['episodes'][episode_num] = {
            'main_theme': episode_info.get('main_theme', '剧情发展'),
            'key_clues': episode_summary.get('key_clues', []),
            'cliffhangers': episode_summary.get('cliffhangers', []),
            'character_development': episode_info.get('continuity_analysis', {}).get('character_development', ''),
            'foreshadowing': episode_info.get('continuity_analysis', {}).get('foreshadowing_for_future', [])
        }
        
        # 更新主要故事线
        main_storyline = context['story_arcs']['main_storyline']
        new_elements = episode_info.get('continuity_analysis', {}).get('new_story_elements', [])
        main_storyline.extend(new_elements)
        
        # 更新未解之谜
        mysteries = context['continuity_elements']['unresolved_mysteries']
        mysteries.extend(episode_summary.get('cliffhangers', []))

    def _fallback_intelligent_analysis(self, subtitles: List[Dict], episode_num: str) -> Dict:
        """智能规则分析（AI不可用时）"""
        print(f"📝 使用智能规则分析")
        
        segments = self._find_key_segments_by_rules(subtitles)
        
        return {
            "episode_analysis": {
                "episode_number": episode_num,
                "main_theme": f"{episode_num}集核心剧情",
                "genre_type": "剧情片",
                "analysis_method": "智能规则"
            },
            "highlight_segments": segments[:3],
            "episode_summary": {
                "note": "基于规则分析，建议启用AI获得更好效果"
            }
        }

    def _find_key_segments_by_rules(self, subtitles: List[Dict]) -> List[Dict]:
        """基于规则找到关键片段 - 无时长限制版本"""
        key_segments = []
        
        keywords = {
            '四二八案': 10, '628案': 10, '听证会': 8, '申诉': 8,
            '证据': 6, '真相': 6, '霸凌': 7, '正当防卫': 8,
            '反转': 5, '发现': 4, '冲突': 4, '决定': 3
        }
        
        # **更新**: 使用动态窗口，不限制时长
        window_sizes = [20, 40, 60, 80]  # 不同大小的窗口
        
        for window_size in window_sizes:
            for i in range(0, len(subtitles) - window_size, window_size // 3):
                window = subtitles[i:i + window_size]
                text = ' '.join([sub['text'] for sub in window])
                
                score = 0
                for keyword, weight in keywords.items():
                    score += text.count(keyword) * weight
                
                if score >= 15:
                    # **保持原始时长，不做调整**
                    actual_duration = self._time_to_seconds(window[-1]['end']) - self._time_to_seconds(window[0]['start'])
                    
                    # 只过滤明显异常的片段
                    if actual_duration < 5 or actual_duration > 1800:  # 5秒到30分钟
                        continue
                    
                    key_segments.append({
                        "segment_id": len(key_segments) + 1,
                        "title": f"【精彩片段{len(key_segments) + 1}】关键剧情",
                        "start_time": window[0]['start'],
                        "end_time": window[-1]['end'],
                        "duration_seconds": actual_duration,
                        "dramatic_value": min(score / 10, 10),
                        "plot_significance": "基于关键词识别的重要片段",
                        "professional_narration": self._generate_professional_narration({"title": f"片段{len(key_segments) + 1}"})
                    })
        
        # 去重和排序
        key_segments.sort(key=lambda x: self._time_to_seconds(x['start_time']))
        return key_segments[:10]  # 最多返回10个片段

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

            # **改进**: 剪辑视频时添加缓冲时间
            if self._create_single_clip_with_buffer(video_file, segment, clip_path):
                # **生成专业旁白文件**
                self._create_enhanced_narration_file(clip_path, segment, analysis)
                created_clips.append(clip_path)

        return created_clips

    def _create_single_clip_with_buffer(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """**改进**: 创建单个片段，添加缓冲时间确保对话完整"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']

            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")

            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            
            # **添加缓冲时间，确保对话完整性**
            buffer = self.clip_duration_standards['buffer_seconds']
            buffer_start = max(0, start_seconds - buffer)
            buffer_end = end_seconds + buffer
            duration = buffer_end - buffer_start

            print(f"   缓冲后: {buffer_start:.1f}s --> {buffer_end:.1f}s ({duration:.1f}s)")

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

            # **优化的FFmpeg命令 - 确保质量和兼容性**
            cmd = [
                ffmpeg_cmd,
                '-hide_banner', '-loglevel', 'error',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(duration),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-preset', 'medium', '-crf', '20',  # 提高质量
                '-movflags', '+faststart',  # 优化播放
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
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return False
            else:
                print(f"   ❌ 剪辑失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def _create_enhanced_narration_file(self, video_path: str, segment: Dict, analysis: Dict):
        """**升级**: 创建增强版专业旁白解说文件（参考示例风格）"""
        try:
            narration_path = video_path.replace('.mp4', '_专业解说.txt')
            
            narration = segment.get('professional_narration', {})
            episode_info = analysis.get('episode_analysis', {})
            
            # **参考用户示例的专业格式**
            content = f"""📺 {episode_info.get('episode_number', '本集')} 专业旁白解说稿
{"=" * 80}

🎭 片段信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 片段标题: {segment.get('title', '精彩片段')}
⏱️ 时间范围: {segment.get('start_time', '')} --> {segment.get('end_time', '')} ({segment.get('duration_seconds', 0):.1f}秒)
🎯 剧情意义: {segment.get('plot_significance', '重要剧情节点')}
🎭 戏剧元素: {', '.join(segment.get('dramatic_elements', ['精彩剧情']))}
👥 角色发展: {segment.get('character_development', '角色关系发展')}
🎪 吸引点: {segment.get('hook_reason', '剧情精彩')}

📝 专业旁白解说:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【开场解说】 (0-15秒)
{narration.get('opening', '在这个关键时刻，精彩剧情即将展开...')}

【背景解说】 (15-45秒)  
{narration.get('background', '随着剧情的深入发展，复杂的情况逐渐显现...')}

【高潮解说】 (45-90秒)
{narration.get('climax', '最精彩的时刻到来，紧张的氛围达到顶点...')}

【结尾解说】 (90-{segment.get('duration_seconds', 120):.0f}秒)
{narration.get('conclusion', '这一幕为后续剧情埋下了重要伏笔...')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📜 完整解说稿:
{narration.get('full_script', '完整的专业旁白解说')}

💡 关键台词:
"""
            
            # 添加关键台词
            for dialogue in segment.get('key_dialogues', []):
                speaker = dialogue.get('speaker', '角色')
                line = dialogue.get('line', '台词')
                impact = dialogue.get('impact', '重要意义')
                content += f"• {speaker}: \"{line}\" - {impact}\n"
            
            content += f"""
✨ 视觉亮点:
"""
            for highlight in segment.get('visual_highlights', ['精彩画面']):
                content += f"• {highlight}\n"
            
            content += f"""
🔗 剧情连接:
{segment.get('continuity_bridge', '与后续剧情的重要连接')}

📊 传播要素:
• 情感冲击力: ⭐⭐⭐⭐⭐
• 话题讨论度: ⭐⭐⭐⭐⭐  
• 故事完整性: ⭐⭐⭐⭐⭐
• 观众代入感: ⭐⭐⭐⭐⭐

📋 使用指南:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 本解说稿可直接用于短视频配音制作
✅ 分段时间仅供参考，可根据实际视频调整
✅ 解说内容突出剧情核心，增强观众理解和共鸣  
✅ 适合抖音、快手、B站等各大短视频平台
✅ 建议配合背景音乐和字幕效果使用

🎯 制作建议:
• 开场3秒内抓住观众注意力
• 背景介绍简洁明了，避免冗长
• 高潮部分突出冲突和转折
• 结尾留下悬念或思考空间
• 整体节奏紧凑，信息密度适中

生成时间: {analysis.get('generation_time', '自动生成')}
分析类型: {'AI智能分析' if unified_config.is_enabled() else '规则分析'}
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📜 生成专业解说: {os.path.basename(narration_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 生成解说文件失败: {e}")

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

    def _seconds_to_time(self, seconds: float) -> str:
        """**新增**: 秒转换为时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def process_single_episode(self, subtitle_file: str) -> bool:
        """处理单集"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False

        # 2. **增强AI分析（含跨集连贯性）**
        analysis = self.analyze_episode(subtitles, subtitle_file)
        if not analysis:
            print(f"❌ 分析失败")
            return False

        # 3. 查找视频
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False

        # 4. **创建标准时长片段**
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
        print(f"⏱️ 片段时长: 无限制，根据剧情自然节奏")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("📺 统一电视剧智能剪辑系统 v2.0")
            print("=" * 60)

            # 显示状态
            config_status = "🤖 已配置" if unified_config.is_enabled() else "❌ 未配置"
            print(f"AI状态: {config_status}")
            print(f"时长标准: {self.clip_duration_standards['min_duration']}-{self.clip_duration_standards['max_duration']}秒")

            srt_files, video_files = self.check_files()
            
            # 显示上下文状态
            series_context = self.load_series_context()
            episodes_count = len(series_context.get('episodes', {}))
            print(f"全剧上下文: {episodes_count} 集已分析")

            print("\n请选择操作:")
            print("1. 🎬 开始智能剪辑")
            print("2. 🤖 配置AI接口")
            print("3. 📁 检查文件状态")
            print("4. 🔄 清空全剧上下文")
            print("5. ❌ 退出")

            try:
                choice = input("\n请输入选择 (1-5): ").strip()

                if choice == '1':
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
                    if os.path.exists(self.series_context_file):
                        os.remove(self.series_context_file)
                        print(f"✅ 已清空全剧上下文")
                    else:
                        print(f"📝 上下文文件不存在")

                elif choice == '5':
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
