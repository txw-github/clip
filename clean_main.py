
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能电视剧剪辑系统 - 全新重构版本
完全AI驱动的智能分析和剪辑系统
"""

import os
import re
import json
import hashlib
import subprocess
import sys
from typing import List, Dict, Optional
from datetime import datetime

class IntelligentTVClipper:
    """智能电视剧剪辑系统"""

    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.clips_folder = "clips"
        self.cache_folder = "cache"
        self.plot_clips_folder = "plot_clips"
        self.plot_reports_folder = "plot_reports"
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, self.cache_folder, 
                      self.plot_clips_folder, self.plot_reports_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 剧情点分类定义
        self.plot_point_types = {
            '关键冲突': {
                'keywords': ['冲突', '争执', '对抗', '质疑', '反驳', '争议', '激烈', '愤怒', '不同意'],
                'weight': 10,
                'ideal_duration': 180  # 3分钟
            },
            '人物转折': {
                'keywords': ['决定', '改变', '选择', '转变', '觉悟', '明白', '意识到', '发现自己'],
                'weight': 9,
                'ideal_duration': 150  # 2.5分钟
            },
            '线索揭露': {
                'keywords': ['发现', '揭露', '真相', '证据', '线索', '秘密', '暴露', '证明', '找到'],
                'weight': 8,
                'ideal_duration': 160  # 2.7分钟
            },
            '情感爆发': {
                'keywords': ['哭', '痛苦', '绝望', '愤怒', '激动', '崩溃', '心痛', '感动', '震撼'],
                'weight': 7,
                'ideal_duration': 140  # 2.3分钟
            },
            '重要对话': {
                'keywords': ['告诉', '承认', '坦白', '解释', '澄清', '说明', '表态', '保证'],
                'weight': 6,
                'ideal_duration': 170  # 2.8分钟
            }
        }
        
        # 主线剧情关键词
        self.main_storylines = {
            '四二八案': ['四二八案', '428案', '段洪山', '正当防卫', '申诉', '重审'],
            '628旧案': ['628案', '628旧案', '张园', '霸凌', '校园'],
            '听证会': ['听证会', '法庭', '审判', '辩论', '质证'],
            '调查线': ['调查', '证据', '线索', '发现', '真相'],
            '情感线': ['父女', '家庭', '亲情', '关系', '支持']
        }
        
        print("🚀 智能电视剧剪辑系统已启动")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.videos_folder}/")
        print(f"📤 输出目录: {self.clips_folder}/")
        print(f"🎭 剧情点目录: {self.plot_clips_folder}/")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        print(f"🤖 AI已配置: {config.get('provider', 'unknown')}")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")
        
        print("📝 AI未配置，将使用基础分析")
        return {'enabled': False}

    def configure_ai(self):
        """配置AI接口"""
        print("\n🤖 AI配置向导")
        print("=" * 40)
        
        print("选择AI服务类型:")
        print("1. 官方API (Gemini)")
        print("2. 中转API (ChatAI, OpenRouter等)")
        print("0. 跳过配置")
        
        choice = input("请选择 (0-2): ").strip()
        
        if choice == '1':
            self.configure_official_api()
        elif choice == '2':
            self.configure_proxy_api()
        else:
            print("⚠️ 跳过AI配置")

    def configure_official_api(self):
        """配置官方API"""
        print("\n🔒 官方API配置")
        print("目前支持: Google Gemini")
        
        api_key = input("请输入Gemini API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return
        
        model = input("模型名称 (默认: gemini-2.5-flash): ").strip() or 'gemini-2.5-flash'
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }
        
        # 测试连接
        if self.test_gemini_connection(config):
            self.save_ai_config(config)
            self.ai_config = config
            print("✅ Gemini配置成功")
        else:
            print("❌ 连接测试失败")

    def configure_proxy_api(self):
        """配置中转API"""
        print("\n🌐 中转API配置")
        
        base_url = input("API地址 (如: https://www.chataiapi.com/v1): ").strip()
        api_key = input("API密钥: ").strip()
        model = input("模型名称 (如: deepseek-r1): ").strip()
        
        if not all([base_url, api_key, model]):
            print("❌ 所有字段都必须填写")
            return
        
        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'proxy',
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }
        
        # 测试连接
        if self.test_proxy_connection(config):
            self.save_ai_config(config)
            self.ai_config = config
            print("✅ 中转API配置成功")
        else:
            print("❌ 连接测试失败")

    def test_gemini_connection(self, config: Dict) -> bool:
        """测试Gemini连接"""
        try:
            from google import genai
            
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents="测试连接"
            )
            return bool(response.text)
        except ImportError:
            print("❌ 需要安装: pip install google-genai")
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def test_proxy_connection(self, config: Dict) -> bool:
        """测试中转API连接"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试连接'}],
                max_tokens=10
            )
            
            return bool(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def save_ai_config(self, config: Dict):
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ 配置已保存")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用"""
        if not self.ai_config.get('enabled'):
            return None
        
        try:
            if self.ai_config.get('api_type') == 'official':
                return self.call_official_api(prompt, system_prompt)
            else:
                return self.call_proxy_api(prompt, system_prompt)
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None

    def call_official_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用官方API"""
        try:
            from google import genai
            
            client = genai.Client(api_key=self.ai_config['api_key'])
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = client.models.generate_content(
                model=self.ai_config['model'],
                contents=full_prompt
            )
            
            return response.text
        except Exception as e:
            print(f"❌ Gemini API调用失败: {e}")
            return None

    def call_proxy_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用中转API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.ai_config['api_key'],
                base_url=self.ai_config['base_url']
            )
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            response = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ 中转API调用失败: {e}")
            return None

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")
        
        # 尝试多种编码
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

    def get_cache_key(self, filename: str) -> str:
        """生成缓存键"""
        return hashlib.md5(filename.encode()).hexdigest()[:12]

    def load_analysis_cache(self, filename: str) -> Optional[Dict]:
        """加载分析缓存"""
        cache_key = self.get_cache_key(filename)
        cache_file = os.path.join(self.cache_folder, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save_analysis_cache(self, filename: str, analysis: Dict):
        """保存分析缓存"""
        cache_key = self.get_cache_key(filename)
        cache_file = os.path.join(self.cache_folder, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def extract_episode_number(self, filename: str) -> str:
        """从文件名提取集数"""
        # 直接使用SRT文件名作为集数标识
        return os.path.splitext(filename)[0]

    def ai_analyze_episode(self, subtitles: List[Dict], filename: str) -> Optional[Dict]:
        """AI分析整集"""
        if not self.ai_config.get('enabled'):
            print(f"⚠️ AI未启用，跳过分析: {filename}")
            return None
        
        # 检查缓存
        cached_analysis = self.load_analysis_cache(filename)
        if cached_analysis:
            print(f"💾 使用缓存分析: {filename}")
            return cached_analysis
        
        # 构建完整上下文
        episode_num = self.extract_episode_number(filename)
        full_context = self.build_context(subtitles)
        
        prompt = f"""你是专业的电视剧剪辑师，分析第{episode_num}集内容，找出3-5个最精彩的2-3分钟片段。

【字幕内容】
{full_context}

请严格按JSON格式输出：
{{
    "episode_info": {{
        "episode_number": "{episode_num}",
        "genre": "剧情类型",
        "theme": "核心主题"
    }},
    "segments": [
        {{
            "id": 1,
            "title": "片段标题",
            "start_time": "00:XX:XX,XXX",
            "end_time": "00:XX:XX,XXX",
            "duration": 120,
            "description": "内容描述",
            "narration": "专业解说词",
            "highlight": "观看提示"
        }}
    ]
}}

要求：
- 时间必须从字幕中选择真实存在的时间点
- 每个片段2-3分钟
- 解说词要生动有趣"""

        system_prompt = "你是专业的影视剪辑师，擅长识别精彩片段。请严格按JSON格式输出。"
        
        try:
            response = self.call_ai_api(prompt, system_prompt)
            if response:
                analysis = self.parse_ai_response(response)
                if analysis:
                    # 保存缓存
                    self.save_analysis_cache(filename, analysis)
                    print(f"✅ AI分析成功: {len(analysis.get('segments', []))} 个片段")
                    return analysis
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")
        
        return None

    def analyze_plot_points(self, subtitles: List[Dict], episode_num: str) -> List[Dict]:
        """分析剧情点并返回多个重要片段"""
        if not subtitles:
            return []
        
        plot_points = []
        window_size = 20  # 分析窗口大小
        
        # 滑动窗口分析
        for i in range(0, len(subtitles) - window_size, 10):
            window_subtitles = subtitles[i:i + window_size]
            combined_text = ' '.join([sub['text'] for sub in window_subtitles])
            
            # 计算各类剧情点得分
            plot_scores = {}
            for plot_type, config in self.plot_point_types.items():
                score = 0
                for keyword in config['keywords']:
                    score += combined_text.count(keyword) * config['weight']
                
                # 主线剧情加权
                for storyline, storyline_keywords in self.main_storylines.items():
                    for keyword in storyline_keywords:
                        if keyword in combined_text:
                            score += 5
                
                plot_scores[plot_type] = score
            
            # 找到最高分的剧情点类型
            best_plot_type = max(plot_scores, key=plot_scores.get)
            best_score = plot_scores[best_plot_type]
            
            if best_score >= 15:  # 阈值筛选
                plot_points.append({
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'plot_type': best_plot_type,
                    'score': best_score,
                    'subtitles': window_subtitles,
                    'content': combined_text,
                    'position_ratio': i / len(subtitles)
                })
        
        # 去重和优化
        plot_points = self._deduplicate_plot_points(plot_points)
        
        # 选择top剧情点（每集2-4个）
        plot_points.sort(key=lambda x: x['score'], reverse=True)
        selected_points = plot_points[:4]
        
        # 按时间顺序排序
        selected_points.sort(key=lambda x: x['start_index'])
        
        # 优化剧情点片段
        optimized_points = []
        for point in selected_points:
            optimized_point = self._optimize_plot_point(subtitles, point, episode_num)
            if optimized_point:
                optimized_points.append(optimized_point)
        
        return optimized_points

    def _deduplicate_plot_points(self, plot_points: List[Dict]) -> List[Dict]:
        """去除重叠的剧情点"""
        if not plot_points:
            return []
        
        plot_points.sort(key=lambda x: x['start_index'])
        deduplicated = [plot_points[0]]
        
        for point in plot_points[1:]:
            last_point = deduplicated[-1]
            overlap = (point['start_index'] <= last_point['end_index'])
            
            if overlap:
                if point['score'] > last_point['score']:
                    deduplicated[-1] = point
            else:
                gap = point['start_index'] - last_point['end_index']
                if gap >= 30:
                    deduplicated.append(point)
                elif point['score'] > last_point['score'] * 1.5:
                    deduplicated[-1] = point
        
        return deduplicated

    def _optimize_plot_point(self, all_subtitles: List[Dict], plot_point: Dict, episode_num: str) -> Optional[Dict]:
        """优化单个剧情点片段"""
        plot_type = plot_point['plot_type']
        target_duration = self.plot_point_types[plot_type]['ideal_duration']
        
        start_idx = plot_point['start_index']
        end_idx = plot_point['end_index']
        
        # 扩展到目标时长
        current_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
        
        while current_duration < target_duration and (start_idx > 0 or end_idx < len(all_subtitles) - 1):
            if end_idx < len(all_subtitles) - 1:
                end_idx += 1
                current_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
            
            if current_duration < target_duration and start_idx > 0:
                start_idx -= 1
                current_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
            
            if current_duration >= target_duration * 1.2:
                break
        
        # 寻找自然边界
        start_idx = self._find_natural_start(all_subtitles, start_idx, plot_point['start_index'])
        end_idx = self._find_natural_end(all_subtitles, plot_point['end_index'], end_idx)
        
        # 生成片段信息
        final_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
        start_time = all_subtitles[start_idx]['start']
        end_time = all_subtitles[end_idx]['end']
        
        # 生成详细的内容解说
        content_explanation = self._generate_content_explanation(all_subtitles, start_idx, end_idx, plot_type)
        
        return {
            'episode_number': episode_num,
            'plot_type': plot_type,
            'title': self._generate_plot_title(all_subtitles, start_idx, end_idx, plot_type, episode_num),
            'start_time': start_time,
            'end_time': end_time,
            'duration': final_duration,
            'start_index': start_idx,
            'end_index': end_idx,
            'score': plot_point['score'],
            'key_dialogues': self._extract_key_dialogues(all_subtitles, start_idx, end_idx),
            'plot_analysis': self._analyze_plot_significance(all_subtitles, start_idx, end_idx, plot_type),
            'content_summary': self._generate_content_summary(all_subtitles, start_idx, end_idx, plot_type),
            'content_explanation': content_explanation,
            'narration': self._generate_professional_narration(all_subtitles, start_idx, end_idx, plot_type)
        }

    def _calculate_subtitle_duration(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> float:
        """计算字幕片段的时长"""
        if start_idx >= len(subtitles) or end_idx >= len(subtitles):
            return 0
        
        start_seconds = self.time_to_seconds(subtitles[start_idx]['start'])
        end_seconds = self.time_to_seconds(subtitles[end_idx]['end'])
        return end_seconds - start_seconds

    def _find_natural_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找自然开始点"""
        scene_starters = ['那么', '现在', '这时', '突然', '接下来', '首先', '然后', '于是', '随着']
        
        for i in range(anchor, max(0, search_start - 5), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(starter in text for starter in scene_starters):
                    return i
                if text.endswith('。') and len(text) < 20:
                    return min(i + 1, anchor)
        
        return search_start

    def _find_natural_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找自然结束点"""
        scene_enders = ['好的', '明白', '知道了', '算了', '结束', '完了', '离开', '再见', '走吧']
        
        for i in range(anchor, min(len(subtitles), search_end + 5)):
            text = subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                return i
            if text.endswith('。') and i > anchor + 15:
                return i
        
        return min(search_end, len(subtitles) - 1)

    def _generate_plot_title(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str, episode_num: str) -> str:
        """生成剧情点标题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])
        
        if plot_type == '关键冲突':
            if '四二八案' in content:
                return f"E{episode_num}：四二八案激烈争议，正当防卫认定冲突"
            elif '听证会' in content:
                return f"E{episode_num}：听证会激烈交锋，法庭争议白热化"
            else:
                return f"E{episode_num}：关键冲突爆发，{plot_type}核心时刻"
        
        elif plot_type == '人物转折':
            if '段洪山' in content:
                return f"E{episode_num}：段洪山态度转变，关键决定时刻"
            else:
                return f"E{episode_num}：{plot_type}重要时刻，角色命运转折"
        
        elif plot_type == '线索揭露':
            if '628案' in content or '张园' in content:
                return f"E{episode_num}：628旧案线索揭露，真相逐步浮现"
            else:
                return f"E{episode_num}：{plot_type}重大发现，案件迎来转机"
        
        elif plot_type == '情感爆发':
            return f"E{episode_num}：{plot_type}高潮时刻，情感震撼人心"
        
        else:
            return f"E{episode_num}：{plot_type}精彩片段，剧情核心时刻"

    def _extract_key_dialogues(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键台词"""
        key_dialogues = []
        priority_keywords = [
            '四二八案', '628案', '段洪山', '张园', '霸凌', '正当防卫',
            '听证会', '申诉', '证据', '真相', '发现', '调查', '重审',
            '决定', '改变', '冲突', '争议', '揭露', '秘密'
        ]
        
        for i in range(start_idx, min(end_idx + 1, start_idx + 25)):
            if i >= len(subtitles):
                break
                
            subtitle = subtitles[i]
            text = subtitle['text']
            importance = 0
            
            for keyword in priority_keywords:
                if keyword in text:
                    importance += 3
            
            importance += text.count('！') * 2
            importance += text.count('？') * 1.5
            
            dramatic_words = ['不可能', '震惊', '真相', '证明', '推翻', '发现', '意外']
            for word in dramatic_words:
                if word in text:
                    importance += 2
            
            if importance >= 4 and len(text) > 8:
                time_code = f"{subtitle['start']} --> {subtitle['end']}"
                key_dialogues.append(f"[{time_code}] {text}")
        
        return key_dialogues[:6]

    def _analyze_plot_significance(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """分析剧情点意义"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        significance_parts = []
        
        if plot_type == '关键冲突':
            if '四二八案' in content and '正当防卫' in content:
                significance_parts.append("四二八案正当防卫认定争议核心冲突")
            if '听证会' in content:
                significance_parts.append("听证会法庭激辩关键交锋时刻")
            if '证据' in content and '质疑' in content:
                significance_parts.append("证据效力争议，法理情理激烈碰撞")
        
        elif plot_type == '人物转折':
            if '决定' in content or '选择' in content:
                significance_parts.append("角色关键决定时刻，命运走向转折点")
            if '段洪山' in content:
                significance_parts.append("段洪山态度转变，父女关系重要节点")
        
        elif plot_type == '线索揭露':
            if '628案' in content or '张园' in content:
                significance_parts.append("628旧案关键线索首次披露")
            if '证据' in content and '发现' in content:
                significance_parts.append("重要证据发现，案件真相逐步浮现")
        
        if '真相' in content:
            significance_parts.append("案件真相重要披露")
        if '证据' in content:
            significance_parts.append("关键证据链条完善")
        
        return "；".join(significance_parts) if significance_parts else f"{plot_type}重要剧情发展节点"

    def _generate_content_summary(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成内容摘要"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 20))])
        
        key_elements = []
        if '四二八案' in content:
            key_elements.append("四二八案")
        if '628案' in content or '张园' in content:
            key_elements.append("628旧案")
        if '听证会' in content:
            key_elements.append("听证会")
        if '段洪山' in content:
            key_elements.append("段洪山")
        if '正当防卫' in content:
            key_elements.append("正当防卫")
        if '证据' in content:
            key_elements.append("关键证据")
        
        elements_str = "、".join(key_elements) if key_elements else "核心剧情"
        return f"{plot_type}：{elements_str}的重要发展，{content[:50]}..."

    def _generate_content_explanation(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成详细的内容解说"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        
        # 基于剧情点类型生成专业解说
        if plot_type == '关键冲突':
            if '四二八案' in content and '正当防卫' in content:
                return """这个片段展现了四二八案正当防卫认定的核心争议。通过法庭激辩，我们看到不同立场对同一事件的截然不同解读。检察官与辩护律师针对证据效力、行为性质等关键问题展开激烈交锋，体现了法律条文在具体案件中的复杂适用。观众可以深入理解正当防卫的法律边界及其在实践中的争议性。"""
            elif '听证会' in content:
                return """听证会现场的激烈争论展现了司法程序的严谨性和复杂性。各方当事人围绕案件关键事实进行质证和辩论，体现了程序正义的重要性。通过这个片段，观众可以了解听证会的运作机制，感受法律条文与现实案件的碰撞。"""
            else:
                return f"""本片段聚焦{plot_type}的关键时刻，展现了人物间的深层矛盾和立场冲突。通过激烈的对话和情感表达，观众可以深入理解角色的内心世界和动机，感受剧情的紧张感和戏剧张力。"""
        
        elif plot_type == '人物转折':
            if '段洪山' in content:
                return """段洪山的态度转变是本集的重要看点。从最初的抗拒到逐渐理解，再到最终的决定，展现了一个父亲在面对法律与亲情双重压力下的心路历程。这个转折不仅推动了剧情发展，也深刻反映了人性的复杂和现实的残酷。"""
            else:
                return f"""本片段记录了角色的重要{plot_type}时刻。通过内心独白、关键对话或者行为改变，我们看到角色面临重大选择时的挣扎和成长。这种转折往往是剧情的转折点，对后续发展产生深远影响。"""
        
        elif plot_type == '线索揭露':
            if '628案' in content or '张园' in content:
                return """628旧案线索的揭露为整个故事增添了新的维度。通过对过往事件的回顾和新证据的发现，观众逐步了解事件的来龙去脉。校园霸凌的真相不仅关联着当前案件，也揭示了社会问题的深层根源。"""
            else:
                return f"""关键{plot_type}的时刻往往是推动剧情发展的重要节点。通过新信息的披露，案件迎来转机，观众的认知也随之更新。这类片段通常具有很强的悬念效果和观看价值。"""
        
        elif plot_type == '情感爆发':
            return """情感爆发的瞬间往往是最打动人心的时刻。无论是愤怒、悲伤还是感动，这些真挚的情感表达都能引起观众的强烈共鸣。通过演员的精湛表演，我们能够感受到角色内心的痛苦和挣扎，体会到人性的复杂和深刻。"""
        
        else:
            return f"""本{plot_type}片段展现了剧情的核心内容，通过精彩的对话和情节发展，为观众呈现了一个完整而引人入胜的故事片段。这些内容不仅推动了主线剧情，也为角色发展和主题表达提供了重要支撑。"""

    def _generate_professional_narration(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成专业旁白解说"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])
        
        if plot_type == '关键冲突':
            if '四二八案' in content:
                return "接下来的片段将展现四二八案的关键争议时刻。我们将看到法庭上的激烈辩论，各方对正当防卫认定的不同观点。这场法理与情理的较量，值得我们深入思考。"
            elif '听证会' in content:
                return "听证会现场即将迎来最激烈的时刻。控辩双方围绕关键证据展开激辩，每一个细节都可能影响最终结果。让我们一起见证这场法律智慧的碰撞。"
            else:
                return f"即将上演的{plot_type}片段充满戏剧张力。人物间的深层矛盾即将爆发，让我们看看这场冲突将如何影响剧情走向。"
        
        elif plot_type == '人物转折':
            if '段洪山' in content:
                return "段洪山即将做出一个重要决定。作为父亲，他在法律与亲情之间艰难抉择。这个转折将如何影响整个案件的走向？让我们拭目以待。"
            else:
                return f"关键的{plot_type}时刻即将到来。角色面临重大选择，这个决定将改变他们的命运轨迹。每一个细节都值得我们仔细观察。"
        
        elif plot_type == '线索揭露':
            if '628案' in content:
                return "628旧案的神秘面纱即将被揭开。新的线索将如何改变我们对整个事件的认知？这个发现对当前案件又意味着什么？精彩内容即将揭晓。"
            else:
                return f"重要的{plot_type}时刻到了。隐藏的真相即将浮出水面，这个发现将为案件带来怎样的转机？让我们一起探寻答案。"
        
        elif plot_type == '情感爆发':
            return "接下来的片段将展现最打动人心的时刻。真挚的情感表达往往比任何言语都更有力量。让我们一起感受这份情感的震撼力。"
        
        else:
            return f"精彩的{plot_type}片段即将开始。这些内容不仅推动剧情发展，也为我们提供了深入思考的空间。让我们一起享受这个精彩时刻。"

    def build_context(self, subtitles: List[Dict]) -> str:
        """构建上下文"""
        context_parts = []
        for i in range(0, len(subtitles), 30):
            segment = subtitles[i:i+30]
            segment_text = '\n'.join([f"[{sub['start']}] {sub['text']}" for sub in segment])
            context_parts.append(segment_text)
        
        return '\n\n=== 场景分割 ===\n\n'.join(context_parts)

    def parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_text = response[start:end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]
            
            result = json.loads(json_text)
            
            if 'segments' in result and 'episode_info' in result:
                return result
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
        
        return None

    def find_video_file(self, srt_filename: str) -> Optional[str]:
        """查找对应的视频文件"""
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if base_name.lower() in filename.lower():
                    return os.path.join(self.videos_folder, filename)
        
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
        """检查FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def create_video_clips(self, analysis: Dict, video_file: str, srt_filename: str) -> List[str]:
        """创建视频片段"""
        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []
        
        created_clips = []
        
        for segment in analysis.get('segments', []):
            segment_id = segment.get('id', 1)
            title = segment.get('title', '精彩片段')
            episode_name = self.extract_episode_number(srt_filename)
            
            # 生成更安全的文件名，避免特殊字符
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', title)
            safe_title = safe_title.replace('__', '_').strip('_')
            
            # 限制文件名长度
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            clip_filename = f"{episode_name}_{safe_title}_seg{segment_id}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)
            
            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                
                # 创建缺失的旁白文件
                self.create_narration_files(clip_path, segment)
                continue
            
            # 剪辑视频
            if self.create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)
                self.create_narration_files(clip_path, segment)
        
        return created_clips

    def create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")
            
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
            
            # 修复Windows编码问题
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 使用适当的编码参数
            if sys.platform.startswith('win'):
                # Windows特殊处理
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300,
                    encoding='utf-8',
                    errors='ignore',
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                # Unix/Linux系统
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300,
                    encoding='utf-8',
                    errors='ignore',
                    env=env
                )
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"   ✅ 成功: {file_size:.1f}MB")
                return True
            else:
                error_msg = result.stderr[:100] if result.stderr else '未知错误'
                print(f"   ❌ 失败: {error_msg}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"   ❌ 剪辑超时")
            return False
        except UnicodeDecodeError as e:
            print(f"   ❌ 编码错误: {e}")
            return False
        except Exception as e:
            print(f"   ❌ 剪辑异常: {e}")
            return False

    def create_narration_files(self, video_path: str, segment: Dict):
        """创建旁白文件"""
        try:
            # 旁白文本文件
            narration_path = video_path.replace('.mp4', '_旁白.txt')
            if not os.path.exists(narration_path):
                content = f"""🎙️ {segment['title']} - 专业旁白解说
{"=" * 50}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration', 0)} 秒
• 描述: {segment.get('description', '精彩剧情片段')}

🎙️ 专业解说:
{segment.get('narration', '暂无解说')}

💡 观看提示:
{segment.get('highlight', '精彩内容值得关注')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                with open(narration_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   📝 旁白文件: {os.path.basename(narration_path)}")
            
            # SRT字幕文件
            srt_path = video_path.replace('.mp4', '_字幕.srt')
            if not os.path.exists(srt_path):
                duration = segment.get('duration', 120)
                title = segment.get('title', '精彩片段')
                highlight = segment.get('highlight', '精彩内容正在播放')
                
                srt_content = f"""1
00:00:00,000 --> 00:00:05,000
{title}

2
00:00:05,000 --> 00:{duration//60:02d}:{duration%60:02d},000
{highlight}
"""
                
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                print(f"   🎬 字幕文件: {os.path.basename(srt_path)}")
        
        except Exception as e:
            print(f"   ⚠️ 旁白文件生成失败: {e}")

    def process_episode(self, srt_filename: str) -> bool:
        """处理单集"""
        print(f"\n📺 处理集数: {srt_filename}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_filename)
        subtitles = self.parse_srt_file(srt_path)
        
        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False
        
        episode_num = self.extract_episode_number(srt_filename)
        
        # 2. AI分析常规片段
        created_clips = []
        
        if self.ai_config.get('enabled'):
            analysis = self.ai_analyze_episode(subtitles, srt_filename)
            if analysis:
                video_file = self.find_video_file(srt_filename)
                if video_file:
                    print(f"📁 视频文件: {os.path.basename(video_file)}")
                    ai_clips = self.create_video_clips(analysis, video_file, srt_filename)
                    created_clips.extend(ai_clips)
        
        # 3. 剧情点聚焦分析
        print(f"🎭 开始剧情点聚焦分析...")
        plot_points = self.analyze_plot_points(subtitles, episode_num)
        
        if plot_points:
            print(f"🎯 识别到 {len(plot_points)} 个剧情点:")
            for i, point in enumerate(plot_points, 1):
                print(f"    {i}. {point['plot_type']} (评分: {point['score']:.1f}, 时长: {point['duration']:.1f}秒)")
            
            # 查找视频文件
            video_file = self.find_video_file(srt_filename)
            if video_file:
                # 创建剧情点合集
                if self.create_plot_point_clips(plot_points, video_file, episode_num):
                    created_clips.extend(['plot_clips'])
        else:
            print(f"❌ 未找到合适的剧情点")
        
        print(f"✅ {srt_filename} 处理完成: {len(created_clips)} 个片段")
        return len(created_clips) > 0

    def create_plot_point_clips(self, plot_points: List[Dict], video_file: str, episode_num: str) -> bool:
        """创建剧情点片段"""
        if not plot_points:
            return False
        
        success_count = 0
        
        for i, plot_point in enumerate(plot_points, 1):
            # 生成安全文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', plot_point['plot_type'])
            clip_filename = f"E{episode_num}_{safe_title}_{i}.mp4"
            clip_path = os.path.join(self.plot_clips_folder, clip_filename)
            
            print(f"\n🎬 创建剧情点{i}: {plot_point['plot_type']}")
            print(f"   标题: {plot_point['title']}")
            print(f"   时间: {plot_point['start_time']} --> {plot_point['end_time']}")
            
            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:
                print(f"✅ 片段已存在，创建解说文件")
                self.create_plot_explanation_files(clip_path, plot_point, episode_num)
                success_count += 1
                continue
            
            # 创建单个片段
            if self.create_single_plot_clip(video_file, plot_point, clip_path):
                self.create_plot_explanation_files(clip_path, plot_point, episode_num)
                success_count += 1
        
        # 生成总体报告
        if success_count > 0:
            self.create_plot_analysis_report(plot_points, episode_num)
        
        return success_count > 0

    def create_single_plot_clip(self, video_file: str, plot_point: Dict, output_path: str) -> bool:
        """创建单个剧情点片段"""
        try:
            start_seconds = self.time_to_seconds(plot_point['start_time'])
            end_seconds = self.time_to_seconds(plot_point['end_time'])
            duration = end_seconds - start_seconds
            
            if duration <= 0:
                print(f"   ❌ 无效时间段")
                return False
            
            # 添加少量缓冲
            buffer_start = max(0, start_seconds - 0.5)
            buffer_duration = duration + 1
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                output_path,
                '-y'
            ]
            
            # Windows编码修复
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            if sys.platform.startswith('win'):
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300,
                    encoding='utf-8',
                    errors='ignore',
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
            
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

    def create_plot_explanation_files(self, video_path: str, plot_point: Dict, episode_num: str):
        """创建剧情点解说文件"""
        try:
            # 详细解说文件
            explanation_path = video_path.replace('.mp4', '_内容解说.txt')
            
            content = f"""📺 E{episode_num} - {plot_point['plot_type']} 内容解说
{"=" * 80}

🎭 剧情点信息:
• 类型: {plot_point['plot_type']}
• 标题: {plot_point['title']}
• 时间段: {plot_point['start_time']} --> {plot_point['end_time']}
• 片段时长: {plot_point['duration']:.1f} 秒
• 重要度评分: {plot_point['score']:.1f}/100

💡 剧情意义分析:
{plot_point['plot_analysis']}

📝 详细内容解说:
{plot_point['content_explanation']}

🎙️ 专业旁白解说:
{plot_point['narration']}

📄 内容摘要:
{plot_point['content_summary']}

🗣️ 关键台词节选:
"""
            
            for dialogue in plot_point['key_dialogues']:
                content += f"  {dialogue}\n"
            
            content += f"""

🎯 观看指导:
本片段展现了{plot_point['plot_type']}的关键时刻，通过精彩的对话和情节发展，
为观众呈现了完整而引人入胜的故事内容。建议观众重点关注：

1. 人物的情感变化和心理活动
2. 关键对话中的信息透露
3. 剧情发展的转折点
4. 法律与情理的冲突表现

📊 制作信息:
• 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• 视频文件: {os.path.basename(video_path)}
• 剧情点类型: {plot_point['plot_type']}
• 智能分析系统版本: v2.0
"""
            
            with open(explanation_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   📝 解说文件: {os.path.basename(explanation_path)}")
            
            # 简化版旁白文件
            narration_path = video_path.replace('.mp4', '_旁白解说.txt')
            
            narration_content = f"""🎙️ {plot_point['title']} - 旁白解说
{"=" * 60}

📺 开场介绍:
{plot_point['narration']}

💡 核心看点:
{plot_point['plot_analysis'][:100]}...

🎯 观看提示:
这个{plot_point['plot_type']}片段值得重点关注，
展现了剧情的重要发展和人物的关键时刻。

⏱️ 最佳观看时机:
适合在{plot_point['duration']:.0f}秒内专注观看，
建议配合字幕理解细节内容。
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(narration_content)
            
            print(f"   🎙️ 旁白文件: {os.path.basename(narration_path)}")
            
        except Exception as e:
            print(f"   ⚠️ 解说文件生成失败: {e}")

    def create_plot_analysis_report(self, plot_points: List[Dict], episode_num: str):
        """创建剧情点分析总报告"""
        try:
            report_path = os.path.join(self.plot_reports_folder, f"E{episode_num}_剧情点分析报告.txt")
            
            content = f"""📺 第{episode_num}集剧情点聚焦分析报告
{"=" * 80}

🎯 剧情点总数: {len(plot_points)} 个
📏 总时长: {sum(point['duration'] for point in plot_points):.1f} 秒
🎬 平均时长: {sum(point['duration'] for point in plot_points) / len(plot_points):.1f} 秒/片段

📊 剧情点类型分布:
"""
            
            # 统计剧情点类型
            type_counts = {}
            for point in plot_points:
                plot_type = point['plot_type']
                type_counts[plot_type] = type_counts.get(plot_type, 0) + 1
            
            for plot_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(plot_points) * 100
                content += f"• {plot_type}: {count} 个 ({percentage:.1f}%)\n"
            
            content += f"\n🎭 详细剧情点分析:\n"
            
            for i, plot_point in enumerate(plot_points, 1):
                content += f"""
{"-" * 60}
🎬 剧情点 {i}: {plot_point['plot_type']}
{"-" * 60}
📝 标题: {plot_point['title']}
⏱️ 时间: {plot_point['start_time']} --> {plot_point['end_time']}
📏 时长: {plot_point['duration']:.1f} 秒
📊 评分: {plot_point['score']:.1f}/100

💡 剧情意义:
{plot_point['plot_analysis']}

🎙️ 专业解说:
{plot_point['narration']}

📄 内容摘要:
{plot_point['content_summary']}

🗣️ 关键台词:
"""
                
                for dialogue in plot_point['key_dialogues'][:3]:
                    content += f"  {dialogue}\n"
            
            content += f"""

🎯 制作总结:
• 本集剧情点聚焦分析完成，共识别{len(plot_points)}个核心剧情点
• 每个剧情点都配备了详细的内容解说和专业旁白
• 片段时长控制在2-3分钟，适合短视频传播
• 涵盖了{len(type_counts)}种不同类型的剧情点
• 保持了完整的故事发展脉络和观看连贯性

📈 观看建议:
建议按顺序观看各个剧情点，配合内容解说文件理解深层含义。
每个片段都是独立完整的故事单元，也可以单独欣赏。

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📄 生成分析报告: E{episode_num}_剧情点分析报告.txt")
            
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 50)
        
        # 获取所有SRT文件，按文件名排序
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        # 按文件名排序（电视剧顺序）
        srt_files.sort()
        
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        print(f"🤖 AI状态: {'启用' if self.ai_config.get('enabled') else '未启用'}")
        
        # 处理每一集
        total_success = 0
        total_clips = 0
        
        for srt_file in srt_files:
            try:
                success = self.process_episode(srt_file)
                if success:
                    total_success += 1
                
                # 统计片段数
                clips = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
                total_clips = len(clips)
                
            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")
        
        # 最终报告
        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")

    def process_plot_focus_mode(self):
        """剧情点聚焦模式"""
        print("\n🎭 剧情点聚焦剪辑模式")
        print("=" * 60)
        print("🎯 功能特点:")
        print("• 每集按剧情点分析：关键冲突、人物转折、线索揭露等")
        print("• 每个剧情点2-3分钟，包含完整内容解说")
        print("• 智能识别剧情点类型和重要度")
        print("• 生成专业旁白和详细分析报告")
        print("=" * 60)
        
        # 获取字幕文件
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        srt_files.sort()
        
        if not srt_files:
            print("❌ 未找到字幕文件")
            return
        
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        
        print("\n🎬 开始剧情点聚焦分析...")
        total_success = 0
        total_plot_points = 0
        
        for srt_file in srt_files:
            try:
                print(f"\n📺 处理: {srt_file}")
                
                # 解析字幕
                srt_path = os.path.join(self.srt_folder, srt_file)
                subtitles = self.parse_srt_file(srt_path)
                
                if not subtitles:
                    print(f"❌ 字幕解析失败")
                    continue
                
                episode_num = self.extract_episode_number(srt_file)
                
                # 分析剧情点
                plot_points = self.analyze_plot_points(subtitles, episode_num)
                
                if not plot_points:
                    print(f"❌ 未找到合适的剧情点")
                    continue
                
                total_plot_points += len(plot_points)
                
                # 查找视频文件
                video_file = self.find_video_file(srt_file)
                if not video_file:
                    print(f"❌ 未找到视频文件")
                    continue
                
                # 创建剧情点片段
                if self.create_plot_point_clips(plot_points, video_file, episode_num):
                    total_success += 1
                
            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")
        
        # 最终报告
        print(f"\n📊 剧情点聚焦处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(srt_files)} 集")
        print(f"🎭 识别剧情点: {total_plot_points} 个")
        print(f"📁 输出目录: {self.plot_clips_folder}/")
        print(f"📄 分析报告: {self.plot_reports_folder}/")

    def show_file_status(self):
        """显示文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        video_files = [f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
        clip_files = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
        plot_files = []
        if os.path.exists(self.plot_clips_folder):
            plot_files = [f for f in os.listdir(self.plot_clips_folder) if f.endswith('.mp4')]
        
        print(f"\n📊 文件状态:")
        print(f"📝 字幕文件: {len(srt_files)} 个")
        print(f"🎬 视频文件: {len(video_files)} 个")
        print(f"📤 智能剪辑片段: {len(clip_files)} 个")
        print(f"🎭 剧情点片段: {len(plot_files)} 个")
        
        if srt_files:
            print(f"\n字幕文件列表:")
            for i, f in enumerate(srt_files[:10], 1):
                print(f"  {i}. {f}")
            if len(srt_files) > 10:
                print(f"  ... 还有 {len(srt_files)-10} 个文件")
        
        if plot_files:
            print(f"\n剧情点片段:")
            for i, f in enumerate(plot_files[:5], 1):
                print(f"  {i}. {f}")
            if len(plot_files) > 5:
                print(f"  ... 还有 {len(plot_files)-5} 个文件")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 智能电视剧剪辑系统")
            print("=" * 60)
            
            # 显示状态
            ai_status = "🤖 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"AI状态: {ai_status}")
            
            # 文件统计
            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))])
            clip_count = len([f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')])
            
            print(f"文件状态: 📝{srt_count}个字幕 🎬{video_count}个视频 📤{clip_count}个片段")
            
            print("\n🎯 功能菜单:")
            print("1. 🤖 配置AI接口")
            print("2. 🎬 开始智能剪辑")
            print("3. 🎭 剧情点聚焦剪辑")
            print("4. 📁 查看文件状态")
            print("0. ❌ 退出系统")
            
            try:
                choice = input("\n请选择操作 (0-4): ").strip()
                
                if choice == '1':
                    self.configure_ai()
                elif choice == '2':
                    if not self.ai_config.get('enabled'):
                        print("\n⚠️ 建议先配置AI接口")
                        confirm = input("是否继续？(y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    self.process_all_episodes()
                elif choice == '3':
                    self.process_plot_focus_mode()
                elif choice == '4':
                    self.show_file_status()
                elif choice == '0':
                    print("\n👋 感谢使用智能电视剧剪辑系统！")
                    break
                else:
                    print(f"❌ 无效选择")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，程序退出")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    # 修复Windows编码问题
    if sys.platform.startswith('win'):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        try:
            import locale
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass
    
    # 检查并安装依赖
    print("🔧 检查依赖...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai', 'google-genai'], 
                      check=False, capture_output=True)
    except:
        pass
    
    clipper = IntelligentTVClipper()
    clipper.show_main_menu()

if __name__ == "__main__":
    main()
