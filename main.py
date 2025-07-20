#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能电视剧剪辑系统 - 简洁版
集成所有功能，简化操作流程
"""

import os
import re
import json
import subprocess
import hashlib
import requests
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class SmartTVClipper:
    def __init__(self):
        """初始化系统"""
        self.setup_directories()
        self.ai_config = self.load_ai_config()

    def setup_directories(self):
        """创建必要目录"""
        self.dirs = {
            'srt': 'srt',
            'videos': 'videos', 
            'output': 'clips',
            'cache': 'cache'
        }

        for name, path in self.dirs.items():
            if not os.path.exists(path):
                os.makedirs(path)

        print("📁 目录已准备完成")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False):
                    print(f"🤖 AI已启用: {config.get('model', '未知模型')}")
                    return config
        except:
            pass
        return {'enabled': False}

    def save_ai_config(self, config: Dict):
        """保存AI配置"""
        with open('.ai_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def quick_ai_setup(self) -> bool:
        """快速AI配置"""
        print("\n🤖 AI配置向导")
        print("=" * 40)
        print("AI分析可以大幅提升剪辑质量和准确性")

        use_ai = input("是否启用AI分析？(Y/n): ").lower().strip()
        if use_ai in ['n', 'no', '否']:
            print("将使用基础规则分析")
            return False

        print("\n选择API类型:")
        print("1. 中转API (推荐)")
        print("2. 跳过配置")

        choice = input("选择 (1-2): ").strip()

        if choice == "1":
            api_key = input("API密钥: ").strip()
            if not api_key:
                print("密钥不能为空，跳过AI配置")
                return False

            base_url = input("API地址 (默认: https://www.chataiapi.com/v1): ").strip()
            if not base_url:
                base_url = "https://www.chataiapi.com/v1"

            model = input("模型名称 (默认: deepseek-r1): ").strip()
            if not model:
                model = "deepseek-r1"

            config = {
                'enabled': True,
                'api_key': api_key,
                'base_url': base_url,
                'model': model
            }

            # 测试连接
            print("🔍 测试连接...")
            if self.test_ai_connection(config):
                self.ai_config = config
                self.save_ai_config(config)
                print("✅ AI配置成功！")
                return True
            else:
                print("❌ 连接失败，将使用基础模式")
                return False

        print("将使用基础规则分析")
        return False

    def test_ai_connection(self, config: Dict) -> bool:
        """测试AI连接"""
        try:
            payload = {
                "model": config['model'],
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            }

            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f"{config['base_url']}/chat/completions",
                headers=headers, 
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件"""
        try:
            # 多编码尝试
            content = ""
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue

            if not content:
                return []

            # 错别字修正
            corrections = {
                '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
                '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
                '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会'
            }

            for old, new in corrections.items():
                content = content.replace(old, new)

            # 解析字幕块
            blocks = re.split(r'\n\s*\n', content.strip())
            subtitles = []

            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1
                        time_match = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
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

            return subtitles

        except Exception as e:
            print(f"❌ 解析字幕失败: {e}")
            return []

    def get_cache_key(self, content: str) -> str:
        """生成缓存键"""
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def load_cache(self, cache_key: str) -> Optional[Dict]:
        """加载缓存"""
        cache_path = os.path.join(self.dirs['cache'], f"{cache_key}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save_cache(self, cache_key: str, data: Dict):
        """保存缓存"""
        cache_path = os.path.join(self.dirs['cache'], f"{cache_key}.json")
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except:
            pass

    def call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        if not self.ai_config.get('enabled'):
            return None

        try:
            payload = {
                "model": self.ai_config['model'],
                "messages": [
                    {"role": "system", "content": "你是专业的电视剧剪辑师，擅长识别精彩片段。请用JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000,
                "temperature": 0.7
            }

            headers = {
                'Authorization': f'Bearer {self.ai_config["api_key"]}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f"{self.ai_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']

                # 处理deepseek-r1的特殊格式
                if 'reasoning_content' in message:
                    print(f"🧠 AI思考: {message['reasoning_content'][:50]}...")

                return message.get('content', '')

        except Exception as e:
            print(f"⚠ AI调用失败: {e}")

        return None

    def smart_analyze_episode(self, subtitles: List[Dict], filename: str) -> Dict:
        """智能分析剧集"""
        # 生成缓存键
        content_str = json.dumps([s['text'] for s in subtitles[:100]], ensure_ascii=False)
        cache_key = self.get_cache_key(content_str + filename)

        # 检查缓存
        cached_result = self.load_cache(cache_key)
        if cached_result:
            print("📋 使用缓存分析")
            return cached_result

        episode_num = self.extract_episode_number(filename)

        # AI分析
        if self.ai_config.get('enabled'):
            print("🤖 AI深度分析中...")

            # 构建上下文
            context_parts = []
            for i in range(0, min(len(subtitles), 200), 20):
                segment = subtitles[i:i+20]
                time_info = f"[{segment[0]['start']}-{segment[-1]['end']}]"
                text = ' '.join([s['text'] for s in segment])
                context_parts.append(f"{time_info} {text[:200]}")

            context = '\n'.join(context_parts)

            prompt = f"""分析第{episode_num}集电视剧，找出2-3个最精彩的片段用于短视频制作。

剧情内容:
{context}

要求:
1. 每个片段2-3分钟，有完整对话
2. 包含戏剧冲突或情感高潮
3. 能独立成为短视频
4. 确保语句完整

返回JSON格式:
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre": "剧情类型",
        "main_theme": "主要主题"
    }},
    "clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "description": "内容描述",
            "dramatic_value": 8.5,
            "significance": "剧情意义"
        }}
    ]
}}"""

            ai_response = self.call_ai_api(prompt)

            if ai_response:
                try:
                    # 提取JSON
                    if "```json" in ai_response:
                        json_start = ai_response.find("```json") + 7
                        json_end = ai_response.find("```", json_start)
                        json_text = ai_response[json_start:json_end]
                    else:
                        start = ai_response.find("{")
                        end = ai_response.rfind("}") + 1
                        json_text = ai_response[start:end]

                    result = json.loads(json_text)

                    # 优化时间码
                    optimized_clips = []
                    for clip in result.get('clips', []):
                        optimized_clip = self.optimize_clip_timing(clip, subtitles)
                        if optimized_clip:
                            optimized_clips.append(optimized_clip)

                    analysis = {
                        'episode_number': episode_num,
                        'analysis': result.get('episode_analysis', {}),
                        'clips': optimized_clips,
                        'ai_generated': True
                    }

                    # 保存缓存
                    self.save_cache(cache_key, analysis)
                    return analysis

                except Exception as e:
                    print(f"⚠ AI结果解析失败: {e}")

        # 基础分析备选
        print("📊 使用基础规则分析")
        analysis = self.basic_analysis(subtitles, filename)
        self.save_cache(cache_key, analysis)
        return analysis

    def basic_analysis(self, subtitles: List[Dict], filename: str) -> Dict:
        """基础分析方法"""
        episode_num = self.extract_episode_number(filename)

        # 关键词评分
        keywords = ['突然', '发现', '真相', '秘密', '不可能', '为什么', '杀人', '死了', 
                   '救命', '危险', '完了', '震惊', '愤怒', '哭', '崩溃', '爱你', '分手']

        scored_segments = []

        for i, subtitle in enumerate(subtitles):
            score = 0
            text = subtitle['text']

            # 关键词评分
            for keyword in keywords:
                score += text.count(keyword) * 2

            # 标点符号评分
            score += text.count('！') + text.count('？') + text.count('...') * 0.5

            if score >= 2:
                scored_segments.append({
                    'index': i,
                    'score': score,
                    'subtitle': subtitle
                })

        # 选择最佳片段
        scored_segments.sort(key=lambda x: x['score'], reverse=True)

        clips = []
        selected_segments = scored_segments[:3]  # 最多3个

        for i, seg in enumerate(selected_segments):
            start_idx = max(0, seg['index'] - 15)
            end_idx = min(len(subtitles) - 1, seg['index'] + 20)

            clips.append({
                'clip_id': i + 1,
                'title': f"精彩片段{i + 1}",
                'start_time': subtitles[start_idx]['start'],
                'end_time': subtitles[end_idx]['end'],
                'description': f"包含戏剧冲突的精彩内容",
                'dramatic_value': min(9.0, seg['score']),
                'significance': '基于关键词识别的精彩片段'
            })

        return {
            'episode_number': episode_num,
            'analysis': {
                'genre': '通用',
                'main_theme': f'第{episode_num}集精彩内容'
            },
            'clips': clips,
            'ai_generated': False
        }

    def optimize_clip_timing(self, clip: Dict, subtitles: List[Dict]) -> Optional[Dict]:
        """优化剪辑时间"""
        start_time = clip.get('start_time', '')
        end_time = clip.get('end_time', '')

        if not start_time or not end_time:
            return None

        start_seconds = self.time_to_seconds(start_time)
        end_seconds = self.time_to_seconds(end_time)

        # 寻找最佳边界
        best_start = start_seconds
        best_end = end_seconds

        for sub in subtitles:
            sub_start = self.time_to_seconds(sub['start'])
            sub_end = self.time_to_seconds(sub['end'])

            # 向前扩展确保完整句子
            if sub_start <= start_seconds <= sub_end:
                best_start = sub_start
            if sub_start <= end_seconds <= sub_end:
                best_end = sub_end

        # 添加缓冲确保完整性
        final_start = max(0, best_start - 1)
        final_end = best_end + 1

        clip_copy = clip.copy()
        clip_copy.update({
            'start_time': self.seconds_to_time(final_start),
            'end_time': self.seconds_to_time(final_end),
            'duration': final_end - final_start
        })

        return clip_copy

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """查找匹配视频"""
        base_name = os.path.splitext(subtitle_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.dirs['videos'], base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for filename in os.listdir(self.dirs['videos']):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if any(part in filename.lower() for part in base_name.lower().split('_') if len(part) > 2):
                    return os.path.join(self.dirs['videos'], filename)

        return None

    def create_video_clip(self, video_file: str, clip: Dict, episode_num: str) -> bool:
        """创建视频片段"""
        try:
            clip_id = clip['clip_id']
            title = clip['title']
            start_time = clip['start_time']
            end_time = clip['end_time']

            # 生成文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            output_filename = f"E{episode_num}_C{clip_id:02d}_{safe_title}.mp4"
            output_path = os.path.join(self.dirs['output'], output_filename)

            # 检查是否已存在
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"  ✓ 已存在: {output_filename}")
                return True

            print(f"  🎬 剪辑: {title}")
            print(f"     时间: {start_time} --> {end_time}")

            # 计算时间
            start_seconds = self.time_to_seconds(start_time)
            duration = self.time_to_seconds(end_time) - start_seconds

            if duration <= 0:
                print(f"  ❌ 时间无效")
                return False

            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                output_path,
                '-y'
            ]

            # 执行剪辑
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"    ✅ 成功: {file_size:.1f}MB")

                # 生成说明文件
                self.create_description_file(output_path, clip)
                return True
            else:
                print(f"    ❌ 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
                return False

        except Exception as e:
            print(f"    ❌ 异常: {e}")
            return False

    def create_description_file(self, video_path: str, clip: Dict):
        """创建说明文件"""
        try:
            desc_path = video_path.replace('.mp4', '_说明.txt')

            content = f"""🎬 {clip['title']}
{"=" * 50}

🎯 戏剧价值: {clip.get('dramatic_value', 0):.1f}/10
📝 剧情意义: {clip.get('significance', '未知')}
📖 内容描述: {clip.get('description', '精彩片段')}

⏱️ 时间轴: {clip.get('start_time', '')} --> {clip.get('end_time', '')}
⏰ 时长: {clip.get('duration', 0):.1f}秒

🎙️ 这个片段展现了剧情的重要转折点，包含了丰富的戏剧冲突和情感张力，适合短视频传播。

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            print(f"    ⚠ 说明文件生成失败: {e}")

    def extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)
        return "00"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            time_str = time_str.replace('.', ',')
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

    def process_single_episode(self, subtitle_file: str) -> bool:
        """处理单集"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.dirs['srt'], subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print("❌ 字幕解析失败")
            return False

        print(f"📝 解析: {len(subtitles)} 条字幕")

        # 2. 智能分析
        analysis = self.smart_analyze_episode(subtitles, subtitle_file)

        if not analysis['clips']:
            print("❌ 未识别到精彩片段")
            return False

        episode_num = analysis['episode_number']
        print(f"🎯 识别: {len(analysis['clips'])} 个精彩片段")

        # 3. 查找视频
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print("❌ 未找到对应视频")
            return False

        print(f"📹 视频: {os.path.basename(video_file)}")

        # 4. 剪辑片段
        success_count = 0
        for clip in analysis['clips']:
            if self.create_video_clip(video_file, clip, episode_num):
                success_count += 1

        print(f"✅ 成功: {success_count}/{len(analysis['clips'])} 个片段")
        return success_count > 0

    def get_subtitle_files(self) -> List[str]:
        """获取字幕文件"""
        if not os.path.exists(self.dirs['srt']):
            return []

        files = [f for f in os.listdir(self.dirs['srt']) 
                if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        return sorted(files)

    def get_video_files(self) -> List[str]:
        """获取视频文件"""
        if not os.path.exists(self.dirs['videos']):
            return []

        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        files = [f for f in os.listdir(self.dirs['videos']) 
                if any(f.lower().endswith(ext) for ext in video_extensions)]
        return sorted(files)

    def run_complete_workflow(self):
        """运行完整工作流"""
        print("🚀 智能电视剧剪辑系统")
        print("=" * 50)

        # 检查文件
        subtitle_files = self.get_subtitle_files()
        video_files = self.get_video_files()

        if not subtitle_files:
            print("❌ 未找到字幕文件")
            print(f"请将.srt或.txt字幕文件放入 {self.dirs['srt']}/ 目录")
            return

        if not video_files:
            print("❌ 未找到视频文件")
            print(f"请将视频文件放入 {self.dirs['videos']}/ 目录")
            return

        print(f"📝 字幕文件: {len(subtitle_files)} 个")
        print(f"📹 视频文件: {len(video_files)} 个")

        ai_status = "🤖 AI智能" if self.ai_config.get('enabled') else "📊 规则分析"
        print(f"🎯 分析模式: {ai_status}")

        # 处理所有集数
        total_success = 0
        total_clips = 0

        for subtitle_file in subtitle_files:
            try:
                if self.process_single_episode(subtitle_file):
                    total_success += 1

                # 统计片段数
                episode_clips = [f for f in os.listdir(self.dirs['output']) 
                               if f.startswith(f"E{self.extract_episode_number(subtitle_file)}")]
                total_clips += len(episode_clips)

            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 失败: {e}")

        # 生成最终报告
        self.create_final_report(total_success, len(subtitle_files), total_clips)

    def create_final_report(self, success_count: int, total_episodes: int, total_clips: int):
        """生成最终报告"""
        try:
            report_path = os.path.join(self.dirs['output'], "剪辑报告.txt")

            content = f"""🎬 智能电视剧剪辑系统 - 完成报告
{"=" * 60}

📊 处理统计:
• 总集数: {total_episodes} 集
• 成功处理: {success_count} 集
• 成功率: {(success_count/total_episodes*100) if total_episodes > 0 else 0:.1f}%
• 生成短视频: {total_clips} 个

🤖 系统信息:
• AI分析: {'启用' if self.ai_config.get('enabled') else '未启用'}
• 缓存机制: 启用
• 输出目录: {self.dirs['output']}/

📁 输出文件:
• 短视频: *.mp4
• 说明文档: *_说明.txt

✨ 主要特点:
• 智能识别精彩片段
• 保证对话完整性
• 支持多种剧情类型
• 缓存避免重复分析
• 自动错别字修正

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"\n📊 最终统计:")
            print(f"✅ 成功: {success_count}/{total_episodes} 集")
            print(f"🎬 短视频: {total_clips} 个")
            print(f"📄 详细报告: {report_path}")

        except Exception as e:
            print(f"⚠ 报告生成失败: {e}")

    def main_menu(self):
        """主菜单"""
        print("🎬 智能电视剧剪辑系统")
        print("=" * 50)
        print("1. 🚀 开始剪辑 (推荐)")
        print("2. 🤖 配置AI")
        print("3. 📊 查看报告")
        print("4. ❌ 退出")

        choice = input("\n请选择 (1-4): ").strip()

        if choice == "1":
            # 如果没有AI配置，询问是否配置
            if not self.ai_config.get('enabled'):
                print("\n💡 建议启用AI分析以获得更好的剪辑效果")
                setup_ai = input("是否现在配置AI？(Y/n): ").lower().strip()
                if setup_ai not in ['n', 'no', '否']:
                    self.quick_ai_setup()

            self.run_complete_workflow()

        elif choice == "2":
            self.quick_ai_setup()

        elif choice == "3":
            report_path = os.path.join(self.dirs['output'], "剪辑报告.txt")
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print("❌ 未找到报告，请先执行剪辑")

        elif choice == "4":
            print("👋 再见！")
            return
        else:
            print("❌ 无效选择")

        # 继续菜单
        input("\n按Enter继续...")
        self.main_menu()

def main():
    """主函数"""
    try:
        clipper = SmartTVClipper()
        clipper.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断退出")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")

if __name__ == "__main__":
    main()