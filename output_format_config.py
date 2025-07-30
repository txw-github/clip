
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
标准化输出格式配置
解决问题4-8：跨集连贯性、固定输出格式、内容亮点、错别字修正等
"""

class OutputFormatConfig:
    """标准化输出格式配置类"""
    
    # 标准文件命名格式
    FILE_NAMING = {
        'episode_report': 'E{episode_num}_完整剧情分析报告.txt',
        'segment_analysis': 'E{episode_num}_{title}_分析报告.txt',
        'video_clip': 'E{episode_num}_{title}.mp4',
        'subtitle_file': 'E{episode_num}_{title}_旁白.srt',
        'series_summary': '全剧剧情连贯性分析.txt'
    }
    
    # 错别字修正词典 (问题7)
    TYPO_CORRECTIONS = {
        # 繁体字修正
        '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
        '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
        '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
        '結束': '结束', '問題': '问题', '機會': '机会', '設計': '设计',
        
        # 日文汉字修正
        '検察官': '检察官', '検查': '检查', '証人': '证人',
        '実現': '实现', '実際': '实际', '実証': '实证',
        '対話': '对话', '対応': '对应', '対象': '对象',
        '関係': '关系', '関連': '关联', '関心': '关心',
        
        # 常见打字错误
        '证剧': '证据', '发线': '发现', '决订': '决定',
        '选泽': '选择', '调叉': '调查', '审判': '审判'
    }
    
    # 标准报告模板 (问题5)
    REPORT_TEMPLATE = """📺 第{episode_num}集 完整剧情分析报告
{"=" * 100}

📊 基本信息:
• 集数: 第{episode_num}集
• 文件: {source_file}
• 剧情点数量: {segment_count} 个
• 成功片段: {clip_count} 个
• 总时长: {total_duration} 秒 ({duration_minutes} 分钟)

🎯 主线剧情:
{main_storyline}

🔗 跨集连贯性分析:
【与前集衔接】: {prev_connection}
【为下集铺垫】: {next_setup}

✨ 内容亮点总览:
{content_highlights}

🎭 剧情点详细分析:
{detailed_segments}

{"=" * 100}
📋 标准化输出格式总结:
{"=" * 100}

🎬 制作规格:
• 剧情点智能识别: 5种类型自动分类
• 片段时长控制: 每个片段2-3分钟
• 非连续合并: 支持跳跃式时间段智能拼接
• 错别字修正: 自动修正常见繁体字和错误
• 旁白生成: 专业旁观者叙述，详细清晰

🔗 连贯性保证:
• 集内连贯: 所有片段组合完整讲述本集故事
• 跨集衔接: 明确标注与前后集的关联点
• 主线追踪: 重点追踪核心案件发展脉络

✨ 质量标准:
• 戏剧张力: 每个片段都有冲突或转折点
• 观看体验: 适合短视频平台传播
• 故事完整: 每个片段都有起承转合
• 信息准确: 字幕错误已修正，便于剪辑参考

生成时间: {generation_time}
系统版本: 智能剧情点剪辑系统 v3.0
"""
    
    # 片段分析模板
    SEGMENT_TEMPLATE = """
{"=" * 60}
片段{segment_num}: {title}
{"=" * 60}
🎭 类型: {plot_type}
📊 评分: {score}/100
⏱️ 时间: {start_time} --> {end_time} ({duration}秒)
💡 意义: {plot_significance}

🎙️ 旁观者叙述:
{narration}

📝 关键台词 (已修正错别字):
{key_dialogues}

✨ 本片段亮点:
{highlights}

🔗 连贯性分析:
{continuity_analysis}

📄 内容摘要: {content_summary}
"""
    
    # 跨集连贯性分析规则 (问题4)
    CONTINUITY_RULES = {
        'previous_connection_keywords': {
            '继续': "承接前集未完成的情节线，故事连续发展",
            '回到': "回顾前集关键事件，为本集发展做铺垫",
            '回想': "回顾前集关键事件，为本集发展做铺垫",
            '申诉': "在前集基础上启动申诉程序",
            '听证会': "前集申诉准备完毕，本集进入听证阶段"
        },
        
        'next_setup_keywords': {
            '继续': "本集情节未完，下集将继续发展",
            '待续': "本集情节未完，下集将继续发展",
            '申诉': "申诉准备工作完成，下集听证会即将开始",
            '听证会': "听证会准备就绪，下集法庭激辩即将展开",
            '证据': "新证据浮现，下集案件将迎来重大转折",
            '真相': "真相即将大白，下集将有重大揭露"
        }
    }
    
    # 内容亮点提取规则 (问题6)
    HIGHLIGHT_RULES = {
        '关键冲突': [
            "激烈冲突场面，戏剧张力强烈",
            "核心争议焦点，观点针锋相对",
            "情绪对抗激烈，冲突升级明显"
        ],
        '线索揭露': [
            "关键线索首次披露，推进主线剧情",
            "重要证据曝光，案件迎来转折",
            "真相逐步浮现，悬念逐步解开"
        ],
        '人物转折': [
            "角色重要转折时刻，人物发展关键节点",
            "内心挣扎清晰展现，角色深度刻画",
            "命运转折点，后续发展关键"
        ],
        '情感爆发': [
            "情感高潮时刻，感染力强",
            "内心情绪彻底释放，真情流露",
            "感人至深的情感表达"
        ],
        '重要对话': [
            "关键信息交流，推进剧情发展",
            "重要决策讨论，影响后续走向",
            "深度对话展现角色关系"
        ]
    }
    
    # 主线剧情识别关键词
    MAIN_STORYLINE_KEYWORDS = {
        '四二八案': "四二八案调查进展",
        '628案': "628旧案重新审视", 
        '628旧案': "628旧案重新审视",
        '申诉': "申诉程序启动",
        '听证会': "听证会激辩",
        '张园': "张园霸凌事件真相",
        '段洪山': "段洪山父女情深",
        '霸凌': "校园霸凌事件调查",
        '正当防卫': "正当防卫争议核心"
    }
    
    @staticmethod
    def correct_typos(text: str) -> str:
        """修正文本中的错别字"""
        corrected = text
        for old, new in OutputFormatConfig.TYPO_CORRECTIONS.items():
            corrected = corrected.replace(old, new)
        return corrected
    
    @staticmethod
    def generate_episode_filename(episode_num: str, file_type: str, title: str = "") -> str:
        """生成标准化文件名"""
        template = OutputFormatConfig.FILE_NAMING.get(file_type, "E{episode_num}_{title}.txt")
        safe_title = title.replace(" ", "_").replace("：", "_") if title else "default"
        return template.format(episode_num=episode_num, title=safe_title)
    
    @staticmethod
    def extract_highlights(plot_type: str, content: str, score: float) -> list:
        """提取内容亮点"""
        highlights = []
        
        # 基于剧情点类型的亮点
        type_highlights = OutputFormatConfig.HIGHLIGHT_RULES.get(plot_type, [])
        if type_highlights:
            highlights.extend(type_highlights)
        
        # 基于评分的亮点
        if score >= 80:
            highlights.append("核心剧情片段，观看价值极高")
        elif score >= 60:
            highlights.append("重要剧情节点，值得重点关注")
        
        # 基于内容的具体亮点
        if '真相' in content or '发现' in content:
            highlights.append("真相揭露时刻，情节反转精彩")
        if '证据' in content:
            highlights.append("关键证据展示，案件进展重要")
        if '决定' in content or '选择' in content:
            highlights.append("关键决策时刻，影响后续发展")
        
        return highlights
    
    @staticmethod
    def analyze_continuity(content: str, plot_type: str, position: str) -> str:
        """分析跨集连贯性"""
        continuity_points = []
        
        rules = OutputFormatConfig.CONTINUITY_RULES
        
        if position == "previous":
            for keyword, description in rules['previous_connection_keywords'].items():
                if keyword in content:
                    continuity_points.append(description)
        elif position == "next":
            for keyword, description in rules['next_setup_keywords'].items():
                if keyword in content:
                    continuity_points.append(description)
        
        # 基于剧情点类型的连贯性分析
        if plot_type == '线索揭露':
            if position == "next":
                continuity_points.append("关键线索已经披露，下集将深入追查")
        elif plot_type == '关键冲突':
            if position == "next":
                continuity_points.append("冲突已经爆发，下集将面临更大挑战")
        
        return "；".join(continuity_points) if continuity_points else "保持剧情逻辑连贯性"
