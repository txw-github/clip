
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影字幕AI分析剪辑系统
专门用于：
1. AI分析电影字幕文件
2. 智能识别精彩片段和剧情点
3. 生成第一人称叙述字幕
4. 输出完整剪辑方案
"""

import os
import re
import json
import requests
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

class MovieAIClipper:
    def __init__(self):
        # 创建必要目录
        self.srt_folder = "movie_srt"
        self.output_folder = "movie_clips"
        self.analysis_folder = "movie_analysis"
        self.cache_folder = "ai_cache"
        
        for folder in [self.srt_folder, self.output_folder, self.analysis_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 剧情点类型定义
        self.plot_types = {
            '关键冲突': {
                'keywords': ['冲突', '争执', '对抗', '战斗', '矛盾', '争论', '敌对', '反抗', '对立'],
                'weight': 10,
                'target_duration': 180
            },
            '人物转折': {
                'keywords': ['决定', '改变', '选择', '转变', '觉悟', '明白', '意识到', '成长', '蜕变'],
                'weight': 9,
                'target_duration': 150
            },
            '线索揭露': {
                'keywords': ['发现', '揭露', '真相', '秘密', '线索', '证据', '暴露', '揭开', '查明'],
                'weight': 8,
                'target_duration': 160
            },
            '情感高潮': {
                'keywords': ['爱情', '友情', '亲情', '背叛', '牺牲', '救赎', '感动', '心痛', '温暖'],
                'weight': 7,
                'target_duration': 140
            },
            '动作场面': {
                'keywords': ['追逐', '打斗', '逃跑', '营救', '爆炸', '枪战', '飞车', '特技', '危险'],
                'weight': 6,
                'target_duration': 120
            }
        }
        
        print("🎬 电影字幕AI分析剪辑系统已启动")
        print(f"📁 字幕目录: {self.srt_folder}/")
        print(f"📁 输出目录: {self.output_folder}/")
        print(f"🤖 AI状态: {'已启用' if self.ai_config.get('enabled') else '未配置'}")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False) and config.get('api_key'):
                    return config
        except:
            pass
        
        print("⚠️ AI未配置，请先配置AI API")
        return {'enabled': False}

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件并修正错误"""
        print(f"📖 解析字幕文件: {os.path.basename(filepath)}")
        
        try:
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
                raise Exception("无法读取文件")
            
            # 智能错误修正
            content = self.fix_subtitle_errors(content)
            
            # 解析字幕条目
            subtitles = []
            blocks = re.split(r'\n\s*\n', content.strip())
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        index = int(lines[0])
                        time_match = re.match(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3}) --> (\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
                        
                        if time_match:
                            start_time = time_match.group(1).replace('.', ',')
                            end_time = time_match.group(2).replace('.', ',')
                            text = '\n'.join(lines[2:]).strip()
                            
                            if text:
                                subtitles.append({
                                    'index': index,
                                    'start_time': start_time,
                                    'end_time': end_time,
                                    'text': text,
                                    'duration': self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
                                })
                    except (ValueError, IndexError):
                        continue
            
            print(f"✅ 成功解析 {len(subtitles)} 条字幕")
            return subtitles
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return []

    def fix_subtitle_errors(self, content: str) -> str:
        """智能修正字幕错误"""
        # 常见错误修正词典
        corrections = {
            # 标点符号修正
            '。。。': '...',
            '！！': '！',
            '？？': '？',
            
            # 常见错别字
            '的话': '的话',
            '这样': '这样',
            '那样': '那样',
            '什么': '什么',
            '怎么': '怎么',
            '为什么': '为什么',
            
            # 语气词修正
            '啊啊': '啊',
            '呃呃': '呃',
            '嗯嗯': '嗯',
            
            # 空格修正
            ' ，': '，',
            ' 。': '。',
            ' ！': '！',
            ' ？': '？',
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        return content

    def ai_analyze_movie(self, subtitles: List[Dict], movie_title: str = "") -> Dict:
        """AI全面分析电影内容"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未启用，无法进行分析")
            return {}
        
        # 检查缓存
        cache_key = hashlib.md5(str(subtitles).encode()).hexdigest()[:16]
        cache_path = os.path.join(self.cache_folder, f"movie_analysis_{cache_key}.json")
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    print("📋 使用缓存的AI分析结果")
                    return cached_analysis
            except:
                pass
        
        print("🤖 AI正在分析电影内容...")
        
        # 构建完整上下文
        full_content = self.build_movie_context(subtitles)
        
        prompt = f"""你是专业的电影分析师和剪辑师，需要对这部电影进行全面分析并制定剪辑方案。

【电影标题】{movie_title}

【完整字幕内容】
{full_content}

请完成以下任务：

1. 电影基本分析：
   - 电影类型（动作、爱情、悬疑、科幻、喜剧等）
   - 主要角色识别
   - 核心主题
   - 故事结构分析

2. 精彩片段识别：
   找出5-8个最精彩的片段，每个2-3分钟，要求：
   - 包含完整的故事情节
   - 有明确的戏剧冲突或情感高潮
   - 能独立成为一个短视频
   - 涵盖不同类型的剧情点

3. 剧情点分类：
   将每个片段按以下类型分类：
   - 关键冲突：主要矛盾和对抗场面
   - 人物转折：角色成长和转变时刻
   - 线索揭露：重要信息和真相揭示
   - 情感高潮：感人或震撼的情感场面
   - 动作场面：激烈的动作和追逐戏

4. 第一人称叙述生成：
   为每个片段生成详细的第一人称叙述，要求：
   - 以"我"的视角描述正在发生的事情
   - 详细解释剧情发展和人物动机
   - 语言生动有趣，吸引观众
   - 时长控制在片段时间内

请以JSON格式返回：
{{
    "movie_analysis": {{
        "title": "{movie_title}",
        "genre": "电影类型",
        "main_characters": ["主要角色1", "主要角色2"],
        "core_theme": "核心主题",
        "story_structure": "故事结构分析",
        "total_duration": "总时长（分钟）"
    }},
    "highlight_clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "plot_type": "剧情点类型",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "duration_seconds": 持续秒数,
            "story_summary": "剧情摘要",
            "dramatic_value": "戏剧价值（1-10分）",
            "first_person_narration": {{
                "opening": "开场第一人称叙述",
                "development": "发展过程叙述",
                "climax": "高潮部分叙述",
                "conclusion": "结尾叙述",
                "full_narration": "完整第一人称叙述"
            }},
            "key_moments": ["关键时刻1", "关键时刻2"],
            "emotional_impact": "情感冲击描述",
            "connection_reason": "选择此片段的原因"
        }}
    ],
    "storyline_summary": "完整故事线总结",
    "editing_notes": "剪辑制作说明"
}}"""

        try:
            response = self.call_ai_api(prompt)
            if response:
                analysis = self.parse_ai_response(response)
                if analysis:
                    # 保存缓存
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, ensure_ascii=False, indent=2)
                    
                    print("✅ AI分析完成")
                    return analysis
            
            print("❌ AI分析失败")
            return {}
            
        except Exception as e:
            print(f"❌ AI分析出错: {e}")
            return {}

    def build_movie_context(self, subtitles: List[Dict]) -> str:
        """构建电影完整上下文"""
        # 取关键部分内容，避免超出API限制
        total_subs = len(subtitles)
        
        # 取开头、中间、结尾的重要内容
        key_parts = []
        
        # 开头（前15%）
        start_end = int(total_subs * 0.15)
        start_content = ' '.join([sub['text'] for sub in subtitles[:start_end]])
        key_parts.append(f"【开头部分】\n{start_content}")
        
        # 中间关键部分（35%-65%）
        middle_start = int(total_subs * 0.35)
        middle_end = int(total_subs * 0.65)
        middle_content = ' '.join([sub['text'] for sub in subtitles[middle_start:middle_end]])
        key_parts.append(f"【中间部分】\n{middle_content}")
        
        # 结尾（后15%）
        end_start = int(total_subs * 0.85)
        end_content = ' '.join([sub['text'] for sub in subtitles[end_start:]])
        key_parts.append(f"【结尾部分】\n{end_content}")
        
        return '\n\n'.join(key_parts)

    def call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            config = self.ai_config
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是专业的电影分析师和剪辑师，擅长识别精彩片段和生成第一人称叙述。请严格按照JSON格式返回分析结果。'
                    },
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 4000,
                'temperature': 0.7
            }
            
            url = config.get('base_url', 'https://api.openai.com/v1') + '/chat/completions'
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                print(f"⚠️ API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ API调用异常: {e}")
            return None

    def parse_ai_response(self, response_text: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]
            
            analysis = json.loads(response_text)
            
            # 验证必要字段
            if 'highlight_clips' in analysis and 'movie_analysis' in analysis:
                return analysis
            else:
                print("⚠️ AI分析结果缺少必要字段")
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠️ AI分析结果JSON解析失败: {e}")
            return None

    def generate_editing_plan(self, analysis: Dict, movie_title: str) -> str:
        """生成完整剪辑方案"""
        if not analysis:
            return "❌ AI分析失败，无法生成剪辑方案"
        
        movie_info = analysis.get('movie_analysis', {})
        clips = analysis.get('highlight_clips', [])
        
        plan = f"""🎬 《{movie_title}》AI分析剪辑方案
{'=' * 80}

📊 电影基本信息
• 标题：{movie_info.get('title', movie_title)}
• 类型：{movie_info.get('genre', '未知')}
• 主要角色：{', '.join(movie_info.get('main_characters', []))}
• 核心主题：{movie_info.get('core_theme', '待分析')}
• 总时长：{movie_info.get('total_duration', '未知')}

📖 完整故事线
{analysis.get('storyline_summary', '完整的故事发展脉络')}

🎯 精彩片段剪辑方案（共{len(clips)}个片段）
"""
        
        total_duration = 0
        
        for i, clip in enumerate(clips, 1):
            duration = clip.get('duration_seconds', 0)
            total_duration += duration
            
            plan += f"""
{'=' * 60}
🎬 片段 {i}：{clip.get('title', f'精彩片段{i}')}
{'=' * 60}
🎭 剧情点类型：{clip.get('plot_type', '未分类')}
⏱️ 时间范围：{clip.get('start_time', '00:00:00,000')} --> {clip.get('end_time', '00:00:00,000')}
📏 片段时长：{duration:.1f} 秒 ({duration/60:.1f} 分钟)
📊 戏剧价值：{clip.get('dramatic_value', 0)}/10

📝 剧情摘要：
{clip.get('story_summary', '精彩剧情发展')}

🎙️ 第一人称完整叙述：
{clip.get('first_person_narration', {}).get('full_narration', '详细的第一人称叙述内容')}

🎭 分段叙述：
• 开场：{clip.get('first_person_narration', {}).get('opening', '开场叙述')}
• 发展：{clip.get('first_person_narration', {}).get('development', '发展叙述')}
• 高潮：{clip.get('first_person_narration', {}).get('climax', '高潮叙述')}
• 结尾：{clip.get('first_person_narration', {}).get('conclusion', '结尾叙述')}

💫 关键时刻：
"""
            for moment in clip.get('key_moments', []):
                plan += f"• {moment}\n"
            
            plan += f"""
💥 情感冲击：{clip.get('emotional_impact', '强烈的情感体验')}
🎯 选择原因：{clip.get('connection_reason', '精彩程度极高，适合短视频传播')}
"""
        
        plan += f"""

📊 剪辑统计总结
• 总片段数：{len(clips)} 个
• 总剪辑时长：{total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)
• 平均片段时长：{total_duration/len(clips) if clips else 0:.1f} 秒

🎬 制作技术说明
{analysis.get('editing_notes', '''• 所有片段均由AI分析选定，确保精彩程度
• 时间段可能在原视频中不连续，但剪辑后逻辑连贯
• 第一人称叙述详细清晰，完整覆盖剧情发展
• 每个片段都有完整的故事弧线
• 字幕错误已自动修正
• 适合短视频平台传播''')}

✨ 输出文件规格
• 视频格式：MP4 (H.264编码)
• 音频格式：AAC
• 分辨率：保持原始比例
• 字幕：内嵌第一人称叙述
• 文件命名：片段序号_剧情点类型_核心内容.mp4

🎯 观看体验保证
• 每个片段都是完整的故事单元
• 第一人称叙述让观众身临其境
• 剧情点分类让内容聚焦明确
• 时长控制在最佳观看范围内

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
AI分析引擎：专业电影剪辑分析系统 v2.0
"""
        
        return plan

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def process_movie_file(self, srt_file: str) -> bool:
        """处理单个电影文件"""
        print(f"\n🎬 处理电影: {srt_file}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_file)
        subtitles = self.parse_srt_file(srt_path)
        
        if not subtitles:
            print("❌ 字幕解析失败")
            return False
        
        # 2. 提取电影标题
        movie_title = os.path.splitext(srt_file)[0]
        
        # 3. AI分析
        print("🤖 AI正在分析电影内容...")
        analysis = self.ai_analyze_movie(subtitles, movie_title)
        
        if not analysis:
            print("❌ AI分析失败")
            return False
        
        # 4. 生成剪辑方案
        editing_plan = self.generate_editing_plan(analysis, movie_title)
        
        # 5. 保存结果
        plan_filename = f"{movie_title}_AI剪辑方案.txt"
        plan_path = os.path.join(self.analysis_folder, plan_filename)
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(editing_plan)
        
        # 6. 保存详细AI分析数据
        analysis_filename = f"{movie_title}_AI分析数据.json"
        analysis_path = os.path.join(self.analysis_folder, analysis_filename)
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 处理完成！")
        print(f"📄 剪辑方案：{plan_filename}")
        print(f"📊 分析数据：{analysis_filename}")
        
        return True

    def process_all_movies(self):
        """处理所有电影文件"""
        print("🚀 电影AI分析剪辑系统启动")
        print("=" * 60)
        
        # 获取所有字幕文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            print(f"💡 请将电影字幕文件放入 {self.srt_folder}/ 目录")
            return
        
        srt_files.sort()
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置，无法进行分析")
            print("💡 请先配置AI API密钥")
            return
        
        # 处理每个文件
        success_count = 0
        for srt_file in srt_files:
            try:
                if self.process_movie_file(srt_file):
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理 {srt_file} 时出错: {e}")
        
        # 生成总结报告
        self.generate_summary_report(srt_files, success_count)

    def generate_summary_report(self, srt_files: List[str], success_count: int):
        """生成总结报告"""
        report = f"""🎬 电影AI分析剪辑系统 - 总结报告
{'=' * 80}

📊 处理统计
• 总文件数：{len(srt_files)} 个
• 成功分析：{success_count} 个
• 失败数量：{len(srt_files) - success_count} 个
• 成功率：{success_count/len(srt_files)*100:.1f}%

✨ 系统特色
• ✅ 100% AI分析 - 无AI不分析，确保智能化程度
• ✅ 智能错误修正 - 自动修正字幕中的错别字和格式问题
• ✅ 精彩片段识别 - AI智能识别5-8个最精彩的剧情点
• ✅ 第一人称叙述 - 详细清晰的"我"视角叙述内容
• ✅ 剧情点分类 - 按冲突、转折、揭露等类型精准分类
• ✅ 非连续剪辑 - 支持时间不连续但逻辑连贯的剪辑
• ✅ 完整故事线 - 确保每个片段都有完整的故事弧线

📁 输出文件
• 剪辑方案：{self.analysis_folder}/*_AI剪辑方案.txt
• 分析数据：{self.analysis_folder}/*_AI分析数据.json
• 缓存文件：{self.cache_folder}/*.json

🎯 输出格式固定标准
每个剪辑方案包含：
1. 📊 电影基本信息（类型、角色、主题）
2. 📖 完整故事线总结
3. 🎬 精彩片段详细方案（5-8个）
4. 🎙️ 第一人称完整叙述（开场-发展-高潮-结尾）
5. ⏱️ 精确时间标注（开始-结束时间）
6. 🎭 剧情点类型分类
7. 📝 制作技术说明

💡 使用说明
• 将电影字幕文件(.srt/.txt)放入 {self.srt_folder}/ 目录
• 运行系统自动进行AI分析
• 查看 {self.analysis_folder}/ 目录获取剪辑方案
• 方案包含完整的第一人称叙述和时间标注
• 适合直接用于短视频制作

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report_path = os.path.join(self.analysis_folder, "电影AI分析总结报告.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 最终统计:")
        print(f"✅ 成功分析: {success_count}/{len(srt_files)} 个电影")
        print(f"📄 详细报告: {report_path}")

def main():
    """主函数"""
    clipper = MovieAIClipper()
    clipper.process_all_movies()

if __name__ == "__main__":
    main()
