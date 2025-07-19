
import os
import re
import json
from typing import Dict, List, Optional

def time_to_seconds(time_str: str) -> float:
    """将SRT时间格式转换为秒数"""
    try:
        h, m, s_ms = time_str.split(':')
        s, ms = s_ms.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    except (ValueError, IndexError) as e:
        print(f"⚠ 时间格式错误 {time_str}: {e}")
        return 0.0

def seconds_to_time(seconds: float) -> str:
    """将秒数转换为SRT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def find_subtitle_files(directories: List[str] = None) -> List[str]:
    """查找所有字幕文件"""
    if directories is None:
        directories = ['srt', '.']
    
    files = []
    patterns = ['e0', 'e1', 'ep', 'episode', '第', '集', 's01e', 's1e', 'ep.', 'e.']
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for f in os.listdir(directory):
            if f.endswith(('.txt', '.srt')):
                file_lower = f.lower()
                if any(pattern in file_lower for pattern in patterns):
                    file_path = os.path.join(directory, f) if directory != '.' else f
                    files.append(file_path)
    
    return sorted(files)

def safe_json_parse(text: str) -> Dict:
    """安全的JSON解析"""
    try:
        # 提取JSON
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            json_text = text[json_start:json_end].strip()
        else:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                json_text = text[start:end]
            else:
                json_text = text

        return json.loads(json_text)
    except json.JSONDecodeError:
        return {}

def validate_config(config: Dict) -> bool:
    """验证配置有效性"""
    required_fields = ['enabled', 'api_key', 'model', 'url']
    return all(field in config for field in required_fields) and config.get('enabled', False)

def get_episode_number(filename: str) -> str:
    """从文件名中提取集数"""
    match = re.search(r'[Ee](\d+)', filename)
    if match:
        return match.group(1)
    return "00"

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.replace('：', '_').replace(' & ', '_').replace('/', '_')
    return filename.strip()
