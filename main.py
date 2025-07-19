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
        print("支持的模型:")
        for i, model in enumerate(self.supported_models, 1):
            print(f"{i}. {model}")

        while True:
            try:
                choice = input(f"\n选择模型 (1-{len(self.supported_models)}): ")
                if choice.isdigit() and 1 <= int(choice) <= len(self.supported_models):
                    selected_model = self.supported_models[int(choice) - 1]
                    break
                else:
                    print("❌ 无效选择，请重试")
            except:
                print("❌ 请输入数字")

        api_key = input("输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        base_url = input(f"API地址 (回车使用默认 {self.ai_config['base_url']}): ").strip()
        if not base_url:
            base_url = self.ai_config['base_url']

        # 测试API连接
        print("🔍 测试API连接...")
        config = {
            'enabled': True,
            'base_url': base_url,
            'api_key': api_key,
            'model': selected_model
        }

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
                    {
                        "role": "system",
                        "content": "你是专业的电视剧剧情分析师"
                    },
                    {
                        "role": "user", 
                        "content": "测试连接"
                    }
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

    def call_ai_api(self, prompt: str, system_prompt: str = "你是专业的电视剧剧情分析师") -> Optional[str]:
        """调用AI API"""
        if not self.ai_config.get('enabled'):
            return None

        try:
            payload = {
                "model": self.ai_config['model'],
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }

            url = self.ai_config['base_url'] + "/chat/completions"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.ai_config["api_key"]}',
                'User-Agent': 'TV-Clipper/1.0.0',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()

                # 处理deepseek-r1的特殊格式
                if self.ai_config['model'] == 'deepseek-r1':
                    message = data['choices'][0]['message']
                    if hasattr(message, 'reasoning_content'):
                        print(f"🧠 AI思考过程: {message.reasoning_content[:100]}...")
                    return message.get('content', '')
                else:
                    return data['choices'][0]['message']['content']
            else:
                print(f"⚠ API调用失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠ AI调用异常: {e}")
            return None

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
            return self.fallback_analysis(subtitles, episode_name)

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
                return self.process_ai_analysis(result, subtitles, episode_name)

            except Exception as e:
                print(f"⚠ AI回复解析失败: {e}")
                return self.fallback_analysis(subtitles, episode_name)

        return self.fallback_analysis(subtitles, episode_name)

    def process_ai_analysis(self, ai_result: Dict, subtitles: List[Dict], episode_name: str) -> Dict:
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

    def fallback_analysis(self, subtitles: List[Dict], episode_name: str) -> Dict:
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

    def time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def analyze_all_episodes(self) -> List[Dict]:
        """分析所有剧集"""
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
                    # 高级智能剪辑
                    print("\n🚀 启动高级智能剪辑系统...")
                    print("特性：")
                    print("• AI深度剧情理解，非固定规则")
                    print("• 完整上下文分析，避免剧情割裂")  
                    print("• 多段精彩识别，每集3-5个短视频")
                    print("• 自动视频剪辑+专业旁白")
                    print("• 保证跨集剧情连贯性")
                    print("• 字幕放srt/目录，视频放videos/目录")

                    try:
                        from advanced_clipper import AdvancedIntelligentClipper
                        clipper = AdvancedIntelligentClipper()
                        clipper.run_complete_analysis()
                    except ImportError:
                        print("❌ 高级剪辑模块未找到")
                    except Exception as e:
                        print(f"❌ 高级剪辑出错: {e}")

                elif choice == '3':
                    self.setup_ai_config()

                elif choice == '4':
                    # 查看多种报告
                    reports = [
                        '智能分析报告.txt',
                        'intelligent_clips/完整剧集连贯性分析.txt',
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

def view_last_results():
    """查看上次分析结果"""
    results_file = "smart_analysis_report.txt"
    if os.path.exists(results_file):
        print(f"\n📊 上次分析结果:")
        print("=" * 60)
        with open(results_file, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ 未找到分析结果，请先运行分析")

    input("\n按回车键继续...")

def show_api_config_menu():
    """显示API配置菜单"""
    while True:
        print("\n🔧 API配置和诊断")
        print("=" * 40)
        print("1. 🚀 快速配置API")
        print("2. 🔍 诊断API连接")
        print("3. 📋 查看当前配置")
        print("4. 🔄 重新配置API")
        print("0. 返回主菜单")

        choice = input("\n请选择 (0-4): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            from quick_api_config import main as config_main
            config_main()
        elif choice == "2":
            from diagnose_api import diagnose_api_connection, quick_fix_suggestions
            diagnose_api_connection()
            quick_fix_suggestions()
        elif choice == "3":
            show_current_config()
        elif choice == "4":
            from api_config_helper import config_helper
            config = config_helper.interactive_setup()
            if config.get('enabled'):
                print("✅ API重新配置成功！")
        else:
            print("❌ 无效选择，请重试")

def show_current_config():
    """显示当前API配置"""
    from api_config_helper import config_helper
    config = config_helper.load_config()

    print("\n📋 当前API配置:")
    print("-" * 30)

    if config.get('enabled'):
        print(f"✅ API状态: 已配置")
        print(f"🏢 服务商: {config.get('provider', '未知')}")
        print(f"🔗 API地址: {config.get('base_url', '未知')}")
        print(f"🤖 模型: {config.get('model', '未知')}")
        print(f"🔑 密钥: {config.get('api_key', '')[:10]}..." if config.get('api_key') else "🔑 密钥: 未设置")

        # 快速测试连接
        print(f"\n🔍 快速连接测试...")
        if config_helper._test_api_connection(config):
            print("✅ API连接正常")
        else:
            print("❌ API连接异常，建议运行诊断")
    else:
        print("❌ API状态: 未配置")
        print("💡 请先配置API以启用智能分析功能")

    input("\n按回车键继续...")

class MainMenu:
    def __init__(self):
        pass

    def show_menu(self):
        print("\n" + "=" * 60)
        print("📺 智能电视剧分析剪辑系统")
        print("=" * 60)
        print("请选择操作:")
        print("1. 📝 智能分析字幕")
        print("2. 🎬 高级智能剪辑 (推荐)")
        print("3. 📊 查看分析报告")
        print("4. 🔧 配置或诊断API")
        print("5. ❌ 退出")

    def get_action(self):
        choice = input("请输入选择 (1-5): ").strip()

        if choice == "1":
            return "analysis_only"
        elif choice == "2":
            return "full_process"
        elif choice == "3":
            return "view_results"
        elif choice == "4":
            return "api_config"
        elif choice == "5":
            return "exit"
        else:
            print("❌ 无效选择，请重新输入")
            return None

def main():
    """主函数"""
    print("🚀 智能电视剧分析剪辑系统启动")

    if not check_environment():
        input("\n按Enter键退出...")
        return

    try:
        system = AIClipperSystem()
        menu = MainMenu()

        while True:
            menu.show_menu()
            action = menu.get_action()

            if action == "analysis_only":
                system.analyze_all_episodes()
            elif action == "full_process":
                # 高级智能剪辑
                print("\n🚀 启动高级智能剪辑系统...")
                print("特性：")
                print("• AI深度剧情理解，非固定规则")
                print("• 完整上下文分析，避免剧情割裂")
                print("• 多段精彩识别，每集3-5个短视频")
                print("• 自动视频剪辑+专业旁白")
                print("• 保证跨集剧情连贯性")
                print("• 字幕放srt/目录，视频放videos/目录")

                try:
                    from advanced_clipper import AdvancedIntelligentClipper
                    clipper = AdvancedIntelligentClipper()
                    clipper.run_complete_analysis()
                except ImportError:
                    print("❌ 高级剪辑模块未找到")
                except Exception as e:
                    print(f"❌ 高级剪辑出错: {e}")
            elif action == "view_results":
                view_last_results()
            elif action == "api_config":
                show_api_config_menu()
            elif action == "exit":
                print("👋 感谢使用智能剪辑系统！")
                break
            else:
                pass # Invalid choice is already handled in get_action()

    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        input("\n按Enter键退出...")

if __name__ == "__main__":
    main()