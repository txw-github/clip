#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧智能剪辑系统 - 主程序
基于AI大模型的智能分析，适应各种剧情类型
"""

import os
import sys
import json
import requests
import hashlib
import subprocess
from typing import List, Dict, Optional

class AIClipperSystem:
    def __init__(self):
        self.ai_config = self.load_ai_config()
        self.supported_models = [
            'claude-3-5-sonnet-20240620',
            'deepseek-r1', 
            'gemini-2.5-pro',
            'gpt-4o',
            'deepseek-chat'
        ]
        
        # 目录配置
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.output_folder = "intelligent_clips"
        self.cache_folder = "cache"
        
        # 创建必要目录
        self.setup_directories()

    def setup_directories(self):
        """创建必要目录"""
        dirs = [self.srt_folder, self.videos_folder, self.output_folder, 
               self.cache_folder, f"{self.cache_folder}/analysis", f"{self.cache_folder}/clips"]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        config_file = '.ai_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {
            'enabled': False,
            'base_url': 'https://www.chataiapi.com/v1',
            'api_key': '',
            'model': 'claude-3-5-sonnet-20240620'
        }

    def save_ai_config(self, config: Dict):
        """保存AI配置"""
        with open('.ai_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def setup_ai_config(self):
        """设置AI配置"""
        print("\n🤖 智能AI分析配置")
        print("=" * 50)
        
        try:
            from api_config_helper import config_helper
            config = config_helper.interactive_setup()
            
            if config.get('enabled'):
                self.ai_config = config
                self.save_ai_config(config)
                print("✅ AI配置成功！")
                return True
            else:
                print("⚠️ 跳过AI配置，将使用基础分析模式")
                return False
                
        except ImportError:
            print("❌ 配置助手模块未找到，使用简化配置")
            return self.setup_simple_ai_config()
        except Exception as e:
            print(f"❌ 配置过程出错: {e}")
            return False

    def setup_simple_ai_config(self):
        """简化的AI配置（备用方案）"""
        print("\n📝 简化AI配置")
        print("=" * 30)
        
        api_key = input("输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        print("\n选择API类型:")
        print("1. 中转API (推荐，如ChatAI)")
        print("2. 官方API (需要魔法上网)")
        
        api_type = input("请选择 (1-2): ").strip()
        
        if api_type == "1":
            base_url = input("API地址 (回车使用 https://www.chataiapi.com/v1): ").strip()
            if not base_url:
                base_url = "https://www.chataiapi.com/v1"
            model = input("模型名称 (回车使用 deepseek-r1): ").strip()
            if not model:
                model = "deepseek-r1"
                
            config = {
                'enabled': True,
                'provider': 'chataiapi',
                'base_url': base_url,
                'api_key': api_key,
                'model': model,
                'api_type': 'openai_compatible'
            }
        else:
            print("❌ 无效选择")
            return False

        # 测试连接
        print("🔍 测试API连接...")
        if self.test_ai_connection(config):
            self.ai_config = config
            self.save_ai_config(config)
            print("✅ AI配置成功！")
            return True
        else:
            print("❌ API连接失败")
            return False

    def test_ai_connection(self, config: Dict) -> bool:
        """测试AI连接"""
        try:
            payload = {
                "model": config['model'],
                "messages": [
                    {"role": "system", "content": "你是专业的电视剧剧情分析师"},
                    {"role": "user", "content": "测试连接"}
                ],
                "max_tokens": 10
            }

            url = config['base_url'] + "/chat/completions"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {config["api_key"]}',
                'User-Agent': 'TV-Clipper/1.0.0',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False

    def get_file_hash(self, content: str) -> str:
        """计算内容哈希用于缓存"""
        return hashlib.md5(content.encode()).hexdigest()

    def load_analysis_cache(self, cache_key: str) -> Optional[Dict]:
        """加载分析缓存"""
        cache_path = os.path.join(self.cache_folder, "analysis", f"{cache_key}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save_analysis_cache(self, cache_key: str, analysis: Dict):
        """保存分析缓存"""
        cache_path = os.path.join(self.cache_folder, "analysis", f"{cache_key}.json")
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")

    def call_ai_api(self, prompt: str, system_prompt: str = "你是专业的电视剧剧情分析师") -> Optional[str]:
        """调用AI API"""
        if not self.ai_config.get('enabled'):
            return None

        try:
            payload = {
                "model": self.ai_config['model'],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000,
                "temperature": 0.7
            }

            url = self.ai_config['base_url'] + "/chat/completions"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.ai_config["api_key"]}',
                'User-Agent': 'TV-Clipper/1.0.0',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']
                
                # 处理deepseek-r1的特殊格式
                if 'reasoning_content' in message:
                    print(f"🧠 AI思考过程: {message['reasoning_content'][:100]}...")
                    
                return message.get('content', '')
            else:
                print(f"⚠ API调用失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠ AI调用异常: {e}")
            return None

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件"""
        try:
            # 多编码尝试
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue

            # 智能错别字修正
            corrections = {
                '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
                '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
                '問題': '问题', '機會': '机会', '決定': '决定', '選擇': '选择',
                '聽證會': '听证会', '辯護': '辩护', '審判': '审判', '調查': '调查'
            }

            for old, new in corrections.items():
                content = content.replace(old, new)

            # 解析字幕块
            import re
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
                                'start_seconds': self.time_to_seconds(start_time),
                                'end_seconds': self.time_to_seconds(end_time),
                                'episode': os.path.basename(filepath)
                            })
                    except (ValueError, IndexError):
                        continue

            return subtitles
        except Exception as e:
            print(f"❌ 解析字幕文件失败 {filepath}: {e}")
            return []

    def merge_subtitles_intelligently(self, subtitles: List[Dict]) -> List[Dict]:
        """智能合并字幕，提供完整上下文给AI决策"""
        if not subtitles:
            return []

        merged_segments = []
        current_segment = {'texts': [], 'start_time': '', 'end_time': '', 'subtitles': []}
        
        for i, subtitle in enumerate(subtitles):
            current_segment['texts'].append(subtitle['text'])
            current_segment['subtitles'].append(subtitle)
            
            if not current_segment['start_time']:
                current_segment['start_time'] = subtitle['start']
            current_segment['end_time'] = subtitle['end']
            
            # 动态决定分段 - 遇到较长停顿或足够内容时分段
            next_subtitle = subtitles[i + 1] if i + 1 < len(subtitles) else None
            should_split = False
            
            if next_subtitle:
                time_gap = next_subtitle['start_seconds'] - subtitle['end_seconds']
                segment_length = len(' '.join(current_segment['texts']))
                
                # 分段条件：时间间隔大于3秒 或 文本长度超过800字 或 遇到场景转换标识
                if (time_gap > 3 or segment_length > 800 or 
                    any(keyword in subtitle['text'] for keyword in ['场景', '切换', '另一边', '同时', '回到'])):
                    should_split = True
            else:
                should_split = True  # 最后一个字幕
            
            if should_split:
                merged_segments.append({
                    'segment_text': ' '.join(current_segment['texts']),
                    'start_time': current_segment['start_time'],
                    'end_time': current_segment['end_time'],
                    'duration': self.time_to_seconds(current_segment['end_time']) - 
                              self.time_to_seconds(current_segment['start_time']),
                    'subtitle_count': len(current_segment['subtitles']),
                    'position_ratio': i / len(subtitles)
                })
                current_segment = {'texts': [], 'start_time': '', 'end_time': '', 'subtitles': []}

        return merged_segments

    def ai_analyze_complete_episode(self, segments: List[Dict], episode_file: str) -> Dict:
        """AI分析完整剧集，支持缓存"""
        # 生成缓存key
        content_for_hash = json.dumps([s['segment_text'] for s in segments], sort_keys=True)
        cache_key = self.get_file_hash(content_for_hash + episode_file)
        
        # 尝试加载缓存
        cached_analysis = self.load_analysis_cache(cache_key)
        if cached_analysis:
            print(f"  📋 使用缓存分析结果")
            return cached_analysis

        if not self.ai_config.get('enabled'):
            return self.fallback_analysis(segments, episode_file)

        # 构建完整上下文
        episode_context = self.build_complete_context(segments, episode_file)
        
        prompt = f"""你是专业的影视剪辑师和剧情分析专家。请深度分析这一集电视剧的完整内容，智能识别出适合制作短视频的精彩片段。

【剧集信息】: {episode_file}
【完整剧情上下文】:
{episode_context}

请进行专业分析：

1. **深度剧情理解**:
   - 分析主要剧情线和角色关系
   - 识别关键冲突点和情感转折
   - 理解剧情的因果关系和发展脉络

2. **智能片段识别** (3-5个精彩片段):
   - 每个片段2-3分钟，有完整戏剧结构
   - 优先选择戏剧冲突、情感高潮、真相揭露等精彩内容
   - 确保片段间逻辑连贯，能完整叙述本集故事
   - 考虑短视频观众的观看习惯和吸引力

3. **专业旁白设计**:
   - 为每个片段设计引人入胜的解说
   - 解释背景、人物动机、剧情意义
   - 语言要生动有趣，适合现代观众

4. **连贯性保证**:
   - 处理可能的剧情反转和伏笔
   - 确保与前后集的逻辑关联
   - 保证一句话讲完的完整性

请以JSON格式返回：
{{
    "episode_analysis": {{
        "main_storyline": "主要剧情线",
        "key_characters": ["主要角色1", "主要角色2"],
        "dramatic_elements": ["戏剧元素1", "戏剧元素2"],
        "emotional_tone": "情感基调"
    }},
    "intelligent_clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "start_time": "00:05:30,000",
            "end_time": "00:08:15,000",
            "duration_seconds": 165,
            "significance": "剧情意义和价值",
            "hook_factor": "吸引观众的核心卖点",
            "narrative_structure": {{
                "setup": "背景铺垫",
                "conflict": "核心冲突", 
                "climax": "高潮部分",
                "resolution": "结果解决"
            }},
            "professional_commentary": {{
                "opening_hook": "开场吸引解说",
                "background_context": "背景解释",
                "plot_analysis": "剧情分析",
                "emotional_impact": "情感冲击说明",
                "conclusion": "总结升华"
            }},
            "connection_next": "与下个片段的逻辑连接"
        }}
    ],
    "episode_summary": "本集完整剧情概述",
    "continuity_notes": "与前后集的连贯性说明",
    "series_context": "在整个剧集中的位置和作用"
}}"""

        print(f"  🤖 AI深度分析中...")
        response = self.call_ai_api(prompt)
        
        if response:
            try:
                # 解析JSON响应
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    json_text = response[json_start:json_end]
                else:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_text = response[start:end]
                
                analysis = json.loads(json_text)
                processed_analysis = self.process_analysis_result(analysis, segments, episode_file)
                
                # 保存到缓存
                self.save_analysis_cache(cache_key, processed_analysis)
                print(f"  ✅ AI分析完成，已缓存")
                
                return processed_analysis
                
            except Exception as e:
                print(f"⚠ AI分析结果解析失败: {e}")
                return self.fallback_analysis(segments, episode_file)
        
        return self.fallback_analysis(segments, episode_file)

    def build_complete_context(self, segments: List[Dict], episode_file: str) -> str:
        """构建完整的剧集上下文"""
        context_parts = []
        
        for i, segment in enumerate(segments[:30]):  # 限制长度避免API超限
            time_info = f"[时间段 {i+1}: {segment['start_time']} - {segment['end_time']}]"
            position_info = f"[剧集位置: {segment['position_ratio']*100:.0f}%]"
            
            # 截取适当长度的文本
            text = segment['segment_text']
            if len(text) > 400:
                text = text[:400] + "..."
            
            context_parts.append(f"{time_info} {position_info}\n{text}")
        
        return "\n\n".join(context_parts)

    def process_analysis_result(self, analysis: Dict, segments: List[Dict], episode_file: str) -> Dict:
        """处理AI分析结果"""
        processed_clips = []
        
        for clip in analysis.get('intelligent_clips', []):
            # 验证和优化时间码
            optimized_clip = self.optimize_clip_timing(clip, segments)
            if optimized_clip:
                processed_clips.append(optimized_clip)
        
        # 提取集数
        import re
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        episode_number = episode_match.group(1) if episode_match else "00"
        
        return {
            'episode_file': episode_file,
            'episode_number': episode_number,
            'episode_analysis': analysis.get('episode_analysis', {}),
            'clips': processed_clips,
            'episode_summary': analysis.get('episode_summary', ''),
            'continuity_notes': analysis.get('continuity_notes', ''),
            'series_context': analysis.get('series_context', ''),
            'ai_generated': True,
            'total_clips': len(processed_clips)
        }

    def optimize_clip_timing(self, clip: Dict, segments: List[Dict]) -> Optional[Dict]:
        """优化剪辑时间，确保完整性"""
        start_time = clip.get('start_time', '')
        end_time = clip.get('end_time', '')
        
        if not start_time or not end_time:
            return None
        
        start_seconds = self.time_to_seconds(start_time)
        end_seconds = self.time_to_seconds(end_time)
        
        # 找到最佳的segment边界
        best_start = start_seconds
        best_end = end_seconds
        
        # 向前扩展确保完整句子
        for segment in segments:
            seg_start = self.time_to_seconds(segment['start_time'])
            seg_end = self.time_to_seconds(segment['end_time'])
            
            if seg_start <= start_seconds <= seg_end:
                best_start = seg_start
            if seg_start <= end_seconds <= seg_end:
                best_end = seg_end
        
        # 添加缓冲确保完整性
        buffer = 2.0
        final_start = max(0, best_start - buffer)
        final_end = best_end + buffer
        
        return {
            'clip_id': clip.get('clip_id', 1),
            'title': clip.get('title', '精彩片段'),
            'start_time': self.seconds_to_time(final_start),
            'end_time': self.seconds_to_time(final_end),
            'duration': final_end - final_start,
            'significance': clip.get('significance', ''),
            'hook_factor': clip.get('hook_factor', ''),
            'narrative_structure': clip.get('narrative_structure', {}),
            'professional_commentary': clip.get('professional_commentary', {}),
            'connection_next': clip.get('connection_next', '')
        }

    def fallback_analysis(self, segments: List[Dict], episode_file: str) -> Dict:
        """备用分析（无AI时）"""
        high_intensity_segments = []
        
        keywords = ['突然', '发现', '真相', '秘密', '不可能', '为什么', '杀人', '死了', 
                   '救命', '危险', '完了', '震惊', '愤怒', '哭', '崩溃', '爱你', '分手',
                   '四二八案', '628旧案', '听证会', '辩护', '检察官', '法官']
        
        for i, segment in enumerate(segments):
            score = 0
            text = segment['segment_text']
            
            for keyword in keywords:
                score += text.count(keyword) * 3
            
            score += text.count('！') * 2 + text.count('？') * 2 + text.count('...') * 1
            
            if score >= 8 and segment['duration'] >= 60:  # 至少1分钟
                high_intensity_segments.append({
                    'segment': segment,
                    'score': score,
                    'index': i
                })
        
        high_intensity_segments.sort(key=lambda x: x['score'], reverse=True)
        selected_segments = high_intensity_segments[:4]  # 选择前4个
        
        clips = []
        for i, item in enumerate(selected_segments):
            segment = item['segment']
            clips.append({
                'clip_id': i + 1,
                'title': f"精彩片段{i + 1}",
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'duration': segment['duration'],
                'significance': '基于关键词识别的戏剧性片段',
                'hook_factor': '包含强烈戏剧冲突',
                'narrative_structure': {
                    'setup': '剧情背景',
                    'conflict': '核心冲突',
                    'climax': '情感高潮',
                    'resolution': '暂时解决'
                },
                'professional_commentary': {
                    'opening_hook': f"在这个关键片段中",
                    'background_context': "剧情发展到重要节点",
                    'plot_analysis': "角色面临重要选择",
                    'emotional_impact': "情感达到高潮",
                    'conclusion': "为后续发展埋下伏笔"
                },
                'connection_next': '与下个片段形成逻辑递进'
            })
        
        import re
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        episode_number = episode_match.group(1) if episode_match else "00"
        
        return {
            'episode_file': episode_file,
            'episode_number': episode_number,
            'episode_analysis': {
                'main_storyline': '剧情发展与冲突',
                'key_characters': ['主要角色'],
                'dramatic_elements': ['戏剧冲突', '情感转折'],
                'emotional_tone': '紧张激烈'
            },
            'clips': clips,
            'episode_summary': '本集包含多个关键剧情转折和情感高潮',
            'continuity_notes': '与前后集保持剧情连贯性',
            'series_context': '推进主线剧情发展',
            'ai_generated': False,
            'total_clips': len(clips)
        }

    def find_matching_video(self, episode_file: str) -> Optional[str]:
        """查找匹配的视频文件"""
        base_name = os.path.splitext(episode_file)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 集数匹配
        import re
        episode_match = re.search(r'[Ee](\d+)', base_name)
        if episode_match:
            episode_num = episode_match.group(1)
            for filename in os.listdir(self.videos_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    video_match = re.search(r'[Ee](\d+)', filename)
                    if video_match and video_match.group(1) == episode_num:
                        return os.path.join(self.videos_folder, filename)
        
        return None

    def create_video_clips(self, video_file: str, analysis: Dict) -> List[str]:
        """创建视频片段，支持缓存和断点续传"""
        created_clips = []
        episode_number = analysis['episode_number']
        
        print(f"  🎬 开始剪辑 {len(analysis['clips'])} 个片段")
        
        for clip in analysis['clips']:
            # 检查是否已存在
            clip_filename = self.generate_clip_filename(episode_number, clip)
            clip_path = os.path.join(self.output_folder, clip_filename)
            
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                print(f"    ✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue
            
            # 执行剪辑
            if self.create_single_clip(video_file, clip, clip_path):
                created_clips.append(clip_path)
                # 创建旁白文件
                self.create_commentary_file(clip_path, clip)
        
        return created_clips

    def generate_clip_filename(self, episode_number: str, clip: Dict) -> str:
        """生成剪辑文件名"""
        safe_title = self.sanitize_filename(clip['title'])
        return f"E{episode_number}_C{clip['clip_id']:02d}_{safe_title}.mp4"

    def sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        import re
        # 保留中文、英文、数字和基本符号
        safe_name = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', filename)
        return safe_name[:30]  # 限制长度

    def create_single_clip(self, video_file: str, clip: Dict, output_path: str, max_retries: int = 3) -> bool:
        """创建单个视频片段（带重试）"""
        for attempt in range(max_retries):
            try:
                start_seconds = self.time_to_seconds(clip['start_time'])
                duration = clip['duration']
                
                print(f"    🎬 剪辑片段 {clip['clip_id']}: {clip['title']} (尝试 {attempt + 1})")
                print(f"        时间: {clip['start_time']} --> {clip['end_time']} ({duration:.1f}秒)")
                
                cmd = [
                    'ffmpeg',
                    '-i', video_file,
                    '-ss', str(start_seconds),
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '23',
                    '-avoid_negative_ts', 'make_zero',
                    output_path,
                    '-y'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024*1024)
                    if file_size > 0.1:  # 至少100KB
                        print(f"        ✅ 剪辑成功: {file_size:.1f}MB")
                        return True
                    else:
                        print(f"        ❌ 文件太小，可能失败")
                        if os.path.exists(output_path):
                            os.remove(output_path)
                else:
                    error_msg = result.stderr[:200] if result.stderr else "未知错误"
                    print(f"        ❌ 剪辑失败 (尝试 {attempt + 1}): {error_msg}")
                    
            except subprocess.TimeoutExpired:
                print(f"        ❌ 剪辑超时 (尝试 {attempt + 1})")
            except Exception as e:
                print(f"        ❌ 剪辑异常 (尝试 {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                print(f"        ⏰ 等待3秒后重试...")
                import time
                time.sleep(3)
        
        print(f"    ❌ 剪辑最终失败: {clip['title']}")
        return False

    def create_commentary_file(self, video_path: str, clip: Dict):
        """创建专业旁白文件"""
        commentary_path = video_path.replace('.mp4', '_旁白解说.txt')
        
        commentary = clip.get('professional_commentary', {})
        
        content = f"""📺 专业旁白解说 - {clip['title']}
{'='*60}

🎯 片段价值: {clip.get('significance', '未知')}
🎪 吸引卖点: {clip.get('hook_factor', '未知')}

📖 叙事结构:
├─ 背景铺垫: {clip.get('narrative_structure', {}).get('setup', '暂无')}
├─ 核心冲突: {clip.get('narrative_structure', {}).get('conflict', '暂无')}
├─ 高潮部分: {clip.get('narrative_structure', {}).get('climax', '暂无')}
└─ 结果解决: {clip.get('narrative_structure', {}).get('resolution', '暂无')}

🎙️ 专业解说词:

【开场引入】
{commentary.get('opening_hook', '在这个精彩片段中...')}

【背景解释】
{commentary.get('background_context', '故事背景说明...')}

【剧情分析】
{commentary.get('plot_analysis', '剧情深度分析...')}

【情感冲击】
{commentary.get('emotional_impact', '情感冲击说明...')}

【总结升华】
{commentary.get('conclusion', '内容总结和升华...')}

🔗 与下片段连接: {clip.get('connection_next', '暂无')}

⏱️ 时间轴: {clip.get('start_time', '')} --> {clip.get('end_time', '')} ({clip.get('duration', 0):.1f}秒)
"""
        
        try:
            with open(commentary_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"        📝 生成旁白: {os.path.basename(commentary_path)}")
        except Exception as e:
            print(f"        ⚠️ 生成旁白失败: {e}")

    def run_advanced_clipping(self):
        """运行高级智能剪辑（整合所有改进）"""
        print("🚀 启动高级智能剪辑系统")
        print("=" * 60)
        print("✨ 集成所有改进功能:")
        print("  • AI深度剧情理解，非固定规则")
        print("  • 完整上下文分析，避免剧情割裂")
        print("  • 智能多段识别，每集3-5个短视频")
        print("  • 自动视频剪辑+专业旁白解说")
        print("  • 缓存系统，支持断点续传")
        print("  • 保证剧情连贯性和完整性")
        print("  • 一句话讲完的完整保证")
        
        # 检查文件
        srt_files = self.get_srt_files()
        if not srt_files:
            print("\n❌ srt目录中没有字幕文件")
            print("请将.srt字幕文件放入srt/目录")
            return
        
        video_files = self.get_video_files()
        if not video_files:
            print("❌ videos目录中没有视频文件")
            print("请将视频文件放入videos/目录")
            return
        
        print(f"\n✅ 找到 {len(srt_files)} 个字幕文件")
        print(f"✅ 找到 {len(video_files)} 个视频文件")
        
        ai_status = "🤖 AI智能分析" if self.ai_config.get('enabled') else "📝 规则分析"
        print(f"🎯 分析模式: {ai_status}")
        
        if self.ai_config.get('enabled'):
            print(f"🤖 AI模型: {self.ai_config.get('model', 'unknown')}")
        
        # 处理所有剧集
        all_results = []
        total_clips = 0
        
        for srt_file in srt_files:
            print(f"\n{'='*60}")
            print(f"📺 处理剧集: {srt_file}")
            print(f"{'='*60}")
            
            try:
                # 1. 解析字幕
                srt_path = os.path.join(self.srt_folder, srt_file)
                subtitles = self.parse_srt_file(srt_path)
                
                if not subtitles:
                    print("  ❌ 字幕解析失败")
                    continue
                
                print(f"  📝 解析字幕: {len(subtitles)} 条")
                
                # 2. 智能合并字幕段落
                segments = self.merge_subtitles_intelligently(subtitles)
                print(f"  📑 智能合并: {len(segments)} 个连贯段落")
                
                # 3. AI深度分析
                analysis = self.ai_analyze_complete_episode(segments, srt_file)
                
                if not analysis['clips']:
                    print("  ❌ 未识别到精彩片段")
                    continue
                
                print(f"  🎯 识别精彩片段: {len(analysis['clips'])} 个")
                print(f"  📖 剧情主线: {analysis['episode_analysis'].get('main_storyline', '未知')}")
                
                # 4. 查找匹配视频
                video_file = self.find_matching_video(srt_file)
                if not video_file:
                    print("  ❌ 未找到匹配的视频文件")
                    continue
                
                print(f"  📹 匹配视频: {os.path.basename(video_file)}")
                
                # 5. 创建视频片段
                created_clips = self.create_video_clips(video_file, analysis)
                
                if created_clips:
                    print(f"  ✅ 成功创建: {len(created_clips)} 个短视频")
                    total_clips += len(created_clips)
                    
                    # 6. 生成剧集说明
                    self.create_episode_report(analysis, created_clips)
                    
                    all_results.append({
                        'episode': srt_file,
                        'analysis': analysis,
                        'clips': created_clips
                    })
                else:
                    print("  ❌ 视频剪辑失败")
                    
            except Exception as e:
                print(f"  ❌ 处理出错: {e}")
        
        # 7. 生成完整报告
        if all_results:
            self.create_complete_report(all_results)
            
            print(f"\n🎉 高级智能剪辑完成！")
            print(f"{'='*60}")
            print(f"📊 处理统计:")
            print(f"  ✅ 成功处理: {len(all_results)} 集")
            print(f"  🎬 创建短视频: {total_clips} 个")
            print(f"  📁 输出目录: {self.output_folder}/")
            print(f"  📝 包含专业旁白解说文件")
            print(f"  💾 分析结果已缓存，支持断点续传")
            print(f"  🔄 保证跨集剧情连贯性")
        else:
            print("\n❌ 没有成功处理任何剧集")

    def get_srt_files(self) -> List[str]:
        """获取字幕文件列表"""
        if not os.path.exists(self.srt_folder):
            return []
        
        files = [f for f in os.listdir(self.srt_folder) if f.endswith('.srt')]
        files.sort()
        return files

    def get_video_files(self) -> List[str]:
        """获取视频文件列表"""
        if not os.path.exists(self.videos_folder):
            return []
        
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        files = [f for f in os.listdir(self.videos_folder) 
                if any(f.lower().endswith(ext) for ext in video_extensions)]
        files.sort()
        return files

    def create_episode_report(self, analysis: Dict, created_clips: List[str]):
        """创建单集详细报告"""
        episode_number = analysis['episode_number']
        report_path = os.path.join(self.output_folder, f"E{episode_number}_详细分析报告.txt")
        
        content = f"""📺 第{episode_number}集 - 智能分析与剪辑报告
{'='*80}

🎭 剧情分析:
主要剧情线: {analysis['episode_analysis'].get('main_storyline', '未知')}
核心角色: {', '.join(analysis['episode_analysis'].get('key_characters', []))}
戏剧元素: {', '.join(analysis['episode_analysis'].get('dramatic_elements', []))}
情感基调: {analysis['episode_analysis'].get('emotional_tone', '未知')}

📖 本集概述:
{analysis.get('episode_summary', '暂无概述')}

🎬 精彩片段详情 ({len(analysis['clips'])} 个):
"""
        
        for i, clip in enumerate(analysis['clips'], 1):
            content += f"""
片段 {clip['clip_id']}: {clip['title']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ 时间轴: {clip['start_time']} --> {clip['end_time']} ({clip['duration']:.1f}秒)
🎯 剧情价值: {clip.get('significance', '未知')}
🎪 吸引卖点: {clip.get('hook_factor', '未知')}

📖 叙事结构:
  背景铺垫: {clip.get('narrative_structure', {}).get('setup', '暂无')}
  核心冲突: {clip.get('narrative_structure', {}).get('conflict', '暂无')}
  高潮部分: {clip.get('narrative_structure', {}).get('climax', '暂无')}
  结果解决: {clip.get('narrative_structure', {}).get('resolution', '暂无')}

🎙️ 专业解说要点:
  开场引入: {clip.get('professional_commentary', {}).get('opening_hook', '暂无')}
  背景解释: {clip.get('professional_commentary', {}).get('background_context', '暂无')}
  剧情分析: {clip.get('professional_commentary', {}).get('plot_analysis', '暂无')}
  情感冲击: {clip.get('professional_commentary', {}).get('emotional_impact', '暂无')}
  总结升华: {clip.get('professional_commentary', {}).get('conclusion', '暂无')}

🔗 连接下片段: {clip.get('connection_next', '暂无')}
"""
        
        content += f"""

🔄 连贯性分析:
{analysis.get('continuity_notes', '暂无')}

📚 剧集定位:
{analysis.get('series_context', '暂无')}

📊 技术信息:
• AI分析: {'是' if analysis.get('ai_generated') else '否'}
• 生成时间: {self.get_current_time()}
• 视频文件: {len(created_clips)} 个
• 缓存支持: 是（支持断点续传）
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    📄 生成详细报告: E{episode_number}_详细分析报告.txt")
        except Exception as e:
            print(f"    ⚠️ 生成报告失败: {e}")

    def create_complete_report(self, all_results: List[Dict]):
        """创建完整剧集连贯性报告"""
        report_path = os.path.join(self.output_folder, "完整剧集连贯性总结.txt")
        
        total_clips = sum(len(r['clips']) for r in all_results)
        
        content = f"""📺 完整剧集智能分析总结报告
{'='*80}
生成时间: {self.get_current_time()}
处理集数: {len(all_results)} 集
总短视频: {total_clips} 个
分析模式: {'AI智能增强' if self.ai_config.get('enabled') else '规则分析'}

🎭 整体剧情发展脉络:
"""
        
        for result in all_results:
            analysis = result['analysis']
            content += f"""
第{analysis['episode_number']}集: {analysis['episode_analysis'].get('main_storyline', '未知')}
├─ 精彩片段: {len(analysis['clips'])} 个
├─ 剧集定位: {analysis.get('series_context', '暂无')}
└─ 连贯性: {analysis.get('continuity_notes', '暂无')}
"""
        
        content += f"""

📊 智能剪辑统计:
• 总处理集数: {len(all_results)} 集
• 总短视频数: {total_clips} 个
• 平均每集短视频: {total_clips / len(all_results):.1f} 个
• 输出目录: {self.output_folder}/
• 旁白解说文件: 每个短视频配套
• 缓存机制: 支持断点续传

🔄 跨集连贯性保证:
• 所有片段按时间顺序能完整叙述剧情
• 每个片段包含专业旁白解说背景和意义
• AI分析考虑了剧情反转和伏笔的前后关联
• 确保一句话讲完的完整性
• 智能识别而非固定规则，适应各种剧情类型

💡 使用建议:
• 每个短视频都有对应的旁白解说文件
• 缓存系统保证多次执行结果一致
• 支持断点续传，已处理内容不重复
• 视频文件在 {self.output_folder}/ 目录
• 旁白文件以 _旁白解说.txt 结尾
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 完整报告: 完整剧集连贯性总结.txt")
        except Exception as e:
            print(f"生成完整报告失败: {e}")

    def get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def seconds_to_time(self, seconds: float) -> str:
        """秒转时间"""
        try:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        except:
            return "00:00:00,000"

    def analyze_all_episodes(self) -> List[Dict]:
        """分析所有剧集（仅分析，不剪辑）"""
        # 智能识别字幕文件
        subtitle_files = []
        for file in os.listdir('.'):
            if file.endswith(('.txt', '.srt')) and not file.startswith('.'):
                # 排除系统文件
                if any(keyword in file.lower() for keyword in ['readme', 'config', 'license']):
                    continue
                subtitle_files.append(file)

        subtitle_files.sort()

        if not subtitle_files:
            print("❌ 未找到字幕文件")
            return []

        print(f"📁 发现 {len(subtitle_files)} 个字幕文件")

        all_results = []

        for filename in subtitle_files:
            print(f"\n🔍 分析: {filename}")
            subtitles = self.parse_subtitle_file(filename)

            if subtitles:
                result = self.ai_analyze_episode_content(subtitles, filename)
                all_results.append(result)

                print(f"✅ {result['theme']}")
                print(f"   剧情类型: {result['genre']}")
                print(f"   推荐片段: {len(result['clips'])} 个")
                if result['ai_analysis']:
                    print("   🤖 AI智能分析")
                else:
                    print("   📝 关键词分析")
            else:
                print(f"❌ 解析失败: {filename}")

        # 生成报告
        self.generate_analysis_report(all_results)

        return all_results

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件 - 通用格式支持"""
        try:
            # 多编码尝试
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue

            # 智能错别字修正
            corrections = {
                '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
                '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
                '問題': '问题', '機會': '机会', '決定': '决定', '選擇': '选择',
                '聽證會': '听证会', '辯護': '辩护', '審判': '审判', '調查': '调查'
            }

            for old, new in corrections.items():
                content = content.replace(old, new)

            # 解析字幕块
            import re
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
        except Exception as e:
            print(f"❌ 解析字幕文件失败 {filepath}: {e}")
            return []

    def ai_analyze_episode_content(self, subtitles: List[Dict], episode_name: str) -> Dict:
        """AI智能分析剧集内容"""
        if not self.ai_config.get('enabled'):
            return self.fallback_analysis_old(subtitles, episode_name)

        # 提取关键对话内容
        key_dialogues = []
        for sub in subtitles[::10]:  # 每10条取1条，避免过长
            if len(sub['text']) > 10:
                key_dialogues.append(f"[{sub['start']}] {sub['text']}")

        content_sample = '\n'.join(key_dialogues[:50])  # 最多50条

        prompt = f"""
请分析以下电视剧片段内容，识别最精彩的剧情片段用于短视频剪辑。

【剧集名称】: {episode_name}
【对话内容】:
{content_sample}

请从以下维度进行智能分析：
1. 剧情类型识别（法律、爱情、犯罪、家庭、古装、现代等）
2. 核心冲突点和戏剧张力
3. 情感高潮时刻
4. 关键信息揭露点
5. 推荐的剪辑片段（2-3个最精彩的时间段）

输出格式（JSON）：
{{
    "genre": "剧情类型",
    "theme": "本集核心主题",
    "key_conflicts": ["冲突1", "冲突2"],
    "emotional_peaks": ["情感高潮1", "情感高潮2"],
    "recommended_clips": [
        {{
            "start_time": "开始时间",
            "end_time": "结束时间", 
            "reason": "推荐理由",
            "content": "内容描述"
        }}
    ],
    "next_episode_hint": "与下集的衔接点"
}}
"""

        ai_response = self.call_ai_api(prompt)

        if ai_response:
            try:
                # 提取JSON部分
                if "```json" in ai_response:
                    json_start = ai_response.find("```json") + 7
                    json_end = ai_response.find("```", json_start)
                    json_text = ai_response[json_start:json_end].strip()
                else:
                    start = ai_response.find("{")
                    end = ai_response.rfind("}") + 1
                    json_text = ai_response[start:end]

                result = json.loads(json_text)
                return self.process_ai_analysis_old(result, subtitles, episode_name)

            except Exception as e:
                print(f"⚠ AI回复解析失败: {e}")
                return self.fallback_analysis_old(subtitles, episode_name)

        return self.fallback_analysis_old(subtitles, episode_name)

    def process_ai_analysis_old(self, ai_result: Dict, subtitles: List[Dict], episode_name: str) -> Dict:
        """处理AI分析结果"""
        clips = []

        for rec_clip in ai_result.get('recommended_clips', []):
            start_time = rec_clip.get('start_time')
            end_time = rec_clip.get('end_time')

            if start_time and end_time:
                clips.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': self.time_to_seconds(end_time) - self.time_to_seconds(start_time),
                    'reason': rec_clip.get('reason', ''),
                    'content': rec_clip.get('content', ''),
                    'ai_recommended': True
                })

        # 提取集数
        import re
        episode_match = re.search(r'[Ee](\d+)', episode_name)
        episode_num = episode_match.group(1) if episode_match else "00"

        return {
            'episode': episode_name,
            'episode_number': episode_num,
            'theme': f"E{episode_num}: {ai_result.get('theme', '精彩片段')}",
            'genre': ai_result.get('genre', '未知'),
            'clips': clips,
            'key_conflicts': ai_result.get('key_conflicts', []),
            'emotional_peaks': ai_result.get('emotional_peaks', []),
            'next_episode_hint': ai_result.get('next_episode_hint', ''),
            'ai_analysis': True
        }

    def fallback_analysis_old(self, subtitles: List[Dict], episode_name: str) -> Dict:
        """备用分析（无AI时）"""
        # 基于关键词的简单分析
        dramatic_keywords = [
            '突然', '发现', '真相', '秘密', '不可能', '为什么', '杀人', '死了', 
            '救命', '危险', '完了', '震惊', '愤怒', '哭', '崩溃'
        ]

        high_score_segments = []

        for i, subtitle in enumerate(subtitles):
            score = 0
            text = subtitle['text']

            # 关键词评分
            for keyword in dramatic_keywords:
                if keyword in text:
                    score += 2

            # 标点符号评分
            score += text.count('！') + text.count('？') + text.count('...') * 0.5

            if score >= 3:
                high_score_segments.append({
                    'index': i,
                    'subtitle': subtitle,
                    'score': score
                })

        # 选择最佳片段
        high_score_segments.sort(key=lambda x: x['score'], reverse=True)

        clips = []
        for seg in high_score_segments[:3]:  # 最多3个片段
            start_idx = max(0, seg['index'] - 10)
            end_idx = min(len(subtitles) - 1, seg['index'] + 15)

            clips.append({
                'start_time': subtitles[start_idx]['start'],
                'end_time': subtitles[end_idx]['end'],
                'duration': self.time_to_seconds(subtitles[end_idx]['end']) - self.time_to_seconds(subtitles[start_idx]['start']),
                'reason': '基于关键词识别的精彩片段',
                'content': seg['subtitle']['text'],
                'ai_recommended': False
            })

        import re
        episode_match = re.search(r'[Ee](\d+)', episode_name)
        episode_num = episode_match.group(1) if episode_match else "00"

        return {
            'episode': episode_name,
            'episode_number': episode_num,
            'theme': f"E{episode_num}: 精彩片段合集",
            'genre': '通用',
            'clips': clips,
            'key_conflicts': ['剧情冲突'],
            'emotional_peaks': ['情感高潮'],
            'next_episode_hint': '故事继续发展',
            'ai_analysis': False
        }

    def generate_analysis_report(self, results: List[Dict]):
        """生成分析报告"""
        if not results:
            return

        content = "📺 智能电视剧分析报告\n"
        content += "=" * 80 + "\n\n"

        if self.ai_config.get('enabled'):
            content += f"🤖 AI分析模式: {self.ai_config['model']}\n"
        else:
            content += "📝 关键词分析模式\n"

        content += f"📊 分析集数: {len(results)} 集\n\n"

        total_clips = 0
        for result in results:
            content += f"📺 {result['theme']}\n"
            content += "-" * 60 + "\n"
            content += f"剧情类型: {result['genre']}\n"
            content += f"推荐片段: {len(result['clips'])} 个\n"

            for i, clip in enumerate(result['clips'], 1):
                content += f"\n🎬 片段 {i}:\n"
                content += f"   时间: {clip['start_time']} --> {clip['end_time']}\n"
                content += f"   时长: {clip['duration']:.1f} 秒\n"
                content += f"   推荐理由: {clip['reason']}\n"
                content += f"   内容: {clip['content'][:50]}...\n"

            if result['key_conflicts']:
                content += f"\n💥 核心冲突: {', '.join(result['key_conflicts'])}\n"

            if result['emotional_peaks']:
                content += f"😊 情感高潮: {', '.join(result['emotional_peaks'])}\n"

            content += f"🔗 下集衔接: {result['next_episode_hint']}\n"
            content += "=" * 80 + "\n\n"

            total_clips += len(result['clips'])

        content += f"📊 总计推荐片段: {total_clips} 个\n"

        with open('智能分析报告.txt', 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n📄 分析报告已保存: 智能分析报告.txt")

    def main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("📺 智能电视剧分析剪辑系统")
            print("=" * 60)

            ai_status = "🤖 AI增强" if self.ai_config.get('enabled') else "📝 关键词分析"
            print(f"当前模式: {ai_status}")

            if self.ai_config.get('enabled'):
                print(f"AI模型: {self.ai_config['model']}")

            print("请选择操作:")
            print("1. 📝 智能分析字幕")
            print("2. 🎬 高级智能剪辑 (推荐)")
            print("3. 🤖 配置AI接口")
            print("4. 📊 查看分析报告")
            print("5. ❌ 退出")

            try:
                choice = input("\n请输入选择 (1-5): ").strip()

                if choice == '1':
                    self.analyze_all_episodes()

                elif choice == '2':
                    # 高级智能剪辑 - 整合所有改进功能
                    self.run_advanced_clipping()

                elif choice == '3':
                    self.setup_ai_config()

                elif choice == '4':
                    # 查看多种报告
                    reports = [
                        '智能分析报告.txt',
                        f'{self.output_folder}/完整剧集连贯性总结.txt',
                        'smart_analysis_report.txt'
                    ]

                    found_report = False
                    for report_file in reports:
                        if os.path.exists(report_file):
                            with open(report_file, 'r', encoding='utf-8') as f:
                                print(f"\n📄 {report_file}:")
                                content = f.read()
                                print(content[:1500] + "..." if len(content) > 1500 else content)
                                found_report = True
                                break

                    if not found_report:
                        print("❌ 未找到分析报告，请先执行分析")

                elif choice == '5':
                    print("\n👋 再见！")
                    break

                else:
                    print("❌ 无效选择")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break

def check_environment():
    """检查环境"""
    print("🔍 检查运行环境...")

    # 检查字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and not file.startswith('.'):
            if not any(keyword in file.lower() for keyword in ['readme', 'config', 'license']):
                subtitle_files.append(file)

    if subtitle_files:
        print(f"✅ 找到 {len(subtitle_files)} 个字幕文件")
        return True
    else:
        print("❌ 未找到字幕文件")
        print("请确保字幕文件(.txt/.srt)在当前目录")
        return False

def main():
    """主函数"""
    print("🚀 智能电视剧分析剪辑系统启动")

    if not check_environment():
        input("\n按Enter键退出...")
        return

    try:
        system = AIClipperSystem()
        system.main_menu()
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        input("\n按Enter键退出...")

if __name__ == "__main__":
    main()