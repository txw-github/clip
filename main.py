## 分析要求
1. 智能识别3-5个最精彩的片段
2. 每个片段2-3分钟，包含完整对话
3. 确保片段间逻辑连贯
4. 生成专业旁白解说和字幕提示

请严格按照以下JSON格式输出：

```json
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "genre_type": "剧情类型",
        "main_theme": "本集核心主题"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "精彩标题",
            "start_time": "00:XX:XX,XXX",
            "end_time": "00:XX:XX,XXX",
            "duration_seconds": 180,
            "plot_significance": "剧情重要意义",
            "professional_narration": "完整的专业旁白解说稿",
            "highlight_tip": "一句话字幕亮点提示"
        }}
    ]
}}
```"""

        system_prompt = "你是专业的影视内容分析专家，专长电视剧情深度解构与叙事分析。"

        try:
            response = self.call_ai_api(prompt, system_prompt)
            if response:
                parsed_result = self.parse_ai_response(response)
                if parsed_result:
                    print(f"✅ AI分析成功：{len(parsed_result.get('highlight_segments', []))} 个片段")
                    self.save_analysis_cache(cache_key, filename, parsed_result)
                    return parsed_result
        except Exception as e:
            print(f"⚠️ AI分析失败: {e}")

        return None

    def parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("", start)
                json_text = response[start:end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]

            result = json.loads(json_text)

            if 'highlight_segments' in result and 'episode_analysis' in result:
                return result
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
        return None

    def extract_episode_number(self, filename: str) -> str:
        """从文件名提取集数，使用字符串排序"""
        base_name = os.path.splitext(filename)[0]
        return base_name

    def get_analysis_cache_key(self, subtitles: List[Dict]) -> str:
        """生成分析缓存键"""
        content = json.dumps(subtitles, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def load_analysis_cache(self, cache_key: str, filename: str) -> Optional[Dict]:
        """加载分析缓存"""
        cache_file = os.path.join(self.cache_folder, f"{filename}_{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                cache_content = platform_fix.safe_file_read(cache_file)
                if cache_content:
                    analysis = json.loads(cache_content)
                    print(f"💾 使用缓存分析: {filename}")
                    return analysis
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
        return None

    def save_analysis_cache(self, cache_key: str, filename: str, analysis: Dict):
        """保存分析缓存"""
        cache_file = os.path.join(self.cache_folder, f"{filename}_{cache_key}.json")
        try:
            cache_content = json.dumps(analysis, ensure_ascii=False, indent=2)
            platform_fix.safe_file_write(cache_file, cache_content)
            print(f"💾 保存分析缓存: {filename}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        base_name = os.path.splitext(subtitle_filename)[0]

        # 精确匹配
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for filename in os.listdir(self.video_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if base_name.lower() in filename.lower():
                    return os.path.join(self.video_folder, filename)

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
        """检查FFmpeg是否可用"""
        try:
            result = platform_fix.safe_subprocess_run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def create_video_clips(self, analysis: Dict, video_file: str, subtitle_filename: str) -> List[str]:
        """创建视频片段"""
        created_clips = []

        if not self.check_ffmpeg():
            print("❌ 未找到FFmpeg，无法剪辑视频")
            return []

        for segment in analysis.get('highlight_segments', []):
            segment_id = segment['segment_id']
            title = segment['title']

            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clip_filename = f"{safe_title}_seg{segment_id}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)

            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                print(f"✅ 片段已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue

            # 剪辑视频
            temp_clip_path = clip_path.replace(".mp4", "_temp.mp4")
            if self.create_single_clip(video_file, segment, temp_clip_path):
                # 添加旁白字幕
                if self.add_narration_subtitles(temp_clip_path, segment, clip_path):
                    created_clips.append(clip_path)
                else:
                    # 如果添加字幕失败，则保留原始剪辑
                    created_clips.append(temp_clip_path)
                    os.rename(temp_clip_path, clip_path)  # 重命名为最终文件名

                # 删除临时文件
                if os.path.exists(temp_clip_path):
                    os.remove(temp_clip_path)

            # 生成旁白文件
            self.create_narration_file(clip_path, segment)

        return created_clips

    def create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = segment['start_time']
            end_time = segment['end_time']

            print(f"🎬 剪辑片段: {os.path.basename(output_path)}")
            print(f"   时间: {start_time} --> {end_time}")

            # 时间转换
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0:
                print(f"   ❌ 无效时间段")
                return False

            # 添加缓冲确保对话完整
            buffer_start = max(0, start_seconds - 3)
            buffer_duration = duration + 6

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

            result = platform_fix.safe_subprocess_run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300
            )

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

    def add_narration_subtitles(self, video_path: str, segment: Dict, output_path: str) -> bool:
        """为视频添加旁白字幕"""
        try:
            print(f"   🎙️ 生成旁白字幕...")

            # 生成旁白内容
            narration = self.generate_segment_narration(segment)

            if not narration:
                return False

            # 获取视频时长
            video_duration = segment.get('duration_seconds', 180)

            # 使用增强版旁白生成器创建字幕滤镜
            narration_generator = EnhancedNarrationGenerator(self.ai_config)
            subtitle_filters = narration_generator.create_subtitle_filters(narration, video_duration)

            # 添加主标题（开头3秒）
            title = segment.get('title', '精彩片段')[:30]
            title_clean = self.clean_text_for_ffmpeg(title)
            subtitle_filters.insert(0,
                f"drawtext=text='{title_clean}':fontsize=28:fontcolor=white:"
                f"x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.8:boxborderw=4:"
                f"enable='between(t,0,3)'"
            )

            if not subtitle_filters:
                return False

            # 合并所有滤镜
            filter_complex = ",".join(subtitle_filters)

            # FFmpeg命令添加字幕
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_complex,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                output_path,
                '-y'
            ]

            result = platform_fix.safe_subprocess_run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )

            success = result.returncode == 0 and os.path.exists(output_path)
            if success:
                print(f"   ✅ 旁白字幕添加成功")
                # 导出旁白文本文件
                narration_generator.export_narration_text(narration, output_path)
            else:
                error_msg = result.stderr[:100] if result.stderr else '未知错误'
                print(f"   ⚠️ 字幕添加失败: {error_msg}")

            return success

        except Exception as e:
            print(f"   ⚠️ 字幕处理异常: {e}")
            return False

    def create_narration_file(self, video_path: str, segment: Dict):
        """创建专业旁白解说文件"""
        try:
            narration_path = video_path.replace('.mp4', '_旁白解说.txt')

            content = f"""📺 {segment['title']} - 专业旁白解说
{"=" * 60}

🎬 片段信息:
• 标题: {segment['title']}
• 时长: {segment.get('duration_seconds', 0)} 秒
• 剧情意义: {segment.get('plot_significance', '关键剧情节点')}

🎙️ 专业旁白解说稿:
{segment.get('professional_narration', '精彩剧情片段')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            platform_fix.safe_file_write(narration_path, content)

            print(f"   📜 生成旁白解说: {os.path.basename(narration_path)}")

        except Exception as e:
            print(f"   ⚠️ 旁白文件生成失败: {e}")

    def process_single_episode(self, subtitle_file: str) -> Optional[bool]:
        """处理单集完整流程"""
        print(f"\n📺 处理: {subtitle_file}")

        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        subtitles = self.parse_subtitle_file(subtitle_path)

        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False

        # 2. AI分析
        analysis = self.analyze_episode_with_ai(subtitles, subtitle_file)
        if analysis is None:
            print(f"⏸️ AI不可用，{subtitle_file} 已跳过")
            return None
        elif not analysis:
            print(f"❌ AI分析失败，跳过此集")
            return False

        # 3. 找到视频文件
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False

        print(f"📁 视频文件: {os.path.basename(video_file)}")

        # 4. 创建视频片段
        created_clips = self.create_video_clips(analysis, video_file, subtitle_file)

        clips_count = len(created_clips)
        print(f"✅ {subtitle_file} 处理完成: {clips_count} 个短视频")

        return clips_count > 0

    def process_all_episodes(self):
        """处理所有集数 - 主流程"""
        print("\n🚀 开始智能剪辑处理")
        print("=" * 50)

        # 检查字幕文件
        subtitle_files = [f for f in os.listdir(self.srt_folder) 
                         if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        if not subtitle_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return

        # 按字符串排序（即按文件名排序）
        subtitle_files.sort()

        print(f"📝 找到 {len(subtitle_files)} 个字幕文件")

        # 处理每一集
        total_success = 0
        total_clips = 0
        total_skipped = 0

        for subtitle_file in subtitle_files:
            try:
                success = self.process_single_episode(subtitle_file)
                if success:
                    total_success += 1
                elif success is None:
                    total_skipped += 1

                # 统计片段数
                episode_clips = [f for f in os.listdir(self.output_folder) 
                               if f.endswith('.mp4')]
                total_clips = len(episode_clips)

            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 出错: {e}")

        # 最终报告
        print(f"\n📊 处理完成:")
        print(f"✅ 成功处理: {total_success}/{len(subtitle_files)} 集")
        print(f"🎬 生成片段: {total_clips} 个")
        print(f"⏸️ 跳过集数: {total_skipped} 集")

    def install_dependencies(self):
        """安装必要依赖"""
        print("🔧 检查并安装必要依赖...")

        dependencies = ['openai', 'google-genai']

        for package in dependencies:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} 已安装")
            except ImportError:
                print(f"📦 安装 {package}...")
                try:
                    result = platform_fix.safe_subprocess_run(
                        [sys.executable, '-m', 'pip', 'install', package],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ {package} 安装成功")
                    else:
                        print(f"❌ {package} 安装失败: {result.stderr}")
                except Exception as e:
                    print(f"❌ {package} 安装失败: {e}")

    def clear_cache(self):
        """清空分析缓存"""
        import shutil
        if os.path.exists(self.cache_folder):
            shutil.rmtree(self.cache_folder)
            os.makedirs(self.cache_folder)
            print(f"✅ 已清空分析缓存")
        else:
            print(f"📝 缓存目录不存在")

    def show_file_status(self):
        """显示文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        video_files = [f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
        output_files = [f for f in os.listdir(self.output_folder) if f.endswith('.mp4')]

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

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 50)
            print("🎬 电视剧智能剪辑系统")
            print("=" * 50)

            # 显示状态
            ai_status = "🤖 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"AI状态: {ai_status}")

            print("\n🎯 主要功能:")
            print("1. 🤖 配置AI接口")
            print("2. 🎬 开始智能剪辑")
            print("3. 📁 查看文件状态")
            print("4. 🔧 安装系统依赖")
            print("5. 🔄 清空分析缓存")
            print("0. ❌ 退出系统")

            try:
                choice = input("\n请选择操作 (0-5): ").strip()

                if choice == '1':
                    self.configure_ai_interactive()
                elif choice == '2':
                    self.process_all_episodes()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '4':
                    self.install_dependencies()
                elif choice == '5':
                    self.clear_cache()
                elif choice == '0':
                    print("\n👋 感谢使用电视剧智能剪辑系统！")
                    break
                else:
                    print("❌ 无效选择，请输入0-5")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")

    def generate_segment_narration(self, segment: Dict) -> Dict:
        """生成片段旁白内容"""
        if not self.ai_config.get('enabled'):
            return {}

        try:
            title = segment.get('title', '精彩片段')
            plot_significance = segment.get('plot_significance', '关键剧情节点')
            professional_narration = segment.get('professional_narration', '精彩剧情片段')
            highlight_tip = segment.get('highlight_tip', '一句话亮点')

            prompt = f"""# 旁白内容生成

请为以下电视剧片段生成更专业的旁白内容：

## 片段信息
• 标题: {title}
• 剧情意义: {plot_significance}
• 解说稿: {professional_narration}
• 亮点提示: {highlight_tip}

## 生成要求
1. 主题解说：概括片段核心看点，1-2句话
2. 字幕亮点：生成吸引眼球的字幕亮点提示，1句话

请严格按照以下JSON格式输出：

```json
{{
    "main_explanation": "片段核心看点",
    "highlight_tip": "吸引眼球的字幕亮点提示"
}}
```"""

            system_prompt = "你是专业的影视内容创作专家，专长电视剧情深度解说与叙事吸引。"

            response = self.call_ai_api(prompt, system_prompt)
            if response:
                narration = self.parse_narration_response(response)
                return narration

        except Exception as e:
            print(f"⚠️ 旁白生成失败: {e}")
            return {}

    def parse_narration_response(self, response: str) -> Dict:
        """解析旁白生成响应"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("