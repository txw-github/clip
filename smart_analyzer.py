# Updated AI call method to use OpenAI client and fallback to requests.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完全智能化剧情分析器 - 解决所有限制问题
特点：
1. 完全动态，无硬编码限制
2. 提供完整上下文片段给AI
3. 每集生成多个精彩短视频
4. AI判断最佳剪辑内容和时长
5. 支持srt目录结构
"""

import os
import re
import json
import requests
from typing import List, Dict, Tuple, Optional
from api_config_helper import config_helper

class SmartAnalyzer:
    def __init__(self):
        self.config = config_helper.load_config()
        self.enabled = self.config.get('enabled', False)

        if self.enabled:
            print(f"🤖 启用AI智能分析: {self.config.get('provider')}/{self.config.get('model')}")
        else:
            print("📝 AI未配置，使用基础规则分析")

    def get_subtitle_files(self) -> List[str]:
        """获取字幕文件 - 支持srt目录结构"""
        files = []

        # 优先检查srt目录
        srt_dir = 'srt'
        if os.path.exists(srt_dir):
            for f in os.listdir(srt_dir):
                if f.endswith(('.txt', '.srt')):
                    files.append(os.path.join(srt_dir, f))

        # 如果srt目录不存在或为空，检查根目录
        if not files:
            print("⚠ srt目录不存在或为空，检查根目录...")
            for f in os.listdir('.'):
                if f.endswith(('.txt', '.srt')) and any(pattern in f.lower() for pattern in ['s01e', 'ep', 'e0', 'e1']):
                    files.append(f)

        # 确保srt目录存在
        if not os.path.exists(srt_dir):
            os.makedirs(srt_dir)
            print(f"✓ 创建字幕目录: {srt_dir}/")
            if not files:
                print("⚠ 请将字幕文件放入srt目录")

        return sorted(files)

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 读取字幕文件失败 {filepath}: {e}")
            return []

        blocks = re.split(r'\n\s*\n', content.strip())
        subtitles = []

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                        text = '\n'.join(lines[2:])

                        subtitles.append({
                            'index': index,
                            'start': start_time,
                            'end': end_time,
                            'text': text,
                            'episode': os.path.basename(filepath)
                        })
                except (ValueError, IndexError):
                    continue

        return subtitles

    def create_context_segments(self, subtitles: List[Dict], window_size: int = 25) -> List[Dict]:
        """创建包含完整上下文的片段组"""
        context_segments = []

        # 使用滑动窗口创建重叠的上下文片段
        step_size = window_size // 2  # 50% 重叠确保连续性

        for i in range(0, len(subtitles), step_size):
            end_idx = min(i + window_size, len(subtitles))

            if end_idx - i < 10:  # 太短的片段跳过
                continue

            segment_subtitles = subtitles[i:end_idx]

            # 合并文本
            full_text = "\n".join([sub['text'] for sub in segment_subtitles])

            # 时间范围
            start_time = segment_subtitles[0]['start']
            end_time = segment_subtitles[-1]['end']
            duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)

            # 上下文信息
            context_before = subtitles[max(0, i-15):i] if i > 0 else []
            context_after = subtitles[end_idx:min(len(subtitles), end_idx+15)] if end_idx < len(subtitles) else []

            context_segments.append({
                'start_index': i,
                'end_index': end_idx - 1,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'full_text': full_text,
                'subtitles': segment_subtitles,
                'context_before': context_before,
                'context_after': context_after,
                'episode_position': i / len(subtitles)  # 在剧集中的位置
            })

        return context_segments

    def ai_analyze_segment(self, segment: Dict, episode_context: str = "") -> Dict:
        """使用AI分析片段 - 完全智能化"""
        if not self.enabled:
            return self._fallback_analysis(segment)

        # 构建丰富的上下文
        context_before = "\n".join([sub['text'] for sub in segment['context_before'][-8:]])
        context_after = "\n".join([sub['text'] for sub in segment['context_after'][:8]])

        prompt = f"""你是专业的电视剧剪辑师，需要分析这个片段是否适合制作成精彩短视频。

【前情提要】
{context_before}

【当前片段内容】（时长：{segment['duration']:.1f}秒）
{segment['full_text']}

【后续发展】
{context_after}

【剧集背景】{episode_context}

【片段位置】在剧集的{segment['episode_position']*100:.1f}%位置

请完成专业分析：

1. **综合评分** (0-10分)：这个片段制作短视频的价值
2. **剧情完整性** (0-10分)：片段是否有完整的起承转合
3. **情感强度** (0-10分)：是否有强烈的情感冲击
4. **观众吸引力** (0-10分)：是否能吸引观众观看
5. **上下文独立性** (0-10分)：脱离上下文是否仍然精彩

6. **片段类型识别**：自动识别这是什么类型的片段（不受限制）
7. **最佳剪辑时长**：建议的剪辑时长（秒）
8. **剪辑调整建议**：
   - 是否需要扩展或缩短
   - 最佳开始和结束点
   - 调整原因
9. **精彩亮点**：识别片段中最精彩的部分
10. **短视频标题**：为这个片段生成吸引人的标题

请以JSON格式返回：
{{
    "overall_score": 综合评分,
    "plot_completeness": 剧情完整性评分,
    "emotional_intensity": 情感强度评分,
    "audience_appeal": 观众吸引力评分,
    "context_independence": 上下文独立性评分,
    "segment_type": "自动识别的片段类型",
    "optimal_duration": 建议剪辑时长,
    "clip_adjustment": {{
        "action": "extend/shrink/keep",
        "reason": "调整原因",
        "new_start_offset": 开始时间偏移秒数,
        "new_end_offset": 结束时间偏移秒数,
        "best_start_dialogue": "最佳开始对话",
        "best_end_dialogue": "最佳结束对话"
    }},
    "highlights": ["亮点1", "亮点2", "亮点3"],
    "video_title": "吸引人的短视频标题",
    "hook_reason": "吸引观众的核心原因",
    "recommended": true/false,
    "confidence": 置信度0-1
}}"""

        try:
            response = self._call_ai_api(prompt)
            if response:
                result = self._parse_ai_response(response)
                result['original_segment'] = segment
                return result
        except Exception as e:
            print(f"AI分析出错: {e}")

        return self._fallback_analysis(segment)

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API - 使用通用API助手"""
        try:
            return config_helper.call_ai_api(prompt, self.config)
        except Exception as e:
            print(f"  ⚠ AI分析异常: {e}")
            return None

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """调用Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/{self.config['model']}:generateContent?key={self.config['api_key']}"

            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 2000,
                    "temperature": 0.7
                }
            }

            response = requests.post(url, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            else:
                print(f"Gemini API错误: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_qwen_api(self, prompt: str) -> Optional[str]:
        """调用通义千问API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': self.config['model'],
                'input': {'prompt': prompt},
                'parameters': {
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            }

            response = requests.post(self.config['url'], headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('output', {}).get('text', '')
            else:
                print(f"通义千问API错误: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"通义千问API调用失败: {e}")
            return None

    def _call_doubao_api(self, prompt: str) -> Optional[str]:
        """调用豆包API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': self.config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剪辑师，专注于识别精彩片段并制定最佳剪辑方案。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }

            response = requests.post(self.config['url'], headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                print(f"豆包API错误: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return None

    def _call_standard_api(self, prompt: str) -> Optional[str]:
        """调用标准API（支持OpenRouter等新服务商）"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            # 为OpenRouter添加特殊头部
            if self.config.get('provider') == 'openrouter':
                headers.update({
                    'HTTP-Referer': 'https://replit.com',
                    'X-Title': 'TV-Clipper-AI'
                })

            data = {
                'model': self.config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剪辑师，专注于识别精彩片段并制定最佳剪辑方案。你的分析不受任何预设限制，完全基于剧情内容进行智能判断。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }

            response = requests.post(self.config['url'], headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                print(f"API错误: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def _parse_ai_response(self, response_text: str) -> Dict:
        """解析AI响应"""
        try:
            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start != -1 and end > start:
                    json_text = response_text[start:end]
                else:
                    json_text = response_text

            result = json.loads(json_text)

            # 确保必要字段存在
            defaults = {
                "overall_score": 5.0,
                "recommended": False,
                "video_title": "精彩片段",
                "optimal_duration": 120,
                "confidence": 0.5
            }

            for key, default_value in defaults.items():
                if key not in result:
                    result[key] = default_value

            return result

        except json.JSONDecodeError:
            # 基础解析
            score_match = re.search(r'(\d+\.?\d*)', response_text)
            score = float(score_match.group(1)) if score_match else 5.0

            return {
                "overall_score": score,
                "recommended": score >= 6.0,
                "video_title": "AI分析片段",
                "reasoning": response_text[:200],
                "confidence": 0.5
            }
        except Exception as e:
            print(f"响应解析异常: {e}")
            return {
                "overall_score": 5.0,
                "recommended": False,
                "video_title": "解析错误",
                "reasoning": "解析失败",
                "confidence": 0.1
            }

    def _fallback_analysis(self, segment: Dict) -> Dict:
        """AI不可用时的备用分析"""
        text = segment['full_text']

        # 简单关键词分析
        exciting_keywords = ['突然', '发现', '真相', '秘密', '危险', '不要', '为什么', '救命', '完了']
        emotional_words = ['愤怒', '哭', '喊', '激动', '震惊', '害怕', '开心', '难过']

        score = 0
        for keyword in exciting_keywords:
            score += text.count(keyword) * 2
        for emotion in emotional_words:
            score += text.count(emotion) * 1.5

        # 对话强度
        score += text.count('！') * 0.5 + text.count('？') * 0.3

        return {
            "overall_score": min(score, 10),
            "recommended": score >= 4,
            "video_title": "精彩片段",
            "optimal_duration": segment['duration'],
            "reasoning": "基础分析模式",
            "confidence": 0.6,
            "original_segment": segment
        }

    def analyze_episode_smartly(self, episode_file: str) -> Dict:
        """智能分析单集，返回多个推荐的短视频片段"""
        print(f"\n🧠 智能分析 {os.path.basename(episode_file)}...")

        subtitles = self.parse_subtitle_file(episode_file)
        if not subtitles:
            return {"error": "无法解析字幕文件"}

        # 创建上下文片段
        context_segments = self.create_context_segments(subtitles)
        print(f"📊 创建了 {len(context_segments)} 个上下文片段")

        # 获取剧集背景
        episode_context = self._get_episode_context(subtitles[:50], subtitles[-30:])

        # AI分析每个片段
        analyzed_segments = []
        for i, segment in enumerate(context_segments):
            print(f"  🔍 分析片段 {i+1}/{len(context_segments)}")

            analysis = self.ai_analyze_segment(segment, episode_context)

            # 只保留高质量片段
            if analysis.get('recommended', False) and analysis.get('overall_score', 0) >= 6.0:
                analyzed_segments.append(analysis)

        # 按分数排序
        analyzed_segments.sort(key=lambda x: x.get('overall_score', 0), reverse=True)

        # 选择最佳片段（避免重叠）
        final_clips = self._select_best_clips(analyzed_segments)

        # 生成剧集总结
        episode_num = self._extract_episode_number(episode_file)

        return {
            'episode': episode_file,
            'episode_number': episode_num,
            'total_clips': len(final_clips),
            'clips': final_clips,
            'total_duration': sum(clip.get('optimal_duration', 120) for clip in final_clips),
            'ai_analysis': self.enabled,
            'episode_context': episode_context[:100]
        }

    def _get_episode_context(self, beginning: List[Dict], ending: List[Dict]) -> str:
        """获取剧集背景"""
        if not self.enabled:
            return "本集精彩内容"

        beginning_text = "\n".join([sub['text'] for sub in beginning])
        ending_text = "\n".join([sub['text'] for sub in ending])

        prompt = f"""请用30字以内简要总结这一集的核心剧情：

开头：{beginning_text}
结尾：{ending_text}

只返回剧情概要，不需要其他内容。"""

        try:
            response = self._call_ai_api(prompt)
            return response[:50] if response else "本集精彩内容"
        except:
            return "本集精彩内容"

    def _select_best_clips(self, clips: List[Dict], max_clips: int = 4) -> List[Dict]:
        """选择最佳片段，避免重叠"""
        if not clips:
            return []

        selected = []
        used_time_ranges = []

        for clip in clips:
            if len(selected) >= max_clips:
                break

            segment = clip['original_segment']
            start_time = self.time_to_seconds(segment['start_time'])
            end_time = self.time_to_seconds(segment['end_time'])

            # 检查是否与已选片段重叠
            overlapping = False
            for used_start, used_end in used_time_ranges:
                if not (end_time < used_start or start_time > used_end):
                    overlapping = True
                    break

            if not overlapping:
                selected.append(clip)
                used_time_ranges.append((start_time, end_time))

        return selected

    def _extract_episode_number(self, filename: str) -> str:
        """提取剧集编号"""
        episode_match = re.search(r'[SE](\d+)[EX](\d+)', filename, re.IGNORECASE)
        if episode_match:
            return f"{episode_match.group(1)}{episode_match.group(2)}"

        episode_match = re.search(r'(\d+)', filename)
        return episode_match.group(1) if episode_match else "00"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

def analyze_all_episodes_smartly():
    """智能分析所有剧集"""
    analyzer = SmartAnalyzer()

    # 获取所有字幕文件
    subtitle_files = analyzer.get_subtitle_files()

    if not subtitle_files:
        print("❌ 未找到字幕文件")
        return []

    print(f"🚀 启动完全智能化分析系统 - 发现 {len(subtitle_files)} 个字幕文件")
    print("🤖 新特性：")
    print("• 完全AI驱动，无任何硬编码限制")
    print("• 提供完整上下文给AI分析")
    print("• 每集生成多个精彩短视频")
    print("• AI判断最佳剪辑内容和时长")
    print("• 支持srt目录结构")
    print("=" * 60)

    all_episodes_plans = []

    for filename in subtitle_files:
        try:
            episode_plan = analyzer.analyze_episode_smartly(filename)

            if 'error' not in episode_plan:
                all_episodes_plans.append(episode_plan)

                print(f"✅ {os.path.basename(filename)}")
                print(f"  🎬 推荐短视频: {episode_plan['total_clips']} 个")
                print(f"  ⏱️ 总时长: {episode_plan['total_duration']:.1f}秒")
                print(f"  🤖 AI分析: {'是' if episode_plan['ai_analysis'] else '否'}")

                # 显示推荐片段
                for i, clip in enumerate(episode_plan['clips'][:3]):
                    title = clip.get('video_title', '未知')
                    score = clip.get('overall_score', 0)
                    print(f"    片段{i+1}: {title} (评分: {score:.1f})")
                print()
            else:
                print(f"❌ 错误处理 {filename}: {episode_plan['error']}")

        except Exception as e:
            print(f"❌ 处理失败 {filename}: {e}")

    # 生成报告
    generate_smart_report(all_episodes_plans)
    return all_episodes_plans

def generate_smart_report(episodes_plans: List[Dict]):
    """生成智能分析报告"""
    if not episodes_plans:
        return

    total_clips = sum(ep['total_clips'] for ep in episodes_plans)
    total_duration = sum(ep['total_duration'] for ep in episodes_plans)
    ai_analyzed = sum(1 for ep in episodes_plans if ep['ai_analysis'])

    content = f"""🤖 完全智能化剧情分析报告
{'='*60}

📊 分析统计：
• 总集数：{len(episodes_plans)} 集
• 推荐短视频：{total_clips} 个
• 总时长：{total_duration/60:.1f} 分钟
• AI智能分析：{ai_analyzed}/{len(episodes_plans)} 集
• 平均每集：{total_clips/len(episodes_plans):.1f} 个短视频

🎬 详细剧集方案：
"""

    for ep in episodes_plans:
        content += f"\n📺 第{ep['episode_number']}集\n"
        content += f"推荐短视频：{ep['total_clips']} 个\n"
        content += f"总时长：{ep['total_duration']/60:.1f} 分钟\n"
        content += f"背景：{ep.get('episode_context', 'N/A')}\n"

        for i, clip in enumerate(ep['clips']):
            segment = clip['original_segment']
            title = clip.get('video_title', '精彩片段')
            score = clip.get('overall_score', 0)
            duration = clip.get('optimal_duration', 120)

            content += f"\n  🎯 短视频 {i+1}：{title}\n"
            content += f"     时间：{segment['start_time']} --> {segment['end_time']}\n"
            content += f"     建议时长：{duration}秒\n"
            content += f"     评分：{score:.1f}/10\n"

            if 'highlights' in clip:
                content += f"     亮点：{', '.join(clip['highlights'][:3])}\n"

        content += "\n" + "-"*40 + "\n"

    with open('smart_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 完全智能化分析报告已保存到 smart_analysis_report.txt")
    print(f"📊 共生成 {total_clips} 个推荐短视频片段")

if __name__ == "__main__":
    analyze_all_episodes_smartly()
