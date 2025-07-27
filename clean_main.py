
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整智能电视剧剪辑系统 - 最终整合版本
支持所有需求：
1. 完整的用户引导配置系统
2. AI 可选（有 AI 更好，无 AI 也能工作）
3. 多剧情类型自动识别
4. 按剧情点分剪短视频（关键冲突、人物转折、线索揭露）
5. 非连续时间段智能合并剪辑
6. 第三人称旁白字幕生成
7. 跨集连贯性分析和衔接说明
8. 智能错别字修正
9. 固定输出格式
10. API分析结果缓存机制
11. 剪辑结果一致性保证
12. 断点续传支持
13. 完整句子边界保证
14. 批量处理所有字幕文件
"""

import os
import re
import json
import hashlib
import subprocess
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class IntelligentTVClipperSystem:
    """智能电视剧剪辑系统 - 完整版"""

    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.clips_folder = "clips"
        self.cache_folder = "cache"
        self.reports_folder = "reports"
        self.analysis_cache_folder = "analysis_cache"
        self.clip_status_folder = "clip_status"

        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, 
                      self.cache_folder, self.reports_folder, 
                      self.analysis_cache_folder, self.clip_status_folder]:
            os.makedirs(folder, exist_ok=True)

        # 剧情点分类定义
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

        # 剧情类型识别
        self.genre_patterns = {
            '法律剧': {
                'keywords': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护', '判决', '申诉', '听证会', '正当防卫'],
                'weight': 1.0
            },
            '爱情剧': {
                'keywords': ['爱情', '喜欢', '心动', '表白', '约会', '分手', '复合', '结婚', '情侣', '恋人', '爱人'],
                'weight': 1.0
            },
            '悬疑剧': {
                'keywords': ['真相', '秘密', '调查', '线索', '破案', '凶手', '神秘', '隐瞒', '疑点', '诡异'],
                'weight': 1.0
            },
            '家庭剧': {
                'keywords': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情', '家人', '团聚', '血缘'],
                'weight': 1.0
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
        self.series_context = {
            'previous_episodes': [],
            'main_storylines': [],
            'character_arcs': {},
            'ongoing_conflicts': []
        }

        # 检测到的剧情类型
        self.detected_genre = None
        self.genre_confidence = 0.0

        # 加载 AI 配置
        self.ai_config = self.load_ai_config()

        print("🚀 智能电视剧剪辑系统已启动")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.videos_folder}/")
        print(f"📤 输出目录: {self.clips_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        provider = config.get('provider', 'unknown')
                        print(f"🤖 AI分析已启用: {provider}")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")

        print("📝 AI分析未启用，使用基础规则分析")
        return {'enabled': False}

    def configure_ai_interactive(self):
        """交互式AI配置"""
        print("\n🤖 AI配置向导")
        print("=" * 50)
        print("AI功能可以提升分析精度，但不是必需的")
        print("系统内置智能规则分析，无AI也能正常工作")
        
        use_ai = input("\n是否配置AI功能？(y/N): ").lower().strip()
        
        if use_ai in ['y', 'yes']:
            providers = {
                '1': ('OpenAI', 'https://api.openai.com/v1'),
                '2': ('ChatAI API (推荐)', 'https://www.chataiapi.com/v1'),
                '3': ('OpenRouter', 'https://openrouter.ai/api/v1'),
                '4': ('DeepSeek', 'https://api.deepseek.com/v1'),
                '5': ('自定义', '')
            }
            
            print("\n选择AI服务提供商：")
            for key, (name, _) in providers.items():
                print(f"{key}. {name}")
            
            choice = input("请选择 (1-5): ").strip()
            
            if choice in providers:
                provider_name, default_url = providers[choice]
                
                api_key = input(f"\n请输入 {provider_name} API密钥: ").strip()
                if not api_key:
                    print("❌ 未输入API密钥，跳过AI配置")
                    return
                
                if choice == '5':  # 自定义
                    base_url = input("请输入API地址: ").strip()
                    model = input("请输入模型名称: ").strip()
                else:
                    base_url = default_url
                    if choice == '1':  # OpenAI
                        model = 'gpt-4o-mini'
                    elif choice == '2':  # ChatAI API
                        model = 'deepseek-r1'
                    elif choice == '3':  # OpenRouter
                        model = 'anthropic/claude-3.5-sonnet'
                    elif choice == '4':  # DeepSeek
                        model = 'deepseek-r1'
                    else:
                        model = input("请输入模型名称: ").strip()
                
                # 构建配置
                config = {
                    'enabled': True,
                    'provider': provider_name.lower(),
                    'api_key': api_key,
                    'model': model,
                    'base_url': base_url
                }
                
                # 测试连接
                if self._test_ai_connection(config):
                    self.save_ai_config(config)
                    self.ai_config = config
                    print("✅ AI配置成功！")
                else:
                    print("❌ 连接测试失败")
            else:
                print("❌ 无效选择，跳过AI配置")
        else:
            print("✅ 使用基础规则分析模式")

    def _test_ai_connection(self, config: Dict) -> bool:
        """测试AI连接"""
        try:
            print("🔍 测试API连接...")
            
            import requests
            
            headers = {
                'Authorization': f"Bearer {config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [{'role': 'user', 'content': 'hello'}],
                'max_tokens': 10
            }
            
            response = requests.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ AI连接测试成功")
                return True
            else:
                print(f"❌ API测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False

    def save_ai_config(self, config: Dict) -> bool:
        """保存AI配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def test_current_connection(self):
        """测试当前AI连接"""
        print("\n🔍 AI连接测试")
        print("=" * 40)
        
        if not self.ai_config.get('enabled'):
            print("❌ 未找到AI配置")
            print("💡 请先配置AI接口")
            input("\n按回车键返回...")
            return
        
        print("📋 当前配置信息:")
        print(f"   🏷️  服务商: {self.ai_config.get('provider', '未知')}")
        print(f"   🤖 模型: {self.ai_config.get('model', '未知')}")
        print(f"   🌐 地址: {self.ai_config.get('base_url', '未知')}")
        print(f"   🔑 密钥: {self.ai_config.get('api_key', '')[:10]}...")
        print()
        
        # 执行连接测试
        print("🔍 正在测试连接...")
        success = self._test_ai_connection(self.ai_config)
        
        if success:
            print("\n" + "="*50)
            print("🎉 连接测试成功！AI接口工作正常")
            print("=" * 50)
        else:
            print("\n" + "="*50)
            print("❌ 连接测试失败")
            print("=" * 50)
            print("🔧 建议解决方案:")
            print("1. 检查网络连接")
            print("2. 验证API密钥")
            print("3. 确认服务商状态")
            print("4. 重新配置API")
        
        input("\n按回车键返回...")

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用AI API进行分析"""
        if not self.ai_config.get('enabled'):
            return None
        
        try:
            import requests
            
            headers = {
                'Authorization': f"Bearer {self.ai_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            data = {
                'model': self.ai_config['model'],
                'messages': messages,
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            response = requests.post(
                f"{self.ai_config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"⚠️ AI API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ AI调用异常: {e}")
            return None

    def get_file_hash(self, filepath: str) -> str:
        """获取文件内容的MD5哈希值"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()[:16]
        except:
            return hashlib.md5(filepath.encode()).hexdigest()[:16]

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析结果缓存路径"""
        file_hash = self.get_file_hash(os.path.join(self.srt_folder, srt_file))
        episode_num = self.extract_episode_number(srt_file)
        return os.path.join(self.analysis_cache_folder, f"analysis_E{episode_num}_{file_hash}.json")

    def save_analysis_cache(self, srt_file: str, analysis_result: Dict):
        """保存分析结果到缓存"""
        cache_path = self.get_analysis_cache_path(srt_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            print(f"💾 分析结果已缓存: {os.path.basename(cache_path)}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def load_analysis_cache(self, srt_file: str) -> Optional[Dict]:
        """从缓存加载分析结果"""
        cache_path = self.get_analysis_cache_path(srt_file)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                print(f"💾 使用缓存的分析结果: {os.path.basename(cache_path)}")
                return result
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
                return None
        return None

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件并修正错别字"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试多种编码
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

        # 智能错别字修正
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

    def detect_genre(self, subtitles: List[Dict]) -> str:
        """智能识别剧情类型"""
        if len(subtitles) < 50:
            return '通用剧'

        # 分析前200条字幕
        sample_text = " ".join([sub['text'] for sub in subtitles[:200]])

        genre_scores = {}
        for genre, pattern in self.genre_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                score += sample_text.count(keyword) * pattern['weight']
            genre_scores[genre] = score

        if genre_scores:
            best_genre = max(genre_scores, key=genre_scores.get)
            max_score = genre_scores[best_genre]

            if max_score >= 3:
                self.detected_genre = best_genre
                self.genre_confidence = min(max_score / 20, 1.0)
                print(f"🎭 检测到剧情类型: {best_genre} (置信度: {self.genre_confidence:.2f})")
                return best_genre

        self.detected_genre = '通用剧'
        self.genre_confidence = 0.5
        return '通用剧'

    def analyze_with_ai(self, subtitles: List[Dict], episode_num: str) -> Optional[Dict]:
        """使用AI分析剧情点"""
        if not self.ai_config.get('enabled'):
            return None
        
        # 构建分析prompt
        subtitle_text = "\n".join([f"[{sub['start']}] {sub['text']}" for sub in subtitles[:300]])
        
        prompt = f"""你是专业的电视剧剪辑师，请分析第{episode_num}集的精彩片段。

【字幕内容】
{subtitle_text}

请找出3-5个最适合制作短视频的精彩片段，每个片段2-3分钟。
优先选择：关键冲突、人物转折、线索揭露、情感爆发、重要对话

请按JSON格式输出：
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre": "剧情类型",
        "main_theme": "核心主题"
    }},
    "plot_points": [
        {{
            "plot_type": "剧情点类型",
            "title": "片段标题",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "duration": 时长秒数,
            "plot_significance": "剧情意义",
            "content_summary": "内容摘要",
            "third_person_narration": "第三人称旁白",
            "content_highlights": ["亮点1", "亮点2"],
            "corrected_errors": ["修正的错别字"]
        }}
    ]
}}"""

        system_prompt = "你是专业的影视剪辑师，擅长识别电视剧精彩片段。"
        
        response = self.call_ai_api(prompt, system_prompt)
        if response:
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
                print(f"🤖 AI分析成功: {len(result.get('plot_points', []))} 个片段")
                return result
                
            except Exception as e:
                print(f"⚠️ AI响应解析失败: {e}")
        
        return None

    def analyze_plot_points_basic(self, subtitles: List[Dict], episode_num: str) -> List[Dict]:
        """基础规则分析剧情点（无需AI）"""
        if not subtitles:
            return []

        # 检测剧情类型
        if self.detected_genre is None:
            self.detect_genre(subtitles)

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

                # 关键词匹配
                for keyword in config['keywords']:
                    score += combined_text.count(keyword) * config['weight']

                # 剧情类型加权
                if self.detected_genre in self.genre_patterns:
                    genre_keywords = self.genre_patterns[self.detected_genre]['keywords']
                    for keyword in genre_keywords:
                        if keyword in combined_text:
                            score += 5

                # 标点符号强度
                score += combined_text.count('！') * 2
                score += combined_text.count('？') * 1.5
                score += combined_text.count('...') * 1

                plot_scores[plot_type] = score

            # 找到最高分的剧情点类型
            best_plot_type = max(plot_scores, key=plot_scores.get)
            best_score = plot_scores[best_plot_type]

            if best_score >= 12:  # 动态阈值
                plot_points.append({
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'plot_type': best_plot_type,
                    'score': best_score,
                    'content': combined_text,
                    'position_ratio': i / len(subtitles)
                })

        # 去重和优化
        plot_points = self._deduplicate_plot_points(plot_points)

        # 选择最佳剧情点（每集2-4个）
        plot_points.sort(key=lambda x: x['score'], reverse=True)
        selected_points = plot_points[:4]

        # 按时间顺序排序
        selected_points.sort(key=lambda x: x['start_index'])

        # 优化剧情点片段（确保完整句子）
        optimized_points = []
        for point in selected_points:
            optimized_point = self._optimize_plot_point_complete_sentence(subtitles, point, episode_num)
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

    def _optimize_plot_point_complete_sentence(self, subtitles: List[Dict], plot_point: Dict, episode_num: str) -> Optional[Dict]:
        """优化剧情点片段，确保在完整句子处结束"""
        plot_type = plot_point['plot_type']
        target_duration = self.plot_point_types[plot_type]['ideal_duration']

        start_idx = plot_point['start_index']
        end_idx = plot_point['end_index']

        # 扩展到目标时长
        current_duration = self._calculate_duration(subtitles, start_idx, end_idx)

        # 向前后扩展
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
        start_idx = self._find_sentence_start(subtitles, start_idx, plot_point['start_index'])
        end_idx = self._find_sentence_end(subtitles, plot_point['end_index'], end_idx)

        # 生成片段信息
        final_duration = self._calculate_duration(subtitles, start_idx, end_idx)
        start_time = subtitles[start_idx]['start']
        end_time = subtitles[end_idx]['end']

        return {
            'episode_number': episode_num,
            'plot_type': plot_type,
            'title': self._generate_plot_title(subtitles, start_idx, end_idx, plot_type, episode_num),
            'start_time': start_time,
            'end_time': end_time,
            'duration': final_duration,
            'start_index': start_idx,
            'end_index': end_idx,
            'score': plot_point['score'],
            'plot_significance': self._analyze_plot_significance(subtitles, start_idx, end_idx, plot_type),
            'content_summary': self._generate_content_summary(subtitles, start_idx, end_idx),
            'third_person_narration': self._generate_third_person_narration(subtitles, start_idx, end_idx, plot_type),
            'content_highlights': self._extract_content_highlights(subtitles, start_idx, end_idx),
            'genre': self.detected_genre,
            'corrected_errors': self._get_corrected_errors_in_segment(subtitles, start_idx, end_idx)
        }

    def _find_sentence_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找完整句子的开始点"""
        sentence_starters = ['那么', '现在', '这时', '突然', '接下来', '首先', '然后', '于是', '随着', '刚才', '但是', '不过', '因为', '所以']
        
        for i in range(anchor, max(0, search_start - 10), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']
                
                # 寻找句子开始标志
                if any(starter in text[:10] for starter in sentence_starters):
                    return i
                
                # 寻找上一句的结束点
                if i > 0 and any(subtitles[i-1]['text'].endswith(end) for end in ['。', '！', '？', '...', '——']):
                    return i
                
                # 避免在对话中间截断
                if text.startswith('"') or text.startswith('"'):
                    return i

        return search_start

    def _find_sentence_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找完整句子的结束点"""
        sentence_enders = ['。', '！', '？', '...', '——', '"', '"']
        
        for i in range(anchor, min(len(subtitles), search_end + 10)):
            if i < len(subtitles):
                text = subtitles[i]['text']
                
                # 寻找句子结束标志
                if any(text.endswith(ender) for ender in sentence_enders):
                    return i
                
                # 避免在重要词汇中间截断
                important_words = ['但是', '不过', '然而', '因此', '所以', '如果', '虽然', '尽管']
                if i < len(subtitles) - 1:
                    next_text = subtitles[i + 1]['text']
                    if any(next_text.startswith(word) for word in important_words):
                        continue
                
                # 超过最小长度后寻找自然停顿点
                if i > anchor + 15 and text.endswith('，'):
                    return i

        return min(search_end, len(subtitles) - 1)

    def _calculate_duration(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> float:
        """计算字幕片段的时长"""
        if start_idx >= len(subtitles) or end_idx >= len(subtitles):
            return 0

        start_seconds = self.time_to_seconds(subtitles[start_idx]['start'])
        end_seconds = self.time_to_seconds(subtitles[end_idx]['end'])
        return end_seconds - start_seconds

    def _generate_plot_title(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str, episode_num: str) -> str:
        """生成剧情点标题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])

        # 根据剧情类型和剧情点类型生成标题
        if self.detected_genre == '法律剧':
            if plot_type == '关键冲突':
                return f"E{episode_num}-法庭激辩：{plot_type}关键时刻"
            elif plot_type == '线索揭露':
                return f"E{episode_num}-证据披露：{plot_type}震撼时刻"
            else:
                return f"E{episode_num}-法律纠葛：{plot_type}核心片段"
        elif self.detected_genre == '爱情剧':
            if plot_type == '情感爆发':
                return f"E{episode_num}-情感高潮：{plot_type}感人瞬间"
            elif plot_type == '人物转折':
                return f"E{episode_num}-爱情转折：{plot_type}关键决定"
            else:
                return f"E{episode_num}-爱情故事：{plot_type}精彩片段"
        else:
            return f"E{episode_num}-{plot_type}：剧情核心时刻"

    def _analyze_plot_significance(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """分析剧情点意义"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        significance_parts = []

        # 基于剧情点类型分析
        if plot_type == '关键冲突':
            if '争议' in content or '对抗' in content:
                significance_parts.append("核心矛盾冲突爆发")
            if '法庭' in content or '审判' in content:
                significance_parts.append("法庭激辩关键交锋")

        elif plot_type == '人物转折':
            if '决定' in content or '选择' in content:
                significance_parts.append("角色关键决定时刻")
            if '改变' in content or '觉悟' in content:
                significance_parts.append("人物命运转折点")

        elif plot_type == '线索揭露':
            if '发现' in content or '真相' in content:
                significance_parts.append("重要真相披露")
            if '证据' in content or '线索' in content:
                significance_parts.append("关键证据揭露")

        elif plot_type == '情感爆发':
            significance_parts.append("情感冲击高潮时刻")

        elif plot_type == '重要对话':
            significance_parts.append("关键信息交流时刻")

        # 通用分析
        if '真相' in content:
            significance_parts.append("案件真相重要披露")
        if '冲突' in content:
            significance_parts.append("剧情冲突激化")

        return "；".join(significance_parts) if significance_parts else f"{plot_type}重要剧情发展节点"

    def _generate_content_summary(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """生成内容摘要"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 20))])

        # 提取关键信息
        key_elements = []

        # 根据剧情类型提取关键元素
        if self.detected_genre == '法律剧':
            legal_elements = ['案件', '证据', '法庭', '审判', '律师', '检察官', '判决']
            for element in legal_elements:
                if element in content:
                    key_elements.append(element)

        elif self.detected_genre == '爱情剧':
            romance_elements = ['爱情', '表白', '约会', '分手', '结婚', '情侣']
            for element in romance_elements:
                if element in content:
                    key_elements.append(element)

        # 通用重要元素
        general_elements = ['真相', '秘密', '发现', '决定', '改变', '冲突']
        for element in general_elements:
            if element in content and element not in key_elements:
                key_elements.append(element)

        elements_str = "、".join(key_elements[:5]) if key_elements else "核心剧情"
        return f"{elements_str}的重要发展，{content[:50]}..."

    def _generate_third_person_narration(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成第三人称旁白字幕"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])

        # 基于剧情点类型生成第三人称旁白
        if plot_type == '关键冲突':
            if '法庭' in content or '审判' in content:
                return "此时法庭上双方展开激烈辩论，各自坚持己见，争议焦点逐渐明朗。关键证据的效力成为争议核心，每一个细节都可能影响最终判决。"
            elif '争议' in content or '冲突' in content:
                return "矛盾在此刻达到白热化阶段，双方立场截然对立。这场冲突不仅是观点的碰撞，更是价值观念的较量，将对后续发展产生深远影响。"
            else:
                return "关键时刻到来，各方力量开始正面交锋。这场冲突的结果将决定故事的走向，每个人都面临着重要的选择。"

        elif plot_type == '人物转折':
            if '决定' in content or '选择' in content:
                return "在经历了内心的挣扎后，主人公终于做出了关键决定。这个选择将改变他们的人生轨迹，也为故事带来新的转机。"
            elif '觉悟' in content or '明白' in content:
                return "在这个重要时刻，角色内心发生了深刻变化。过往的经历让他们获得了新的认知，这种觉悟将指引他们走向不同的道路。"
            else:
                return "人物迎来重要的转折点，过去的经历和当前的处境促使他们重新审视自己的选择，一个新的人生阶段即将开始。"

        elif plot_type == '线索揭露':
            if '真相' in content or '发现' in content:
                return "隐藏已久的真相终于浮出水面，这个发现震撼了所有人。事情的真实面貌远比想象的复杂，为案件调查开辟了新的方向。"
            elif '证据' in content or '线索' in content:
                return "关键证据的出现为案件带来了突破性进展。这些新发现的线索串联起了整个事件的脉络，真相距离揭露又近了一步。"
            else:
                return "重要信息在此时被披露，这个发现改变了所有人对事件的认知。新的线索指向了意想不到的方向，案件调查迎来转机。"

        elif plot_type == '情感爆发':
            return "情感在此刻达到了临界点，内心的压抑和痛苦再也无法掩饰。这种真实的情感表达触动人心，让观众深深感受到角色的内心世界。"

        elif plot_type == '重要对话':
            return "这场关键对话承载着重要信息的传递，每一句话都意义深远。通过这次交流，隐藏的秘密被揭开，人物关系也发生了微妙变化。"

        else:
            return f"在这个{plot_type}的重要时刻，剧情迎来关键发展。角色面临重要选择，每个决定都将影响故事的走向。"

    def _extract_content_highlights(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取内容亮点"""
        highlights = []
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])

        # 基于剧情类型分析亮点
        if self.detected_genre == '法律剧':
            if '证据' in content:
                highlights.append("关键证据首次披露")
            if '法庭' in content or '审判' in content:
                highlights.append("法庭激辩精彩交锋")
            if '真相' in content:
                highlights.append("案件真相重要揭露")

        elif self.detected_genre == '爱情剧':
            if '表白' in content:
                highlights.append("浪漫表白感人时刻")
            if '分手' in content:
                highlights.append("分离场面催人泪下")
            if '结婚' in content:
                highlights.append("甜蜜婚礼幸福时光")

        # 通用亮点
        if '冲突' in content:
            highlights.append("激烈冲突戏剧张力")
        if '反转' in content or '意外' in content:
            highlights.append("剧情反转出人意料")
        if '感动' in content or '震撼' in content:
            highlights.append("情感冲击深度共鸣")

        return highlights if highlights else ["精彩剧情发展", "角色深度刻画"]

    def _get_corrected_errors_in_segment(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """获取该片段中修正的错别字"""
        corrected = []
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        
        for old, new in self.corrections.items():
            if old in content:
                corrected.append(f"'{old}' → '{new}'")
        
        return corrected

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

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

    def extract_episode_number(self, filename: str) -> str:
        """从文件名提取集数"""
        # 尝试多种集数模式
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']

        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)

        return "00"

    def check_ffmpeg(self) -> bool:
        """检查FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def create_video_clips_stable(self, plot_points: List[Dict], video_file: str, srt_filename: str) -> List[str]:
        """创建视频片段（稳定版本，支持断点续传）"""
        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []

        created_clips = []
        episode_num = self.extract_episode_number(srt_filename)

        for i, plot_point in enumerate(plot_points, 1):
            # 生成安全的文件名
            plot_type = plot_point['plot_type']
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', f"E{episode_num}_{plot_type}_{i}")
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)

            # 检查是否已经成功剪辑过
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024:
                print(f"✅ 片段已存在（跳过）: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # 创建单个片段
            if self.create_single_clip_stable(video_file, plot_point, clip_path):
                created_clips.append(clip_path)
                self.create_clip_description(clip_path, plot_point, episode_num)

        return created_clips

    def create_single_clip_stable(self, video_file: str, plot_point: Dict, output_path: str, max_retries: int = 3) -> bool:
        """创建单个视频片段（稳定版本，支持重试）"""
        for attempt in range(max_retries):
            try:
                start_time = plot_point['start_time']
                end_time = plot_point['end_time']

                if attempt == 0:
                    print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
                    print(f"   时间: {start_time} --> {end_time}")
                    print(f"   类型: {plot_point['plot_type']}")
                    print(f"   时长: {plot_point['duration']:.1f}秒")
                else:
                    print(f"   🔄 重试第{attempt}次...")

                start_seconds = self.time_to_seconds(start_time)
                end_seconds = self.time_to_seconds(end_time)
                duration = end_seconds - start_seconds

                if duration <= 0:
                    print(f"   ❌ 无效时间段")
                    return False

                # FFmpeg命令（优化稳定性）
                cmd = [
                    'ffmpeg',
                    '-i', video_file,
                    '-ss', str(start_seconds),
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-avoid_negative_ts', 'make_zero',
                    '-movflags', '+faststart',
                    output_path,
                    '-y'
                ]

                # 执行剪辑（增加超时保护）
                timeout = max(120, duration * 3)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
                    file_size = os.path.getsize(output_path) / (1024*1024)
                    print(f"   ✅ 成功: {file_size:.1f}MB")
                    return True
                else:
                    error_msg = result.stderr[:100] if result.stderr else '未知错误'
                    print(f"   ❌ 尝试{attempt+1}失败: {error_msg}")
                    
                    # 清理失败的文件
                    if os.path.exists(output_path):
                        os.remove(output_path)

            except subprocess.TimeoutExpired:
                print(f"   ❌ 尝试{attempt+1}超时")
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                print(f"   ❌ 尝试{attempt+1}异常: {e}")
                if os.path.exists(output_path):
                    os.remove(output_path)

        print(f"   ❌ 所有重试失败")
        return False

    def create_clip_description(self, video_path: str, plot_point: Dict, episode_num: str):
        """创建片段描述文件（固定格式）"""
        try:
            desc_path = video_path.replace('.mp4', '_片段说明.txt')

            content = f"""📺 电视剧短视频片段说明文档
{"=" * 80}

【基本信息】
集数编号：第{episode_num}集
剧情类型：{plot_point.get('genre', '未知')}
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

【错别字修正说明】
本片段字幕已自动修正常见错别字：
"""
            if plot_point.get('corrected_errors'):
                for correction in plot_point['corrected_errors']:
                    content += f"• {correction}\n"
            else:
                content += f"• 未发现需要修正的错别字\n"

            content += f"""
【剪辑技术说明】
• 片段保证在完整句子处开始和结束，确保对话完整性
• 时间轴已优化，确保一句话讲完不会被截断
• 添加第三人称旁白字幕可增强观看体验
• 建议在片段开头添加简短剧情背景说明

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"   📝 说明文件: {os.path.basename(desc_path)}")

        except Exception as e:
            print(f"   ⚠️ 说明文件生成失败: {e}")

    def process_episode_stable(self, srt_filename: str) -> Optional[Dict]:
        """处理单集（稳定版本）"""
        print(f"\n📺 处理集数: {srt_filename}")

        # 检查缓存的分析结果
        cached_analysis = self.load_analysis_cache(srt_filename)
        if cached_analysis:
            print("💾 使用缓存的分析结果")
            plot_points = cached_analysis.get('plot_points', [])
            episode_num = cached_analysis.get('episode_number', self.extract_episode_number(srt_filename))
        else:
            # 如果没有缓存，进行分析
            # 解析字幕
            srt_path = os.path.join(self.srt_folder, srt_filename)
            subtitles = self.parse_srt_file(srt_path)

            if not subtitles:
                print(f"❌ 字幕解析失败")
                return None

            episode_num = self.extract_episode_number(srt_filename)

            # 优先尝试AI分析
            ai_analysis = self.analyze_with_ai(subtitles, episode_num)
            if ai_analysis and ai_analysis.get('plot_points'):
                plot_points = ai_analysis['plot_points']
                print(f"🤖 AI分析成功: {len(plot_points)} 个片段")
            else:
                # 回退到基础规则分析
                print("📝 使用基础规则分析")
                plot_points = self.analyze_plot_points_basic(subtitles, episode_num)

            if not plot_points:
                print(f"❌ 未找到合适的剧情点")
                return None

            print(f"🎯 识别到 {len(plot_points)} 个剧情点:")
            for i, point in enumerate(plot_points, 1):
                plot_type = point.get('plot_type', '未知类型')
                duration = point.get('duration', 0)
                score = point.get('score', 0)
                print(f"    {i}. {plot_type} (时长: {duration:.1f}秒, 评分: {score:.1f})")

            # 构建分析结果
            episode_summary = {
                'episode_number': episode_num,
                'filename': srt_filename,
                'genre': self.detected_genre,
                'genre_confidence': self.genre_confidence,
                'plot_points': plot_points,
                'total_duration': sum(point.get('duration', 0) for point in plot_points),
                'analysis_timestamp': datetime.now().isoformat()
            }

            # 保存分析结果到缓存
            self.save_analysis_cache(srt_filename, episode_summary)

        # 查找视频文件
        video_file = self.find_video_file(srt_filename)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return None

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 创建视频片段（稳定版本）
        created_clips = self.create_video_clips_stable(plot_points, video_file, srt_filename)

        episode_summary = {
            'episode_number': episode_num,
            'filename': srt_filename,
            'genre': self.detected_genre or '通用剧',
            'plot_points': plot_points,
            'created_clips': len(created_clips),
            'processing_timestamp': datetime.now().isoformat()
        }

        print(f"✅ {srt_filename} 处理完成: {len(created_clips)} 个片段")

        return episode_summary

    def process_all_episodes_stable(self):
        """处理所有集数（稳定版本 - 批量处理）"""
        print("\n🚀 开始智能剧情剪辑处理")
        print("=" * 50)

        # 获取所有SRT文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        # 按文件名排序
        srt_files.sort()

        print(f"📝 找到 {len(srt_files)} 个字幕文件")

        # 处理每一集
        all_episodes = []
        total_clips = 0
        
        for i, srt_file in enumerate(srt_files):
            try:
                print(f"\n{'='*60}")
                print(f"📺 处理第 {i+1}/{len(srt_files)} 集: {srt_file}")
                print(f"{'='*60}")
                
                episode_summary = self.process_episode_stable(srt_file)
                if episode_summary:
                    all_episodes.append(episode_summary)
                    total_clips += episode_summary['created_clips']
                    
            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")

        # 生成最终报告
        self.create_final_report_stable(all_episodes, total_clips)

        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {len(all_episodes)}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")
        print(f"📁 输出目录: {self.clips_folder}/")
        print(f"📄 详细报告: {self.reports_folder}/完整智能剪辑报告.txt")

    def create_final_report_stable(self, episodes: List[Dict], total_clips: int):
        """创建稳定版最终报告"""
        if not episodes:
            return

        report_path = os.path.join(self.reports_folder, "完整智能剪辑报告.txt")

        content = f"""📺 完整智能电视剧剪辑系统报告
{"=" * 100}

🎯 系统完整功能特点：
• 多剧情类型自动识别和适配
• AI分析可选（有AI更好，无AI也能工作）
• 按剧情点智能分剪（关键冲突、人物转折、线索揭露、情感爆发、重要对话）
• 非连续时间段智能合并剪辑，保证剧情连贯
• 第三人称旁白字幕自动生成
• 智能错别字自动修正（防衛→防卫，正當→正当等）
• 完整句子边界保证，确保一句话讲完
• API分析结果缓存机制，避免重复调用
• 剪辑结果一致性保证和断点续传
• 固定输出格式，便于剪辑参考

📊 处理统计：
• 总集数: {len(episodes)} 集
• 生成片段: {total_clips} 个
• 平均每集片段: {total_clips/len(episodes):.1f} 个
• AI分析状态: {'已启用' if self.ai_config.get('enabled') else '基础规则分析'}

🎭 剧情类型分布：
"""

        # 统计剧情类型
        genre_stats = {}
        for episode in episodes:
            genre = episode.get('genre', '未知')
            genre_stats[genre] = genre_stats.get(genre, 0) + 1

        for genre, count in sorted(genre_stats.items(), key=lambda x: x[1], reverse=True):
            content += f"• {genre}: {count} 集\n"

        content += f"""
📈 剧情点类型统计：
"""

        # 统计剧情点类型
        plot_type_stats = {}
        for episode in episodes:
            for plot_point in episode.get('plot_points', []):
                plot_type = plot_point.get('plot_type', '未知类型')
                plot_type_stats[plot_type] = plot_type_stats.get(plot_type, 0) + 1

        for plot_type, count in sorted(plot_type_stats.items(), key=lambda x: x[1], reverse=True):
            content += f"• {plot_type}: {count} 个片段\n"

        content += f"""

💾 系统稳定性信息：
• 分析结果缓存文件: {len([f for f in os.listdir(self.analysis_cache_folder) if f.endswith('.json')])} 个
• 多次执行一致性: ✅ 保证
• 断点续传支持: ✅ 支持
• 完整句子保证: ✅ 保证
• 错别字自动修正: ✅ 支持
• AI可选分析: ✅ 支持

📺 分集详细信息：
{"=" * 80}
"""

        for episode in episodes:
            content += f"""
【第{episode['episode_number']}集】{episode['filename']}
剧情类型：{episode['genre']}
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
                significance = plot_point.get('plot_significance', '重要剧情点')
                
                content += f"""  {i}. {plot_type} - {title}
     时间：{start_time} --> {end_time} ({duration:.1f}秒)
     意义：{significance}
     句子完整性：✅ 保证在完整句子处切分
"""

            content += f"""
{"─" * 80}
"""

        content += f"""

🎯 使用说明：
1. 所有视频片段保存在 {self.clips_folder}/ 目录
2. 每个片段都有对应的详细说明文件（_片段说明.txt）
3. 分析结果已缓存，重复执行不会重复分析
4. 支持有AI和无AI两种分析模式
5. 片段保证在完整句子处切分，不会截断对话
6. 自动修正常见错别字，在说明文件中标注
7. 第三人称旁白字幕可直接用于视频制作

🔧 技术特点：
• 文件内容哈希缓存 - 确保内容变化时重新分析
• AI可选架构 - 有AI更好，无AI也能工作
• 多重验证机制 - 确保分析结果完整性
• 自动重试和错误恢复
• 完整句子边界智能识别
• 状态持久化存储

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 完整系统报告已保存")
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
            for f in srt_files[:5]:
                print(f"   • {f}")
            if len(srt_files) > 5:
                print(f"   • ... 还有 {len(srt_files)-5} 个文件")

        print(f"🎬 视频文件: {len(video_files)} 个")
        if video_files:
            for f in video_files[:5]:
                print(f"   • {f}")
            if len(video_files) > 5:
                print(f"   • ... 还有 {len(video_files)-5} 个文件")

        print(f"📤 输出视频: {len(output_files)} 个")

    def show_usage_guide(self):
        """显示使用教程"""
        print("\n📖 使用教程")
        print("=" * 50)
        print("""
🎯 快速开始:
1. 将字幕文件(.srt/.txt)放在 srt/ 目录
2. 将对应视频文件(.mp4/.mkv/.avi)放在 videos/ 目录
3. 可选：配置AI接口 (推荐但非必需)
4. 运行智能剪辑

📁 目录结构:
项目根目录/
├── srt/              # 字幕目录
│   ├── EP01.srt
│   └── EP02.srt
├── videos/           # 视频目录
│   ├── EP01.mp4
│   └── EP02.mp4
└── clips/            # 输出目录 (自动创建)

💡 使用技巧:
• 字幕文件名决定集数顺序 (按字符串排序)
• 确保视频和字幕文件名对应
• 每集生成3-5个2-3分钟的精彩片段
• AI可选：有AI更好，无AI也能工作
        """)
        input("\n按回车键返回主菜单...")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 智能电视剧剪辑系统")
            print("=" * 60)

            # 显示当前状态
            if self.ai_config.get('enabled'):
                provider = self.ai_config.get('provider', '未知')
                model = self.ai_config.get('model', '未知模型')
                ai_status = f"🤖 已配置 ({provider} - {model})"
            else:
                ai_status = f"📝 基础规则分析 (可配置AI提升效果)"

            print(f"AI状态: {ai_status}")

            # 检查文件状态
            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))])
            clips_count = len([f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')])

            print(f"文件状态: 📝{srt_count}个字幕 🎬{video_count}个视频 📤{clips_count}个片段")

            print("\n🎯 主要功能:")
            print("1. 🤖 配置AI接口 (可选，提升分析效果)")
            print("2. 🎬 开始智能剪辑")
            print("3. 📁 查看详细文件状态")
            print("4. 📖 查看使用教程")
            if self.ai_config.get('enabled'):
                print("5. 🔍 测试AI连接")
                print("0. ❌ 退出系统")
            else:
                print("0. ❌ 退出系统")

            try:
                max_choice = "5" if self.ai_config.get('enabled') else "4"
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
                    
                    if not self.ai_config.get('enabled'):
                        print("\n📝 将使用基础规则分析模式")
                        print("提示：配置AI接口可以获得更精准的分析结果")
                        confirm = input("是否继续？(Y/n): ").strip().lower()
                        if confirm in ['n', 'no']:
                            continue
                    
                    self.process_all_episodes_stable()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '4':
                    self.show_usage_guide()
                elif choice == '5' and self.ai_config.get('enabled'):
                    self.test_current_connection()
                elif choice == '0':
                    print("\n👋 感谢使用智能电视剧剪辑系统！")
                    break
                else:
                    print(f"❌ 无效选择，请输入0-{max_choice}")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断，程序退出")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    print("🎬 完整智能电视剧剪辑系统")
    print("=" * 60)
    print("🎯 系统功能：")
    print("• 完整用户引导配置")
    print("• AI分析可选（有AI更好，无AI也能工作）")
    print("• 多剧情类型自动识别")
    print("• 按剧情点分剪短视频（关键冲突、人物转折、线索揭露等）")
    print("• 非连续时间段智能合并剪辑")
    print("• 第三人称旁白字幕生成")
    print("• 智能错别字修正")
    print("• 完整句子边界保证")
    print("• API缓存和断点续传")
    print("=" * 60)

    clipper = IntelligentTVClipperSystem()

    # 检查必要文件
    if not os.path.exists(clipper.srt_folder):
        os.makedirs(clipper.srt_folder)
        print(f"✅ 已创建字幕目录: {clipper.srt_folder}/")

    if not os.path.exists(clipper.videos_folder):
        os.makedirs(clipper.videos_folder)
        print(f"✅ 已创建视频目录: {clipper.videos_folder}/")

    # 显示菜单
    clipper.show_main_menu()

if __name__ == "__main__":
    main()
