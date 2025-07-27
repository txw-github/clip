#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整智能电视剧剪辑系统 - 重构版
功能特点：
1. 清晰的AI配置系统（官方API vs 中转API）
2. 智能剧情点识别和剪辑
3. 按SRT文件名排序处理
4. 第三人称旁白生成
5. 完整句子边界保证
6. 错别字自动修正
7. 分析结果缓存
"""

import os
import re
import json
import hashlib
import subprocess
import sys
from typing import List, Dict, Optional
from datetime import datetime

class IntelligentTVClipperSystem:
    """智能电视剧剪辑系统"""

    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.clips_folder = "clips"
        self.cache_folder = "cache"
        self.reports_folder = "reports"
        self.analysis_cache_folder = "analysis_cache"
        self.clip_status_folder = "clip_status" #add

        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, 
                      self.cache_folder, self.reports_folder, self.analysis_cache_folder, self.clip_status_folder]: #add clip_status
            os.makedirs(folder, exist_ok=True)

        # 剧情点分类配置
        self.plot_point_types = {
            '关键冲突': {
                'keywords': ['冲突', '争执', '对抗', '质疑', '反驳', '争议', '激烈', '愤怒', '不同意', '矛盾', '争论', '辩论'],
                'weight': 10,
                'ideal_duration': 180
            },
            '人物转折': {
                'keywords': ['决定', '改变', '选择', '转变', '觉悟', '明白', '意识到', '发现自己', '成长', '突破', '蜕变'],
                'weight': 9,
                'ideal_duration': 150
            },
            '线索揭露': {
                'keywords': ['发现', '揭露', '真相', '证据', '线索', '秘密', '暴露', '证明', '找到', '曝光', '披露'],
                'weight': 8,
                'ideal_duration': 160
            },
            '情感爆发': {
                'keywords': ['哭', '痛苦', '绝望', '愤怒', '激动', '崩溃', '心痛', '感动', '震撼', '泪水', '悲伤'],
                'weight': 7,
                'ideal_duration': 140
            },
            '重要对话': {
                'keywords': ['告诉', '承认', '坦白', '解释', '澄清', '说明', '表态', '保证', '承诺', '宣布'],
                'weight': 6,
                'ideal_duration': 170
            }
        }

        # 错别字修正库
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '聽證會': '听证会',
            '問題': '问题', '機會': '机会', '開始': '开始', '結束': '结束',
            '証人': '证人', '証言': '证言', '実現': '实现', '対話': '对话'
        }

        # 全剧上下文缓存
        self.series_context = { #add series_context
            'previous_episodes': [],
            'main_storylines': [],
            'character_arcs': {},
            'ongoing_conflicts': []
        }
        
        # 每集分析上下文
        self.episode_contexts = {}

        # 检测到的剧情类型
        self.detected_genre = None #add detected_genre
        self.genre_confidence = 0.0 #add genre_confidence

        # 加载AI配置
        self.ai_config = self._load_ai_config()

        print("🚀 智能电视剧剪辑系统已启动")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.videos_folder}/")
        print(f"📤 输出目录: {self.clips_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/") #add cache

    def _load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        api_type = config.get('api_type', 'proxy')
                        provider = config.get('provider', 'unknown')
                        print(f"🤖 AI分析已启用: {api_type} - {provider}")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")

        print("📝 AI分析未启用，使用基础规则分析")
        return {'enabled': False}

    def _save_ai_config(self, config: Dict) -> bool:
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def configure_ai_interactive(self):
        """交互式AI配置"""
        print("\n🤖 AI配置向导")
        print("=" * 50)

        print("选择AI接口类型:")
        print("1. 🔒 官方API (Google Gemini等)")
        print("2. 🌐 中转API (ChatAI, OpenRouter等)")
        print("3. 🚫 跳过配置")

        choice = input("请选择 (1-3): ").strip()

        if choice == '1':
            self._configure_official_api()
        elif choice == '2':
            self._configure_proxy_api()
        else:
            print("✅ 使用基础规则分析模式")

    def _configure_official_api(self):
        """配置官方API"""
        print("\n🔒 官方API配置")
        print("目前支持: Google Gemini")

        provider = input("选择提供商 (gemini): ").strip().lower() or 'gemini'
        api_key = input("请输入API密钥: ").strip()

        if not api_key:
            print("❌ API密钥不能为空")
            return

        model = input("模型名称 (默认: gemini-2.5-flash): ").strip() or 'gemini-2.5-flash'

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': provider,
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_official_api(config):
            self._save_ai_config(config)
            self.ai_config = config
            print("✅ AI配置成功！")
        else:
            print("❌ 连接测试失败")

    def _configure_proxy_api(self):
        """配置中转API"""
        print("\n🌐 中转API配置")

        base_url = input("API地址 (如: https://www.chataiapi.com/v1): ").strip()
        api_key = input("API密钥: ").strip()
        model = input("模型名称 (如: deepseek-r1): ").strip()

        if not all([base_url, api_key, model]):
            print("❌ 配置信息不完整")
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
        print("🔍 测试连接...")
        if self._test_proxy_api(config):
            self._save_ai_config(config)
            self.ai_config = config
            print("✅ AI配置成功！")
        else:
            print("❌ 连接测试失败")

    def _test_official_api(self, config: Dict) -> bool:
        """测试官方API连接"""
        try:
            if config['provider'] == 'gemini':
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
            print(f"❌ 测试失败: {e}")
            return False

    def _test_proxy_api(self, config: Dict) -> bool:
        """测试中转API连接"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )

            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试连接'}],
                max_tokens=10
            )

            return bool(completion.choices[0].message.content)
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False

    def test_current_connection(self):
        """测试当前AI连接"""
        print("\n🔍 AI连接测试")
        print("=" * 40)

        if not self.ai_config.get('enabled'):
            print("❌ 未找到AI配置")
            print("💡 请先配置AI接口") #add
            input("\n按回车键返回...")
            return

        print("📋 当前配置信息:")
        print(f"   类型: {self.ai_config.get('api_type', '未知')}")
        print(f"   服务商: {self.ai_config.get('provider', '未知')}")
        print(f"   模型: {self.ai_config.get('model', '未知')}")
        if self.ai_config.get('base_url'):
            print(f"   地址: {self.ai_config['base_url']}")
        print(f"   密钥: {self.ai_config.get('api_key', '')[:10]}...")
        print() #add

        # 执行测试
        api_type = self.ai_config.get('api_type')
        if api_type == 'official':
            success = self._test_official_api(self.ai_config)
        else:
            success = self._test_proxy_api(self.ai_config)

        if success:
            print("\n✅ 连接测试成功！AI接口工作正常") #add
        else:
            print("\n❌ 连接测试失败")
            print("🔧 建议解决方案:") #add
            print("1. 检查网络连接") #add
            print("2. 验证API密钥") #add
            print("3. 确认服务商状态") #add
            print("4. 重新配置API") #add

        input("\n按回车键返回...")

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用"""
        if not self.ai_config.get('enabled'):
            return None

        try:
            api_type = self.ai_config.get('api_type')

            if api_type == 'official':
                return self._call_official_api(prompt, system_prompt)
            else:
                return self._call_proxy_api(prompt, system_prompt)

        except Exception as e:
            print(f"⚠️ AI调用失败: {e}")
            return None

    def _call_official_api(self, prompt: str, system_prompt: str) -> Optional[str]:
        """调用官方API"""
        try:
            if self.ai_config['provider'] == 'gemini':
                from google import genai

                client = genai.Client(api_key=self.ai_config['api_key'])

                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

                response = client.models.generate_content(
                    model=self.ai_config['model'],
                    contents=full_prompt
                )

                return response.text
        except Exception as e:
            print(f"⚠️ 官方API调用失败: {e}")
            return None

    def _call_proxy_api(self, prompt: str, system_prompt: str) -> Optional[str]:
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

            completion = client.chat.completions.create(
                model=self.ai_config['model'],
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )

            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ 中转API调用失败: {e}")
            return None

    def get_file_hash(self, filepath: str) -> str: #add
        """获取文件内容的MD5哈希值""" #add
        try: #add
            with open(filepath, 'rb') as f: #add
                content = f.read() #add
                return hashlib.md5(content).hexdigest()[:16] #add
        except: #add
            return hashlib.md5(filepath.encode()).hexdigest()[:16] #add

    def _extract_episode_number(self, filename: str) -> str:
        """从SRT文件名提取集数"""
        # 直接使用文件名（去掉扩展名）作为集数标识
        base_name = os.path.splitext(filename)[0]

        # 尝试提取数字作为集数
        match = re.search(r'(\d+)', base_name)
        if match:
            return match.group(1).zfill(2)

        return base_name

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试多种编码读取文件
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue

        if not content:
            print(f"❌ 无法读取文件: {filepath}")
            return []

        # 错别字修正
        for old, new in self.corrections.items():
            content = content.replace(old, new)

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

    def detect_genre(self, subtitles: List[Dict]) -> str: #add
        """智能识别剧情类型""" #add
        if len(subtitles) < 50: #add
            return '通用剧' #add

        # 分析前200条字幕 #add
        sample_text = " ".join([sub['text'] for sub in subtitles[:200]]) #add

        genre_scores = {} #add
        genre_patterns = { #add
            '法律剧': { #add
                'keywords': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护', '判决', '申诉', '听证会', '正当防卫'], #add
                'weight': 1.0 #add
            }, #add
            '爱情剧': { #add
                'keywords': ['爱情', '喜欢', '心动', '表白', '约会', '分手', '复合', '结婚', '情侣', '恋人', '爱人'], #add
                'weight': 1.0 #add
            }, #add
            '悬疑剧': { #add
                'keywords': ['真相', '秘密', '调查', '线索', '破案', '凶手', '神秘', '隐瞒', '疑点', '诡异'], #add
                'weight': 1.0 #add
            }, #add
            '家庭剧': { #add
                'keywords': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情', '家人', '团聚', '血缘'], #add
                'weight': 1.0 #add
            } #add
        } #add
        for genre, pattern in genre_patterns.items(): #add
            score = 0 #add
            for keyword in pattern['keywords']: #add
                score += sample_text.count(keyword) * pattern['weight'] #add
            genre_scores[genre] = score #add

        if genre_scores: #add
            best_genre = max(genre_scores, key=genre_scores.get) #add
            max_score = genre_scores[best_genre] #add

            if max_score >= 3: #add
                self.detected_genre = best_genre #add
                self.genre_confidence = min(max_score / 20, 1.0) #add
                print(f"🎭 检测到剧情类型: {best_genre} (置信度: {self.genre_confidence:.2f})") #add
                return best_genre #add

        self.detected_genre = '通用剧' #add
        self.genre_confidence = 0.5 #add
        return '通用剧' #add

    def analyze_with_ai(self, subtitles: List[Dict], episode_num: str, episode_context: str = "") -> Optional[Dict]:
        """使用AI分析剧情点 - 使用完整字幕"""
        if not self.ai_config.get('enabled'):
            return None

        # 使用全部字幕文本，不截断
        subtitle_text = "\n".join([f"[{sub['start']}] {sub['text']}" for sub in subtitles])
        
        # 动态生成上下文信息
        context_info = f"\n【前情提要】{episode_context}" if episode_context else ""
        
        # 计算总时长用于参考
        total_duration = self._time_to_seconds(subtitles[-1]['end']) if subtitles else 0
        
        prompt = f"""你是资深电视剧剪辑师，现在要为第{episode_num}集制作精彩短视频片段。

【完整剧集信息】
- 集数：第{episode_num}集
- 总时长：{total_duration//60:.0f}分钟{episode_context}

【完整字幕内容】
{subtitle_text}

【专业分析要求】
请深度分析这一集的完整内容，识别出3-4个最具观赏价值的片段：

1. 每个片段必须是完整的戏剧单元（120-200秒）
2. 时间点必须精确到秒，确保在字幕范围内
3. 片段类型要多样化，避免重复
4. 考虑剧情连贯性和情感递进
5. 每集分析结果应该独特，体现该集特色

【输出要求】
严格按照以下JSON格式输出，时间格式必须是 HH:MM:SS,mmm：

{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre": "具体剧情类型（如法律剧/悬疑剧等）",
        "main_theme": "第{episode_num}集的核心主题",
        "unique_features": ["该集独有特点1", "该集独有特点2"],
        "emotional_arc": "情感发展脉络"
    }},
    "plot_points": [
        {{
            "plot_type": "剧情点类型（关键冲突/人物转折/线索揭露/情感爆发/重要对话）",
            "title": "具体片段标题（体现该集特色）",
            "start_time": "HH:MM:SS,mmm",
            "end_time": "HH:MM:SS,mmm", 
            "duration": 具体秒数,
            "plot_significance": "在整个剧集中的意义",
            "content_summary": "片段详细内容概述",
            "key_dialogues": ["核心对话1", "核心对话2"],
            "third_person_narration": "适合短视频的第三人称解说",
            "content_highlights": ["观众关注点1", "观众关注点2"],
            "emotional_peak": "情感高潮描述",
            "visual_elements": "画面重点元素"
        }}
    ]
}}

【特别注意】
- 时间必须在字幕范围内，检查首末字幕时间
- 每个片段要有明确的开始和结束标志
- 确保片段具有独立的戏剧价值
- 第{episode_num}集要有该集独特的分析角度"""

        system_prompt = f"""你是专业的影视剪辑师，具有丰富的电视剧分析经验。你的任务是：
1. 深度理解剧情发展脉络
2. 准确识别戏剧高潮点
3. 确保时间段的准确性
4. 为每集提供独特的分析视角
5. 生成适合短视频传播的内容

请确保每次分析都体现该集的独特性，避免千篇一律的结果。"""

        response = self.call_ai_api(prompt, system_prompt)
        if response:
            try:
                # 提取JSON
                if "```json" in response:
                    start = response.find("```json") + 7
                    end = response.find("```", start)
                    json_text = response[start:end]
                elif "```" in response:
                    start = response.find("```") + 3
                    end = response.rfind("```")
                    json_text = response[start:end]
                else:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_text = response[start:end]

                result = json.loads(json_text)
                
                # 验证时间范围的有效性
                if self._validate_time_ranges(result.get('plot_points', []), subtitles):
                    print(f"🤖 AI分析成功: {len(result.get('plot_points', []))} 个片段")
                    return result
                else:
                    print(f"⚠️ AI返回的时间范围无效，使用基础规则分析")
                    return None

            except json.JSONDecodeError as e:
                print(f"⚠️ AI响应JSON解析失败: {e}")
                print(f"原始响应前200字符: {response[:200]}")
            except Exception as e:
                print(f"⚠️ AI响应处理失败: {e}")

        return None

    def analyze_plot_points_basic(self, subtitles: List[Dict], episode_num: str) -> List[Dict]:
        """基础规则分析剧情点"""
        if not subtitles:
            return []

        plot_points = []
        window_size = 20  # 分析窗口大小

        # 检测剧情类型 #add
        if self.detected_genre is None: #add
            self.detect_genre(subtitles) #add

        # 滑动窗口分析
        for i in range(0, len(subtitles) - window_size, 10):
            window_subtitles = subtitles[i:i + window_size]
            combined_text = ' '.join([sub['text'] for sub in window_subtitles])

            # 计算各类剧情点得分
            plot_scores = {}
            for plot_type, config in self.plot_point_types.items():
                score = 0

                # 关键词匹配
                for keyword in config['keywords']:
                    score += combined_text.count(keyword) * config['weight']

                # 标点符号强度
                score += combined_text.count('！') * 2
                score += combined_text.count('？') * 1.5
                score += combined_text.count('...') * 1

                plot_scores[plot_type] = score

            # 找到最高分的剧情点类型
            best_plot_type = max(plot_scores, key=plot_scores.get)
            best_score = plot_scores[best_plot_type]

            if best_score >= 12:  # 阈值
                plot_points.append({
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'plot_type': best_plot_type,
                    'score': best_score,
                    'content': combined_text
                })

        # 去重和选择最佳剧情点
        plot_points = self._deduplicate_plot_points(plot_points)
        plot_points.sort(key=lambda x: x['score'], reverse=True)
        selected_points = plot_points[:4]  # 每集最多4个片段
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
                if gap >= 30:  # 至少间隔30个字幕条
                    deduplicated.append(point)

        return deduplicated

    def _optimize_plot_point(self, subtitles: List[Dict], plot_point: Dict, episode_num: str) -> Optional[Dict]:
        """优化剧情点片段，确保完整句子"""
        plot_type = plot_point['plot_type']
        target_duration = self.plot_point_types[plot_type]['ideal_duration']

        start_idx = plot_point['start_index']
        end_idx = plot_point['end_index']

        # 扩展到目标时长
        current_duration = self._calculate_duration(subtitles, start_idx, end_idx)

        while current_duration < target_duration and (start_idx > 0 or end_idx < len(subtitles) - 1):
            if end_idx < len(subtitles) - 1:
                end_idx += 1
                current_duration = self._calculate_duration(subtitles, start_idx, end_idx)

            if current_duration < target_duration and start_idx > 0:
                start_idx -= 1
                current_duration = self._calculate_duration(subtitles, start_idx, end_idx)

            if current_duration >= target_duration * 1.2:
                break

        # 寻找完整句子边界
        start_idx = self._find_sentence_start(subtitles, start_idx)
        end_idx = self._find_sentence_end(subtitles, end_idx)

        # 生成片段信息
        final_duration = self._calculate_duration(subtitles, start_idx, end_idx)
        start_time = subtitles[start_idx]['start']
        end_time = subtitles[end_idx]['end']

        return {
            'episode_number': episode_num,
            'plot_type': plot_type,
            'title': f"E{episode_num}-{plot_type}：剧情核心时刻",
            'start_time': start_time,
            'end_time': end_time,
            'duration': final_duration,
            'start_index': start_idx,
            'end_index': end_idx,
            'score': plot_point['score'],
            'plot_significance': f"{plot_type}重要剧情发展节点",
            'content_summary': self._generate_content_summary(subtitles, start_idx, end_idx),
            'third_person_narration': self._generate_third_person_narration(subtitles, start_idx, end_idx, plot_type),
            'content_highlights': ["精彩剧情发展", "角色深度刻画"],
            'corrected_errors': self._get_corrected_errors_in_segment(subtitles, start_idx, end_idx) #add
        }

    def _find_sentence_start(self, subtitles: List[Dict], start_idx: int) -> int:
        """寻找完整句子的开始点"""
        sentence_starters = ['那么', '现在', '这时', '突然', '接下来', '首先', '然后', '于是', '随着', '刚才', '但是', '不过', '因为', '所以'] #add

        for i in range(start_idx, max(0, start_idx - 10), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(starter in text[:10] for starter in sentence_starters):
                    return i
                if i > 0 and any(subtitles[i-1]['text'].endswith(end) for end in ['。', '！', '？', '...', '——']): #add ... ——
                    return i
                if text.startswith('"') or text.startswith('"'): #add
                    return i #add

        return start_idx

    def _find_sentence_end(self, subtitles: List[Dict], end_idx: int) -> int:
        """寻找完整句子的结束点"""
        sentence_enders = ['。', '！', '？', '...', '——', '"', '"'] #add "

        for i in range(end_idx, min(len(subtitles), end_idx + 10)):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(text.endswith(ender) for ender in sentence_enders):
                    return i

        return end_idx

    def _calculate_duration(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> float:
        """计算字幕片段的时长"""
        if start_idx >= len(subtitles) or end_idx >= len(subtitles):
            return 0

        start_seconds = self._time_to_seconds(subtitles[start_idx]['start'])
        end_seconds = self._time_to_seconds(subtitles[end_idx]['end'])
        return end_seconds - start_seconds

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def _generate_content_summary(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """生成内容摘要"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 20))])
        return f"核心剧情发展，{content[:50]}..."

    def _generate_third_person_narration(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成第三人称旁白"""
        if plot_type == '关键冲突':
            return "此时双方展开激烈辩论，各自坚持己见，争议焦点逐渐明朗。关键证据的效力成为争议核心，每一个细节都可能影响最终判决。"
        elif plot_type == '人物转折':
            return "在经历了内心的挣扎后，主人公终于做出了关键决定。这个选择将改变他们的人生轨迹，也为故事带来新的转机。"
        elif plot_type == '线索揭露':
            return "隐藏已久的真相终于浮出水面，这个发现震撼了所有人。事情的真实面貌远比想象的复杂，为案件调查开辟了新的方向。"
        elif plot_type == '情感爆发':
            return "情感在此刻达到了临界点，内心的压抑和痛苦再也无法掩饰。这种真实的情感表达触动人心，让观众深深感受到角色的内心世界。"
        else:
            return f"在这个{plot_type}的重要时刻，剧情迎来关键发展。角色面临重要选择，每个决定都将影响故事的走向。"

    def _get_corrected_errors_in_segment(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]: #add
        """获取该片段中修正的错别字""" #add
        corrected = [] #add
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)]) #add

        for old, new in self.corrections.items(): #add
            if old in content: #add
                corrected.append(f"'{old}' → '{new}'") #add

        return corrected #add

    def _validate_time_ranges(self, plot_points: List[Dict], subtitles: List[Dict]) -> bool:
        """验证AI返回的时间范围是否有效"""
        if not plot_points or not subtitles:
            return False
            
        first_subtitle_time = subtitles[0]['start']
        last_subtitle_time = subtitles[-1]['end']
        
        first_seconds = self._time_to_seconds(first_subtitle_time)
        last_seconds = self._time_to_seconds(last_subtitle_time)
        
        for point in plot_points:
            start_time = point.get('start_time', '')
            end_time = point.get('end_time', '')
            
            if not start_time or not end_time:
                print(f"⚠️ 缺少时间信息: {point.get('title', '未知片段')}")
                return False
                
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            
            # 检查时间是否在字幕范围内
            if start_seconds < first_seconds or end_seconds > last_seconds:
                print(f"⚠️ 时间超出范围: {start_time}-{end_time} (字幕范围: {first_subtitle_time}-{last_subtitle_time})")
                return False
                
            # 检查时间段是否有效
            if start_seconds >= end_seconds:
                print(f"⚠️ 无效时间段: {start_time}-{end_time}")
                return False
                
            # 检查时长是否合理（60-300秒）
            duration = end_seconds - start_seconds
            if duration < 60 or duration > 300:
                print(f"⚠️ 时长不合理: {duration:.1f}秒")
                return False
                
        return True

    def _build_episode_context(self, episode_num: str, subtitles: List[Dict]) -> str:
        """构建集数上下文信息"""
        if episode_num in self.episode_contexts:
            return self.episode_contexts[episode_num]
            
        # 分析该集的基本信息
        all_text = " ".join([sub['text'] for sub in subtitles])
        
        # 提取关键角色
        key_characters = []
        character_patterns = ['检察官', '律师', '法官', '被告', '证人', '警察']
        for pattern in character_patterns:
            if pattern in all_text:
                key_characters.append(pattern)
                
        # 提取关键事件
        key_events = []
        event_patterns = ['案件', '审判', '证据', '听证会', '申诉', '调查']
        for pattern in event_patterns:
            if pattern in all_text:
                key_events.append(pattern)
        
        context = f"主要角色：{', '.join(key_characters[:3])}；关键事件：{', '.join(key_events[:3])}"
        self.episode_contexts[episode_num] = context
        
        return context

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析结果缓存路径"""
        file_hash = self.get_file_hash(os.path.join(self.srt_folder, srt_file)) # fix
        episode_num = self._extract_episode_number(srt_file)
        return os.path.join(self.analysis_cache_folder, f"analysis_E{episode_num}_{file_hash}.json")

    def save_analysis_cache(self, srt_file: str, analysis_result: Dict):
        """保存分析结果到缓存"""
        cache_path = self.get_analysis_cache_path(srt_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            print(f"💾 分析结果已缓存: {os.path.basename(cache_path)}") #fix
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def load_analysis_cache(self, srt_file: str) -> Optional[Dict]:
        """从缓存加载分析结果"""
        cache_path = self.get_analysis_cache_path(srt_file)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                print(f"💾 使用缓存的分析结果: {os.path.basename(cache_path)}") #fix
                return result
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
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

    def check_ffmpeg(self) -> bool:
        """检查FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def create_video_clips_stable(self, plot_points: List[Dict], video_file: str, srt_filename: str) -> List[str]: #fix
        """创建视频片段"""
        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []

        created_clips = []
        episode_num = self._extract_episode_number(srt_filename)

        for i, plot_point in enumerate(plot_points, 1):
            plot_type = plot_point['plot_type']
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', f"E{episode_num}_{plot_type}_{i}")
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)

            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # 创建片段
            if self._create_single_clip_stable(video_file, plot_point, clip_path): #fix
                created_clips.append(clip_path)
                self._create_clip_description(clip_path, plot_point, episode_num)

        return created_clips

    def _create_single_clip_stable(self, video_file: str, plot_point: Dict, output_path: str, max_retries: int = 3) -> bool: #fix
        """创建单个视频片段"""
        for attempt in range(max_retries): #add
            try: #add
                start_time = plot_point['start_time']
                end_time = plot_point['end_time']

                if attempt == 0: #add
                    print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
                    print(f"   时间: {start_time} --> {end_time}")
                    print(f"   类型: {plot_point['plot_type']}")

                start_seconds = self._time_to_seconds(start_time)
                end_seconds = self._time_to_seconds(end_time)
                duration = end_seconds - start_seconds

                if duration <= 0:
                    print(f"   ❌ 无效时间段: 开始{start_seconds:.1f}s >= 结束{end_seconds:.1f}s")
                    return False

                if duration < 30:
                    print(f"   ❌ 时长过短: {duration:.1f}秒")
                    return False

                # 添加小量缓冲时间
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
                    '-avoid_negative_ts', 'make_zero', #add
                    '-movflags', '+faststart', #add
                    output_path,
                    '-y'
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1024: #fix
                    file_size = os.path.getsize(output_path) / (1024*1024) #fix
                    print(f"   ✅ 成功: {file_size:.1f}MB (实际时长: {duration:.1f}秒)") #fix
                    return True
                else:
                    error_msg = result.stderr[:200] if result.stderr else '未知错误'
                    print(f"   ❌ 尝试{attempt+1}失败: {error_msg}")
                    # 清理失败的文件 #add
                    if os.path.exists(output_path): #add
                        os.remove(output_path) #add

            except subprocess.TimeoutExpired: #add
                print(f"   ❌ 尝试{attempt+1}超时")
                if os.path.exists(output_path): #add
                    os.remove(output_path) #add
            except Exception as e: #add
                print(f"   ❌ 尝试{attempt+1}异常: {e}")
                if os.path.exists(output_path): #add
                    os.remove(output_path) #add

        print(f"   ❌ 所有重试失败") #add
        return False

    def _create_clip_description(self, video_path: str, plot_point: Dict, episode_num: str):
        """创建片段描述文件"""
        try:
            desc_path = video_path.replace('.mp4', '_片段说明.txt')

            content = f"""📺 电视剧短视频片段说明文档
{"=" * 60}

【基本信息】
集数编号：第{episode_num}集
片段类型：{plot_point['plot_type']}
片段标题：{plot_point['title']}

【时间信息】
开始时间：{plot_point['start_time']}
结束时间：{plot_point['end_time']}
片段时长：{plot_point['duration']:.1f} 秒

【剧情分析】
剧情意义：{plot_point['plot_significance']}
内容摘要：{plot_point['content_summary']}

【内容亮点】
"""
            for highlight in plot_point['content_highlights']:
                content += f"• {highlight}\n"

            content += f"""
【第三人称旁白字幕】
{plot_point['third_person_narration']}

【技术说明】
• 片段保证在完整句子处开始和结束
• 自动修正了常见错别字
• 第三人称旁白可直接用于视频制作

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   📝 说明文件: {os.path.basename(desc_path)}") # add

        except Exception as e:
            print(f"   ⚠️ 说明文件生成失败: {e}")

    def process_episode_stable(self, srt_filename: str) -> Optional[Dict]: #fix
        """处理单集"""
        print(f"\n📺 处理集数: {srt_filename}")

        # 检查缓存
        cached_analysis = self.load_analysis_cache(srt_filename)
        if cached_analysis:
            plot_points = cached_analysis.get('plot_points', [])
            episode_num = cached_analysis.get('episode_number', self._extract_episode_number(srt_filename))
        else:
            # 解析字幕
            srt_path = os.path.join(self.srt_folder, srt_filename)
            subtitles = self.parse_srt_file(srt_path)

            if not subtitles:
                print(f"❌ 字幕解析失败")
                return None

            episode_num = self._extract_episode_number(srt_filename)

            # 构建该集的上下文
            episode_context = self._build_episode_context(episode_num, subtitles)
            
            # AI分析优先，基础规则兜底
            ai_analysis = self.analyze_with_ai(subtitles, episode_num, episode_context)
            if ai_analysis and ai_analysis.get('plot_points'):
                plot_points = ai_analysis['plot_points']
                print(f"🎯 AI识别到 {len(plot_points)} 个剧情点:")
                for i, point in enumerate(plot_points, 1):
                    plot_type = point.get('plot_type', '未知类型')
                    title = point.get('title', '无标题')
                    duration = point.get('duration', 0)
                    print(f"    {i}. {plot_type}: {title} ({duration:.1f}秒)")
            else:
                print("📝 AI分析失败，使用基础规则分析")
                plot_points = self.analyze_plot_points_basic(subtitles, episode_num)
                print(f"🎯 规则识别到 {len(plot_points)} 个剧情点:")
                for i, point in enumerate(plot_points, 1):
                    plot_type = point.get('plot_type', '未知类型')
                    duration = point.get('duration', 0)
                    print(f"    {i}. {plot_type} (时长: {duration:.1f}秒)")

            if not plot_points:
                print(f"❌ 未找到合适的剧情点")
                return None

            print(f"🎯 识别到 {len(plot_points)} 个剧情点:") #add
            for i, point in enumerate(plot_points, 1): #add
                plot_type = point.get('plot_type', '未知类型') #add
                duration = point.get('duration', 0) #add
                score = point.get('score', 0) #add
                print(f"    {i}. {plot_type} (时长: {duration:.1f}秒, 评分: {score:.1f})") #add

            # 保存分析结果到缓存
            episode_summary = {
                'episode_number': episode_num,
                'filename': srt_filename,
                'plot_points': plot_points,
                'analysis_timestamp': datetime.now().isoformat()
            }
            self.save_analysis_cache(srt_filename, episode_summary)

        # 查找视频文件
        video_file = self.find_video_file(srt_filename)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return None

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 创建视频片段
        created_clips = self.create_video_clips_stable(plot_points, video_file, srt_filename) #fix

        return {
            'episode_number': episode_num,
            'filename': srt_filename,
            'plot_points': plot_points,
            'created_clips': len(created_clips),
            'processing_timestamp': datetime.now().isoformat()
        }

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能剧情剪辑处理")
        print("=" * 50)

        # 获取所有SRT文件并按名称排序
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        # 按字符串排序（即按SRT文件名排序）
        srt_files.sort()

        print(f"📝 找到 {len(srt_files)} 个字幕文件（按文件名排序）")
        for i, f in enumerate(srt_files, 1):
            print(f"   {i}. {f}")

        # 处理每一集
        all_episodes = []
        total_clips = 0

        for i, srt_file in enumerate(srt_files):
            try:
                print(f"\n{'='*60}")
                print(f"📺 处理第 {i+1}/{len(srt_files)} 集: {srt_file}")
                print(f"{'='*60}")

                episode_summary = self.process_episode_stable(srt_file) #fix
                if episode_summary:
                    all_episodes.append(episode_summary)
                    total_clips += episode_summary['created_clips']

            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")

        # 生成最终报告
        self._create_final_report(all_episodes, total_clips)

        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {len(all_episodes)}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")
        print(f"📁 输出目录: {self.clips_folder}/")

    def _create_final_report(self, episodes: List[Dict], total_clips: int):
        """创建最终报告"""
        if not episodes:
            return

        report_path = os.path.join(self.reports_folder, "智能剪辑报告.txt")

        content = f"""📺 智能电视剧剪辑系统报告
{"=" * 80}

📊 处理统计：
• 总集数: {len(episodes)} 集
• 生成片段: {total_clips} 个
• 平均每集片段: {total_clips/len(episodes):.1f} 个
• AI分析状态: {'已启用' if self.ai_config.get('enabled') else '基础规则分析'}

📺 分集详细信息：
{"=" * 60}
"""

        for episode in episodes:
            content += f"""
【第{episode['episode_number']}集】{episode['filename']}
生成片段：{episode['created_clips']} 个
处理时间：{episode.get('processing_timestamp', '未知')}

剧情点详情：
"""
            for i, plot_point in enumerate(episode['plot_points'], 1):
                plot_type = plot_point.get('plot_type', '未知类型')
                title = plot_point.get('title', '无标题')
                start_time = plot_point.get('start_time', '00:00:00,000')
                end_time = plot_point.get('end_time', '00:00:00,000')
                duration = plot_point.get('duration', 0)

                content += f"""  {i}. {plot_type} - {title}
     时间：{start_time} --> {end_time} ({duration:.1f}秒)
"""

            content += f"""{"─" * 60}
"""

        content += f"""
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 详细报告已保存: {report_path}")
        except Exception as e:
            print(f"⚠️ 报告保存失败: {e}")

    def show_file_status(self):
        """显示文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        video_files = [f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
        output_files = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]

        print(f"\n📊 文件状态:")
        print(f"📝 字幕文件: {len(srt_files)} 个")
        if srt_files:
            srt_files.sort()  # 按名称排序显示
            for i, f in enumerate(srt_files[:5], 1):
                print(f"   {i}. {f}")
            if len(srt_files) > 5:
                print(f"   ... 还有 {len(srt_files)-5} 个文件")

        print(f"🎬 视频文件: {len(video_files)} 个")
        print(f"📤 输出视频: {len(output_files)} 个")

    def show_usage_guide(self): #add
        """显示使用教程""" #add
        print("\n📖 使用教程") #add
        print("=" * 50) #add
        print(""" #add
🎯 快速开始: #add
1. 将字幕文件(.srt/.txt)放在 srt/ 目录 #add
2. 将对应视频文件(.mp4/.mkv/.avi)放在 videos/ 目录 #add
3. 可选：配置AI接口 (推荐但非必需) #add
4. 运行智能剪辑 #add

📁 目录结构: #add
项目根目录/ #add
├── srt/ #add
│ ├── EP01.srt #add
│ └── EP02.srt #add
├── videos/ #add
│ ├── EP01.mp4 #add
│ └── EP02.mp4 #add
└── clips/ #add
# 输出目录 (自动创建) #add

💡 使用技巧: #add
字幕文件名决定集数顺序 (按字符串排序) #add
确保视频和字幕文件名对应 #add
每集生成3-5个2-3分钟的精彩片段 #add
AI可选：有AI更好，无AI也能工作 #add
""") #add
        input("\n按回车键返回主菜单...") #add

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 智能电视剧剪辑系统")
            print("=" * 60)

            # 显示AI状态
            if self.ai_config.get('enabled'):
                api_type = self.ai_config.get('api_type', '未知')
                provider = self.ai_config.get('provider', '未知')
                ai_status = f"🤖 已配置 ({api_type} - {provider})"
            else:
                ai_status = f"📝 基础规则分析"

            print(f"AI状态: {ai_status}")

            # 文件状态
            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))])
            clips_count = len([f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')])

            print(f"文件状态: 📝{srt_count}个字幕 🎬{video_count}个视频 📤{clips_count}个片段")

            print("\n🎯 主要功能:")
            print("1. 🤖 配置AI接口")
            print("2. 🎬 开始智能剪辑")
            print("3. 📁 查看文件状态")
            if self.ai_config.get('enabled'):
                print("4. 🔍 测试AI连接")
                print("5. 📖 查看使用教程") #add
                print("0. ❌ 退出系统")
            else:
                print("4. 📖 查看使用教程") #add
                print("0. ❌ 退出系统")

            try:
                max_choice = "5" if self.ai_config.get('enabled') else "4" #fix
                choice = input(f"\n请选择操作 (0-{max_choice}): ").strip()

                if choice == '1':
                    self.configure_ai_interactive()
                elif choice == '2':
                    if srt_count == 0:
                        print("\n⚠️ 请先将字幕文件放入 srt/ 目录")
                        continue
                    if video_count == 0:
                        print("\n⚠️ 请先将视频文件放入 videos/ 目录")
                        continue

                    self.process_all_episodes()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '4' and self.ai_config.get('enabled'):
                    self.test_current_connection()
                elif choice == '4' and not self.ai_config.get('enabled'): #add
                    self.show_usage_guide() #add
                elif choice == '5' and self.ai_config.get('enabled'): #add
                    self.show_usage_guide() #add
                elif choice == '0':
                    print("\n👋 感谢使用智能电视剧剪辑系统！")
                    break
                else:
                    print(f"❌ 无效选择，请输入0-{max_choice}")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断，程序退出")
                break
            except Exception as e: # add
                print(f"❌ 操作错误: {e}") # add
                input("按回车键继续...") # add

def main():
    """主函数"""
    print("🎬 智能电视剧剪辑系统")
    print("=" * 60)

    clipper = IntelligentTVClipperSystem()
    clipper.show_main_menu()

if __name__ == "__main__":
    main()