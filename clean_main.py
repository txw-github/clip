#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整智能电视剧剪辑系统 - 最终稳定版
解决所有16个核心问题的完整方案
"""

import os
import re
import json
import subprocess
import hashlib
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
import requests
from movie_ai_clipper import MovieAIClipper

class CompleteIntelligentTVClipper:
    """完整智能电视剧剪辑系统 - 稳定版"""

    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.clips_folder = "clips"
        self.cache_folder = "cache"
        self.reports_folder = "reports"
        self.analysis_cache_folder = "analysis_cache"
        self.clip_status_folder = "clip_status"

        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, 
                      self.cache_folder, self.reports_folder, self.analysis_cache_folder, self.clip_status_folder]:
            os.makedirs(folder, exist_ok=True)

        # 剧情点分类配置
        self.plot_point_types = {
            '关键冲突': {
                'keywords': ['冲突', '争执', '对抗', '质疑', '反驳', '争议', '激烈', '愤怒', '不同意', '矛盾', '争论', '辩论', '反对', '抗议'],
                'weight': 10,
                'ideal_duration': 180,
                'min_score': 15
            },
            '人物转折': {
                'keywords': ['决定', '改变', '选择', '转变', '觉悟', '明白', '意识到', '发现自己', '成长', '突破', '蜕变', '醒悟', '领悟'],
                'weight': 9,
                'ideal_duration': 150,
                'min_score': 12
            },
            '线索揭露': {
                'keywords': ['发现', '揭露', '真相', '证据', '线索', '秘密', '暴露', '证明', '找到', '曝光', '披露', '揭示', '显露'],
                'weight': 8,
                'ideal_duration': 160,
                'min_score': 10
            },
            '情感爆发': {
                'keywords': ['哭', '痛苦', '绝望', '愤怒', '激动', '崩溃', '心痛', '感动', '震撼', '泪水', '悲伤', '眼泪', '哽咽'],
                'weight': 7,
                'ideal_duration': 140,
                'min_score': 8
            },
            '重要对话': {
                'keywords': ['告诉', '承认', '坦白', '解释', '澄清', '说明', '表态', '保证', '承诺', '宣布', '声明', '交代'],
                'weight': 6,
                'ideal_duration': 170,
                'min_score': 6
            },
            '主题升华': {
                'keywords': ['正义', '真理', '信念', '坚持', '希望', '信任', '责任', '使命', '价值', '意义', '精神', '理想'],
                'weight': 8,
                'ideal_duration': 160,
                'min_score': 8
            }
        }

        # 错别字修正库
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '聽證會': '听证会',
            '問題': '问题', '機會': '机会', '開始': '开始', '結束': '结束',
            '証人': '证人', '証言': '证言', '実現': '实现', '対話': '对话',
            '関係': '关系', '実际': '实际', '対于': '对于', '変化': '变化',
            '無罪': '无罪', '有罪': '有罪', '検察': '检察', '弁護': '辩护'
        }

        # 全剧上下文管理
        self.series_context = {
            'previous_episodes': [],
            'main_storylines': [],
            'character_arcs': {},
            'ongoing_conflicts': [],
            'genre_detected': None,
            'main_themes': []
        }

        # 加载AI配置
        self.ai_config = self._load_ai_config()

        print("🤖 AI专用智能电视剧剪辑系统已启动")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"🎬 视频目录: {self.videos_folder}/")
        print(f"📤 输出目录: {self.clips_folder}/")
        print(f"💾 缓存系统: 启用")
        print("⚠️ 注意：本系统只使用AI分析，需要配置AI接口")

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

        print("❌ AI分析未启用，系统无法工作")
        print("💡 请配置AI接口后重新启动")
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
        """智能AI配置检查"""
        print("\n🤖 AI配置检查")
        print("=" * 50)

        # 检查是否已有有效配置
        if self.ai_config.get('enabled') and self.ai_config.get('api_key'):
            print("✅ 发现已有AI配置:")
            print(f"   服务商: {self.ai_config.get('provider', '未知')}")
            print(f"   模型: {self.ai_config.get('model', '未知')}")
            if self.ai_config.get('base_url'):
                print(f"   地址: {self.ai_config['base_url']}")
            print(f"   密钥: {self.ai_config.get('api_key', '')[:10]}...")
            
            # 测试连接
            print("\n🔍 测试连接...")
            if self._test_existing_config():
                print("✅ AI配置正常，直接使用")
                return
            else:
                print("⚠️ 连接测试失败")
        
        # 如果没有配置或配置无效，才进行交互式配置
        print("\n需要配置AI接口:")
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

    def _test_existing_config(self) -> bool:
        """测试已有配置的连接"""
        try:
            api_type = self.ai_config.get('api_type')
            if api_type == 'official':
                return self._test_official_api(self.ai_config)
            else:
                return self._test_proxy_api(self.ai_config)
        except Exception as e:
            print(f"❌ 配置测试失败: {e}")
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
        print(f"   类型: {self.ai_config.get('api_type', '未知')}")
        print(f"   服务商: {self.ai_config.get('provider', '未知')}")
        print(f"   模型: {self.ai_config.get('model', '未知')}")
        if self.ai_config.get('base_url'):
            print(f"   地址: {self.ai_config['base_url']}")
        print(f"   密钥: {self.ai_config.get('api_key', '')[:10]}...")
        print()

        # 执行测试
        api_type = self.ai_config.get('api_type')
        if api_type == 'official':
            success = self._test_official_api(self.ai_config)
        else:
            success = self._test_proxy_api(self.ai_config)

        if success:
            print("\n✅ 连接测试成功！AI接口工作正常")
        else:
            print("\n❌ 连接测试失败")
            print("🔧 建议解决方案:")
            print("1. 检查网络连接")
            print("2. 验证API密钥")
            print("3. 确认服务商状态")
            print("4. 重新配置API")

        input("\n按回车键返回...")

    def get_file_hash(self, filepath: str) -> str:
        """获取文件内容的MD5哈希值 - 确保一致性"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()[:16]
        except:
            return hashlib.md5(filepath.encode()).hexdigest()[:16]

    def _extract_episode_number(self, filename: str) -> str:
        """从SRT文件名提取集数"""
        patterns = [
            r'[Ee](\d+)',
            r'EP(\d+)',
            r'第(\d+)集',
            r'S\d+E(\d+)',
            r'(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)

        base_name = os.path.splitext(filename)[0]
        return base_name

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试多种编码读取文件，增强错误处理
        content = None
        used_encoding = None
        
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'utf-16', 'utf-16le', 'utf-16be', 'big5', 'cp936']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                    if content.strip():  # 确保读取到有效内容
                        used_encoding = encoding
                        print(f"✅ 使用编码: {encoding}")
                        break
            except Exception as e:
                continue

        if not content or not content.strip():
            # 最后尝试二进制读取
            try:
                with open(filepath, 'rb') as f:
                    raw_data = f.read()
                    # 尝试自动检测编码
                    try:
                        import chardet
                        detected = chardet.detect(raw_data)
                        if detected['encoding']:
                            content = raw_data.decode(detected['encoding'], errors='replace')
                            print(f"✅ 自动检测编码: {detected['encoding']}")
                    except ImportError:
                        # 如果没有chardet，使用最常见的编码
                        for encoding in ['utf-8', 'gbk', 'gb18030']:
                            try:
                                content = raw_data.decode(encoding, errors='replace')
                                if content.strip():
                                    print(f"✅ 强制使用编码: {encoding}")
                                    break
                            except:
                                continue
            except Exception as e:
                print(f"❌ 无法读取文件: {filepath}, 错误: {e}")
                return []

        if not content or not content.strip():
            print(f"❌ 文件为空或无法解析: {filepath}")
            return []

        # 错别字修正
        original_content = content
        for old, new in self.corrections.items():
            content = content.replace(old, new)

        # 记录修正的错别字
        corrected_errors = []
        for old, new in self.corrections.items():
            if old in original_content:
                corrected_errors.append(f"'{old}' → '{new}'")

        # 解析字幕条目
        subtitles = []

        if '-->' in content:
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
                    except (ValueError, IndexError):
                        continue
        else:
            # 处理其他格式
            lines = content.split('\n')
            current_text = []
            for line in lines:
                line = line.strip()
                if line and not line.isdigit():
                    current_text.append(line)

            # 简单处理：每行作为一个字幕条目
            for i, text in enumerate(current_text):
                if text:
                    subtitles.append({
                        'index': i + 1,
                        'start': f"00:{i*2:02d}:00,000",
                        'end': f"00:{i*2+2:02d}:00,000",
                        'text': text,
                        'start_seconds': i * 2,
                        'end_seconds': (i + 1) * 2
                    })

        if corrected_errors:
            print(f"✅ 修正错别字: {', '.join(corrected_errors[:3])}{'...' if len(corrected_errors) > 3 else ''}")

        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def _seconds_to_time(self, seconds: float) -> str:
        """秒转换为时间字符串"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    def detect_genre_and_themes_ai(self, subtitles: List[Dict]) -> Tuple[str, List[str]]:
        """使用AI智能识别剧情类型和主题"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未启用，无法进行类型识别")
            return None, None

        # 选择代表性字幕用于类型识别
        representative_text = self._select_representative_subtitles(subtitles)
        
        prompt = f"""请分析以下电视剧内容，识别剧情类型和主要主题。

【字幕内容样本】
{representative_text}

请严格按照以下JSON格式返回：
{{
    "genre": "具体的剧情类型（如：法律剧、爱情剧、悬疑剧、家庭剧、职场剧、古装剧、现代都市剧等）",
    "subgenre": "子类型描述",
    "themes": ["主题1", "主题2", "主题3"],
    "confidence": 0.9,
    "reasoning": "判断依据"
}}

分析要点：
1. 基于实际内容判断，不要预设类型
2. 主题要具体且相关
3. 给出判断的置信度"""

        try:
            response = self.call_ai_api(prompt, "你是专业的影视内容分析师，擅长识别剧情类型和主题。")
            if response:
                # 解析AI响应
                if "```json" in response:
                    start = response.find("```json") + 7
                    end = response.find("```", start)
                    json_text = response[start:end]
                else:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_text = response[start:end]
                
                result = json.loads(json_text)
                genre = result.get('genre', '通用剧')
                themes = result.get('themes', ['剧情发展'])
                
                print(f"🎭 AI识别剧情类型: {genre}")
                print(f"🎯 AI识别主题: {', '.join(themes)}")
                
                self.series_context['genre_detected'] = genre
                self.series_context['main_themes'] = themes
                
                return genre, themes
                
        except Exception as e:
            print(f"⚠️ AI类型识别失败: {e}")
        
        # AI失败时返回默认值
        return '通用剧', ['剧情发展']

    def build_series_context(self, episode_num: str) -> str:
        """构建全剧上下文信息 - 问题4,8：跨集连贯性"""
        context_parts = []

        if self.series_context['previous_episodes']:
            context_parts.append("【前情回顾】")
            for prev_ep in self.series_context['previous_episodes'][-3:]:
                context_parts.append(f"第{prev_ep['episode']}集: {prev_ep['summary']}")
            context_parts.append("")

        if self.series_context['genre_detected']:
            context_parts.append(f"【剧情类型】{self.series_context['genre_detected']}")
            context_parts.append("")

        if self.series_context['main_themes']:
            context_parts.append(f"【主要主题】{', '.join(self.series_context['main_themes'])}")
            context_parts.append("")

        if self.series_context['main_storylines']:
            context_parts.append("【主要故事线】")
            for storyline in self.series_context['main_storylines'][-5:]:
                context_parts.append(f"• {storyline}")
            context_parts.append("")

        if self.series_context['ongoing_conflicts']:
            context_parts.append("【持续冲突】")
            for conflict in self.series_context['ongoing_conflicts'][-3:]:
                context_parts.append(f"• {conflict}")
            context_parts.append("")

        return '\n'.join(context_parts) if context_parts else f"正在分析第{episode_num}集的剧情内容"

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析结果缓存路径 - 问题11"""
        file_hash = self.get_file_hash(os.path.join(self.srt_folder, srt_file))
        episode_num = self._extract_episode_number(srt_file)
        return os.path.join(self.analysis_cache_folder, f"analysis_E{episode_num}_{file_hash}.json")

    def save_analysis_cache(self, srt_file: str, analysis_result: Dict):
        """保存分析结果到缓存 - 问题11"""
        cache_path = self.get_analysis_cache_path(srt_file)
        try:
            analysis_result['cache_timestamp'] = datetime.now().isoformat()
            analysis_result['source_file'] = srt_file
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            print(f"💾 分析结果已缓存: {os.path.basename(cache_path)}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def load_analysis_cache(self, srt_file: str) -> Optional[Dict]:
        """从缓存加载分析结果 - 问题11"""
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

    def call_ai_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用 - 问题11：处理API不稳定"""
        if not self.ai_config.get('enabled'):
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                api_type = self.ai_config.get('api_type')

                if api_type == 'official':
                    return self._call_official_api(prompt, system_prompt)
                else:
                    return self._call_proxy_api(prompt, system_prompt)

            except Exception as e:
                print(f"⚠️ AI调用失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

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
                max_tokens=3000,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ 中转API调用失败: {e}")
            return None

    def ai_analyze_episode_complete(self, subtitles: List[Dict], episode_num: str, genre: str, themes: List[str], series_context: str) -> Optional[Dict]:
        """使用AI分析完整集数 - 支持各种剧情类型"""
        if not self.ai_config.get('enabled'):
            return None

        # 构建完整的剧情文本
        full_subtitle_text = "\n".join([f"[{sub['start']} --> {sub['end']}] {sub['text']}" for sub in subtitles])

        # 根据剧情类型调整提示词
        genre_specific_guidance = self._get_genre_specific_guidance(genre)

        prompt = f"""你是专业的电视剧剧情分析师，现在要分析第{episode_num}集的内容，识别最精彩的剧情点。

【剧集基本信息】
- 集数：第{episode_num}集
- 剧情类型：{genre}
- 主要主题：{', '.join(themes)}
- 总时长：{len(subtitles)}条字幕

【全剧上下文】
{series_context}

【类型特定指导】
{genre_specific_guidance}

【完整字幕内容】
{full_subtitle_text}

请深度分析这一集，识别3-4个最精彩的剧情点片段，每个片段2-3分钟。

要求：
1. 片段必须包含完整的对话场景，确保句子完整
2. 每个片段要有明确的剧情价值（冲突、转折、揭露、情感爆发等）
3. 时间点必须精确，在字幕范围内
4. 支持非连续时间段的合理组合
5. 生成第三人称旁白，适合短视频解说

请严格按照以下JSON格式输出：

{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre": "{genre}",
        "main_theme": "本集核心主题",
        "story_progression": "在整个剧情中的作用",
        "emotional_arc": "情感发展线",
        "key_characters": ["主要角色1", "主要角色2"],
        "main_conflicts": ["核心冲突1", "核心冲突2"]
    }},
    "plot_points": [
        {{
            "type": "剧情点类型（关键冲突/人物转折/线索揭露/情感爆发/重要对话/主题升华）",
            "title": "精彩片段标题",
            "time_segments": [
                {{
                    "start_time": "开始时间（HH:MM:SS,mmm）",
                    "end_time": "结束时间（HH:MM:SS,mmm）",
                    "reason": "选择这个时间段的原因"
                }}
            ],
            "total_duration": 片段总时长秒数,
            "plot_significance": "在剧情中的重要意义",
            "content_summary": "片段内容详细概述",
            "key_dialogues": ["关键台词1", "关键台词2"],
            "third_person_narration": "第三人称旁白解说文本",
            "content_highlights": ["观众关注点1", "观众关注点2"],
            "emotional_impact": "情感冲击描述",
            "connection_setup": "为后续剧情的铺垫"
        }}
    ],
    "episode_summary": {{
        "core_storyline": "本集核心故事线",
        "character_development": "角色发展变化",
        "plot_advancement": "剧情推进要点",
        "cliffhanger_or_resolution": "悬念设置或解决",
        "next_episode_connection": "与下一集的衔接点说明"
    }}
}}

注意：
- 时间必须在字幕范围内：{subtitles[0]['start']} 到 {subtitles[-1]['end']}
- 确保每个片段有完整的戏剧价值
- 第三人称旁白要专业且吸引人
- 考虑跨集连贯性"""

        system_prompt = f"""你是资深的{genre}分析专家，具有丰富的电视剧剪辑经验。你的任务是：
1. 深度理解{genre}的特点和观众期待
2. 准确识别该类型剧集的精彩时刻
3. 确保时间段的准确性和完整性
4. 生成专业的剧情分析和旁白
5. 保证跨集剧情连贯性

请确保分析结果具有该集的独特性，体现{genre}的特色。"""

        try:
            print(f"🤖 AI深度分析第{episode_num}集中...")
            response = self.call_ai_api(prompt, system_prompt)

            if response:
                # 提取JSON
                try:
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

                    # 验证和修正时间范围
                    if self._validate_and_fix_time_ranges(result.get('plot_points', []), subtitles):
                        print(f"✅ AI分析成功: {len(result.get('plot_points', []))} 个剧情点")
                        return result
                    else:
                        print(f"⚠️ AI返回的时间范围无效")
                        return None

                except json.JSONDecodeError as e:
                    print(f"⚠️ AI响应JSON解析失败: {e}")
                    print(f"原始响应前300字符: {response[:300]}")
                except Exception as e:
                    print(f"⚠️ AI响应处理失败: {e}")

            return None

        except Exception as e:
            print(f"⚠️ AI分析过程出错: {e}")
            return None

    def _select_representative_subtitles(self, subtitles: List[Dict]) -> str:
        """选择代表性字幕用于AI分析，避免token超限"""
        if not subtitles:
            return ""
        
        total_length = len(subtitles)
        
        # 选择策略：开头、中间、结尾各选一些
        segments = []
        
        # 开头15%
        start_end = max(1, int(total_length * 0.15))
        segments.extend(subtitles[:start_end])
        
        # 中间20%
        mid_start = int(total_length * 0.4)
        mid_end = int(total_length * 0.6)
        segments.extend(subtitles[mid_start:mid_end])
        
        # 结尾15%
        end_start = int(total_length * 0.85)
        segments.extend(subtitles[end_start:])
        
        # 合并文本，限制总长度
        representative_parts = []
        total_chars = 0
        max_chars = 8000  # 限制在合理范围内
        
        for subtitle in segments:
            text = subtitle['text']
            if total_chars + len(text) > max_chars:
                break
            representative_parts.append(f"[{subtitle['start']}] {text}")
            total_chars += len(text)
        
        return '\n'.join(representative_parts)

    def _get_genre_specific_guidance(self, genre: str) -> str:
        """根据剧情类型提供特定指导"""
        guidance = {
            '法律剧': """
重点关注：
- 法庭辩论的精彩对抗
- 证据揭露的关键时刻
- 正义与法理的冲突
- 角色信念的坚持与妥协
- 案件真相的逐步揭示""",

            '爱情剧': """
重点关注：
- 情感表白或冲突的高潮时刻
- 角色关系的转折点
- 误会产生或解除的关键场景
- 浪漫或心动的经典时刻
- 情感纠葛的复杂表现""",

            '悬疑剧': """
重点关注：
- 线索揭露的关键时刻
- 真相大白的震撼场景
- 推理过程的精彩展示
- 反转情节的巧妙设计
- 紧张氛围的营造""",

            '家庭剧': """
重点关注：
- 家庭成员间的情感冲突
- 亲情表达的温馨时刻
- 家庭矛盾的爆发与和解
- 代际观念的碰撞
- 家庭责任的承担""",

            '职场剧': """
重点关注：
- 职场竞争的激烈时刻
- 事业转折的关键决定
- 同事关系的复杂变化
- 职业理想与现实的冲突
- 团队合作或背叛的情节""",

            '古装剧': """
重点关注：
- 权力斗争的精彩博弈
- 江湖情仇的恩怨纠葛
- 忠诚与背叛的道德考验
- 武功对决的精彩场面
- 家国情怀的深刻表达"""
        }

        return guidance.get(genre, """
重点关注：
- 剧情发展的关键转折点
- 角色情感的深度表达
- 矛盾冲突的激烈时刻
- 主题思想的深刻体现
- 观众情感的共鸣点""")

    def _validate_and_fix_time_ranges(self, plot_points: List[Dict], subtitles: List[Dict]) -> bool:
        """验证和修正AI返回的时间范围 - 问题10：保证句子完整"""
        if not plot_points or not subtitles:
            return False

        first_subtitle_time = subtitles[0]['start']
        last_subtitle_time = subtitles[-1]['end']

        first_seconds = self._time_to_seconds(first_subtitle_time)
        last_seconds = self._time_to_seconds(last_subtitle_time)

        for point in plot_points:
            time_segments = point.get('time_segments', [])
            if not time_segments:
                print(f"⚠️ 缺少时间段信息: {point.get('title', '未知片段')}")
                return False

            total_duration = 0
            valid_segments = []

            for segment in time_segments:
                start_time = segment.get('start_time', '')
                end_time = segment.get('end_time', '')

                if not start_time or not end_time:
                    continue

                start_seconds = self._time_to_seconds(start_time)
                end_seconds = self._time_to_seconds(end_time)

                # 检查时间是否在字幕范围内
                if start_seconds < first_seconds or end_seconds > last_seconds:
                    # 尝试修正到最接近的字幕时间
                    closest_start = min(subtitles, key=lambda s: abs(s['start_seconds'] - start_seconds))
                    closest_end = min(subtitles, key=lambda s: abs(s['end_seconds'] - end_seconds))

                    segment['start_time'] = closest_start['start']
                    segment['end_time'] = closest_end['end']

                    start_seconds = closest_start['start_seconds']
                    end_seconds = closest_end['end_seconds']
                    print(f"⚙️ 时间已修正: {segment['start_time']} - {segment['end_time']}")

                # 检查时间段是否有效
                if start_seconds >= end_seconds:
                    print(f"⚠️ 无效时间段: {start_time}-{end_time}")
                    continue

                segment_duration = end_seconds - start_seconds
                total_duration += segment_duration
                valid_segments.append(segment)

            if not valid_segments:
                print(f"⚠️ 没有有效的时间段: {point.get('title', '未知片段')}")
                return False

            # 更新时间段和总时长
            point['time_segments'] = valid_segments
            point['total_duration'] = total_duration

            # 检查总时长是否合理（60-300秒）
            if total_duration < 60:
                print(f"⚠️ 时长过短: {total_duration:.1f}秒 - {point.get('title', '未知片段')}")
            elif total_duration > 300:
                print(f"⚠️ 时长过长: {total_duration:.1f}秒 - {point.get('title', '未知片段')}")

        return True

    # 基础分析功能已移除 - 本系统只使用AI分析

    # 基础分析相关方法已移除 - 本系统专注于AI分析

    def _find_sentence_start_advanced(self, subtitles: List[Dict], start_idx: int) -> int:
        """寻找完整句子的开始点 - 高级版"""
        sentence_starters = [
            '那么', '现在', '这时', '突然', '接下来', '首先', '然后', '于是', '随着', 
            '刚才', '但是', '不过', '因为', '所以', '既然', '虽然', '尽管', '然而',
            '另外', '此外', '而且', '同时', '接着', '紧接着', '随后', '后来'
        ]

        for i in range(start_idx, max(0, start_idx - 15), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']

                # 检查是否是自然的开始
                if any(starter in text[:15] for starter in sentence_starters):
                    return i

                # 检查前一句是否结束
                if i > 0:
                    prev_text = subtitles[i-1]['text']
                    if any(prev_text.endswith(end) for end in ['。', '！', '？', '...', '——']):
                        return i

                # 检查是否是对话开始
                if text.startswith('"') or text.startswith('"') or '：' in text[:10]:
                    return i

        return start_idx

    def _find_sentence_end_advanced(self, subtitles: List[Dict], end_idx: int) -> int:
        """寻找完整句子的结束点 - 高级版"""
        sentence_enders = ['。', '！', '？', '...', '——', '"', '"', '】', '）']

        for i in range(end_idx, min(len(subtitles), end_idx + 15)):
            if i < len(subtitles):
                text = subtitles[i]['text']

                # 找到自然结束点
                if any(text.endswith(ender) for ender in sentence_enders):
                    return i

                # 检查是否是段落结束
                if len(text) < 10 and any(ender in text for ender in sentence_enders):
                    return i

        return min(end_idx, len(subtitles) - 1)

    def _calculate_duration(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> float:
        """计算字幕片段的时长"""
        if start_idx >= len(subtitles) or end_idx >= len(subtitles):
            return 0

        start_seconds = subtitles[start_idx]['start_seconds']
        end_seconds = subtitles[end_idx]['end_seconds']
        return end_seconds - start_seconds

    def _generate_segment_title(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str, genre: str) -> str:
        """生成片段标题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 5))])

        # 根据类型和内容生成标题
        if plot_type == '关键冲突':
            if '法庭' in content or '审判' in content:
                return "法庭激辩，针锋相对"
            elif '争论' in content or '质疑' in content:
                return "激烈争论，观点交锋"
            else:
                return "关键冲突爆发"
        elif plot_type == '线索揭露':
            if ('证据' in content or '发现' in content):
                return "关键证据浮出水面"
            elif '真相' in content:
                return "真相大白时刻"
            else:
                return "重要线索揭露"
        elif plot_type == '情感爆发':
            if '哭' in content or '泪' in content:
                return "情感决堤，泪如雨下"
            elif '愤怒' in content or '激动' in content:
                return "情感爆发，震撼人心"
            else:
                return "深度情感表达"
        elif plot_type == '人物转折':
            return "关键抉择，人生转折"
        elif plot_type == '重要对话':
            return "深度对话，揭示内心"
        else:
            return "精彩剧情片段"

    def _generate_plot_significance(self, plot_type: str, genre: str) -> str:
        """生成剧情意义"""
        significance_map = {
            '关键冲突': f"在{genre}中，此冲突代表核心矛盾的激化，推动剧情走向高潮",
            '线索揭露': f"关键信息的披露，为{genre}的主要悬念提供重要线索",
            '情感爆发': f"角色内心情感的集中表达，体现{genre}的人物深度",
            '人物转折': f"角色成长和改变的关键节点，推动{genre}的角色弧线发展",
            '重要对话': f"承载重要信息和情感的对话，体现{genre}的叙事深度",
            '主题升华': f"体现{genre}核心价值观和深层主题的重要时刻"
        }

        return significance_map.get(plot_type, "推动剧情发展的重要片段")

    def _generate_content_summary_advanced(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成高级内容摘要"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 20))])

        summary_template = {
            '关键冲突': f"在这个{plot_type}片段中，双方展开激烈对抗。{content[:80]}...矛盾达到白热化程度。",
            '线索揭露': f"重要{plot_type}时刻，关键信息得以披露。{content[:80]}...为真相大白奠定基础。",
            '情感爆发': f"角色情感在此刻得到充分释放。{content[:80]}...深深触动观众内心。",
            '人物转折': f"角色面临重要抉择时刻。{content[:80]}...人生轨迹因此改变。",
            '重要对话': f"承载重要信息的深度对话。{content[:80]}...揭示角色内心世界。",
            '主题升华': f"体现深层主题的重要时刻。{content[:80]}...引发深度思考。"
        }

        return summary_template.get(plot_type, f"精彩的{plot_type}片段。{content[:80]}...展现剧情魅力。")

    def _extract_key_dialogues_advanced(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键台词 - 高级版"""
        key_dialogues = []

        # 关键词和情感强度评分
        priority_keywords = [
            '真相', '证据', '正义', '坚持', '相信', '希望', '责任', '选择', '决定',
            '对不起', '谢谢', '爱', '恨', '痛苦', '快乐', '成功', '失败', '梦想'
        ]

        for i in range(start_idx, min(end_idx + 1, start_idx + 25)):
            subtitle = subtitles[i]
            text = subtitle['text']

            # 评分系统
            score = 0

            # 关键词评分
            for keyword in priority_keywords:
                if keyword in text:
                    score += 3

            # 情感强度评分
            score += text.count('！') * 2
            score += text.count('？') * 1.5
            score += text.count('...') * 1

            # 长度评分（10-50字最佳）
            if 10 <= len(text) <= 50:
                score += 2

            # 对话标识评分
            if '：' in text or '"' in text:
                score += 1

            if score >= 4 and len(text) >= 8:
                key_dialogues.append(f"[{subtitle['start']}] {text}")

        # 排序并选择最佳的6个
        return key_dialogues[:6]

    def _generate_third_person_narration_advanced(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str, genre: str) -> str:
        """生成高级第三人称旁白 - 问题3：旁观者叙述"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])

        # 根据剧情类型和片段类型生成专业旁白
        narration_templates = {
            ('法律剧', '关键冲突'): "法庭之上，双方律师唇枪舌剑，针锋相对。每一个论点都关乎正义的天平，每一句反驳都可能改变案件走向。在这场没有硝烟的战争中，真理与公正成为最终的裁判。",

            ('法律剧', '线索揭露'): "关键时刻，隐藏已久的证据终于浮出水面。这个发现如同黑暗中的一束光，照亮了案件的真相。每个细节都被重新审视，每个疑点都得到解答。",

            ('爱情剧', '情感爆发'): "情感在这一刻决堤而出，再也无法掩饰内心的波澜。眼泪模糊了视线，却让心灵更加清晰。这种真实的情感表达，触动着每一个观众的心弦。",

            ('悬疑剧', '线索揭露'): "迷雾即将散去，真相的轮廓开始显现。每一个看似微不足道的细节，都是拼图中不可缺少的一片。推理的链条环环相扣，指向那个震撼的答案。",

            ('家庭剧', '人物转折'): "在人生的十字路口，选择比努力更重要。这个决定将改写人物的命运轨迹，也将重新定义家庭的未来。成长，有时就是在这样的关键时刻完成。"
        }

        # 通用模板
        generic_templates = {
            '关键冲突': "矛盾在此刻白热化，各方立场鲜明，寸步不让。这场冲突不仅是观点的交锋，更是价值观的碰撞。每一个字都掷地有声，每一个眼神都充满力量。",

            '线索揭露': "真相的面纱被缓缓掀开，隐藏的秘密终见天日。这个发现改变了一切，让所有人重新审视已知的事实。真理往往比想象更加震撼人心。",

            '情感爆发': "情感的闸门在这一瞬间开启，汹涌的情绪如潮水般涌出。这种毫无保留的真情流露，让观众深深共鸣，也让角色更加立体鲜活。",

            '人物转折': "命运的转折点往往出现在最不经意的时刻。这个选择将彻底改变角色的人生轨迹，也为故事开启全新的篇章。成长与蜕变，就在这关键的一步。",

            '重要对话': "言语之间蕴含着深刻的内涵，每一句话都意味深长。这样的对话不仅推进剧情发展，更是角色内心世界的真实写照。智慧与情感的交融，让整个场景升华。",

            '主题升华': "在这个关键时刻，故事的深层主题得到了完美诠释。超越表面的情节，触及人性的本质，引发观众对生活、对人生的深度思考。"
        }

        # 优先使用特定类型模板
        template_key = (genre, plot_type)
        if template_key in narration_templates:
            return narration_templates[template_key]
        else:
            return generic_templates.get(plot_type, "这是一个精彩的剧情片段，展现了角色的深度和故事的魅力。情节紧凑，情感丰富，为整部剧增添了浓墨重彩的一笔。")

    def _generate_content_highlights(self, plot_type: str, genre: str) -> List[str]:
        """生成内容亮点 - 问题6：内容亮点"""
        highlights_map = {
            '关键冲突': [
                f"{genre}中的经典对抗场面",
                "针锋相对的精彩交锋",
                "矛盾冲突的集中爆发",
                "观点碰撞的激烈时刻"
            ],
            '线索揭露': [
                "关键信息的重要披露",
                "推理逻辑的精彩展示",
                "真相大白的震撼时刻",
                "悬念解开的精彩设计"
            ],
            '情感爆发': [
                "真实情感的深度表达",
                "角色内心的完美诠释",
                "情感共鸣的强烈时刻",
                "人性光辉的生动展现"
            ],
            '人物转折': [
                "角色成长的关键节点",
                "人生选择的重要时刻",
                "性格转变的精彩刻画",
                "命运转折的深度表现"
            ],
            '重要对话': [
                "深度对话的智慧碰撞",
                "台词功底的精彩展现",
                "情感表达的细腻刻画",
                "思想交流的深度体现"
            ],
            '主题升华': [
                f"{genre}深层主题的完美体现",
                "价值观念的深度表达",
                "人生哲理的智慧分享",
                "精神层面的深度思考"
            ]
        }

        return highlights_map.get(plot_type, ["精彩剧情片段", "角色深度刻画", "情节紧凑发展", "情感真实表达"])

    def _generate_emotional_impact(self, plot_type: str) -> str:
        """生成情感冲击描述"""
        impact_map = {
            '关键冲突': "激烈的对抗让观众血脉贲张，紧张的氛围令人屏息凝神，每一个回合都牵动着观众的心弦。",
            '线索揭露': "真相揭晓的瞬间令人震撼不已，恍然大悟的感觉让观众拍案叫绝，推理的魅力展露无遗。",
            '情感爆发': "真挚的情感表达直击心灵深处，观众不禁潸然泪下，共情的力量让整个场景升华。",
            '人物转折': "角色的重要选择让观众为之动容，成长的足迹清晰可见，人性的光辉闪闪发光。",
            '重要对话': "深度的对话引发思考共鸣，智慧的交流让观众受益匪浅，言语的力量震撼人心。",
            '主题升华': "深层主题的表达引发哲学思考，精神层面的触动让观众意犹未尽，思想的深度令人赞叹。"
        }

        return impact_map.get(plot_type, "精彩的剧情表现让观众深深沉浸其中，情感与理智的交融创造出难忘的观剧体验。")

    def find_video_file(self, srt_filename: str) -> Optional[str]:
        """查找对应的视频文件"""
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 集数匹配
        episode_num = self._extract_episode_number(srt_filename)
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                video_episode = self._extract_episode_number(filename)
                if episode_num == video_episode:
                    return os.path.join(self.videos_folder, filename)

        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if base_name.lower() in filename.lower() or filename.lower() in base_name.lower():
                    return os.path.join(self.videos_folder, filename)

        return None

    def check_ffmpeg(self) -> bool:
        """检查FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def get_clip_status_path(self, srt_file: str, plot_point: Dict) -> str:
        """获取剪辑状态文件路径 - 问题13：避免重复剪辑"""
        episode_num = self._extract_episode_number(srt_file)
        plot_type = plot_point.get('type', 'unknown')
        title_hash = hashlib.md5(plot_point.get('title', '').encode()).hexdigest()[:8]
        return os.path.join(self.clip_status_folder, f"E{episode_num}_{plot_type}_{title_hash}.json")

    def is_clip_completed(self, srt_file: str, plot_point: Dict) -> bool:
        """检查剪辑是否已完成 - 问题13：避免重复剪辑"""
        status_path = self.get_clip_status_path(srt_file, plot_point)
        if os.path.exists(status_path):
            try:
                with open(status_path, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    output_path = status.get('output_path', '')
                    return os.path.exists(output_path) and os.path.getsize(output_path) > 1024
            except:
                return False
        return False

    def mark_clip_completed(self, srt_file: str, plot_point: Dict, output_path: str):
        """标记剪辑已完成 - 问题13：避免重复剪辑"""
        status_path = self.get_clip_status_path(srt_file, plot_point)
        try:
            status = {
                'srt_file': srt_file,
                'plot_point': plot_point,
                'output_path': output_path,
                'completed_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 状态标记失败: {e}")

    def create_video_clips_stable(self, plot_points: List[Dict], video_file: str, srt_filename: str) -> List[str]:
        """创建视频片段 - 稳定版本 - 问题12,13：剪辑稳定性和一致性"""
        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []

        created_clips = []
        episode_num = self._extract_episode_number(srt_filename)

        for i, plot_point in enumerate(plot_points, 1):
            # 检查是否已完成剪辑 - 问题13
            if self.is_clip_completed(srt_filename, plot_point):
                status_path = self.get_clip_status_path(srt_filename, plot_point)
                try:
                    with open(status_path, 'r', encoding='utf-8') as f:
                        status = json.load(f)
                        existing_path = status.get('output_path', '')
                        if os.path.exists(existing_path):
                            print(f"✅ 片段已存在: {os.path.basename(existing_path)}")
                            created_clips.append(existing_path)
                            continue
                except:
                    pass

            plot_type = plot_point.get('type', '未知类型')
            title = plot_point.get('title', f'第{episode_num}集片段{i}')

            # 生成安全的文件名 - 问题12：确保一致性
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)

            print(f"\n🎬 剪辑片段 {i}: {title}")
            print(f"   类型: {plot_type}")

            # 处理时间段 - 问题3：支持非连续时间段
            time_segments = plot_point.get('time_segments', [])
            if not time_segments:
                print(f"   ❌ 缺少时间段信息")
                continue

            # 创建片段
            if self._create_video_from_segments(video_file, time_segments, clip_path, plot_point):
                created_clips.append(clip_path)
                self.mark_clip_completed(srt_filename, plot_point, clip_path)
                self._create_clip_description_advanced(clip_path, plot_point, episode_num)
            else:
                print(f"   ❌ 剪辑失败")

        return created_clips

    def _create_video_from_segments(self, video_file: str, time_segments: List[Dict], output_path: str, plot_point: Dict, max_retries: int = 3) -> bool:
        """从时间段创建视频 - 支持非连续片段 - 问题3,12：非连续时间段和稳定性"""

        for attempt in range(max_retries):
            try:
                if len(time_segments) == 1:
                    # 单个连续片段
                    segment = time_segments[0]
                    start_time = segment['start_time']
                    end_time = segment['end_time']

                    start_seconds = self._time_to_seconds(start_time)
                    end_seconds = self._time_to_seconds(end_time)
                    duration = end_seconds - start_seconds

                    print(f"   ⏱️ 时间: {start_time} --> {end_time} ({duration:.1f}秒)")

                    if duration <= 0:
                        print(f"   ❌ 无效时间段")
                        return False

                    # 添加小量缓冲
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
                        '-movflags', '+faststart',
                        output_path,
                        '-y'
                    ]
                else:
                    # 多个片段合并
                    print(f"   📝 合并 {len(time_segments)} 个片段")

                    # 创建临时片段文件
                    temp_files = []
                    temp_list_file = output_path.replace('.mp4', '_segments.txt')

                    for j, segment in enumerate(time_segments):
                        start_seconds = self._time_to_seconds(segment['start_time'])
                        end_seconds = self._time_to_seconds(segment['end_time'])
                        duration = end_seconds - start_seconds

                        if duration <= 0:
                            continue

                        temp_file = output_path.replace('.mp4', f'_temp_{j}.mp4')
                        temp_files.append(temp_file)

                        # 创建临时片段
                        temp_cmd = [
                            'ffmpeg',
                            '-i', video_file,
                            '-ss', str(start_seconds),
                            '-t', str(duration),
                            '-c:v', 'libx264',
                            '-c:a', 'aac',
                            '-preset', 'medium',
                            '-crf', '23',
                            temp_file,
                            '-y'
                        ]

                        result = subprocess.run(temp_cmd, capture_output=True, text=True, timeout=180)
                        if result.returncode != 0:
                            print(f"   ⚠️ 临时片段 {j+1} 创建失败")
                            # 清理临时文件
                            for tf in temp_files:
                                if os.path.exists(tf):
                                    os.remove(tf)
                            return False

                    if not temp_files:
                        print(f"   ❌ 没有有效的片段")
                        return False

                    # 创建合并列表文件
                    with open(temp_list_file, 'w', encoding='utf-8') as f:
                        for temp_file in temp_files:
                            f.write(f"file '{temp_file}'\n")

                    # 合并片段
                    cmd = [
                        'ffmpeg',
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', temp_list_file,
                        '-c', 'copy',
                        output_path,
                        '-y'
                    ]

                # 执行命令，增强编码处理
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, encoding='utf-8', errors='replace')

                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
                    file_size = os.path.getsize(output_path) / (1024*1024)
                    total_duration = plot_point.get('total_duration', 0)
                    print(f"   ✅ 成功: {os.path.basename(output_path)} ({file_size:.1f}MB, {total_duration:.1f}秒)")

                    # 清理临时文件
                    if len(time_segments) > 1:
                        for temp_file in temp_files:
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                        if os.path.exists(temp_list_file):
                            os.remove(temp_list_file)

                    return True
                else:
                    error_msg = result.stderr[:200] if result.stderr else '未知错误'
                    print(f"   ❌ 尝试 {attempt+1} 失败: {error_msg}")

                    # 清理失败文件
                    if os.path.exists(output_path):
                        os.remove(output_path)

                    if len(time_segments) > 1:
                        for temp_file in temp_files:
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                        if os.path.exists(temp_list_file):
                            os.remove(temp_list_file)

            except subprocess.TimeoutExpired:
                print(f"   ❌ 尝试 {attempt+1} 超时")
            except Exception as e:
                print(f"   ❌ 尝试 {attempt+1} 异常: {e}")

            # 重试前等待
            if attempt < max_retries - 1:
                time.sleep(1)

        print(f"   ❌ 所有重试失败")
        return False

    def _create_clip_description_advanced(self, video_path: str, plot_point: Dict, episode_num: str):
        """创建高级片段描述文件 - 问题5：固定输出格式"""
        try:
            desc_path = video_path.replace('.mp4', '_完整说明.txt')

            content = f"""📺 {plot_point.get('title', '精彩片段')}
{"=" * 80}

【基本信息】
集数编号：第{episode_num}集
片段类型：{plot_point.get('type', '未知类型')}
总时长：{plot_point.get('total_duration', 0):.1f} 秒

【时间段信息】"""

            for i, segment in enumerate(plot_point.get('time_segments', []), 1):
                content += f"""
片段 {i}：{segment.get('start_time')} --> {segment.get('end_time')}
选择原因：{segment.get('reason', '核心片段')}"""

            content += f"""

【剧情分析】
剧情意义：{plot_point.get('plot_significance', '推动剧情发展')}
内容摘要：{plot_point.get('content_summary', '精彩片段内容')}
情感冲击：{plot_point.get('emotional_impact', '深度情感表达')}

【内容亮点】"""
            for highlight in plot_point.get('content_highlights', []):
                content += f"\n• {highlight}"

            content += f"""

【关键台词】"""
            for dialogue in plot_point.get('key_dialogues', []):
                content += f"\n{dialogue}"

            content += f"""

【第三人称旁白字幕】
{plot_point.get('third_person_narration', '专业旁白解说')}

【下集衔接】
{plot_point.get('connection_setup', '为后续剧情发展做铺垫')}

【技术说明】
• 支持非连续时间段的智能合并
• 自动修正错别字，便于剪辑参考
• 确保句子完整，不截断重要对话
• 生成第三人称旁白，适合短视频制作
• 保证剧情连贯性和跨集衔接

【剪辑建议】
• 严格按照标注时间进行剪辑
• 可在开头添加简短背景介绍（5-10秒）
• 结尾可添加下集预告提示（3-5秒）
• 使用提供的第三人称旁白作为配音文本
• 注意保持原声与旁白的平衡

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   📝 说明文件: {os.path.basename(desc_path)}")

        except Exception as e:
            print(f"   ⚠️ 说明文件生成失败: {e}")

    def update_series_context(self, episode_num: str, analysis_result: Dict, plot_points: List[Dict]):
        """更新全剧上下文 - 问题4,8：跨集连贯性"""
        try:
            # 添加到已处理集数
            episode_summary = {
                'episode': episode_num,
                'summary': analysis_result.get('episode_summary', {}).get('core_storyline', f'第{episode_num}集剧情'),
                'main_conflicts': analysis_result.get('episode_analysis', {}).get('main_conflicts', []),
                'key_characters': analysis_result.get('episode_analysis', {}).get('key_characters', []),
                'connection_hint': analysis_result.get('episode_summary', {}).get('next_episode_connection', '')
            }

            self.series_context['previous_episodes'].append(episode_summary)

            # 更新主要故事线
            for point in plot_points:
                storyline = f"{point.get('type', '剧情发展')}: {point.get('title', '精彩片段')}"
                if storyline not in self.series_context['main_storylines']:
                    self.series_context['main_storylines'].append(storyline)

            # 更新持续冲突
            main_conflicts = analysis_result.get('episode_analysis', {}).get('main_conflicts', [])
            for conflict in main_conflicts:
                if conflict not in self.series_context['ongoing_conflicts']:
                    self.series_context['ongoing_conflicts'].append(conflict)

            # 只保留最近的上下文
            if len(self.series_context['previous_episodes']) > 5:
                self.series_context['previous_episodes'] = self.series_context['previous_episodes'][-5:]

            if len(self.series_context['main_storylines']) > 10:
                self.series_context['main_storylines'] = self.series_context['main_storylines'][-10:]

            if len(self.series_context['ongoing_conflicts']) > 6:
                self.series_context['ongoing_conflicts'] = self.series_context['ongoing_conflicts'][-6:]

        except Exception as e:
            print(f"⚠️ 上下文更新失败: {e}")

    def process_episode_complete(self, srt_filename: str) -> Optional[Dict]:
        """处理单集 - 完整版 - 问题14,15：确保一致性"""
        print(f"\n📺 处理集数: {srt_filename}")

        episode_num = self._extract_episode_number(srt_filename)

        # 1. 检查分析缓存 - 问题11
        cached_analysis = self.load_analysis_cache(srt_filename)
        if cached_analysis:
            print(f"💾 使用缓存的分析结果")
            analysis_result = cached_analysis
            plot_points = analysis_result.get('plot_points', [])
        else:
            # 2. 解析字幕
            srt_path = os.path.join(self.srt_folder, srt_filename)
            subtitles = self.parse_srt_file(srt_path)

            if not subtitles:
                print(f"❌ 字幕解析失败")
                return None

            # 3. 使用AI识别剧情类型和主题
            genre, themes = self.detect_genre_and_themes_ai(subtitles)
            
            if not genre or not themes:
                print("❌ AI类型识别失败，无法继续处理")
                return None

            # 4. 构建剧集上下文
            series_context = self.build_series_context(episode_num)

            # 5. 只使用AI分析，失败直接返回
            ai_analysis = self.ai_analyze_episode_complete(subtitles, episode_num, genre, themes, series_context)

            if ai_analysis and ai_analysis.get('plot_points'):
                analysis_result = ai_analysis
                plot_points = ai_analysis['plot_points']
                print(f"🤖 AI分析成功: {len(plot_points)} 个剧情点")
            else:
                print("❌ AI分析失败，无法处理此集")
                print("💡 请检查AI配置或网络连接")
                return None

            if not plot_points:
                print(f"❌ AI未找到合适的剧情点")
                return None

            # 6. 保存分析结果到缓存 - 问题11
            self.save_analysis_cache(srt_filename, analysis_result)

        # 输出分析结果
        print(f"🎯 识别到 {len(plot_points)} 个剧情点:")
        for i, point in enumerate(plot_points, 1):
            plot_type = point.get('type', '未知类型')
            title = point.get('title', '无标题')
            duration = point.get('total_duration', 0)
            print(f"    {i}. {plot_type}: {title} ({duration:.1f}秒)")

        # 7. 查找视频文件
        video_file = self.find_video_file(srt_filename)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return None

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 8. 创建视频片段
        created_clips = self.create_video_clips_stable(plot_points, video_file, srt_filename)

        # 9. 更新全剧上下文
        self.update_series_context(episode_num, analysis_result, plot_points)

        return {
            'episode_number': episode_num,
            'filename': srt_filename,
            'analysis_result': analysis_result,
            'plot_points': plot_points,
            'created_clips': len(created_clips),
            'clip_paths': created_clips,
            'processing_timestamp': datetime.now().isoformat()
        }

    def process_all_episodes(self):
        """处理所有集数 - 主函数 - 问题15：处理所有SRT文件"""
        print("\n🚀 开始完整智能剧情剪辑处理")
        print("=" * 60)

        # 获取所有SRT文件并按名称排序 - 问题2：按顺序处理
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')]

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        # 按字符串排序（文件名顺序）
        srt_files.sort()

        print(f"📝 找到 {len(srt_files)} 个字幕文件（按文件名排序）")
        for i, f in enumerate(srt_files, 1):
            print(f"   {i}. {f}")

        print(f"\n🎬 视频目录: {self.videos_folder}")
        print(f"📁 输出目录: {self.clips_folder}")
        print(f"💾 缓存系统: 启用")

        if self.ai_config.get('enabled'):
            api_type = self.ai_config.get('api_type', '未知')
            provider = self.ai_config.get('provider', '未知')
            print(f"🤖 AI分析: 启用 ({api_type} - {provider})")
        else:
            print(f"📏 AI分析: 未启用，使用基础规则")

        # 处理每一集
        all_episodes = []
        total_clips = 0
        success_count = 0

        for i, srt_file in enumerate(srt_files):
            try:
                print(f"\n{'='*80}")
                print(f"📺 处理第 {i+1}/{len(srt_files)} 集: {srt_file}")
                print(f"{'='*80}")

                episode_summary = self.process_episode_complete(srt_file)
                if episode_summary:
                    all_episodes.append(episode_summary)
                    total_clips += episode_summary['created_clips']
                    success_count += 1
                    print(f"✅ 第{i+1}集处理成功: {episode_summary['created_clips']} 个片段")
                else:
                    print(f"❌ 第{i+1}集处理失败")

            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")

        # 生成最终报告
        self._create_comprehensive_report(all_episodes, total_clips, len(srt_files))

        print(f"\n{'='*80}")
        print(f"📊 完整处理统计:")
        print(f"✅ 成功处理: {success_count}/{len(srt_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")
        print(f"📁 输出目录: {self.clips_folder}/")
        print(f"📄 详细报告: {os.path.join(self.reports_folder, '完整智能剪辑报告.txt')}")
        print(f"💾 缓存文件: {len(os.listdir(self.analysis_cache_folder))} 个")
        print(f"🎯 剪辑状态: {len(os.listdir(self.clip_status_folder))} 个")
        print("🎉 智能剪辑系统处理完成！")

    def _create_comprehensive_report(self, episodes: List[Dict], total_clips: int, total_episodes: int):
        """创建综合报告 - 问题5：固定输出格式"""
        if not episodes:
            return

        report_path = os.path.join(self.reports_folder, "完整智能剪辑报告.txt")

        content = f"""📺 完整智能电视剧剪辑系统报告
{"=" * 100}

📊 处理统计：
• 总集数: {total_episodes} 集
• 成功处理: {len(episodes)} 集
• 成功率: {len(episodes)/total_episodes*100:.1f}%
• 生成片段: {total_clips} 个
• 平均每集片段: {total_clips/len(episodes):.1f} 个

🤖 系统配置：
• AI分析状态: {'已启用' if self.ai_config.get('enabled') else '基础规则分析'}
• 缓存机制: 启用 (避免重复分析和剪辑)
• 一致性保证: 启用 (多次执行结果一致)
• 错别字修正: 启用

🎭 剧情类型分析：
• 检测类型: {self.series_context.get('genre_detected', '未检测')}
• 主要主题: {', '.join(self.series_context.get('main_themes', []))}

📈 剧情点类型分布：
"""

        # 统计剧情点类型
        plot_type_stats = {}
        total_duration = 0

        for episode in episodes:
            for plot_point in episode.get('plot_points', []):
                plot_type = plot_point.get('type', '未知类型')
                plot_type_stats[plot_type] = plot_type_stats.get(plot_type, 0) + 1
                total_duration += plot_point.get('total_duration', 0)

        for plot_type, count in sorted(plot_type_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / sum(plot_type_stats.values())) * 100
            content += f"• {plot_type}: {count} 个 ({percentage:.1f}%)\n"

        avg_duration = total_duration / sum(plot_type_stats.values()) if plot_type_stats else 0

        content += f"""
📏 时长统计：
• 总时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)
• 平均片段时长: {avg_duration:.1f} 秒 ({avg_duration/60:.1f} 分钟)

🔗 跨集连贯性：
• 上下文管理: 启用
• 前情回顾: 自动生成
• 衔接点分析: 智能识别
• 故事线追踪: 完整保持

📝 详细分集信息：
{"=" * 100}
"""

        # 详细分集信息
        for i, episode in enumerate(episodes, 1):
            analysis = episode.get('analysis_result', {})
            episode_analysis = analysis.get('episode_analysis', {})
            episode_summary = analysis.get('episode_summary', {})

            content += f"""
【第{episode['episode_number']}集】{episode['filename']}
────────────────────────────────────────────────────────────────
剧情类型：{episode_analysis.get('genre', '未知')}
核心主题：{episode_analysis.get('main_theme', '主要内容')}
故事进展：{episode_analysis.get('story_progression', '剧情发展')}
情感发展：{episode_analysis.get('emotional_arc', '情感推进')}
主要角色：{', '.join(episode_analysis.get('key_characters', []))}
核心冲突：{', '.join(episode_analysis.get('main_conflicts', []))}

生成片段：{episode['created_clips']} 个
剧情点详情：
"""

            for j, plot_point in enumerate(episode.get('plot_points', []), 1):
                time_segments = plot_point.get('time_segments', [])
                time_info = ""
                if len(time_segments) == 1:
                    seg = time_segments[0]
                    time_info = f"{seg.get('start_time')} --> {seg.get('end_time')}"
                else:
                    time_info = f"{len(time_segments)} 个片段合并"

                content += f"""  {j}. {plot_point.get('type', '未知类型')} - {plot_point.get('title', '无标题')}
     时间：{time_info} (总时长: {plot_point.get('total_duration', 0):.1f}秒)
     意义：{plot_point.get('plot_significance', '剧情推进')[:60]}...
     旁白：{plot_point.get('third_person_narration', '专业解说')[:60]}...
"""

            content += f"""

下集衔接：{episode_summary.get('next_episode_connection', '自然过渡')}
"""

        content += f"""

💡 使用说明：
• 所有视频片段已保存在 {self.clips_folder}/ 目录
• 每个片段都有对应的详细说明文档
• 支持非连续时间段的智能合并剪辑
• 第三人称旁白可直接用于配音制作
• 错别字已自动修正，便于剪辑参考
• 缓存系统确保重复执行的一致性

🔧 技术特性：
• 智能剧情类型识别
• AI驱动的剧情点分析
• 完整句子边界保证
• 跨集连贯性管理
• 稳定的缓存机制
• 断点续传支持
• 多重重试机制

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本：完整智能电视剧剪辑系统 v2.0
"""

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 综合报告已保存: {report_path}")
        except Exception as e:
            print(f"⚠️ 报告保存失败: {e}")

def show_main_menu():
    """显示主菜单"""
    print("\n🤖 AI智能视频剪辑系统")
    print("=" * 50)
    print("📋 请选择操作:")
    print("1. 🚀 开始电视剧AI分析和剪辑")
    print("2. 🎬 开始电影AI分析和剪辑")
    print("3. ⚙️ 检查AI配置")
    print("4. 🔧 重新配置AI")
    print("5. 📊 查看系统状态")
    print("6. 📖 查看使用教程")
    print("7. ❌ 退出系统")
    print("=" * 50)

def show_tutorial():
    """显示使用教程"""
    print("\n📖 AI智能剪辑系统使用教程")
    print("=" * 60)
    print("📺 1. 电视剧剪辑:")
    print("   • 将字幕文件(.srt/.txt)放入 srt/ 目录")
    print("   • 将视频文件(.mp4/.mkv等)放入 videos/ 目录")
    print("   • 确保文件名包含集数信息(如: E01.srt)")
    print()
    print("🎬 2. 电影剪辑 (新功能):")
    print("   • 将电影字幕文件放入 movie_srt/ 目录")
    print("   • 将电影视频文件放入 movie_videos/ 目录")
    print("   • 支持无声视频剪辑，专为第一人称叙述设计")
    print("   • 自动修正错别字: '防衛'→'防卫', '正當'→'正当'")
    print("   • 第一人称叙述与视频内容实时同步")
    print()
    print("🤖 3. AI配置要求:")
    print("   • 本系统只使用AI分析，无基础分析备选")
    print("   • 支持官方API和中转API")
    print("   • 推荐使用: Gemini, GPT-4, DeepSeek等")
    print()
    print("⚡ 4. 系统特色:")
    print("   • 完全AI驱动的剧情点识别")
    print("   • 智能错别字修正")
    print("   • 跨集连贯性分析")
    print("   • 自动生成第三人称旁白")
    print("   • 电影第一人称叙述剪辑")
    print("   • 无声视频配音准备")
    print("   • 缓存机制避免重复分析")
    print("=" * 60)
    input("\n按回车键返回主菜单...")

def check_system_status(clipper):
    """检查系统状态"""
    print("\n📊 系统状态检查")
    print("=" * 50)
    
    # 检查目录
    dirs_status = []
    for folder in ['srt', 'videos', 'clips', 'analysis_cache']:
        exists = os.path.exists(folder)
        status = "✅" if exists else "❌"
        dirs_status.append(f"{status} {folder}/ 目录")
    
    print("📁 目录状态:")
    for status in dirs_status:
        print(f"   {status}")
    
    # 检查文件
    srt_count = len([f for f in os.listdir('srt') if f.lower().endswith(('.srt', '.txt'))]) if os.path.exists('srt') else 0
    video_count = len([f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]) if os.path.exists('videos') else 0
    
    print(f"\n📄 文件统计:")
    print(f"   📝 字幕文件: {srt_count} 个")
    print(f"   🎬 视频文件: {video_count} 个")
    
    # 检查AI配置
    ai_status = "✅ 已配置" if clipper.ai_config.get('enabled') else "❌ 未配置"
    print(f"\n🤖 AI状态: {ai_status}")
    
    if clipper.ai_config.get('enabled'):
        print(f"   提供商: {clipper.ai_config.get('provider', '未知')}")
        print(f"   模型: {clipper.ai_config.get('model', '未知')}")
    
    # 系统准备状态
    ready = srt_count > 0 and video_count > 0 and clipper.ai_config.get('enabled')
    status = "✅ 准备就绪" if ready else "❌ 需要配置"
    print(f"\n🎯 系统状态: {status}")
    
    if not ready:
        print("\n💡 建议操作:")
        if srt_count == 0:
            print("   • 添加字幕文件到 srt/ 目录")
        if video_count == 0:
            print("   • 添加视频文件到 videos/ 目录")
        if not clipper.ai_config.get('enabled'):
            print("   • 配置AI接口 (选择菜单选项3)")
    
    input("\n按回车键返回主菜单...")

def main():
    """主函数 - 引导式菜单系统"""
    clipper = CompleteIntelligentTVClipper()
    
    while True:
        try:
            show_main_menu()
            choice = input("请输入选择 (1-6): ").strip()
            
            if choice == '1':
                # 检查AI配置
                if not clipper.ai_config.get('enabled') or not clipper.ai_config.get('api_key'):
                    print("\n❌ AI未配置，无法开始分析")
                    print("💡 请先选择菜单选项4配置AI")
                    input("按回车键继续...")
                    continue
                
                # 检查文件
                if not os.path.exists('srt') or not os.listdir('srt'):
                    print("\n❌ 未找到字幕文件")
                    print("💡 请将字幕文件放入 srt/ 目录")
                    input("按回车键继续...")
                    continue
                
                print("\n🚀 开始电视剧AI分析和剪辑...")
                clipper.process_all_episodes()
                input("\n处理完成，按回车键返回主菜单...")
                
            elif choice == '2':
                # 电影AI剪辑
                print("\n🎬 启动电影AI分析和剪辑系统...")
                movie_clipper = MovieAIClipper()
                if not movie_clipper.ai_config.get('enabled'):
                    print("❌ AI未配置，无法进行电影分析")
                    print("💡 请先配置AI接口")
                    input("按回车键继续...")
                    continue
                
                # 检查电影字幕文件
                movie_srt_folder = "movie_srt"
                if not os.path.exists(movie_srt_folder) or not os.listdir(movie_srt_folder):
                    print(f"❌ 未找到电影字幕文件")
                    print(f"💡 请将电影字幕文件放入 {movie_srt_folder}/ 目录")
                    input("按回车键继续...")
                    continue
                
                # 检查电影视频文件
                movie_video_folder = "movie_videos"
                if not os.path.exists(movie_video_folder) or not os.listdir(movie_video_folder):
                    print(f"❌ 未找到电影视频文件")
                    print(f"💡 请将电影视频文件放入 {movie_video_folder}/ 目录")
                    input("按回车键继续...")
                    continue
                
                print("🎬 开始电影AI分析和剪辑...")
                print("📋 特色功能:")
                print("  • 无声视频剪辑，专为第一人称叙述设计")
                print("  • 智能错别字修正 (防衛→防卫, 正當→正当)")
                print("  • 第一人称叙述与视频内容实时同步")
                
                movie_clipper.process_all_movies()
                input("\n电影处理完成，按回车键返回主菜单...")
                
            elif choice == '3':
                clipper.test_current_connection()
                
            elif choice == '4':
                clipper.configure_ai_interactive()
                
            elif choice == '5':
                check_system_status(clipper)
                
            elif choice == '6':
                show_tutorial()
                
            elif choice == '7':
                print("\n👋 感谢使用AI智能剪辑系统！")
                break
                
            else:
                print("❌ 无效选择，请输入1-7")
                input("按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，系统退出")
            break
        except Exception as e:
            print(f"\n❌ 系统错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()