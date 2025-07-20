
# 🎬 智能电视剧剪辑系统

专业的电视剧短视频剪辑工具，支持AI智能分析和规则分析双模式。

## ✨ 核心功能

- 🤖 **AI智能分析**: 支持多种大模型接口，智能识别精彩片段
- 📋 **规则分析**: 基于关键词和时间的传统分析方法
- 🔄 **混合模式**: AI分析 + 规则分析，确保最佳效果
- 🌐 **多接口支持**: 官方API、中转API、自定义API全支持
- 🧠 **智能推荐**: 根据使用场景自动推荐最佳配置

## 🚀 一键启动

```bash
python one_click_smart_start.py
```

这个脚本会：
1. 🔍 自动检测现有配置
2. 🧠 智能推荐最佳API配置
3. ⚙️ 一键完成所有设置
4. 🎬 直接启动剪辑系统

## 🌟 支持的AI模型

### 官方API (需要魔法上网)
- **Google Gemini**: `gemini-2.5-pro`, `gemini-2.5-flash`
- **OpenAI GPT**: `gpt-4o`, `gpt-4o-mini`
- **DeepSeek**: `deepseek-r1`, `deepseek-v3`

### 中转API (国内可访问)
- **ChatAI**: 支持Claude、GPT、Gemini、DeepSeek
- **算力云**: 支持DeepSeek、Qwen等国产模型
- **OpenRouter**: 支持多种开源模型

## 📖 快速配置指南

### 方法1: 智能推荐配置
```python
from smart_api_selector import smart_selector
smart_selector.smart_configure()
```

### 方法2: 快速配置ChatAI
```python
from quick_api_config import quick_setup_chataiapi
quick_setup_chataiapi()
```

### 方法3: 完整交互配置
```python
from api_config_helper import config_helper
config_helper.interactive_setup()
```

## 🔧 手动配置示例

### ChatAI中转API配置
```python
config = {
    'enabled': True,
    'provider': 'chataiapi',
    'api_key': 'sk-你的密钥',
    'model': 'claude-3-5-sonnet-20240620',
    'base_url': 'https://www.chataiapi.com/v1',
    'api_type': 'openai_compatible'
}
```

### Gemini官方API配置
```python
config = {
    'enabled': True,
    'provider': 'gemini_official',
    'api_key': '你的Gemini密钥',
    'model': 'gemini-2.5-flash',
    'api_type': 'gemini_official'
}
```

## 🎯 使用建议

### 🎭 电视剧剧情分析
- **推荐**: Claude-3.5-Sonnet 或 GPT-4o
- **特点**: 优秀的文本理解和剧情分析能力

### 🧠 复杂逻辑推理  
- **推荐**: DeepSeek-R1
- **特点**: 深度思考，提供详细推理过程

### ⚡ 快速响应需求
- **推荐**: Gemini-2.5-Flash
- **特点**: 响应速度快，成本较低

### 💰 成本控制
- **推荐**: 中转API + DeepSeek系列
- **特点**: 价格便宜，效果不错

## 🛠️ 问题排查

### API连接问题
```bash
python diagnose_api.py
```

### 重新配置
```bash
python quick_api_config.py
```

### 修复连接错误
```bash
python fix_unified_api.py
```

## 📋 使用流程

1. **配置AI接口** (可选但推荐)
2. **准备字幕文件** (SRT格式)
3. **运行剪辑分析**
4. **获取剪辑方案**
5. **导出结果**

## 🤝 技术支持

- 配置问题: 运行诊断脚本
- API问题: 检查密钥和网络
- 功能建议: 欢迎反馈

---

🎬 **让AI为您的短视频创作提供专业支持！**
