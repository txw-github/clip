
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一智能剪辑系统 - 清理后的完整解决方案
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional
from api_config_helper import config_helper

class UnifiedVideoClipper:
    def __init__(self):
        self.config = config_helper.load_config()
        self.enabled = self.config.get('enabled', False)
        
        # 确保必要目录存在
        for dir_name in ['srt', 'videos', 'output_clips']:
            os.makedirs(dir_name, exist_ok=True)

    def process_all_episodes(self) -> Dict:
        """处理所有剧集"""
        print("🚀 启动统一智能剪辑系统")
        print("=" * 50)
        
        # 获取字幕文件
        srt_files = self.get_srt_files()
        if not srt_files:
            print("❌ 未找到字幕文件")
            return {}
        
        print(f"📺 找到 {len(srt_files)} 集")
        
        results = []
        
        for srt_file in srt_files:
            print(f"\n处理: {srt_file}")
            
            # 解析字幕
            subtitles = self.parse_srt(srt_file)
            if not subtitles:
                continue
            
            # AI分析（一次性分析整集）
            analysis = self.analyze_episode(subtitles, srt_file)
            
            # 识别精彩片段
            highlights = self.find_highlights(subtitles, analysis)
            
            # 创建视频片段
            created_clips = self.create_clips(srt_file, highlights)
            
            results.append({
                'episode': srt_file,
                'clips_created': len(created_clips),
                'clips': created_clips
            })
        
        self.generate_summary_report(results)
        return results

    def get_srt_files(self) -> List[str]:
        """获取字幕文件列表"""
        srt_dir = 'srt'
        if not os.path.exists(srt_dir):
            return []
        
        files = [f for f in os.listdir(srt_dir) if f.endswith('.srt')]
        files.sort()
        return files

    def parse_srt(self, srt_file: str) -> List[Dict]:
        """解析SRT字幕"""
        srt_path = os.path.join('srt', srt_file)
        
        try:
            with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 修正常见错误
            content = self.fix_subtitle_errors(content)
            
            subtitles = []
            blocks = re.split(r'\n\s*\n', content.strip())
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        index = int(lines[0])
                        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                        if time_match:
                            start_time = time_match.group(1)
                            end_time = time_match.group(2)
                            text = ' '.join(lines[2:]).strip()
                            
                            subtitles.append({
                                'index': index,
                                'start': start_time,
                                'end': end_time,
                                'text': text,
                                'start_seconds': self.time_to_seconds(start_time),
                                'end_seconds': self.time_to_seconds(end_time)
                            })
                    except (ValueError, IndexError):
                        continue
            
            print(f"  解析完成: {len(subtitles)} 条字幕")
            return subtitles
            
        except Exception as e:
            print(f"  解析失败: {e}")
            return []

    def fix_subtitle_errors(self, content: str) -> str:
        """修正常见字幕错误"""
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
            '聽證會': '听证会', '辯護': '辩护', '審判': '审判', '調查': '调查'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        return content

    def analyze_episode(self, subtitles: List[Dict], episode_file: str) -> Dict:
        """AI分析整集内容 - 一次性分析完整剧情，避免割裂"""
        if not self.enabled or not subtitles:
            return self.fallback_analysis(episode_file)
        
        # 构建完整剧情文本 - 保持时间线和上下文
        full_episode_text = self.build_complete_episode_context(subtitles)
        
        # 提取集数
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        episode_num = episode_match.group(1) if episode_match else "1"
        
        prompt = f"""你是专业的电视剧剪辑师。请分析第{episode_num}集的完整剧情，一次性识别3-5个最精彩、最连贯的片段。

【完整剧情内容（按时间顺序）】
{full_episode_text}

请进行整体剧情分析：

1. **完整剧情理解**：
   - 理解整集的核心故事线
   - 识别主要角色关系和冲突发展
   - 把握剧情节奏和情感变化

2. **精彩片段选择**（3-5个）：
   - 每个片段必须是完整的故事单元（有起承转合）
   - 片段间要有逻辑连贯性，能串联成完整故事
   - 优先选择包含关键信息、戏剧冲突、情感高潮的部分
   - 每个片段控制在90-180秒

3. **剧情连贯性**：
   - 确保选出的片段组合起来能完整叙述本集故事
   - 考虑前后呼应和伏笔揭示
   - 处理可能的剧情反转

请返回JSON格式：
{{
    "episode_theme": "本集核心主题",
    "story_arc": "整体故事弧线描述",
    "key_plot_points": ["关键剧情点1", "关键剧情点2"],
    "highlights": [
        {{
            "title": "片段标题",
            "start_minute": 开始分钟数,
            "end_minute": 结束分钟数,
            "plot_significance": "剧情重要性",
            "emotional_core": "情感核心",
            "key_dialogue": "关键对话内容",
            "connection_to_story": "与整体故事的关系",
            "why_essential": "为什么这个片段不可缺少"
        }}
    ],
    "narrative_flow": "片段间的叙事流程",
    "missing_context": "如果只看这些片段，观众还需要了解什么背景"
}}"""

        try:
            print(f"  🤖 AI整体剧情分析中...")
            response = config_helper.call_ai_api(prompt, self.config)
            if response:
                print(f"  ✅ 完整剧情分析完成")
                return self.parse_ai_response(response)
            else:
                print(f"  ⚠️ AI分析返回空结果，使用备用分析")
        except Exception as e:
            error_msg = str(e)
            if "10054" in error_msg or "远程主机" in error_msg:
                print(f"  🔌 网络连接中断 (Error 10054)")
                print(f"  💡 建议: 检查网络连接或更换API服务商")
            else:
                print(f"  ❌ AI分析失败: {e}")
        
        return self.fallback_analysis(episode_file)

    def build_complete_episode_context(self, subtitles: List[Dict]) -> str:
        """构建保持时间线的完整剧情上下文"""
        # 不再强制分割，保持自然的对话流
        episode_content = []
        current_time_block = []
        last_minute = -1
        
        for subtitle in subtitles:
            current_minute = int(subtitle['start_seconds'] // 60)
            
            # 每5分钟添加一个时间标记，但不强制分割
            if current_minute != last_minute and current_minute % 5 == 0:
                if current_time_block:
                    episode_content.append(' '.join(current_time_block))
                    current_time_block = []
                episode_content.append(f"\n[{current_minute}分钟]\n")
                last_minute = current_minute
            
            current_time_block.append(subtitle['text'])
        
        # 添加最后一段
        if current_time_block:
            episode_content.append(' '.join(current_time_block))
        
        full_text = ''.join(episode_content)
        
        # 如果文本太长，智能截取但保持完整性
        if len(full_text) > 8000:
            # 截取前80%，确保包含完整的剧情发展
            cutoff = int(len(full_text) * 0.8)
            # 找到最近的句号或感叹号，确保句子完整
            for i in range(cutoff, min(cutoff + 200, len(full_text))):
                if full_text[i] in '。！？':
                    full_text = full_text[:i+1] + "\n\n[剧情继续，因篇幅限制仅分析至此]"
                    break
        
        return full_text

    def parse_ai_response(self, response: str) -> Dict:
        """解析AI响应"""
        try:
            # 提取JSON部分
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_text = response[start:end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]
            
            return json.loads(json_text)
        except Exception as e:
            print(f"  解析AI响应失败: {e}")
            return {"highlights": []}

    def fallback_analysis(self, episode_file: str) -> Dict:
        """备用分析方法"""
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        episode_num = episode_match.group(1) if episode_match else "1"
        
        return {
            "episode_theme": f"第{episode_num}集精彩内容",
            "highlights": [
                {
                    "title": f"第{episode_num}集精彩片段",
                    "time_range": "10-13分钟",
                    "plot_point": "重要剧情发展",
                    "emotional_impact": "情感高潮",
                    "key_content": "核心剧情内容"
                }
            ]
        }

    def find_highlights(self, subtitles: List[Dict], analysis: Dict) -> List[Dict]:
        """根据AI分析结果找到具体的连贯字幕片段"""
        highlights = analysis.get('highlights', [])
        result_clips = []
        
        for highlight in highlights:
            # 使用AI提供的分钟范围
            start_min = highlight.get('start_minute', 0)
            end_min = highlight.get('end_minute', start_min + 3)
            
            start_seconds = start_min * 60
            end_seconds = end_min * 60
            
            # 找到时间范围内的所有字幕
            segment_subs = [sub for sub in subtitles 
                          if start_seconds <= sub['start_seconds'] <= end_seconds]
            
            if segment_subs:
                # 扩展边界确保完整场景
                complete_segment = self.ensure_complete_scene(segment_subs, subtitles, start_seconds, end_seconds)
                
                if complete_segment and len(complete_segment) >= 3:  # 至少3条字幕
                    result_clips.append({
                        'title': highlight.get('title', '精彩片段'),
                        'subtitles': complete_segment,
                        'plot_significance': highlight.get('plot_significance', ''),
                        'emotional_core': highlight.get('emotional_core', ''),
                        'key_dialogue': highlight.get('key_dialogue', ''),
                        'connection_to_story': highlight.get('connection_to_story', ''),
                        'why_essential': highlight.get('why_essential', ''),
                        'ai_selected': True
                    })
        
        return result_clips

    def ensure_complete_scene(self, segment_subs: List[Dict], all_subs: List[Dict], 
                            target_start: float, target_end: float) -> List[Dict]:
        """确保完整场景边界，而不是简单的句子完整性"""
        if not segment_subs:
            return []
        
        # 找到在全部字幕中的位置
        start_idx = next((i for i, sub in enumerate(all_subs) 
                         if sub['index'] == segment_subs[0]['index']), 0)
        end_idx = next((i for i, sub in enumerate(all_subs) 
                       if sub['index'] == segment_subs[-1]['index']), len(all_subs) - 1)
        
        # 场景开始标识词
        scene_starters = ['突然', '这时', '忽然', '当时', '那时', '现在', '接着', '然后', '随后']
        # 场景结束标识词  
        scene_enders = ['走了', '离开了', '结束了', '完了', '好了', '算了', '再见', '拜拜']
        
        # 向前扩展寻找场景开始
        extend_start = start_idx
        for i in range(start_idx - 1, max(0, start_idx - 15), -1):  # 最多向前15条
            text = all_subs[i]['text']
            # 如果找到明显的场景开始，就从这里开始
            if any(starter in text for starter in scene_starters):
                extend_start = i
                break
            # 如果遇到明显的场景结束，就不再向前
            if any(ender in text for ender in scene_enders):
                break
            # 如果时间差距太大（超过30秒），停止扩展
            if start_idx > 0 and all_subs[start_idx]['start_seconds'] - all_subs[i]['start_seconds'] > 30:
                break
        
        # 向后扩展寻找场景结束
        extend_end = end_idx
        for i in range(end_idx + 1, min(len(all_subs), end_idx + 15)):  # 最多向后15条
            text = all_subs[i]['text']
            # 如果找到明显的场景结束，就在这里结束
            if any(ender in text for ender in scene_enders):
                extend_end = i
                break
            # 如果遇到新场景开始，停止扩展
            if any(starter in text for starter in scene_starters):
                break
            # 如果时间差距太大（超过30秒），停止扩展
            if all_subs[i]['start_seconds'] - all_subs[end_idx]['start_seconds'] > 30:
                break
        
        final_segment = all_subs[extend_start:extend_end + 1]
        
        # 检查最终片段的合理性
        if final_segment:
            duration = final_segment[-1]['end_seconds'] - final_segment[0]['start_seconds']
            # 如果片段太短或太长，回退到原始范围加小幅扩展
            if duration < 60 or duration > 300:
                buffer_start = max(0, start_idx - 5)
                buffer_end = min(len(all_subs) - 1, end_idx + 5)
                final_segment = all_subs[buffer_start:buffer_end + 1]
        
        return final_segment

    def create_clips(self, episode_file: str, highlights: List[Dict]) -> List[str]:
        """创建视频片段"""
        video_file = self.find_video_file(episode_file)
        if not video_file:
            print(f"  未找到视频文件: {episode_file}")
            return []
        
        created_clips = []
        
        for i, highlight in enumerate(highlights, 1):
            clip_file = self.create_single_clip(video_file, highlight, episode_file, i)
            if clip_file:
                created_clips.append(clip_file)
                # 生成说明文件
                self.create_clip_description(clip_file, highlight)
        
        return created_clips

    def find_video_file(self, srt_file: str) -> Optional[str]:
        """查找对应的视频文件"""
        base_name = os.path.splitext(srt_file)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        
        videos_dir = 'videos'
        if not os.path.exists(videos_dir):
            return None
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(videos_dir, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 集数匹配
        episode_match = re.search(r'[Ee](\d+)', base_name)
        if episode_match:
            episode_num = episode_match.group(1)
            
            for file in os.listdir(videos_dir):
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    file_episode = re.search(r'[Ee](\d+)', file)
                    if file_episode and file_episode.group(1) == episode_num:
                        return os.path.join(videos_dir, file)
        
        return None

    def create_single_clip(self, video_file: str, highlight: Dict, 
                          episode_file: str, clip_num: int) -> Optional[str]:
        """创建单个视频片段"""
        try:
            subtitles = highlight['subtitles']
            if not subtitles:
                return None
            
            # 计算时间
            start_time = subtitles[0]['start']
            end_time = subtitles[-1]['end']
            
            start_seconds = self.time_to_seconds(start_time) - 2  # 2秒缓冲
            end_seconds = self.time_to_seconds(end_time) + 2
            duration = end_seconds - start_seconds
            
            # 检查时长
            if duration < 30:  # 太短
                print(f"    片段过短，跳过: {duration:.1f}秒")
                return None
            
            if duration > 300:  # 超过5分钟，截取到5分钟
                duration = 300
            
            # 生成文件名
            episode_match = re.search(r'[Ee](\d+)', episode_file)
            ep_num = episode_match.group(1) if episode_match else "1"
            
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', highlight['title'])
            output_name = f"E{ep_num}_{clip_num:02d}_{safe_title}.mp4"
            output_path = os.path.join('output_clips', output_name)
            
            print(f"    剪辑: {highlight['title']} ({duration:.1f}秒)")
            
            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(max(0, start_seconds)),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-crf', '23',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"      ✅ 成功: {size_mb:.1f}MB")
                return output_path
            else:
                print(f"      ❌ 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
                return None
                
        except Exception as e:
            print(f"      ❌ 剪辑出错: {e}")
            return None

    def create_clip_description(self, clip_file: str, highlight: Dict):
        """创建片段说明文件"""
        desc_file = clip_file.replace('.mp4', '_说明.txt')
        
        content = f"""📺 短视频片段说明
{"=" * 30}

片段标题: {highlight['title']}

核心剧情点: {highlight['plot_point']}

情感冲击: {highlight['emotional_impact']}

关键内容: {highlight['key_content']}

剪辑说明: 
本片段从完整剧情中精选，保持了故事的连贯性和完整性。
包含了重要的剧情转折和情感高潮，适合作为短视频展示。

时间轴对应:
"""
        
        # 添加字幕时间轴
        for subtitle in highlight['subtitles'][:5]:  # 显示前5条
            content += f"{subtitle['start']} --> {subtitle['end']}: {subtitle['text']}\n"
        
        if len(highlight['subtitles']) > 5:
            content += f"... 还有 {len(highlight['subtitles']) - 5} 条字幕\n"
        
        try:
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"      创建说明文件失败: {e}")

    def generate_summary_report(self, results: List[Dict]):
        """生成总结报告"""
        report_path = os.path.join('output_clips', '剪辑总结报告.txt')
        
        total_clips = sum(result['clips_created'] for result in results)
        
        content = f"""📺 智能剪辑系统 - 总结报告
{"=" * 50}

📊 总体统计:
• 处理集数: {len(results)} 集
• 创建短视频: {total_clips} 个
• 输出目录: output_clips/

📋 详细信息:
"""
        
        for result in results:
            content += f"\n{result['episode']}:\n"
            content += f"  • 创建短视频: {result['clips_created']} 个\n"
            
            for clip in result['clips']:
                clip_name = os.path.basename(clip)
                content += f"    - {clip_name}\n"
        
        content += f"\n💡 使用建议:\n"
        content += "• 每个短视频都有对应的说明文件\n"
        content += "• 建议按集数和序号顺序观看\n"
        content += "• 所有片段保持了剧情的连贯性\n"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 总结报告: {report_path}")
        except Exception as e:
            print(f"生成报告失败: {e}")

    def time_to_seconds(self, time_str: str) -> float:
        """时间转秒数"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0


def main():
    """主函数"""
    print("🎬 统一智能剪辑系统")
    print("=" * 40)
    
    clipper = UnifiedVideoClipper()
    
    # 检查环境
    srt_files = clipper.get_srt_files()
    if not srt_files:
        print("❌ srt/目录中没有字幕文件")
        print("请将.srt字幕文件放入srt/目录")
        return
    
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    
    if not video_files:
        print("❌ videos/目录中没有视频文件")
        print("请将视频文件放入videos/目录")
        return
    
    print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    # 开始处理
    results = clipper.process_all_episodes()
    
    total_clips = sum(r['clips_created'] for r in results)
    print(f"\n🎉 处理完成!")
    print(f"📺 处理了 {len(results)} 集")
    print(f"🎬 创建了 {total_clips} 个短视频")
    print(f"📁 输出目录: output_clips/")


if __name__ == "__main__":
    main()
