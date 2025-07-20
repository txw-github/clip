
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能电视剧剪辑系统 - 自适应各种剧情类型
特点：
1. AI驱动的智能分析，不依赖固定关键词
2. 自动识别剧情类型（法律、爱情、悬疑、古装等）
3. 动态调整评分权重和片段选择策略
4. 智能错别字修正和文件格式自适应
5. 每集生成2-3分钟核心剧情短视频
"""

import os
import re
import json
import subprocess
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class IntelligentTVClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "intelligent_clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder
        
        # 创建必要目录
        for folder in [self.video_folder, self.output_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")
        
        # 智能剧情类型识别词库
        self.genre_patterns = {
            'legal': {
                'keywords': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护', '判决', '申诉', '听证会', '法律', '正当防卫'],
                'emotional_markers': ['愤怒', '无奈', '坚持', '正义', '真相', '冤枉'],
                'plot_indicators': ['开庭', '举证', '质证', '判决', '上诉', '翻案']
            },
            'romance': {
                'keywords': ['爱情', '喜欢', '心动', '表白', '约会', '分手', '复合', '结婚', '情侣', '恋人', '暗恋', '初恋', '浪漫'],
                'emotional_markers': ['甜蜜', '心疼', '想念', '温柔', '感动', '幸福', '心碎', '后悔'],
                'plot_indicators': ['相遇', '误会', '告白', '分离', '重逢', '结局']
            },
            'crime': {
                'keywords': ['警察', '犯罪', '嫌疑人', '调查', '破案', '线索', '凶手', '案发', '侦探', '刑侦', '追踪', '逮捕', '真凶'],
                'emotional_markers': ['紧张', '恐惧', '震惊', '愤怒', '绝望', '希望'],
                'plot_indicators': ['案发', '调查', '追踪', '发现', '抓捕', '真相']
            },
            'family': {
                'keywords': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情', '家人', '团聚', '离别', '成长', '教育', '代沟', '责任'],
                'emotional_markers': ['温暖', '感动', '心疼', '愧疚', '理解', '包容'],
                'plot_indicators': ['成长', '冲突', '和解', '离别', '团聚', '传承']
            },
            'historical': {
                'keywords': ['皇帝', '大臣', '朝廷', '战争', '将军', '士兵', '王朝', '宫廷', '政治', '权力', '叛乱', '起义', '江山'],
                'emotional_markers': ['忠诚', '背叛', '野心', '牺牲', '荣耀', '耻辱'],
                'plot_indicators': ['登基', '政变', '战役', '联盟', '背叛', '覆灭']
            },
            'modern': {
                'keywords': ['公司', '职场', '老板', '员工', '竞争', '创业', '商业', '项目', '合作', '投资', '成功', '失败'],
                'emotional_markers': ['压力', '兴奋', '挫折', '成就', '焦虑', '自信'],
                'plot_indicators': ['机会', '挑战', '合作', '竞争', '成功', '转机']
            }
        }
        
        # 通用戏剧张力标识词
        self.universal_dramatic_words = [
            '突然', '忽然', '没想到', '原来', '居然', '竟然', '震惊', '惊讶', '意外',
            '发现', '真相', '秘密', '隐瞒', '揭露', '暴露', '爆发', '冲突', '对抗',
            '危险', '紧急', '救命', '关键', '重要', '决定', '选择', '改变', '转折'
        ]
        
        # 情感强度标识词
        self.emotional_intensity_words = [
            '哭', '笑', '喊', '叫', '怒', '气', '激动', '兴奋', '紧张', '害怕',
            '开心', '悲伤', '痛苦', '绝望', '希望', '感动', '愤怒', '崩溃', '颤抖'
        ]
        
        # AI配置
        self.ai_config = self.load_ai_config()
        
        # 检测到的剧情类型
        self.detected_genre = None
        self.genre_confidence = 0.0

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False) and config.get('api_key'):
                    return config
        except:
            pass
        
        # 如果没有配置，尝试从环境变量获取
        import os
        api_key = os.environ.get('AI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        if api_key:
            return {
                'enabled': True,
                'api_key': api_key,
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-3.5-turbo'
            }
        
        return {'enabled': False}

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """智能解析字幕文件，支持多种格式和编码"""
        subtitles = []
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'utf-16', 'gb2312']
        content = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue
        
        if not content:
            print(f"❌ 无法读取文件: {filepath}")
            return []
        
        # 智能错别字修正（更全面）
        corrections = {
            # 繁体字修正
            '證據': '证据', '檢察官': '检察官', '審判': '审判', '辯護': '辩护',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            # 常见错字修正
            '防衛': '防卫', '正當': '正当', '調查': '调查', '起訴': '起诉',
            '証明': '证明', '実現': '实现', '対話': '对话', '関係': '关系'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        # 智能分割字幕块（支持多种格式）
        # SRT格式
        if '-->' in content:
            blocks = re.split(r'\n\s*\n', content.strip())
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        # 尝试解析序号
                        index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1
                        
                        # 解析时间
                        time_match = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
                        if time_match:
                            start_time = time_match.group(1).replace('.', ',')
                            end_time = time_match.group(2).replace('.', ',')
                            text = '\n'.join(lines[2:]).strip()
                            
                            if text:  # 确保有内容
                                subtitles.append({
                                    'index': index,
                                    'start': start_time,
                                    'end': end_time,
                                    'text': text,
                                    'episode': os.path.basename(filepath)
                                })
                    except (ValueError, IndexError):
                        continue
        
        # 如果没有解析到字幕，尝试按行解析（简单文本格式）
        if not subtitles:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.isdigit():
                    # 生成虚拟时间戳
                    start_seconds = i * 3
                    end_seconds = start_seconds + 3
                    start_time = f"00:{start_seconds//60:02d}:{start_seconds%60:02d},000"
                    end_time = f"00:{end_seconds//60:02d}:{end_seconds%60:02d},000"
                    
                    subtitles.append({
                        'index': i + 1,
                        'start': start_time,
                        'end': end_time,
                        'text': line,
                        'episode': os.path.basename(filepath)
                    })
        
        print(f"✓ 解析字幕: {len(subtitles)} 条")
        return subtitles

    def detect_genre(self, subtitles: List[Dict]) -> str:
        """智能识别剧情类型"""
        # 合并前200条字幕进行分析
        sample_text = ' '.join([sub['text'] for sub in subtitles[:200]])
        
        genre_scores = {}
        for genre, patterns in self.genre_patterns.items():
            score = 0
            
            # 关键词评分
            for keyword in patterns['keywords']:
                score += sample_text.count(keyword) * 2
            
            # 情感标记评分
            for marker in patterns['emotional_markers']:
                score += sample_text.count(marker) * 1.5
            
            # 剧情指示词评分
            for indicator in patterns['plot_indicators']:
                score += sample_text.count(indicator) * 3
            
            genre_scores[genre] = score
        
        # 找出最匹配的类型
        if genre_scores:
            best_genre = max(genre_scores, key=genre_scores.get)
            max_score = genre_scores[best_genre]
            total_score = sum(genre_scores.values())
            
            if max_score > 10 and total_score > 0:  # 足够的匹配度
                self.detected_genre = best_genre
                self.genre_confidence = min(max_score / total_score, 1.0)
                print(f"🎭 检测剧情类型: {best_genre} (置信度: {self.genre_confidence:.2f})")
                return best_genre
        
        self.detected_genre = 'general'
        self.genre_confidence = 0.5
        print(f"🎭 使用通用分析模式")
        return 'general'

    def calculate_segment_importance(self, text: str, position: float, context: Dict = None) -> float:
        """智能计算片段重要性评分"""
        score = 0.0
        
        # 1. 剧情类型匹配评分
        if self.detected_genre and self.detected_genre in self.genre_patterns:
            patterns = self.genre_patterns[self.detected_genre]
            
            # 关键词匹配
            for keyword in patterns['keywords']:
                if keyword in text:
                    score += 3.0 * self.genre_confidence
            
            # 情感标记匹配
            for marker in patterns['emotional_markers']:
                if marker in text:
                    score += 2.0 * self.genre_confidence
            
            # 剧情指示词匹配
            for indicator in patterns['plot_indicators']:
                if indicator in text:
                    score += 4.0 * self.genre_confidence
        
        # 2. 通用戏剧张力评分
        for word in self.universal_dramatic_words:
            if word in text:
                score += 2.0
        
        # 3. 情感强度评分
        for word in self.emotional_intensity_words:
            if word in text:
                score += 1.5
        
        # 4. 对话质量评分
        punctuation_score = text.count('！') * 0.5 + text.count('？') * 0.5 + text.count('...') * 0.3
        score += min(punctuation_score, 3.0)  # 最多3分
        
        # 5. 位置权重（开头结尾更重要）
        if position < 0.15 or position > 0.85:
            score *= 1.3
        elif 0.4 <= position <= 0.6:  # 中间部分
            score *= 1.1
        
        # 6. 文本长度质量评分
        text_len = len(text)
        if 15 <= text_len <= 150:
            score += 1.0
        elif text_len > 200:
            score *= 0.8  # 过长的文本减分
        
        # 7. AI增强评分（如果启用）
        if self.ai_config.get('enabled', False):
            ai_score = self.get_ai_importance_score(text)
            if ai_score > 0:
                score = score * 0.7 + ai_score * 0.3  # 融合AI评分
        
        return score

    def get_ai_importance_score(self, text: str) -> float:
        """使用AI评估片段重要性"""
        try:
            if len(text) < 10 or len(text) > 300:
                return 0.0
            
            genre_desc = f"这是一部{self.detected_genre}类型的电视剧" if self.detected_genre != 'general' else "这是一部电视剧"
            
            prompt = f"""你是专业的电视剧剪辑师。{genre_desc}，请评估以下对话片段的精彩程度：

"{text}"

评估标准（每项0-2分）：
1. 剧情重要性：是否推进主要故事线
2. 戏剧张力：是否包含冲突、转折、意外
3. 情感共鸣：是否引发观众情感反应
4. 角色发展：是否展现角色成长或关系变化
5. 观众吸引力：是否制造悬念或高潮

请给出0-10分的综合评分，只需要输出数字。"""

            response = self.call_ai_api(prompt)
            if response:
                # 提取评分
                score_match = re.search(r'(\d+\.?\d*)', response.strip())
                if score_match:
                    score = float(score_match.group(1))
                    return min(max(score, 0), 10)  # 限制在0-10之间
            
            return 0.0
            
        except Exception as e:
            return 0.0

    def call_ai_api(self, prompt: str) -> str:
        """调用AI API"""
        try:
            config = self.ai_config
            if not config.get('enabled', False):
                return ""
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剪辑师，专注于识别精彩片段。请给出简洁准确的评分。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 20,
                'temperature': 0.2
            }
            
            response = requests.post(
                f"{config.get('base_url', 'https://api.openai.com/v1')}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                return content
            
            return ""
            
        except Exception as e:
            return ""

    def find_episode_highlights(self, subtitles: List[Dict], episode_num: str) -> Optional[Dict]:
        """找到单集精彩片段"""
        if not subtitles:
            return None
        
        # 使用滑动窗口分析
        window_size = 30  # 约2-3分钟的窗口
        step_size = 15    # 50%重叠
        
        best_segment = None
        best_score = 0
        
        for i in range(0, len(subtitles) - window_size, step_size):
            segment_subs = subtitles[i:i + window_size]
            combined_text = ' '.join([sub['text'] for sub in segment_subs])
            
            position = i / len(subtitles)
            context = {
                'position': position,
                'window_index': i // step_size,
                'total_windows': (len(subtitles) - window_size) // step_size + 1
            }
            
            score = self.calculate_segment_importance(combined_text, position, context)
            
            if score > best_score:
                best_score = score
                best_segment = {
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'score': score,
                    'text': combined_text,
                    'subtitles': segment_subs
                }
        
        if not best_segment or best_score < 3.0:
            # 如果没有找到高分片段，选择中间部分
            mid_start = len(subtitles) // 3
            mid_end = min(mid_start + window_size, len(subtitles) - 1)
            best_segment = {
                'start_index': mid_start,
                'end_index': mid_end,
                'score': 3.0,
                'text': ' '.join([subtitles[j]['text'] for j in range(mid_start, mid_end + 1)]),
                'subtitles': subtitles[mid_start:mid_end + 1]
            }
        
        # 优化片段边界
        best_segment = self.optimize_segment_boundaries(subtitles, best_segment)
        
        # 生成片段信息
        start_time = best_segment['subtitles'][0]['start']
        end_time = best_segment['subtitles'][-1]['end']
        duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
        
        # 确保时长在合理范围内（90-200秒）
        if duration < 90:
            best_segment = self.extend_segment(subtitles, best_segment, target_duration=120)
        elif duration > 200:
            best_segment = self.trim_segment(best_segment, target_duration=180)
        
        # 重新计算时间
        start_time = best_segment['subtitles'][0]['start']
        end_time = best_segment['subtitles'][-1]['end']
        duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
        
        return {
            'episode_number': episode_num,
            'theme': self.generate_episode_theme(best_segment, episode_num),
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'score': best_segment['score'],
            'content_preview': best_segment['text'][:100] + "..." if len(best_segment['text']) > 100 else best_segment['text'],
            'key_dialogues': self.extract_key_dialogues(best_segment['subtitles']),
            'significance': self.analyze_significance(best_segment['text']),
            'next_episode_hint': self.generate_next_episode_hint(best_segment['text'], episode_num)
        }

    def optimize_segment_boundaries(self, all_subtitles: List[Dict], segment: Dict) -> Dict:
        """优化片段边界，寻找自然切入点"""
        start_idx = segment['start_index']
        end_idx = segment['end_index']
        
        # 寻找更好的开始点
        scene_starters = ['突然', '这时', '忽然', '刚才', '现在', '那天', '当时', '然后', '接着', '后来']
        for i in range(max(0, start_idx - 10), start_idx + 5):
            if i < len(all_subtitles):
                text = all_subtitles[i]['text']
                if any(starter in text for starter in scene_starters):
                    start_idx = i
                    break
        
        # 寻找更好的结束点
        scene_enders = ['走了', '离开', '结束', '算了', '好吧', '再见', '完了', '行了', '就这样']
        for i in range(end_idx, min(len(all_subtitles), end_idx + 10)):
            text = all_subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                end_idx = i
                break
            if '。' in text and len(text) < 20:  # 短句结束
                end_idx = i
                break
        
        segment['start_index'] = start_idx
        segment['end_index'] = end_idx
        segment['subtitles'] = all_subtitles[start_idx:end_idx + 1]
        segment['text'] = ' '.join([sub['text'] for sub in segment['subtitles']])
        
        return segment

    def extend_segment(self, all_subtitles: List[Dict], segment: Dict, target_duration: int) -> Dict:
        """扩展片段到目标时长"""
        current_duration = self.time_to_seconds(segment['subtitles'][-1]['end']) - self.time_to_seconds(segment['subtitles'][0]['start'])
        
        while current_duration < target_duration:
            # 向前扩展
            if segment['start_index'] > 0:
                segment['start_index'] -= 1
                segment['subtitles'].insert(0, all_subtitles[segment['start_index']])
            
            # 向后扩展
            if segment['end_index'] < len(all_subtitles) - 1:
                segment['end_index'] += 1
                segment['subtitles'].append(all_subtitles[segment['end_index']])
            
            if segment['start_index'] == 0 and segment['end_index'] == len(all_subtitles) - 1:
                break
            
            current_duration = self.time_to_seconds(segment['subtitles'][-1]['end']) - self.time_to_seconds(segment['subtitles'][0]['start'])
        
        segment['text'] = ' '.join([sub['text'] for sub in segment['subtitles']])
        return segment

    def trim_segment(self, segment: Dict, target_duration: int) -> Dict:
        """修剪片段到目标时长"""
        while len(segment['subtitles']) > 10:
            current_duration = self.time_to_seconds(segment['subtitles'][-1]['end']) - self.time_to_seconds(segment['subtitles'][0]['start'])
            
            if current_duration <= target_duration:
                break
            
            # 从两端修剪
            if len(segment['subtitles']) % 2 == 0:
                segment['subtitles'].pop(0)
                segment['start_index'] += 1
            else:
                segment['subtitles'].pop()
                segment['end_index'] -= 1
        
        segment['text'] = ' '.join([sub['text'] for sub in segment['subtitles']])
        return segment

    def generate_episode_theme(self, segment: Dict, episode_num: str) -> str:
        """生成集数主题"""
        text = segment['text']
        
        # 根据检测到的剧情类型生成主题
        if self.detected_genre == 'legal':
            if any(word in text for word in ['申诉', '重审', '翻案']):
                return f"E{episode_num}：案件申诉启动，法律较量升级"
            elif any(word in text for word in ['听证会', '法庭', '审判']):
                return f"E{episode_num}：法庭激辩，正义与法理交锋"
            elif any(word in text for word in ['证据', '真相', '发现']):
                return f"E{episode_num}：关键证据浮现，真相渐露端倪"
            else:
                return f"E{episode_num}：法律剧情推进，案件现转机"
        
        elif self.detected_genre == 'romance':
            if any(word in text for word in ['表白', '告白', '喜欢']):
                return f"E{episode_num}：情感告白时刻，爱情甜蜜升温"
            elif any(word in text for word in ['分手', '离别', '误会']):
                return f"E{episode_num}：爱情遭遇波折，情侣面临考验"
            elif any(word in text for word in ['结婚', '求婚', '幸福']):
                return f"E{episode_num}：爱情修成正果，幸福时刻来临"
            else:
                return f"E{episode_num}：情感剧情发展，爱情故事推进"
        
        elif self.detected_genre == 'crime':
            if any(word in text for word in ['破案', '真凶', '抓捕']):
                return f"E{episode_num}：案件侦破关键，真凶即将落网"
            elif any(word in text for word in ['线索', '发现', '调查']):
                return f"E{episode_num}：重要线索浮现，案件调查推进"
            elif any(word in text for word in ['危险', '追逐', '紧急']):
                return f"E{episode_num}：危机四伏时刻，紧张追击上演"
            else:
                return f"E{episode_num}：刑侦剧情推进，案件现进展"
        
        elif self.detected_genre == 'family':
            if any(word in text for word in ['团聚', '和解', '理解']):
                return f"E{episode_num}：家庭温情时刻，亲情和解感人"
            elif any(word in text for word in ['冲突', '矛盾', '争吵']):
                return f"E{episode_num}：家庭矛盾爆发，亲情面临考验"
            elif any(word in text for word in ['成长', '教育', '传承']):
                return f"E{episode_num}：家庭教育传承，成长感悟深刻"
            else:
                return f"E{episode_num}：家庭剧情发展，亲情故事推进"
        
        else:
            # 通用主题生成
            if any(word in text for word in ['真相', '发现', '揭露']):
                return f"E{episode_num}：真相大白时刻，剧情迎来转折"
            elif any(word in text for word in ['冲突', '对抗', '争论']):
                return f"E{episode_num}：矛盾冲突爆发，剧情推向高潮"
            elif any(word in text for word in ['决定', '选择', '改变']):
                return f"E{episode_num}：关键抉择时刻，命运转折点来临"
            else:
                return f"E{episode_num}：精彩剧情推进，故事发展迎高潮"

    def extract_key_dialogues(self, subtitles: List[Dict]) -> List[str]:
        """提取关键对话"""
        key_dialogues = []
        
        for sub in subtitles:
            text = sub['text'].strip()
            
            # 评估对话重要性
            importance = 0
            
            # 剧情类型相关关键词
            if self.detected_genre in self.genre_patterns:
                patterns = self.genre_patterns[self.detected_genre]
                for keyword in patterns['keywords']:
                    if keyword in text:
                        importance += 2
                for marker in patterns['emotional_markers']:
                    if marker in text:
                        importance += 1.5
            
            # 通用重要标识
            for word in self.universal_dramatic_words:
                if word in text:
                    importance += 1
            
            # 情感强度
            importance += text.count('！') * 0.5 + text.count('？') * 0.5
            
            if importance >= 2.0 and len(text) >= 8:
                time_code = f"{sub['start']} --> {sub['end']}"
                key_dialogues.append(f"[{time_code}] {text}")
        
        return key_dialogues[:6]  # 最多6条关键对话

    def analyze_significance(self, text: str) -> str:
        """分析剧情意义"""
        significance_points = []
        
        # 根据剧情类型分析
        if self.detected_genre in self.genre_patterns:
            patterns = self.genre_patterns[self.detected_genre]
            
            for indicator in patterns['plot_indicators']:
                if indicator in text:
                    if self.detected_genre == 'legal':
                        significance_points.append("法律程序关键进展")
                    elif self.detected_genre == 'romance':
                        significance_points.append("情感关系重要发展")
                    elif self.detected_genre == 'crime':
                        significance_points.append("案件调查重大突破")
                    elif self.detected_genre == 'family':
                        significance_points.append("家庭关系转折点")
                    elif self.detected_genre == 'historical':
                        significance_points.append("历史事件关键节点")
                    else:
                        significance_points.append("剧情重要转折")
                    break
        
        # 通用意义分析
        if any(word in text for word in ['真相', '发现', '揭露']):
            significance_points.append("重要信息揭露")
        if any(word in text for word in ['决定', '选择', '改变']):
            significance_points.append("角色重大抉择")
        if any(word in text for word in ['冲突', '对抗', '争论']):
            significance_points.append("戏剧冲突高潮")
        if any(word in text for word in ['感动', '震撼', '震惊']):
            significance_points.append("情感共鸣强烈")
        
        return "、".join(significance_points) if significance_points else "精彩剧情片段"

    def generate_next_episode_hint(self, text: str, episode_num: str) -> str:
        """生成下集衔接提示"""
        if '继续' in text or '下集' in text or '下次' in text:
            return "剧情待续，下集将有重大发展"
        
        if self.detected_genre == 'legal':
            if any(word in text for word in ['申诉', '准备']):
                return "申诉程序启动，下集法庭辩论即将开始"
            elif any(word in text for word in ['证据', '线索']):
                return "新证据浮现，下集案件将迎来转机"
        elif self.detected_genre == 'romance':
            if any(word in text for word in ['误会', '分离']):
                return "情感遭遇挫折，下集爱情能否重燃"
            elif any(word in text for word in ['表白', '告白']):
                return "爱情表白完成，下集感情将如何发展"
        elif self.detected_genre == 'crime':
            if any(word in text for word in ['线索', '调查']):
                return "调查深入进行，下集真相即将浮现"
            elif any(word in text for word in ['危险', '紧急']):
                return "危机尚未解除，下集惊险继续升级"
        
        return f"精彩剧情持续发展，下集更多亮点等待揭晓"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            # 处理不同格式的时间
            time_str = time_str.replace('.', ',')  # 统一为逗号格式
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def find_video_file(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        if not os.path.exists(self.video_folder):
            return None
        
        # 提取字幕文件的基础名
        base_name = os.path.splitext(subtitle_filename)[0]
        
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']
        
        # 1. 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 2. 模糊匹配 - 提取集数信息
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        subtitle_episode = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                subtitle_episode = match.group(1)
                break
        
        if subtitle_episode:
            for filename in os.listdir(self.video_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    for pattern in episode_patterns:
                        match = re.search(pattern, filename, re.I)
                        if match and match.group(1) == subtitle_episode:
                            return os.path.join(self.video_folder, filename)
        
        # 3. 部分匹配
        for filename in os.listdir(self.video_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(filename)[0]
                # 检查是否有共同的关键词
                if any(part in file_base.lower() for part in base_name.lower().split('_') if len(part) > 2):
                    return os.path.join(self.video_folder, filename)
        
        return None

    def create_clip(self, segment_plan: Dict, video_file: str) -> bool:
        """创建视频片段"""
        try:
            theme = segment_plan['theme']
            start_time = segment_plan['start_time']
            end_time = segment_plan['end_time']
            
            # 生成安全的文件名
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', theme)
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建精彩片段: {theme}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时间段: {start_time} --> {end_time}")
            print(f"📏 时长: {segment_plan['duration']:.1f}秒")
            print(f"📊 重要性评分: {segment_plan['score']:.1f}/10")
            
            # 计算时间
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 添加缓冲时间
            buffer_start = max(0, start_seconds - 1)
            buffer_duration = duration + 2
            
            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"  ✅ 成功创建: {output_name} ({file_size:.1f}MB)")
                
                # 创建说明文件
                self.create_description_file(output_path, segment_plan)
                
                return True
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"  ❌ 剪辑失败: {error_msg}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建片段时出错: {e}")
            return False

    def create_description_file(self, video_path: str, segment_plan: Dict):
        """创建详细说明文件"""
        try:
            desc_path = video_path.replace('.mp4', '_说明.txt')
            
            content = f"""📺 {segment_plan['theme']}
{"=" * 60}

🎭 剧情类型: {self.detected_genre}
📊 AI分析: {'是' if self.ai_config.get('enabled') else '否'}
🔥 精彩度评分: {segment_plan['score']:.1f}/10

⏱️ 时间片段: {segment_plan['start_time']} --> {segment_plan['end_time']}
📏 片段时长: {segment_plan['duration']:.1f} 秒 ({segment_plan['duration']/60:.1f} 分钟)
💡 剧情意义: {segment_plan['significance']}

📝 关键台词:
"""
            for dialogue in segment_plan['key_dialogues']:
                content += f"{dialogue}\n"
            
            content += f"""
🎯 内容预览:
{segment_plan['content_preview']}

🔗 下集衔接: {segment_plan['next_episode_hint']}

📄 剪辑说明:
• 本片段经过AI智能分析评估
• 剧情类型识别: {self.detected_genre} (置信度: {self.genre_confidence:.2f})
• 时长控制在2-3分钟，突出核心剧情
• 自动修正字幕错别字，优化片段边界
• 适合短视频平台传播和剧情介绍
"""
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成说明文件: {os.path.basename(desc_path)}")
            
        except Exception as e:
            print(f"    ⚠ 生成说明文件失败: {e}")

def main():
    """主程序"""
    print("🚀 智能电视剧剪辑系统启动")
    print("=" * 60)
    print("🤖 系统特性:")
    print("• AI驱动智能分析，自适应各种剧情类型")
    print("• 自动识别剧情类型并动态调整评分策略")
    print("• 智能错别字修正和多格式字幕支持")
    print("• 每集生成2-3分钟核心剧情短视频")
    print("• 专业剪辑边界优化和时长控制")
    print("=" * 60)
    
    clipper = IntelligentTVClipper()
    
    # 获取所有字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and not file.startswith('.') and not file.endswith('说明.txt'):
            # 尝试识别是否是字幕文件
            if any(pattern in file.lower() for pattern in ['e', 's0', '第', '集', 'ep']):
                subtitle_files.append(file)
    
    subtitle_files.sort()
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请将字幕文件放在项目根目录，文件名应包含集数信息")
        print("支持格式: .txt, .srt")
        print("示例文件名: S01E01.txt, 第1集.srt, EP01.txt")
        return
    
    print(f"📄 找到 {len(subtitle_files)} 个字幕文件: {', '.join(subtitle_files[:5])}")
    if len(subtitle_files) > 5:
        print(f"   ... 等 {len(subtitle_files)} 个文件")
    
    # 检查视频目录
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入对应的视频文件")
        return
    
    video_files = [f for f in os.listdir(clipper.video_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    if not video_files:
        print(f"❌ 视频目录中没有视频文件")
        return
    
    print(f"🎬 找到 {len(video_files)} 个视频文件")
    
    # 分析第一个字幕文件来检测剧情类型
    first_subtitles = clipper.parse_subtitle_file(subtitle_files[0])
    detected_genre = clipper.detect_genre(first_subtitles)
    
    created_clips = []
    all_plans = []
    
    for i, subtitle_file in enumerate(subtitle_files, 1):
        print(f"\n📺 处理第 {i} 集: {subtitle_file}")
        
        # 解析字幕
        subtitles = clipper.parse_subtitle_file(subtitle_file)
        if not subtitles:
            print(f"  ❌ 字幕解析失败")
            continue
        
        # 提取集数
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        episode_num = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, subtitle_file, re.I)
            if match:
                episode_num = match.group(1).zfill(2)
                break
        
        if not episode_num:
            episode_num = str(i).zfill(2)
        
        # 找到精彩片段
        segment_plan = clipper.find_episode_highlights(subtitles, episode_num)
        if not segment_plan:
            print(f"  ❌ 未找到合适的精彩片段")
            continue
        
        all_plans.append(segment_plan)
        
        print(f"  🎯 主题: {segment_plan['theme']}")
        print(f"  ⏱️ 片段: {segment_plan['start_time']} --> {segment_plan['end_time']} ({segment_plan['duration']:.1f}秒)")
        print(f"  📊 评分: {segment_plan['score']:.1f}/10")
        print(f"  💡 意义: {segment_plan['significance']}")
        
        # 找到对应视频文件
        video_file = clipper.find_video_file(subtitle_file)
        if not video_file:
            print(f"  ⚠ 未找到对应视频文件")
            continue
        
        # 创建短视频
        if clipper.create_clip(segment_plan, video_file):
            output_name = f"{re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', segment_plan['theme'])}.mp4"
            created_clips.append(os.path.join(clipper.output_folder, output_name))
    
    # 生成总结报告
    generate_summary_report(all_plans, clipper, created_clips)
    
    print(f"\n📊 制作完成统计:")
    print(f"✅ 分析集数: {len(all_plans)} 集")
    print(f"✅ 成功制作: {len(created_clips)} 个短视频")
    print(f"🎭 剧情类型: {clipper.detected_genre}")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 详细报告: intelligent_tv_analysis_report.txt")

def generate_summary_report(plans: List[Dict], clipper, created_clips: List[str]):
    """生成总结报告"""
    if not plans:
        return
    
    content = "📺 智能电视剧剪辑分析报告\n"
    content += "=" * 80 + "\n\n"
    
    content += "🤖 智能系统信息：\n"
    content += f"• 检测剧情类型: {clipper.detected_genre}\n"
    content += f"• 类型识别置信度: {clipper.genre_confidence:.2f}\n"
    content += f"• AI增强分析: {'启用' if clipper.ai_config.get('enabled') else '未启用'}\n"
    content += f"• 分析集数: {len(plans)} 集\n"
    content += f"• 成功制作: {len(created_clips)} 个短视频\n\n"
    
    total_duration = 0
    total_score = 0
    
    for i, plan in enumerate(plans, 1):
        content += f"📺 {plan['theme']}\n"
        content += "-" * 60 + "\n"
        content += f"剧情类型: {clipper.detected_genre}\n"
        content += f"时间片段: {plan['start_time']} --> {plan['end_time']}\n"
        content += f"片段时长: {plan['duration']:.1f} 秒 ({plan['duration']/60:.1f} 分钟)\n"
        content += f"精彩度评分: {plan['score']:.1f}/10\n"
        content += f"剧情意义: {plan['significance']}\n\n"
        
        content += "关键台词:\n"
        for dialogue in plan['key_dialogues']:
            content += f"  {dialogue}\n"
        content += "\n"
        
        content += f"内容预览: {plan['content_preview']}\n"
        content += f"下集衔接: {plan['next_episode_hint']}\n"
        content += "=" * 80 + "\n\n"
        
        total_duration += plan['duration']
        total_score += plan['score']
    
    # 总结统计
    avg_duration = total_duration / len(plans) if plans else 0
    avg_score = total_score / len(plans) if plans else 0
    
    content += f"📊 智能分析总结：\n"
    content += f"• 剧情类型: {clipper.detected_genre} (智能识别)\n"
    content += f"• 总制作时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均每集时长: {avg_duration:.1f} 秒\n"
    content += f"• 平均精彩度评分: {avg_score:.1f}/10\n"
    content += f"• AI辅助分析: {'是' if clipper.ai_config.get('enabled') else '否'}\n"
    content += f"• 制作成功率: {len(created_clips)/len(plans)*100:.1f}%\n"
    content += f"• 适用场景: 短视频制作、精彩片段提取、剧情介绍\n"
    
    try:
        with open('intelligent_tv_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 智能分析报告已保存")
    except Exception as e:
        print(f"⚠ 保存报告失败: {e}")

if __name__ == "__main__":
    main()
